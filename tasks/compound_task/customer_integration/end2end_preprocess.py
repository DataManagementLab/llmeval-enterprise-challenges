import logging
import random
import shutil

import hydra
import pandas as pd
from omegaconf import DictConfig

from llms4de.data import get_download_dir, get_instances_dir

pd.options.mode.chained_assignment = None  # default='warn'
logger = logging.getLogger(__name__)

_random = random.Random(218411458)


@hydra.main(version_base=None, config_path="../../../config/compound_task", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    logger.info("#################### End2End ###########################")
    assert cfg.dataset.dataset_name == "customer_integration", "This script is dataset-specific."
    download_dir = get_download_dir(cfg.task_name, cfg.dataset.dataset_name)
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    # load customers A data
    company_A_df = pd.read_csv(download_dir / cfg.sub_dataset / "company_A_table.csv", dtype=str, sep=";")

    # load customers B data
    company_B_info_df = pd.read_csv(download_dir / cfg.sub_dataset / "company_B_table_info.csv", dtype=str, sep=";")
    company_B_contact_df = pd.read_csv(download_dir / cfg.sub_dataset / "company_B_table_contact.csv", dtype=str,
                                       sep=";")

    assert len(company_B_contact_df) == len(company_B_info_df)

    # save company dfs (but remove info_ columns!)
    company_A_df_filtered = company_A_df[company_A_df.columns[~company_A_df.columns.str.startswith("info_")]]
    company_A_df_filtered.to_csv(instances_dir / "company_A_data.csv", index=False, sep=";")

    company_B_info_df_filtered = company_B_info_df[
        company_B_info_df.columns[~company_B_info_df.columns.str.startswith("info_")]]
    company_B_info_df_filtered.to_csv(instances_dir / "company_B_info_data.csv", index=False, sep=";")

    company_B_contact_df_filtered = company_B_contact_df[
        company_B_contact_df.columns[~company_B_contact_df.columns.str.startswith("info_")]]
    company_B_contact_df_filtered.to_csv(instances_dir / "company_B_contact_data.csv", index=False, sep=";")

    # copy ground truth
    shutil.copy(download_dir / cfg.sub_dataset / "ground_truth_table.csv", instances_dir / "end2end_final_table.csv")

    logger.debug("Done preprocessing")


if __name__ == "__main__":
    main()
