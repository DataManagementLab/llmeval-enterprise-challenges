import logging

import hydra
from omegaconf import DictConfig

from llms4de.data import get_download_dir, dump_cfg

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="../../../config/text2signal", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    assert cfg.dataset.dataset_name == "signavio", "This script is dataset-specific."
    download_dir = get_download_dir(cfg.task_name,
                                    cfg.dataset.dataset_name)  # do not clear download directory to enable manual download

    dump_cfg(cfg, download_dir / "config.cfg")
    while not download_dir.joinpath("signavio_test_data.csv").is_file():
        input(f"You must manually obtain the signavio dataset and place it in "
              f"`data/text2signal/signavio/download`.\nThen press enter.")


if __name__ == "__main__":
    main()
