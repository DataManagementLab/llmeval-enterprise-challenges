import collections
import io
import json
import logging
import os
import random
import shutil
import statistics

import hydra
import numpy as np
import pandas as pd
import tqdm
from omegaconf import DictConfig, OmegaConf

from llms4de.data import get_download_dir, get_instances_dir, load_json, dump_json, dump_str, dump_cfg, load_str
from llms4de.evaluation.inspection import compute_cell_level_sparsity
from llms4de.model.generic import compute_cost_for_response, execute_requests, extract_text_from_response
from llms4de.preprocessing import shuffle_instances, sample_rows
from llms4de.prompting.linearize import linearize_table
from llms4de.prompting.parse import parse_list
from llms4de.prompting.template import fill_chat_template

logger = logging.getLogger(__name__)

adapt_width_random = random.Random(505592983762)
adapt_sparsity_random = random.Random(505995586388)


@hydra.main(version_base=None, config_path="../../../config/column_type_annotation", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    assert cfg.dataset.dataset_name == "enterprisetables_cta_pub", "This script is dataset-specific."
    download_dir = get_download_dir(cfg.task_name, cfg.dataset.dataset_name)
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    logger.debug("Load metadata.")
    metadata = {}  # sport --> (key --> (data_type --> (column_header --> column_type)))
    for sport in cfg.dataset.sports:
        metadata[sport] = load_json(download_dir / f"{sport}_metadata.json")

    all_column_types = set()
    all_column_types_by_data_type = collections.defaultdict(set)
    for sport in cfg.dataset.sports:
        for mappings in metadata[sport].values():
            for key, mapping in mappings.items():
                # there is a problem in this file:
                # https://github.com/DHBWMosbachWI/SportsTables/blob/main/basketball/metadata.json
                if isinstance(mapping, dict):
                    all_column_types = all_column_types.union(set(mapping.values()))
                    all_column_types_by_data_type[key] = all_column_types_by_data_type[key].union(set(mapping.values()))
    all_column_types = list(sorted(set(filter(lambda x: x is not None, all_column_types))))
    all_column_types_by_data_type = {key: list(sorted(set(filter(lambda x: x is not None, types)))) for key, types in
                                     all_column_types_by_data_type.items()}
    all_column_types_by_data_type["numerical_cols"].append(None)

    dump_json(all_column_types, instances_dir / "all_column_types.json")

    column_type2data_type = {}
    for key, values in all_column_types_by_data_type.items():
        for value in values:
            column_type2data_type[value] = key

    logger.debug("Glob table paths.")
    table_paths = []
    for sport in cfg.dataset.sports:
        table_paths += [(sport, path) for path in sorted(download_dir.joinpath(sport).glob("*.csv"))]

    table_paths = shuffle_instances(table_paths)

    ix = 0
    all_widths, all_sparsities = [], []
    total_cost = 0
    adapt_width_failures, adapt_descriptiveness_failures, adapt_data_types_failures = 0, 0, 0
    for sport, table_path in tqdm.tqdm(table_paths,
                                       desc=f"{cfg.task_name} - {cfg.dataset.dataset_name} - {cfg.exp_name} - preprocess"):
        instance_dir = instances_dir / f"{ix}"
        os.makedirs(instance_dir, exist_ok=True)

        dump_str(table_path.name[:-4], instance_dir / "table_name.txt")

        table = pd.read_csv(table_path)
        table = sample_rows(table, num_rows=cfg.dataset.adapt_num_rows, mode="random")
        new_columns = None
        if cfg.dataset.adapt_width:
            betavariate = adapt_width_random.betavariate(
                cfg.dataset.target_width_alpha,
                cfg.dataset.target_width_beta
            )
            target_width = int(betavariate ** cfg.dataset.target_width_exponent * cfg.dataset.target_width_multiplier)
            if len(table.columns) < target_width:
                target_num_new_columns = target_width - len(table.columns)
                try:
                    # generate list of column names
                    request = {
                        "model": cfg.dataset.adapt_width_model,
                        "messages": fill_chat_template(
                            OmegaConf.to_container(cfg.dataset.adapt_width_generate_column_names_chat_template),
                            table=linearize_table(
                                table,
                                None,
                                template="{{table}}",
                                mode="csv",
                                csv_params={"index": False, "header": True}
                            ),
                            num_new_columns=str(target_num_new_columns),
                            newline="\n"
                        ),
                        "max_tokens": None,
                        "temperature": cfg.dataset.adapt_width_temperature,
                        "seed": cfg.dataset.adapt_width_model_seed
                    }
                    response = execute_requests(
                        [request],
                        cfg.dataset.adapt_width_api_name,
                        force=cfg.dataset.adapt_force
                    )[0]
                    total_cost += compute_cost_for_response(response)
                    if total_cost > cfg.dataset.adapt_max_cost:
                        logger.error(f"adapting width: total_cost exceeds adapt_max_cost")
                        exit()
                    response_text = extract_text_from_response(response)
                    if response_text.startswith("```json"):
                        response_text = response_text[len("```json"):]
                    if response_text.endswith("```"):
                        response_text = response_text[:-len("```")]
                    response_text = response_text.strip()
                    new_column_names = parse_list(response_text, mode="json_list",
                                                  json_params={"strip": True, "strict": False})
                    if len(new_column_names) != target_num_new_columns:
                        logger.warning(
                            f"adapting width: generated an incorrect number of new column names ({len(new_column_names)} != {target_num_new_columns})"
                        )
                    # generate example rows
                    requests = []
                    for left in range(0, len(new_column_names), cfg.dataset.adapt_width_generate_data_chunk_size):
                        request = {
                            "model": cfg.dataset.adapt_width_model,
                            "messages": fill_chat_template(
                                OmegaConf.to_container(cfg.dataset.adapt_width_generate_data_chat_template),
                                table=linearize_table(
                                    table,
                                    None,
                                    template="{{table}}",
                                    mode="csv",
                                    csv_params={"index": False, "header": True}
                                ),
                                new_column_names=json.dumps(
                                    new_column_names[left:left + cfg.dataset.adapt_width_generate_data_chunk_size]),
                                num_example_rows=str(cfg.dataset.adapt_num_rows),
                                newline="\n"
                            ),
                            "max_tokens": None,
                            "temperature": cfg.dataset.adapt_width_temperature,
                            "seed": cfg.dataset.adapt_width_model_seed
                        }
                        requests.append(request)
                    responses = execute_requests(
                        requests,
                        cfg.dataset.adapt_width_api_name,
                        force=cfg.dataset.adapt_force
                    )
                    new_columns_chunks = []
                    existing_columns = set()
                    for response in responses:
                        total_cost += compute_cost_for_response(response)
                        response_text = extract_text_from_response(response)
                        if response_text.startswith("```csv"):
                            response_text = response_text[len("```csv"):]
                        if response_text.endswith("```"):
                            response_text = response_text[:-len("```")]
                        response_text = response_text.strip()
                        new_columns_chunk = pd.read_csv(io.StringIO(response_text))
                        new_columns_chunk.reset_index(drop=True, inplace=True)
                        assert len(new_columns_chunk.index) == cfg.dataset.adapt_num_rows, \
                            f"adapting width: generated an incorrect number of rows ({len(new_columns_chunk.index)} != {cfg.dataset.adapt_num_rows})"
                        columns_to_remove = []
                        for column in new_columns_chunk.columns:
                            if column in existing_columns:
                                logger.warning(
                                    f"adapting width: column chunk contains same column as previous chunk, remove: {column}"
                                )
                                columns_to_remove.append(column)
                            existing_columns.add(column)
                        for column in columns_to_remove:
                            del new_columns_chunk[column]
                        new_columns_chunks.append(new_columns_chunk)
                    if total_cost > cfg.dataset.adapt_max_cost:
                        logger.error(f"adapting width: total_cost exceeds adapt_max_cost")
                        exit()
                    new_columns = pd.concat(new_columns_chunks, axis=1)
                    if len(new_columns.columns) != target_num_new_columns:
                        logger.warning(
                            f"adapting width: generated an incorrect number of new columns ({len(new_columns.columns)} != {target_num_new_columns})"
                        )
                    assert len(new_columns.index) == cfg.dataset.adapt_num_rows, \
                        f"adapting width: generated an incorrect number of rows ({len(new_columns.index)} != {cfg.dataset.adapt_num_rows})"
                    columns_to_remove = []
                    for column in new_columns.columns:
                        if column in table.columns:
                            logger.warning(
                                f"adapting width: used column name from original table, remove: {column}"
                            )
                            columns_to_remove.append(column)
                    for column in columns_to_remove:
                        del new_columns[column]
                    new_columns = new_columns[new_columns.columns[:target_num_new_columns]]
                    # merge the new columns into the old table
                    old_table = table
                    actual_width = len(old_table.columns) + len(new_columns.columns)
                    old_table_idxes = set(adapt_width_random.sample(range(actual_width), len(old_table.columns)))
                    table = pd.DataFrame(index=old_table.index, columns=[])
                    old_idx, new_idx = 0, 0
                    for idx in range(actual_width):
                        if idx in old_table_idxes:
                            table[old_table.columns[old_idx]] = old_table[old_table.columns[old_idx]]
                            old_idx += 1
                        else:
                            table[new_columns.columns[new_idx]] = new_columns[new_columns.columns[new_idx]]
                            new_idx += 1
                    assert old_idx == len(old_table.columns)
                    assert new_idx == len(new_columns.columns)
                    assert len(table.columns) == actual_width
                    assert len(table.index) == cfg.dataset.adapt_num_rows
                except Exception as e:
                    logger.error(
                        "\n" * 3 + "=" * 20 + f"\nfailed to extend original table: {e}" + "=" * 20 + "\n" * 3
                    )
                    adapt_width_failures += 1
                    shutil.rmtree(instance_dir)
                    continue
            else:
                logger.warning(
                    f"actual table width is larger than target table width ({len(table.columns)} > {target_width})"
                )
            all_widths.append(len(table.columns))

        abbreviated_column_names = None
        if cfg.dataset.adapt_descriptiveness:
            try:
                # translate table name and column names into German
                requests = []
                request = {
                    "model": cfg.dataset.adapt_descriptiveness_model,
                    "messages": fill_chat_template(
                        OmegaConf.to_container(cfg.dataset.adapt_descriptiveness_table_name_to_german_chat_template),
                        table_name=load_str(instance_dir / "table_name.txt"),
                        newline="\n"
                    ),
                    "max_tokens": None,
                    "temperature": cfg.dataset.adapt_descriptiveness_temperature,
                    "seed": cfg.dataset.adapt_descriptiveness_model_seed
                }
                requests.append(request)
                for left in range(0, len(table.columns), cfg.dataset.adapt_descriptiveness_to_german_chunk_size):
                    request = {
                        "model": cfg.dataset.adapt_descriptiveness_model,
                        "messages": fill_chat_template(
                            OmegaConf.to_container(cfg.dataset.adapt_descriptiveness_to_german_chat_template),
                            table=linearize_table(
                                table[
                                    table.columns[left:left + cfg.dataset.adapt_descriptiveness_to_german_chunk_size]],
                                None,
                                template="{{table}}",
                                mode="csv",
                                csv_params={"index": False, "header": True}
                            ),
                            newline="\n"
                        ),
                        "max_tokens": None,
                        "temperature": cfg.dataset.adapt_descriptiveness_temperature,
                        "seed": cfg.dataset.adapt_descriptiveness_model_seed
                    }
                    requests.append(request)

                responses = execute_requests(
                    requests,
                    cfg.dataset.adapt_descriptiveness_api_name,
                    force=cfg.dataset.adapt_force
                )
                total_cost += compute_cost_for_response(responses[0])
                if total_cost > cfg.dataset.adapt_max_cost:
                    logger.error(f"adapting descriptiveness: total_cost exceeds adapt_max_cost")
                    exit()
                response_text = extract_text_from_response(responses[0])
                if response_text.startswith("```json"):
                    response_text = response_text[len("```json"):]
                if response_text.endswith("```"):
                    response_text = response_text[:-len("```")]
                response_text = response_text.strip()
                german_table_name = json.loads(response_text)["german_table_name"]
                german_column_names = []
                for response in responses[1:]:
                    total_cost += compute_cost_for_response(response)
                    if total_cost > cfg.dataset.adapt_max_cost:
                        logger.error(f"adapting descriptiveness: total_cost exceeds adapt_max_cost")
                        exit()
                    response_text = extract_text_from_response(response)
                    if response_text.startswith("```json"):
                        response_text = response_text[len("```json"):]
                    if response_text.endswith("```"):
                        response_text = response_text[:-len("```")]
                    response_text = response_text.strip()
                    gcn = parse_list(response_text, mode="json_list", json_params={"strip": True, "strict": False})
                    german_column_names += gcn
                assert len(german_column_names) == len(table.columns), \
                    f"adapting descriptiveness: generated an incorrect number of German column names ({len(german_column_names)} != {len(table.columns)})"
                # abbreviate table name and column names
                requests = []
                request = {
                    "model": cfg.dataset.adapt_descriptiveness_model,
                    "messages": fill_chat_template(
                        OmegaConf.to_container(
                            cfg.dataset.adapt_descriptiveness_table_name_to_abbreviation_chat_template),
                        german_table_name=german_table_name,
                        newline="\n"
                    ),
                    "max_tokens": None,
                    "temperature": cfg.dataset.adapt_descriptiveness_temperature,
                    "seed": cfg.dataset.adapt_descriptiveness_model_seed
                }
                requests.append(request)
                for left in range(0, len(german_column_names),
                                  cfg.dataset.adapt_descriptiveness_to_abbreviation_chunk_size):
                    request = {
                        "model": cfg.dataset.adapt_descriptiveness_model,
                        "messages": fill_chat_template(
                            OmegaConf.to_container(cfg.dataset.adapt_descriptiveness_to_abbreviation_chat_template),
                            german_column_names=json.dumps(german_column_names[
                                                           left:left + cfg.dataset.adapt_descriptiveness_to_abbreviation_chunk_size]),
                            newline="\n"
                        ),
                        "max_tokens": None,
                        "temperature": cfg.dataset.adapt_descriptiveness_temperature,
                        "seed": cfg.dataset.adapt_descriptiveness_model_seed
                    }
                    requests.append(request)
                responses = execute_requests(
                    requests,
                    cfg.dataset.adapt_descriptiveness_api_name,
                    force=cfg.dataset.adapt_force
                )
                total_cost += compute_cost_for_response(responses[0])
                if total_cost > cfg.dataset.adapt_max_cost:
                    logger.error(f"adapting descriptiveness: total_cost exceeds adapt_max_cost")
                    exit()
                response_text = extract_text_from_response(responses[0])
                if response_text.startswith("```json"):
                    response_text = response_text[len("```json"):]
                if response_text.endswith("```"):
                    response_text = response_text[:-len("```")]
                response_text = response_text.strip()
                abbreviated_table_name = json.loads(response_text)["abbreviated_table_name"]
                dump_str(abbreviated_table_name, instance_dir / "table_name.txt")
                abbreviated_column_names = []
                for response in responses[1:]:
                    total_cost += compute_cost_for_response(response)
                    if total_cost > cfg.dataset.adapt_max_cost:
                        logger.error(f"adapting descriptiveness: total_cost exceeds adapt_max_cost")
                        exit()
                    response_text = extract_text_from_response(response)
                    if response_text.startswith("```json"):
                        response_text = response_text[len("```json"):]
                    if response_text.endswith("```"):
                        response_text = response_text[:-len("```")]
                    response_text = response_text.strip()
                    acn = parse_list(response_text, mode="json_list", json_params={"strip": True, "strict": False})
                    abbreviated_column_names += acn
                assert len(abbreviated_column_names) == len(table.columns), \
                    f"adapting descriptiveness: generated an incorrect number of abbreviated column names ({len(abbreviated_column_names)} != {len(table.columns)})"
                if len(abbreviated_column_names) != len(set(abbreviated_column_names)):
                    logger.warning(
                        f"adapting descriptiveness: generated duplicate abbreviated column names {abbreviated_column_names}"
                    )

            except Exception as e:
                logger.error(
                    "\n" * 3 + "=" * 20 + f"\nfailed to adapt descriptiveness original table: {e}" + "=" * 20 + "\n" * 3
                )
                adapt_descriptiveness_failures += 1
                shutil.rmtree(instance_dir)
                continue

        if cfg.dataset.adapt_data_types:
            try:
                requests = []
                for left in range(0, len(table.columns), cfg.dataset.adapt_data_types_chunk_size):
                    request = {
                        "model": cfg.dataset.adapt_data_types_model,
                        "messages": fill_chat_template(
                            OmegaConf.to_container(cfg.dataset.adapt_data_types_chat_template),
                            table=linearize_table(
                                table[
                                    table.columns[left:left + cfg.dataset.adapt_data_types_chunk_size]],
                                None,
                                template="{{table}}",
                                mode="csv",
                                csv_params={"index": False, "header": True}
                            ),
                            newline="\n"
                        ),
                        "max_tokens": None,
                        "temperature": cfg.dataset.adapt_data_types_temperature,
                        "seed": cfg.dataset.adapt_data_types_model_seed
                    }
                    requests.append(request)

                responses = execute_requests(
                    requests,
                    cfg.dataset.adapt_data_types_api_name,
                    force=cfg.dataset.adapt_force
                )
                table_chunks = []
                for response in responses:
                    total_cost += compute_cost_for_response(response)
                    response_text = extract_text_from_response(response)
                    left = response_text.find("```csv")
                    right = response_text.find("```", left + 6)
                    response_text = response_text[left + 6:right]
                    response_text = response_text.strip()
                    table_chunk = pd.read_csv(io.StringIO(response_text))
                    table_chunk.reset_index(drop=True, inplace=True)
                    assert len(table_chunk.index) == cfg.dataset.adapt_num_rows, \
                        f"adapting data types: generated an incorrect number of rows ({len(table_chunk.index)} != {cfg.dataset.adapt_num_rows})"
                    table_chunks.append(table_chunk)
                if total_cost > cfg.dataset.adapt_max_cost:
                    logger.error(f"adapting data types: total_cost exceeds adapt_max_cost")
                    exit()
                new_table = pd.concat(table_chunks, axis=1)
                assert len(new_table.columns) == len(table.columns), \
                    f"adapting data types: generated an incorrect number of columns ({len(new_table.columns)} != {len(table.columns)})"
                assert len(new_table.index) == cfg.dataset.adapt_num_rows, \
                    f"adapting data types: generated an incorrect number of rows ({len(new_table.index)} != {cfg.dataset.adapt_num_rows})"
                new_table.columns = table.columns.to_list()
                table = new_table

            except Exception as e:
                logger.error(
                    "\n" * 3 + "=" * 20 + f"\nfailed to adapt data types original table: {e}" + "=" * 20 + "\n" * 3
                )
                adapt_data_types_failures += 1
                shutil.rmtree(instance_dir)
                continue

        if cfg.dataset.adapt_sparsity:
            num_sparse_columns = int(len(table.columns) * cfg.dataset.target_col_sparsity)
            sparse_columns = adapt_sparsity_random.sample(table.columns.to_list(), num_sparse_columns)
            for column in sparse_columns:
                table[column] = np.nan

            cell_sparsity = compute_cell_level_sparsity(table)
            if cell_sparsity < cfg.dataset.target_cell_sparsity:
                target_num_sparse_cells = int(cfg.dataset.target_cell_sparsity * len(table.index) * len(table.columns))
                num_sparse_cells = table.isna().sum().sum()
                nested_idx_pairs = [[(x, y) for y in list(range(len(table.columns)))] for x in
                                    list(range(len(table.index)))]
                idx_pairs = [(x, y) for l in nested_idx_pairs for x, y in l]
                adapt_sparsity_random.shuffle(idx_pairs)
                for x, y in idx_pairs:
                    if target_num_sparse_cells == num_sparse_cells:
                        break
                    if not pd.isna(table.iat[x, y]):
                        table.iat[x, y] = np.nan
                        num_sparse_cells += 1
            else:
                logger.warning(
                    f"actual cell sparsity is larger than target cell sparsity ({cell_sparsity} > {cfg.dataset.target_cell_sparsity})"
                )
            all_sparsities.append(compute_cell_level_sparsity(table))

        df = table.copy()
        if cfg.dataset.adapt_descriptiveness:
            table.columns = abbreviated_column_names
        table.to_csv(instance_dir / "table.csv", index=False)
        # shutil.copy(table_path, instance_dir / "table.csv")

        matched = False
        for key, mappings in metadata[sport].items():
            if key in table_path.name:
                if matched:
                    raise AssertionError(f"Found more than one matching type dictionary for '{table_path.name}'!")
                matched = True

                all_mappings = mappings["textual_cols"] | mappings["numerical_cols"]

                column_types = []
                data_types = []
                num_new_column = 0
                new_columns_names = set(new_columns.columns.to_list()) if new_columns is not None else None
                for column in df.columns:
                    if new_columns_names is not None and column in new_columns_names:
                        logger.debug(f"New column: set column type to None!")
                        column_types.append(None)
                        num_new_column += 1
                    elif column not in all_mappings.keys():
                        logger.info(f"Dictionary contains no column type for '{column}', set to None!")
                        column_types.append(None)
                    else:
                        column_types.append(all_mappings[column])
                    data_type = column_type2data_type[column_types[-1]]
                    if data_type == "textual_cols":
                        data_types.append("non-numerical")
                    elif data_type == "numerical_cols":
                        data_types.append("numerical")
                    else:
                        raise AssertionError(f"Invalid data type '{data_type}'!")
                if cfg.dataset.adapt_width:
                    assert new_columns is None or num_new_column == len(
                        new_columns.columns), "all new columns should not have column types!"

                dump_json(column_types, instance_dir / "column_types.json")
                dump_json(data_types, instance_dir / "data_types.json")
        if not matched:
            raise AssertionError(f"Found no matching type dictionary for '{table_path.name}'!")

        # filter out tables that contain no column type annotations
        column_types = load_json(instance_dir / "column_types.json")
        if set(column_types) == {None}:
            logger.warning("Discard instance without any column type annotations.")
            shutil.rmtree(instance_dir)
            continue

        ix += 1
        if ix == cfg.limit_instances and (cfg.task_mode == "all" or cfg.task_mode == "chunking"):
            break

    if cfg.dataset.adapt_width:
        logger.info(
            f"adapting width: failures = {adapt_width_failures}, mean = {statistics.mean(all_widths)}, med = {statistics.median(all_widths)}, max = {max(all_widths)}"
        )
    if cfg.dataset.adapt_descriptiveness:
        logger.info(
            f"adapting descriptiveness: failures = {adapt_descriptiveness_failures}"
        )
    if cfg.dataset.adapt_data_types:
        logger.info(
            f"adapting data types: failures = {adapt_data_types_failures}"
        )
    if cfg.dataset.adapt_sparsity:
        logger.info(f"adapting sparsity: mean = {statistics.mean(all_sparsities)}")

    dump_cfg(cfg, instances_dir / "config.cfg")


if __name__ == "__main__":
    main()
