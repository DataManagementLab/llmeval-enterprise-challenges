import logging
import random

import hydra
import pandas as pd
from omegaconf import DictConfig

from llms4de.data import get_download_dir, get_instances_dir, dump_json
from llms4de.preprocessing import sample_rows
from llms4de.prompting.linearize import linearize_table

pd.options.mode.chained_assignment = None  # default='warn'
logger = logging.getLogger(__name__)

_random = random.Random(218411458)


@hydra.main(version_base=None, config_path="../../../config/compound_task", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    logger.info("#################### Schema Matching ###########################")
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

    # remove info_ columns from dataframes
    company_A_df_filtered = company_A_df[company_A_df.columns[~company_A_df.columns.str.startswith("info_")]]

    company_B_info_df_filtered = company_B_info_df[
        company_B_info_df.columns[~company_B_info_df.columns.str.startswith("info_")]]

    company_B_contact_df_filtered = company_B_contact_df[
        company_B_contact_df.columns[~company_B_contact_df.columns.str.startswith("info_")]]

    # save ground truth
    ground_truth = {
        "MANDT": [],
        "KUNNR": [],
        "LAND1": ["Address 1"],
        "NAME1": ["Organization Name"],
        "STRAS": ["Address 1"],
        "ORT01": ["Address 1"],
        "PSTLZ": ["Address 1"],
        "TELF1": ["Country Prefix", "Contact Number"],
        "SMTP_ADDR": ["Email Address"],
        "SPRAS": [],
        "ERDAT": ["Creation Date"],
        # "ERNAM": ["User Created"],
        "UPDAT": ["Modification Date"],
        "WAERS": [],
        "STCEG": ["TAX Number"],
        "STCD1": ["TAX Number"],
    }

    examples_A = sample_rows(table=company_A_df_filtered, num_rows=3, mode='full')
    examples_B_info = sample_rows(table=company_B_info_df_filtered, num_rows=3, mode='full')
    examples_B_contact = sample_rows(table=company_B_contact_df_filtered, num_rows=3, mode='full')

    # save instances (pair every column from A with every column from B)
    request_idx = 0
    for column_from_A in company_A_df_filtered.columns:

        for column_from_B in company_B_contact_df_filtered.columns:
            match = False
            if column_from_B in ground_truth[column_from_A]:
                match = True

            dump_json({"col_A": column_from_A,
                       "col_B": column_from_B,
                       "match": match,
                       # "example_A": list(examples_A[column_from_A]),
                       # "example_B": list(examples_B_contact[column_from_B])
                       "example_A": linearize_table(examples_A, table_name=None, **cfg.linearize_table),
                       "example_B": linearize_table(examples_B_contact, table_name=None, **cfg.linearize_table),
                       },
                      instances_dir / f"{request_idx}.json")
            request_idx += 1

        for column_from_B in company_B_info_df_filtered.columns:
            match = False
            if column_from_B in ground_truth[column_from_A]:
                match = True

            if column_from_B == "ID":
                continue  # already have "Customer ID" from contact table, skip here
            else:
                dump_json({"col_A": column_from_A,
                           "col_B": column_from_B,
                           "match": match,
                           # "example_A": list(examples_A[column_from_A]),
                           # "example_B": list(examples_B_info[column_from_B])
                           "example_A": linearize_table(examples_A, table_name=None, **cfg.linearize_table),
                           "example_B": linearize_table(examples_B_info, table_name=None, **cfg.linearize_table),
                           },
                          instances_dir / f"{request_idx}.json")
                request_idx += 1

    dump_json(ground_truth, instances_dir / "schema_matching_ground_truth.json")

    logger.debug("Done preprocessing")


if __name__ == "__main__":
    main()
