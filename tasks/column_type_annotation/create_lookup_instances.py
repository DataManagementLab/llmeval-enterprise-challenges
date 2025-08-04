import logging
import os
import random
import shutil

import hydra
import tqdm
from omegaconf import DictConfig

from llms4de.data import get_instances_dir, dump_json, load_json, dump_cfg
from llms4de.preprocessing import distribute_budget_across_instances

logger = logging.getLogger(__name__)

_sample_cols_random = random.Random(650072706)


@hydra.main(version_base=None, config_path="../../config/column_type_annotation", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    if not cfg.task_mode.startswith("lookup"):
        raise AssertionError(f"This script only works for task modes `lookup...`, not `{cfg.task_mode}`!")

    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    old_instances_dir = instances_dir.parent / f"{instances_dir.name}_before_lookup"
    if old_instances_dir.is_dir():
        shutil.rmtree(old_instances_dir)
    shutil.move(instances_dir, old_instances_dir)
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)
    old_instance_paths = list(sorted(old_instances_dir.glob("*/")))

    shutil.copy(old_instances_dir / "all_column_types.json", instances_dir / "all_column_types.json")

    cols_by_inst = []
    for instance_path in old_instance_paths:
        column_types = load_json(instance_path / "column_types.json")
        cols_by_inst.append(len([column_type for column_type in column_types if column_type is not None]))

    if cfg.limit_instances is not None:
        assigned_cols_by_inst = distribute_budget_across_instances(cols_by_inst, cfg.limit_instances)
    else:
        assigned_cols_by_inst = cols_by_inst

    ix = 0
    for old_instance_path, assigned_cols in zip(
            tqdm.tqdm(old_instance_paths,
                      f"{cfg.task_name} - {cfg.dataset.dataset_name} - {cfg.exp_name} - create lookup instances"),
            assigned_cols_by_inst
    ):
        column_types = load_json(old_instance_path / "column_types.json")
        indices = [ix for ix, column_type in enumerate(column_types) if column_type is not None]
        sampled_indices = _sample_cols_random.sample(indices, assigned_cols)
        for index in sampled_indices:
            instance_path = instances_dir / f"{ix}"
            os.makedirs(instance_path)

            shutil.copy(old_instance_path / "table_name.txt", instance_path / "table_name.txt")
            shutil.copy(old_instance_path / "table.csv", instance_path / "table.csv")
            shutil.copy(old_instance_path / "column_types.json", instance_path / "column_types.json")
            dump_json(index, instance_path / "index.json")
            column_types = load_json(old_instance_path / "column_types.json")
            dump_json(column_types[index], instance_path / "column_type.json")
            data_types = load_json(old_instance_path / "data_types.json")
            dump_json(data_types[index], instance_path / "data_type.json")

            ix += 1

    dump_cfg(cfg, instances_dir / "config.cfg")


if __name__ == "__main__":
    main()
