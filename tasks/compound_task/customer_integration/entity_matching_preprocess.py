import logging
import random

import hydra
import pandas as pd
from omegaconf import DictConfig

from llms4de.data import get_data_path, get_download_dir, get_instances_dir, dump_json, load_json
from llms4de.prompting.linearize import linearize_table

pd.options.mode.chained_assignment = None  # default='warn'
logger = logging.getLogger(__name__)

_random = random.Random(218411458)


@hydra.main(version_base=None, config_path="../../../config/compound_task", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    logger.info("#################### Entity Matching ###########################")
    assert cfg.dataset.dataset_name == "customer_integration", "This script is dataset-specific."
    download_dir = get_download_dir(cfg.task_name, cfg.dataset.dataset_name)
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    # load customers A data
    company_A_df = pd.read_csv(download_dir / cfg.sub_dataset / "company_A_table.csv", dtype=str, sep=";")

    # load customers B data from schema_matching experiment
    # exp_name: "${subtask}-${sub_dataset}-${model}"
    schema_matching_exp_name = "schema_matching-" + cfg.sub_dataset + "-" + cfg.model
    schema_matching_results_dir = get_data_path() / cfg.task_name / cfg.dataset.dataset_name / "experiments" / schema_matching_exp_name / "results"

    company_B_df_predicted = pd.read_csv(schema_matching_results_dir / "table_B_in_predicted_schema.csv", dtype=str,
                                         sep=";")

    company_B_df_gt = pd.read_csv(schema_matching_results_dir / "table_B_in_gt_schema.csv", dtype=str, sep=";")

    # load GT
    gt_matches = load_json(download_dir / cfg.sub_dataset / "GT_entity_matching.json")["matches"]
    request_idx = 0
    # loop through company A rows:
    for index_A, row_from_A in company_A_df.iterrows():
        row_A_idx = row_from_A["info_internal_id"]
        # get row A without info columns
        company_A_row_filtered = row_from_A[~row_from_A.index.str.startswith("info_")]
        # linearize row_A

        for index_B, row_from_B in company_B_df_predicted.iterrows():
            row_B_idx = row_from_B["info_internal_id"]
            company_B_row_filtered = row_from_B[~row_from_B.index.str.startswith("info_")]

            match = False
            altered_in = "No"

            if row_A_idx == row_B_idx:
                match = True
                altered_in = [x["altered_in"] for x in gt_matches if x["info_internal_id"] == int(row_A_idx)][0]

            dump_json(
                {"row_A": linearize_table(company_A_row_filtered.to_frame().T, table_name=None, **cfg.linearize_table),
                 "row_B": linearize_table(company_B_row_filtered.to_frame().T, table_name=None, **cfg.linearize_table),
                 "match": match,
                 "altered_in": altered_in,
                 "row_A_idx": row_A_idx,
                 "row_B_idx": row_B_idx
                 },
                instances_dir / f"{request_idx}.json"
            )
            request_idx += 1

    logger.debug("Done preprocessing")


if __name__ == "__main__":
    main()
