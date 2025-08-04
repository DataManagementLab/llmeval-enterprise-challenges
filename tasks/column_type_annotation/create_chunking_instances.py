import logging
import os
import random
import shutil

import hydra
import pandas as pd
import tqdm
from omegaconf import DictConfig

from llms4de.data import get_instances_dir, dump_json, load_json, dump_cfg

logger = logging.getLogger(__name__)

_sample_chunks_random = random.Random(650072706)


@hydra.main(version_base=None, config_path="../../config/column_type_annotation", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    assert cfg.task_mode == "chunking", f"This script only works for task mode `chunking`, not `{cfg.task_mode}`!"

    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    old_instances_dir = instances_dir.parent / f"{instances_dir.name}_before_chunking"
    if old_instances_dir.is_dir():
        shutil.rmtree(old_instances_dir)
    shutil.move(instances_dir, old_instances_dir)
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)
    old_instance_paths = list(sorted(old_instances_dir.glob("*/")))

    shutil.copy(old_instances_dir / "all_column_types.json", instances_dir / "all_column_types.json")

    ix = 0
    for old_instance_path in tqdm.tqdm(
            old_instance_paths[:cfg.limit_instances],
            f"{cfg.task_name} - {cfg.dataset.dataset_name} - {cfg.exp_name} - create chunking instances"
    ):
        column_types = load_json(old_instance_path / "column_types.json")
        for left in range(0, len(column_types), cfg.chunk_size):
            instance_path = instances_dir / f"{ix}"
            os.makedirs(instance_path)
            shutil.copy(old_instance_path / "table_name.txt", instance_path / "table_name.txt")
            shutil.copy(old_instance_path / "column_types.json", instance_path / "table_column_types.json")
            table = pd.read_csv(old_instance_path / "table.csv")
            table = table[table.columns[left:left + cfg.chunk_size]]
            table.to_csv(instance_path / "table.csv", index=False)
            load_json(old_instance_path / "column_types.json")
            dump_json(column_types[left:left + cfg.chunk_size], instance_path / "column_types.json")
            data_types = load_json(old_instance_path / "data_types.json")
            dump_json(data_types[left:left + cfg.chunk_size], instance_path / "data_types.json")

            if set(column_types[left:left + cfg.chunk_size]) == {None}:
                logger.warning("Discard chunking instance without any column type annotations.")
                shutil.rmtree(instance_path)
                continue
            ix += 1

    if cfg.limit_instances_chunking is not None:
        old_instances_dir = instances_dir.parent / f"{instances_dir.name}_before_reduction"
        if old_instances_dir.is_dir():
            shutil.rmtree(old_instances_dir)
        shutil.move(instances_dir, old_instances_dir)
        old_instance_paths = list(sorted(old_instances_dir.glob("*/")))
        old_instance_paths = _sample_chunks_random.sample(old_instance_paths,
                                                          k=min(cfg.limit_instances_chunking, len(old_instance_paths)))
        instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

        for ix, old_instance_path in enumerate(old_instance_paths):
            instance_path = instances_dir / f"{ix}"
            os.makedirs(instance_path)
            for file in old_instance_path.iterdir():
                if file.is_file():
                    shutil.copy(file, instance_path)

        shutil.copy(old_instances_dir / "all_column_types.json", instances_dir / "all_column_types.json")

    dump_cfg(cfg, instances_dir / "config.cfg")


if __name__ == "__main__":
    main()
