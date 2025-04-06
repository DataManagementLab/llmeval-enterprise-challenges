import gzip
import io
import logging
import shutil

import hydra
import requests
from omegaconf import DictConfig

from llms4de.data import get_download_dir, dump_cfg

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="../../../config/other_datasets", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    assert cfg.dataset.dataset_name == "imdb", "This script is dataset-specific."
    download_dir = get_download_dir(cfg.task_name, cfg.dataset.dataset_name, clear=True)
    for file_and_url in cfg.dataset.files_and_urls:
        logger.info(f"download and extract {file_and_url['url']}")
        response = requests.get(file_and_url['url'])
        zip_data = io.BytesIO(response.content)
        with gzip.open(zip_data, "rb") as f_in:
            with open(download_dir / file_and_url["file_name"], "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

    dump_cfg(cfg, download_dir / "config.cfg")


if __name__ == "__main__":
    main()
