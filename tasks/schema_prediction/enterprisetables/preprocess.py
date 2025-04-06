import logging
import os

import hydra
import tqdm
from omegaconf import DictConfig

from llms4de.data import get_download_dir, get_instances_dir, dump_str, dump_json, load_json
from llms4de.preprocessing import shuffle_instances

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="../../../config/schema_prediction", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    assert cfg.dataset.dataset_name == "enterprisetables", "This script is dataset-specific."
    download_dir = get_download_dir(cfg.task_name, cfg.dataset.dataset_name)
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    table_paths = list(sorted(download_dir.glob("*.json")))
    table_paths = shuffle_instances(table_paths)
    logger.info(f"loaded {len(table_paths)} tables")

    table_names = [table_path.name[:-12] for table_path in table_paths]  # remove "_header.json"

    logger.info("load column names")
    all_column_names = set()
    for table_name in table_names:
        logger.info(f"load column names for table `{table_name}`")
        column_names = load_json(download_dir / f"{table_name}_header.json")
        before = len(all_column_names)
        all_column_names = all_column_names.union(set(column_names["COLUMN_NAME"].values()))
        logger.info(f"added {len(all_column_names) - before} new column names that were not in a previous table")

    all_column_names = list(sorted(set(filter(lambda x: x is not None, all_column_names))))
    logger.info(f"there are {len(all_column_names)} column names across all tables")
    dump_json(all_column_names, instances_dir / "all_column_names.json")

    logger.info("create instances")
    ix = 0
    for table_name in tqdm.tqdm(table_names,
                                desc=f"{cfg.task_name} - {cfg.dataset.dataset_name} - {cfg.exp_name} - preprocess"):
        instance_dir = instances_dir / f"{ix}"
        os.makedirs(instance_dir, exist_ok=True)

        dump_str(table_name, instance_dir / "table_name.txt")
        table_header = load_json(download_dir / f"{table_name}_header.json")
        columns = list(table_header["COLUMN_NAME"].values())
        dump_json(columns, instance_dir / "table_header.json")

        ix += 1
        if ix == cfg.limit_instances:
            break


if __name__ == "__main__":
    main()
