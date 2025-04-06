import logging

import hydra
from omegaconf import DictConfig

from llms4de.data import get_download_dir, dump_cfg, download_url

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="../../../config/other_datasets", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    assert cfg.dataset.dataset_name == "narayan", "This script is dataset-specific."
    download_dir = get_download_dir(cfg.task_name, cfg.dataset.dataset_name, clear=True)

    download_url(cfg.dataset.url, download_dir, untar=True)
    dump_cfg(cfg, download_dir / "config.cfg")


if __name__ == "__main__":
    main()
