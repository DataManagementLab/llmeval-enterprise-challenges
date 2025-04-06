import logging

import hydra
from omegaconf import DictConfig

from llms4de.data import get_download_dir, dump_cfg

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="../../../config/column_type_annotation", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    assert cfg.dataset.dataset_name == "wikitables-turl", "This script is dataset-specific."
    download_dir = get_download_dir(cfg.task_name,
                                    cfg.dataset.dataset_name)  # do not clear download directory to enable manual download

    dump_cfg(cfg, download_dir / "config.cfg")
    while not download_dir.joinpath("train.table_col_type.json").is_file():
        input(f"You must manually download the dataset from:\n{cfg.dataset.url}\nand place `train.table_col_type.json` "
              f"in `data/column_type_annotation/wikitables-turl/download`.\nThen press enter.")


if __name__ == "__main__":
    main()
