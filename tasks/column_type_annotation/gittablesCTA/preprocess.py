import logging
import os
import shutil

import hydra
import pandas as pd
import tqdm
from omegaconf import DictConfig

from llms4de.data import get_download_dir, get_instances_dir, dump_json, dump_str, dump_cfg
from llms4de.preprocessing import shuffle_instances

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="../../../config/column_type_annotation", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    assert cfg.dataset.dataset_name == "gittablesCTA", "This script is dataset-specific."
    download_dir = get_download_dir(cfg.task_name, cfg.dataset.dataset_name)
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    logger.debug("Load metadata.")
    ground_truth = pd.read_csv(download_dir / f"{cfg.dataset.ontology}_gt.csv", index_col=0)
    labels = pd.read_csv(download_dir / f"{cfg.dataset.ontology}_labels.csv", index_col=0)
    targets = pd.read_csv(download_dir / f"{cfg.dataset.ontology}_targets.csv", index_col=0)

    all_column_types = list(sorted(set(labels["annotation_label"].to_list())))
    dump_json(all_column_types, instances_dir / "all_column_types.json")

    logger.debug("Glob table paths.")
    table_paths = list(sorted(download_dir.joinpath("tables").glob("*.csv")))
    table_paths = shuffle_instances(table_paths)

    ix = 0
    for table_path in tqdm.tqdm(table_paths,
                                desc=f"{cfg.task_name} - {cfg.dataset.dataset_name} - {cfg.exp_name} - preprocess"):
        instance_dir = instances_dir / f"{ix}"
        os.makedirs(instance_dir, exist_ok=True)

        table_name = table_path.name[:-4]
        dump_str(table_name, instance_dir / "table_name.txt")  # this is not a real name...

        if download_dir.joinpath("tables-have-no-index-column.txt").is_file():
            df = pd.read_csv(table_path)
        else:
            df = pd.read_csv(table_path, index_col=0)
        df.to_csv(instance_dir / "table.csv", index=False)  # write again instead of copying to remove index column

        column_types = []
        data_types = []
        for col_ix, (column, dtype) in enumerate(zip(df.columns.to_list(), df.dtypes.to_list())):
            ground_truth_rows = ground_truth.loc[
                (ground_truth["table_id"] == f"{table_name}_{cfg.dataset.ontology}") & (
                        ground_truth["target_column"] == col_ix)]
            if len(ground_truth_rows) == 0:
                column_types.append(None)  # column type is not specified
            elif len(ground_truth_rows) == 1:
                column_types.append(ground_truth_rows.iloc[0]["annotation_label"])
            else:
                raise AssertionError("There are multiple column type annotations for the same column!")

            if dtype.kind in ("i", "f", "u"):
                data_types.append("numerical")
            else:
                data_types.append("non-numerical")

        dump_json(column_types, instance_dir / "column_types.json")
        dump_json(data_types, instance_dir / "data_types.json")

        # filter out tables that contain no column type annotations
        if set(column_types) == {None}:
            logger.warning("Discard instance without any column type annotations.")
            shutil.rmtree(instance_dir)
            continue

        ix += 1
        if ix == cfg.limit_instances and (cfg.task_mode == "all" or cfg.task_mode == "chunking"):
            break

    dump_cfg(cfg, instances_dir / "config.cfg")


if __name__ == "__main__":
    main()
