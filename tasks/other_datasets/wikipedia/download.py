import logging

import datasets
import hydra
from omegaconf import DictConfig

from llms4de.data import get_download_dir, dump_cfg

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="../../../config/other_datasets", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    assert cfg.dataset.dataset_name == "wikipedia", "This script is dataset-specific."
    download_dir = get_download_dir(cfg.task_name, cfg.dataset.dataset_name, clear=True)

    datasets.load_dataset(
        "wikipedia",
        cfg.dataset.name,
        cache_dir=str(download_dir),
    )

    dump_cfg(cfg, download_dir / "config.cfg")


if __name__ == "__main__":
    main()
