import logging
import os

import hydra
import pandas as pd
import tqdm
from omegaconf import DictConfig

from llms4de.data import get_download_dir, get_instances_dir, dump_json

logger = logging.getLogger(__name__)


def random_sort_df(df):
    return df.sample(frac=1).reset_index(drop=True)


@hydra.main(version_base=None, config_path="../../../config/text2signal", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    assert cfg.dataset.dataset_name == "signavio", "This script is dataset-specific."
    download_dir = get_download_dir(cfg.task_name, cfg.dataset.dataset_name)
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    #   signal_queries = load_json(download_dir / f"signal.json")
    file_path = download_dir / f"signavio_test_data.csv"

    try:
        df = pd.read_csv(file_path)
    #        df = random_sort_df(df)

    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
    except pd.errors.EmptyDataError:
        print(f"Error: The file at {file_path} is empty.")
    except Exception as e:
        print(f"An error occurred: {e}")

    ix = 0
    for _, row in tqdm.tqdm(df.iterrows(),
                            desc=f"{cfg.task_name} - {cfg.dataset.dataset_name} - {cfg.exp_name} - preprocess"):
        instance_dir = instances_dir / f"{ix}"
        os.makedirs(instance_dir, exist_ok=True)
        signal = row.to_dict()

        dump_json(signal, instance_dir / f"signal.json")

        ix += 1
        if ix == cfg.limit_instances:
            break


if __name__ == "__main__":
    main()
