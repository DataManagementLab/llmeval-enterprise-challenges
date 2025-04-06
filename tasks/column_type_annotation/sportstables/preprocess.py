import collections
import logging
import os
import shutil

import hydra
import pandas as pd
import tqdm
from omegaconf import DictConfig

from llms4de.data import get_download_dir, get_instances_dir, load_json, dump_json, dump_str, dump_cfg
from llms4de.preprocessing import shuffle_instances

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="../../../config/column_type_annotation", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    assert cfg.dataset.dataset_name == "sportstables", "This script is dataset-specific."
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
    for sport, table_path in tqdm.tqdm(table_paths,
                                       desc=f"{cfg.task_name} - {cfg.dataset.dataset_name} - {cfg.exp_name} - preprocess"):
        instance_dir = instances_dir / f"{ix}"
        os.makedirs(instance_dir, exist_ok=True)

        dump_str(table_path.name[:-4], instance_dir / "table_name.txt")

        shutil.copy(table_path, instance_dir / "table.csv")
        df = pd.read_csv(table_path)

        matched = False
        for key, mappings in metadata[sport].items():
            if key in table_path.name:
                if matched:
                    raise AssertionError(f"Found more than one matching type dictionary for '{table_path.name}'!")
                matched = True

                all_mappings = mappings["textual_cols"] | mappings["numerical_cols"]

                column_types = []
                data_types = []
                for column in df.columns:
                    if column not in all_mappings.keys():
                        logger.warning(f"Dictionary contains no column type for '{column}', set to None!")
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
        if ix == cfg.limit_instances and cfg.task_mode == "all":
            break

    dump_cfg(cfg, instances_dir / "config.cfg")


if __name__ == "__main__":
    main()
