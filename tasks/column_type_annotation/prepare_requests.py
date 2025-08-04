import logging
import random
import statistics

import hydra
import pandas as pd
import tqdm
from omegaconf import DictConfig, OmegaConf

from llms4de.data import get_instances_dir, get_requests_dir, load_json, load_str, dump_json, dump_cfg
from llms4de.evaluation.inspection import compute_cell_level_sparsity
from llms4de.model.generic import max_tokens_for_ground_truth
from llms4de.preprocessing import sample_rows, sample_examples
from llms4de.prompting.linearize import linearize_table, linearize_list
from llms4de.prompting.template import fill_chat_template

logger = logging.getLogger(__name__)

_prepare_requests_random = random.Random(859962185)


@hydra.main(version_base=None, config_path="../../config/column_type_annotation", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    requests_dir = get_requests_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    all_column_types = load_json(instances_dir / "all_column_types.json")
    all_column_types = list(sorted(set(filter(lambda x: x is not None, all_column_types))))
    linearized_all_column_types = linearize_list(all_column_types, **cfg.linearize_list)

    all_sparsities = []
    instance_paths = list(sorted(instances_dir.glob("*/")))
    for path in tqdm.tqdm(instance_paths,
                          f"{cfg.task_name} - {cfg.dataset.dataset_name} - {cfg.exp_name} - prepare requests"):
        # load instance
        table_name = load_str(path / "table_name.txt")
        df = pd.read_csv(path / "table.csv")

        match cfg.task_mode:
            case "all":
                column_types = load_json(path / "column_types.json")
                inst_all_column_types = set(column_types)
            case "lookup-index" | "lookup-header":
                column_types = load_json(path / "column_types.json")
                inst_all_column_types = set(column_types)
                column_type = load_json(path / "column_type.json")
                index = load_json(path / "index.json")
            case "chunking":
                table_column_types = load_json(path / "table_column_types.json")
                inst_all_column_types = set(table_column_types)
                column_types = load_json(path / "column_types.json")
            case _:
                raise AssertionError(f"invalid task mode `{cfg.task_mode}`")

        df = sample_rows(df, **cfg.sample_rows)
        if len(df.index) == 0 or len(df.columns) == 0:
            logger.warning("cannot compute sparsity for empty table in prompt")
        else:
            all_sparsities.append(compute_cell_level_sparsity(df))
        linearized_table = linearize_table(df, table_name, **cfg.linearize_table)

        # create examples
        examples = []
        for ex_path in sample_examples(path, instance_paths, **cfg.sample_examples):
            ex_table_name = load_str(ex_path / "table_name.txt")
            ex_df = pd.read_csv(ex_path / "table.csv")
            match cfg.task_mode:
                case "all":
                    ex_column_types = load_json(ex_path / "column_types.json")
                    inst_all_column_types = inst_all_column_types.union(ex_column_types)
                case "lookup-index" | "lookup-header":
                    ex_column_types = load_json(ex_path / "column_types.json")
                    inst_all_column_types = inst_all_column_types.union(ex_column_types)
                    ex_column_type = load_json(ex_path / "column_type.json")
                    ex_index = load_json(ex_path / "index.json")
                case "chunking":
                    ex_table_column_types = load_json(ex_path / "table_column_types.json")
                    inst_all_column_types = inst_all_column_types.union(ex_table_column_types)
                    ex_column_types = load_json(ex_path / "column_types.json")
                case _:
                    raise AssertionError(f"invalid task mode `{cfg.task_mode}`")

            if cfg.remove_unspecified_columns_in_example:
                match cfg.task_mode:
                    case "all":
                        ex_columns = [c for ix, c in enumerate(ex_df.columns.tolist()) if
                                      ex_column_types[ix] is not None]
                        ex_column_types = [col_type for col_type in ex_column_types if
                                           col_type is not None]
                        ex_df = ex_df[ex_columns]
                    case _:
                        raise AssertionError(f"removing unspecified columns is only supported for task mode `all`")

            if cfg.limit_example_columns is not None:
                match cfg.task_mode:
                    case "all" | "chunking":
                        if cfg.limit_example_columns < len(ex_df.columns):
                            ex_column_indices = list(sorted(
                                _prepare_requests_random.sample(list(range(len(ex_df.columns))),
                                                                k=cfg.limit_example_columns)))
                            ex_columns = ex_df.columns.tolist()
                            ex_columns = [ex_columns[ix] for ix in ex_column_indices]
                            ex_column_types = [ex_column_types[ix] for ix in ex_column_indices]
                            ex_df = ex_df[ex_columns]
                    case "lookup-index" | "lookup-header":
                        if cfg.limit_example_columns < len(ex_df.columns):
                            ex_column_indices = list(sorted(
                                _prepare_requests_random.sample(list(range(len(ex_df.columns))),
                                                                k=cfg.limit_example_columns - 1)))
                            ex_column_indices.append(ex_index)
                            ex_column_indices.sort()
                            ex_index = ex_column_indices.index(ex_index)
                            ex_columns = ex_df.columns.tolist()
                            ex_columns = [ex_columns[ix] for ix in ex_column_indices]
                            ex_column_types = [ex_column_types[ix] for ix in ex_column_indices]
                            ex_df = ex_df[ex_columns]
                    case _:
                        raise AssertionError(f"limiting example columns is only supported for task mode `all`")

            ex_df = sample_rows(ex_df, **cfg.sample_rows)
            ex_linearized_table = linearize_table(ex_df, ex_table_name, **cfg.linearize_table)

            example = {
                "table": ex_linearized_table,
                "newline": "\n"
            }
            match cfg.task_mode:
                case "all" | "chunking":
                    ex_linearized_column_types = linearize_list(
                        stringify_unspecified_column_types(
                            ex_column_types,
                            cfg.unspecified_column_type_string
                        ),
                        **cfg.linearize_list
                    )
                    example["column_types"] = ex_linearized_column_types
                case "lookup-index" | "lookup-header":
                    ex_linearized_column_type = str(ex_column_type)
                    example["column_type"] = ex_linearized_column_type
                    example["lookup"] = create_lookup_string(ex_index, ex_df, cfg.task_mode)
                case _:
                    raise AssertionError(f"invalid task mode `{cfg.task_mode}`")

            examples.append(example)

        # create instance
        match cfg.task_mode:
            case "all" | "chunking":
                ground_truth = linearize_list(
                    stringify_unspecified_column_types(
                        column_types,
                        cfg.unspecified_column_type_string
                    ),
                    **cfg.linearize_list
                )
            case "lookup-index" | "lookup-header":
                ground_truth = str(column_type)
            case _:
                raise AssertionError(f"invalid task mode `{cfg.task_mode}`")

        if cfg.use_inst_all_column_types:
            if len(inst_all_column_types) < cfg.num_inst_all_column_types:
                remaining_column_types = set(all_column_types).difference(inst_all_column_types)
                required_num = cfg.num_inst_all_column_types - len(inst_all_column_types)
                if required_num > len(remaining_column_types):
                    logger.warning(
                        f"Not enough column types in total to achieve `cfg.num_inst_all_column_types`!")
                    required_num = len(remaining_column_types)
                inst_all_column_types = inst_all_column_types.union(
                    _prepare_requests_random.sample(list(sorted(remaining_column_types)), k=required_num))
            else:
                logger.warning(
                    f"Instance requires more than `cfg.num_inst_all_column_types` column types "
                    f"({len(inst_all_column_types)} > {cfg.num_inst_all_column_types})!"
                )

            all_column_types = list(sorted(set(filter(lambda x: x is not None, inst_all_column_types))))
            linearized_all_column_types = linearize_list(all_column_types, **cfg.linearize_list)

        request = {
            "model": cfg.model,
            "max_tokens": max_tokens_for_ground_truth(
                ground_truth,
                cfg.api_name,
                cfg.model,
                cfg.max_tokens_over_ground_truth
            ),
            "temperature": cfg.temperature
        }

        example_messages = []
        for example in examples:
            example_messages += fill_chat_template(OmegaConf.to_container(cfg.example_chat_template), **example)

        match cfg.task_mode:
            case "all" | "chunking":
                request["messages"] = fill_chat_template(
                    OmegaConf.to_container(cfg.prompt_chat_template),
                    all_column_types=linearized_all_column_types,
                    examples=example_messages,
                    table=linearized_table,
                    newline="\n"
                )
            case "lookup-index" | "lookup-header":
                request["messages"] = fill_chat_template(
                    OmegaConf.to_container(cfg.prompt_chat_template),
                    all_column_types=linearized_all_column_types,
                    examples=example_messages,
                    table=linearized_table,
                    lookup=create_lookup_string(index, df, cfg.task_mode),
                    newline="\n"
                )
            case _:
                raise AssertionError(f"invalid task mode `{cfg.task_mode}`")

        dump_json(request, requests_dir / f"{path.name}.json")

    logger.info(f"average sparsity of tables in prompt: {statistics.mean(all_sparsities)}")
    dump_cfg(cfg, requests_dir / "config.cfg")


def stringify_unspecified_column_types(
        column_types: list[str | None],
        unspecified_column_type_string: str
) -> list[str]:
    return [ct if ct is not None else unspecified_column_type_string for ct in column_types]


def create_lookup_string(index: int, table: pd.DataFrame, task_mode: str) -> str:
    if task_mode == "lookup-index":
        return f"at index {index}"
    elif task_mode == "lookup-header":
        return str(table.columns[index])
    else:
        raise AssertionError(f"Invalid lookup task mode `{task_mode}`!")


if __name__ == "__main__":
    main()
