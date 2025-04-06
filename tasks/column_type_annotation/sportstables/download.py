import logging
import os
import shutil
import subprocess

import hydra
import nbformat
from omegaconf import DictConfig

from llms4de.data import get_download_dir, dump_cfg

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="../../../config/column_type_annotation", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    assert cfg.dataset.dataset_name == "sportstables", "This script is dataset-specific."
    download_path = get_download_dir(cfg.task_name,
                                     cfg.dataset.dataset_name)  # do not clear download directory to enable manual clone

    repo_dir = download_path / "SportsTables"
    if not repo_dir.is_dir():
        logger.info(f"Clone the git repository.")
        try:
            subprocess.check_call(["git", "clone", cfg.dataset.url, str(repo_dir)])
        except:
            while not repo_dir.is_dir():
                logger.error("Automatically cloning the git repository failed.")
                input(f"Please manually execute `git clone {cfg.dataset.url} {repo_dir}` and press enter!")

    logger.info("Prepare and execute scraping code.")
    for sport in cfg.dataset.sports:
        logger.info(f"Scrape {sport}")

        # remove old data
        if download_path.joinpath(sport).is_dir():
            shutil.rmtree(download_path / sport)
        os.makedirs(download_path / sport)

        # copy metadata
        logger.info("Copy metadata.")
        shutil.copy(download_path / "SportsTables" / sport / "metadata.json", download_path / f"{sport}_metadata.json")

        # the code we need to scrape the tables is in a jupyter notebook...
        with open(download_path / "SportsTables" / sport / "web_scraping.ipynb", "r", encoding="utf-8") as file:
            notebook = nbformat.reads(file.read(), as_version=4)

        code = notebook.cells[1]["source"]
        code = code.replace("from dotenv import load_dotenv\nload_dotenv(override=True)",
                            f"import os\nos.environ['SportsTables'] = '{download_path}'")

        script_path = download_path / "SportsTables" / sport / "run.py"
        with open(script_path, "w", encoding="utf-8") as file:
            file.write(code)

        logger.info("Call the script. (This may take a while...)")
        subprocess.call(["python", str(script_path)])

    logger.info("Remove repository.")
    shutil.rmtree(repo_dir)

    dump_cfg(cfg, download_path / "config.cfg")
    logger.info("Done.")


if __name__ == "__main__":
    main()
