import logging
import random

import hydra
import pandas as pd
from omegaconf import DictConfig

from llms4de.data import get_data_path, get_download_dir, get_instances_dir, dump_json, load_json
from llms4de.preprocessing import sample_rows
from llms4de.prompting.linearize import linearize_table

pd.options.mode.chained_assignment = None  # default='warn'
logger = logging.getLogger(__name__)

_random = random.Random(218411458)


def create_instances(request_idx, predicted_matches, company_A_df_complete, company_B_df_predicted, instances_dir,
                     examples_from_A_df, company_B_transform_df, cfg, setup_mode):
    # create instances for merging 
    # need to load data of pairs, then for each pair get A & B row and linearize them to dump them
    for match in predicted_matches:
        row_A = company_A_df_complete[company_A_df_complete["info_internal_id"] == match["internal_id_A"]]
        row_A_filtered = row_A.loc[:, ~row_A.columns.str.startswith("info_")]
        row_B = company_B_df_predicted[company_B_df_predicted["info_internal_id"] == match["internal_id_B"]]
        row_B_filtered = row_B.loc[:, ~row_B.columns.str.startswith("info_")]

        dump_json({
            "row_A": linearize_table(row_A_filtered, table_name=None, **cfg.linearize_table),
            "row_B": linearize_table(row_B_filtered, table_name=None, **cfg.linearize_table),
            "task": "merge",
            "mode": setup_mode
        },
            instances_dir / f"{request_idx}.json"
        )
        request_idx += 1

    # get three example rows from company_A_keep_df
    examples_A_df_filtered = examples_from_A_df[
        examples_from_A_df.columns[~examples_from_A_df.columns.str.startswith("info_")]]
    examples_A = sample_rows(table=examples_A_df_filtered, num_rows=3, mode='full')

    # create instances for transformation 
    for row_idx, row_to_transform in company_B_transform_df.iterrows():
        company_B_row_filtered = row_to_transform[~row_to_transform.index.str.startswith("info_")]
        dump_json(
            {"row_B": linearize_table(company_B_row_filtered.to_frame().T, table_name=None, **cfg.linearize_table),
             "example_A": linearize_table(examples_A, table_name=None, **cfg.linearize_table),
             "task": "transform",
             "mode": setup_mode
             },
            instances_dir / f"{request_idx}.json"
        )
        request_idx += 1

    return request_idx


@hydra.main(version_base=None, config_path="../../../config/compound_task", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    logger.info("#################### Data Integration ###########################")
    assert cfg.dataset.dataset_name == "customer_integration", "This script is dataset-specific."
    download_dir = get_download_dir(cfg.task_name, cfg.dataset.dataset_name)
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    # load company A data
    company_A_df_complete = pd.read_csv(download_dir / cfg.sub_dataset / "company_A_table.csv", dtype=str, sep=";")

    schema_matching_exp_name = "schema_matching-" + cfg.sub_dataset + "-" + cfg.model
    schema_matching_results_dir = get_data_path() / cfg.task_name / cfg.dataset.dataset_name / "experiments" / schema_matching_exp_name / "results"

    request_idx = 0

    ################# Standalone instances ############################################

    # load info
    dataset_info = load_json(download_dir / cfg.sub_dataset / "data_info_ids.json")
    example_from_A_df = pd.read_csv(download_dir / cfg.sub_dataset / "examples_company_A.csv", dtype=str, sep=";")
    company_A_keep_df = company_A_df_complete[
        company_A_df_complete["info_internal_id"].isin([str(x) for x in dataset_info["only_A"]])]

    # need true matches
    predicted_matches = []
    for overlap_id in dataset_info["overlap"]:
        predicted_matches.append({"internal_id_A": str(overlap_id), "internal_id_B": str(overlap_id)})

    # need true rows that are only in company B
    company_B_transform_df = pd.read_csv(download_dir / cfg.sub_dataset / "company_B_table_joined.csv", dtype=str,
                                         sep=";")
    company_B_transform_df = company_B_transform_df[
        company_B_transform_df["info_internal_id"].isin([str(x) for x in dataset_info["only_B"]])]
    # need table B in correct schema
    company_B_df_predicted = pd.read_csv(schema_matching_results_dir / "table_B_in_gt_schema.csv", dtype=str, sep=";")

    request_idx = create_instances(request_idx=request_idx,
                                   predicted_matches=predicted_matches,
                                   company_A_df_complete=company_A_df_complete,
                                   company_B_df_predicted=company_B_df_predicted,
                                   examples_from_A_df=example_from_A_df,
                                   company_B_transform_df=company_B_transform_df,
                                   instances_dir=instances_dir,
                                   cfg=cfg,
                                   setup_mode="standalone")

    ################# Pipeline instances ############################################

    # load entity matching results
    entity_matching_exp_name = "entity_matching-" + cfg.sub_dataset + "-" + cfg.model
    entity_matching_results_dir = get_data_path() / cfg.task_name / cfg.dataset.dataset_name / "experiments" / entity_matching_exp_name / "results"

    company_A_keep_df = pd.read_csv(entity_matching_results_dir / "entity_matching_rows_A_keep.csv", dtype=str, sep=";")
    company_B_transform_df = pd.read_csv(entity_matching_results_dir / "entity_matching_rows_B_transform.csv",
                                         dtype=str, sep=";")

    predicted_matches = load_json(entity_matching_results_dir / "predicted_matches.json")

    # load company B data
    company_B_df_predicted = pd.read_csv(schema_matching_results_dir / "table_B_in_predicted_schema.csv", dtype=str,
                                         sep=";")

    request_idx = create_instances(request_idx=request_idx,
                                   predicted_matches=predicted_matches,
                                   company_A_df_complete=company_A_df_complete,
                                   company_B_df_predicted=company_B_df_predicted,
                                   examples_from_A_df=example_from_A_df,
                                   company_B_transform_df=company_B_transform_df,
                                   instances_dir=instances_dir,
                                   cfg=cfg,
                                   setup_mode="pipeline")

    logger.debug(f"Done preprocessing, request_idx is {request_idx}")


if __name__ == "__main__":
    main()
