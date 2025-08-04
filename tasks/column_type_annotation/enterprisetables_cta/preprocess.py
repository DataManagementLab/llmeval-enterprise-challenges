import logging
import os
import random
import shutil

import hydra
import numpy as np
import pandas as pd
import tqdm
from omegaconf import DictConfig

from llms4de.data import get_download_dir, get_instances_dir, dump_str, dump_json, load_json, load_str, dump_cfg
from llms4de.preprocessing import shuffle_instances, sample_rows

logger = logging.getLogger(__name__)

_sample_columns_random = random.Random(319313273)
_sparsity_random = random.Random(931169624)


@hydra.main(version_base=None, config_path="../../../config/column_type_annotation", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    assert cfg.dataset.dataset_name == "enterprisetables_cta", "This script is dataset-specific."
    download_dir = get_download_dir(cfg.task_name, cfg.dataset.dataset_name)
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    if cfg.dataset.sample_columns:
        if cfg.dataset.sparsify:
            logger.info("Sample columns will be ignored as sampling happens as part of sparsifying")
            cfg.dataset.sample_columns = False

    logger.info("Load tables.")
    table_paths = list(sorted(download_dir.glob("*.csv")))
    table_paths = shuffle_instances(table_paths)
    table_names = [table_path.name[:-4] for table_path in table_paths]

    logger.info("Load column types and data types.")
    metadata = {}  # table_name -> data type -> column types
    mapping = {}  # table_name -> column name -> column type
    for table_name in table_names:
        metadata[table_name] = load_json(download_dir / f"{table_name}_metadata.json")
        mapping[table_name] = load_json(download_dir / f"{table_name}_mapping.json")

    all_column_types = set()
    column_type2data_type = {}  # column type -> data type
    for table_name in table_names:
        for data_type, column_types in metadata[table_name].items():
            for column_type in column_types:
                all_column_types.add(column_type)
                column_type2data_type[column_type] = data_type

    all_column_types = list(sorted(set(filter(lambda x: x is not None, all_column_types))))
    logger.info(f"There are {len(all_column_types)} column types across all tables.")
    dump_json(all_column_types, instances_dir / "all_column_types.json")
    dump_json(column_type2data_type, instances_dir / "column_type2data_type.json")

    logger.info("Create instances.")
    ix = 0
    for table_name in tqdm.tqdm(table_names,
                                desc=f"{cfg.task_name} - {cfg.dataset.dataset_name} - {cfg.exp_name} - preprocess"):
        instance_dir = instances_dir / f"{ix}"
        os.makedirs(instance_dir, exist_ok=True)

        dump_str(table_name, instance_dir / "table_name.txt")

        shutil.copy(download_dir / f"{table_name}.csv", instance_dir / "table.csv")

        df = pd.read_csv(download_dir / f"{table_name}.csv", sep=",")

        all_column_types_for_table = [mapping[table_name].get(column, None) for column in
                                      df.columns.to_list()]  # some columns do not have a column type
        dump_json(all_column_types_for_table, instance_dir / "column_types.json")
        data_types = [column_type2data_type[column_type] for column_type in all_column_types_for_table]
        dump_json(data_types, instance_dir / "data_types.json")

        ix += 1
        if ix == cfg.limit_instances:
            break

    if cfg.dataset.sample_columns:
        logger.info("Create new instances with sampled columns.")
        old_instances_dir = instances_dir.parent / f"old_{instances_dir.name}"
        if old_instances_dir.is_dir():
            shutil.rmtree(old_instances_dir)
        shutil.move(instances_dir, old_instances_dir)
        instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)
        dump_json(all_column_types, instances_dir / "all_column_types.json")
        dump_json(column_type2data_type, instances_dir / "column_type2data_type.json")

        ix = 0
        for num_columns in [5, 10, 20, 30, 40, 60, 80, 100]:
            for old_instance_dir in old_instances_dir.glob("*/"):
                instance_dir = instances_dir / f"{ix}"
                os.makedirs(instance_dir, exist_ok=True)

                table_name = load_str(old_instance_dir / "table_name.txt")
                dump_str(table_name, instance_dir / "table_name.txt")

                df = pd.read_csv(old_instance_dir / "table.csv", sep=",")

                if num_columns > len(df.columns):
                    logger.warning(
                        f"Table '{table_name}' does not have enough columns to sample {num_columns} columns! ==> Skip.")
                    shutil.rmtree(instance_dir)
                    continue

                logger.info(f"Sample {num_columns} columns for table {table_name}.")
                sampled_indexes = _sample_columns_random.sample(list(range(len(df.columns))), k=num_columns)
                sampled_indexes = list(sorted(sampled_indexes))  # keep order from original tables

                columns = df.columns.to_list()
                columns = [columns[idx] for idx in sampled_indexes]
                df = df[columns]

                df.to_csv(instance_dir / "table.csv", index=False)

                all_column_types_for_table = [mapping[table_name].get(column, None) for column in df.columns.to_list()]
                dump_json(all_column_types_for_table, instance_dir / "column_types.json")
                data_types = [column_type2data_type[column_type] for column_type in all_column_types_for_table]
                dump_json(data_types, instance_dir / "data_types.json")

                ix += 1
                if ix == cfg.limit_instances:
                    break

    if cfg.dataset.sparsify:
        logger.info("Create new instances with sparsity.")
        old_instances_dir = instances_dir.parent / f"old_{instances_dir.name}"
        if old_instances_dir.is_dir():
            shutil.rmtree(old_instances_dir)
        shutil.move(instances_dir, old_instances_dir)
        instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)
        dump_json(all_column_types, instances_dir / "all_column_types.json")
        dump_json(column_type2data_type, instances_dir / "column_type2data_type.json")

        ix = 0
        num_columns = 20
        for sparsity in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
            _sparsity_sample_columns_random = random.Random(779863789)

            for old_instance_dir in old_instances_dir.glob("*/"):
                instance_dir = instances_dir / f"{ix}"
                os.makedirs(instance_dir, exist_ok=True)

                table_name = load_str(old_instance_dir / "table_name.txt")
                dump_str(table_name, instance_dir / "table_name.txt")

                df = pd.read_csv(old_instance_dir / "table.csv", sep=",")

                # we must sample rows here to ensure that we measure the sparsity of the sampled rows
                df = sample_rows(df, **cfg.sample_rows)

                if num_columns > len(df.columns):
                    logger.warning(
                        f"Table '{table_name}' does not have enough columns to sample {num_columns} columns! ==> Skip.")
                    shutil.rmtree(instance_dir)
                    continue

                non_sparse_idx = []
                for idx, column in enumerate(df.columns.to_list()):
                    if not df[column].isna().any():
                        non_sparse_idx.append(idx)

                if num_columns > len(non_sparse_idx):
                    logger.warning(
                        f"Table '{table_name}' does not have enough NON-SPARSE columns to sample {num_columns} NON-SPARSE columns! ==> Skip.")
                    shutil.rmtree(instance_dir)
                    continue

                sampled_indexes = _sparsity_sample_columns_random.sample(non_sparse_idx, k=num_columns)
                sampled_indexes = list(sorted(sampled_indexes))  # keep order from original tables

                columns = df.columns.to_list()
                columns = [columns[idx] for idx in sampled_indexes]
                df = df[columns]

                num_sparse_cells = int(sparsity * len(df.index) * len(df.columns))
                nested_idx_pairs = [[(x, y) for y in list(range(len(df.columns)))] for x in list(range(len(df.index)))]
                idx_pairs = [(x, y) for l in nested_idx_pairs for x, y in l]
                for x, y in _sparsity_random.sample(idx_pairs, k=num_sparse_cells):
                    df.iat[x, y] = np.nan

                df.to_csv(instance_dir / "table.csv", index=False)

                all_column_types_for_table = [mapping[table_name].get(column, None) for column in df.columns.to_list()]
                dump_json(all_column_types_for_table, instance_dir / "column_types.json")
                data_types = [column_type2data_type[column_type] for column_type in all_column_types_for_table]
                dump_json(data_types, instance_dir / "data_types.json")

                ix += 1
                if ix == cfg.limit_instances and (cfg.task_mode == "all" or cfg.task_mode == "chunking"):
                    break

    dump_cfg(cfg, instances_dir / "config.cfg")


if __name__ == "__main__":
    main()
