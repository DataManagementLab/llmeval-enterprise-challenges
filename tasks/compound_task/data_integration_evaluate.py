import logging
import logging
import os
import pathlib
import re

import hydra
import pandas as pd
from omegaconf import DictConfig

from llms4de.data import dump_json, get_data_path, get_download_dir, get_instances_dir, get_results_dir, load_json, \
    get_responses_dir
from llms4de.evaluation.compound_task_metric import table_accuracy_alternative_names
from llms4de.model.generic import extract_text_from_response

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="../../config/compound_task", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    logger.debug("Starting evaluation")
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    responses_dir = get_responses_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    results_dir = get_results_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    # load ground truth df
    download_dir = get_download_dir(task_name=cfg.task_name, dataset_name=cfg.dataset.dataset_name)
    dataset_info = load_json(download_dir / cfg.sub_dataset / "data_info_ids.json")
    ground_truth_df = pd.read_csv(download_dir / cfg.sub_dataset / "ground_truth_table.csv", dtype=str, sep=";")
    ground_truth_merge_df = ground_truth_df[
        ground_truth_df["info_internal_id"].isin([str(x) for x in dataset_info["overlap"]])]
    ground_truth_transform_df = ground_truth_df[
        ground_truth_df["info_internal_id"].isin([str(x) for x in dataset_info["only_B"]])]

    # delete "info_" columns
    ground_truth_df = ground_truth_df[ground_truth_df.columns[~ground_truth_df.columns.str.startswith("info_")]]
    ground_truth_merge_df = ground_truth_merge_df[
        ground_truth_merge_df.columns[~ground_truth_merge_df.columns.str.startswith("info_")]]
    ground_truth_transform_df = ground_truth_transform_df[
        ground_truth_transform_df.columns[~ground_truth_transform_df.columns.str.startswith("info_")]]
    logger.info(
        f"Ground truth has {len(ground_truth_df)} rows, {len(ground_truth_merge_df)} merge, {len(ground_truth_transform_df)} overlap")

    # need real only rows from company A to build standalone prediction
    company_A_df_complete = pd.read_csv(download_dir / cfg.sub_dataset / "company_A_table.csv", dtype=str, sep=";")
    company_A_keep_df_standalone = company_A_df_complete[
        company_A_df_complete["info_internal_id"].isin([str(x) for x in dataset_info["only_A"]])]

    # for pipeline: load entity matching results to get rows that were only in table A to build pipeline predicted table
    entity_matching_exp_name = "entity_matching-" + cfg.sub_dataset + "-" + cfg.model
    entity_matching_results_dir = get_data_path() / cfg.task_name / cfg.dataset.dataset_name / "experiments" / entity_matching_exp_name / "results"
    company_A_keep_df_pipeline = pd.read_csv(entity_matching_results_dir / "entity_matching_rows_A_keep.csv", dtype=str,
                                             sep=";")

    final_predicted_df_pipeline = company_A_keep_df_pipeline[
        company_A_keep_df_pipeline.columns[~company_A_keep_df_pipeline.columns.str.startswith("info_")]]
    final_predicted_df_standalone = company_A_keep_df_standalone[
        company_A_keep_df_standalone.columns[~company_A_keep_df_standalone.columns.str.startswith("info_")]]

    row_answer_dir_pipeline = pathlib.Path(results_dir / "row_answers_pipeline")
    os.makedirs(row_answer_dir_pipeline)

    row_answer_dir_standalone = pathlib.Path(results_dir / "row_answers_standalone")
    os.makedirs(row_answer_dir_standalone)

    predicted_merge_df_standalone = pd.DataFrame(columns=final_predicted_df_standalone.columns)
    predicted_merge_df_pipeline = pd.DataFrame(columns=final_predicted_df_standalone.columns)
    predicted_transform_df_standalone = pd.DataFrame(columns=final_predicted_df_standalone.columns)
    predicted_transform_df_pipeline = pd.DataFrame(columns=final_predicted_df_standalone.columns)

    for idx in range(len(list(instances_dir.glob("*.json")))):
        # create pairwise requests (pair every column from A with every column from B)
        try:
            instance_data = load_json(instances_dir / f"{idx}.json")
        except FileNotFoundError as e:
            print(e)
            continue

        # load and parse response
        response = load_json(responses_dir / f"{idx}.json")
        response_text = extract_text_from_response(response)

        mode = instance_data["mode"]
        task = instance_data["task"]

        # clean response text:
        response_text = response_text.strip("```").strip()
        response_text = re.sub(r"^csv|csv$", "", response_text)

        response_text = response_text.replace("Here is the merged data in csv format with ; as the delimiter:\n\n", "")
        response_text = response_text.replace(
            "Here is the reformatted row from company B in the format of company A:\n\n", "")

        rows = response_text.strip().split("\n")

        # Extract header and data row
        header, data_rows = rows[0], rows[1:]
        if not "MANDT" in header:
            continue
        header_count = len(header.split(";"))
        column_counts = [len(row.split(";")) for row in data_rows]
        filtered_rows = [row for row, count in zip(data_rows, column_counts) if
                         count <= header_count and count > 0.75 * header_count]
        # if len(filtered_rows) < len(data_rows):
        #    logger.info(f"Cleaned output table, from {len(data_rows)} kept only {len(filtered_rows)}")
        cleaned_response_table = "\n".join([header] + filtered_rows) + "\n"

        with open(results_dir / f"row_answers_{mode}" / f'{idx}_row.csv', 'w') as f:
            f.write(cleaned_response_table)

        # with open(results_dir /  f"row_answers_{mode}" / f'{idx}_comment.txt', 'w') as f:
        #   f.write(response.comments.replace(".", ". \n"))

        try:
            predicted_output_row_df = pd.read_csv(results_dir / f"row_answers_{mode}" / f'{idx}_row.csv', sep=';',
                                                  dtype=str)

            if mode == "standalone":
                final_predicted_df_standalone = pd.concat((final_predicted_df_standalone, predicted_output_row_df),
                                                          ignore_index=True)
                if task == "merge":
                    predicted_merge_df_standalone = pd.concat((predicted_merge_df_standalone, predicted_output_row_df),
                                                              ignore_index=True)
                elif task == "transform":
                    predicted_transform_df_standalone = pd.concat(
                        (predicted_transform_df_standalone, predicted_output_row_df), ignore_index=True)
                else:
                    raise ValueError

            elif mode == "pipeline":
                final_predicted_df_pipeline = pd.concat((final_predicted_df_pipeline, predicted_output_row_df),
                                                        ignore_index=True)
                if task == "merge":
                    predicted_merge_df_pipeline = pd.concat((predicted_merge_df_pipeline, predicted_output_row_df),
                                                            ignore_index=True)
                elif task == "transform":
                    predicted_transform_df_pipeline = pd.concat(
                        (predicted_transform_df_pipeline, predicted_output_row_df), ignore_index=True)
                else:
                    raise ValueError

        except pd.errors.ParserError as e:
            logger.info(f"Parse error: {e}")

    for x in [predicted_merge_df_standalone, predicted_merge_df_pipeline, predicted_transform_df_standalone,
              predicted_transform_df_pipeline]:
        print(len(x))

    final_predicted_df_standalone.to_csv(results_dir / "final_predicted_table_standalone.csv", index=False, sep=";")
    final_predicted_df_pipeline.to_csv(results_dir / "final_predicted_table_pipeline.csv", index=False, sep=";")

    logger.info(f"Acc for pipeline")
    final_accuracy_pipeline, error_stats_pipe = table_accuracy_alternative_names(cfg, final_predicted_df_pipeline,
                                                                                 ground_truth_df,
                                                                                 primary_column="NAME1")
    logger.info(f"Acc for standalone")
    final_accuracy_standalone, error_stats_standalone = table_accuracy_alternative_names(cfg,
                                                                                         final_predicted_df_standalone,
                                                                                         ground_truth_df,
                                                                                         primary_column="NAME1")
    logger.info(f"Acc for pipeline merge")
    final_accuracy_merge_pipeline, _ = table_accuracy_alternative_names(cfg, predicted_merge_df_pipeline,
                                                                        ground_truth_merge_df, primary_column="NAME1")
    logger.info(f"Acc for standalone merge")
    final_accuracy_merge_standalone, _ = table_accuracy_alternative_names(cfg, predicted_merge_df_standalone,
                                                                          ground_truth_merge_df, primary_column="NAME1")
    logger.info(f"Acc for pipeline transform")
    final_accuracy_transform_pipeline, _ = table_accuracy_alternative_names(cfg, predicted_transform_df_pipeline,
                                                                            ground_truth_transform_df,
                                                                            primary_column="NAME1")
    logger.info(f"Acc for standalone transform")
    final_accuracy_transform_standalone, _ = table_accuracy_alternative_names(cfg, predicted_transform_df_standalone,
                                                                              ground_truth_transform_df,
                                                                              primary_column="NAME1")

    logger.info(
        f"DI Standalone - Final acc: {final_accuracy_standalone} - Merge: {final_accuracy_merge_standalone} - Transform: {final_accuracy_transform_standalone}")
    logger.info(
        f"DI Pipeline - Final acc: {final_accuracy_pipeline} - Merge: {final_accuracy_merge_pipeline} - Transform: {final_accuracy_transform_pipeline}")

    dump_json(obj={"accuracy_pipeline": final_accuracy_pipeline,
                   "acc_pipeline_merge": final_accuracy_merge_pipeline,
                   "acc_pipeline_transform": final_accuracy_transform_pipeline,
                   "accuracy_standalone": final_accuracy_standalone,
                   "acc_standalone_merge": final_accuracy_merge_standalone,
                   "acc_standalone_transform": final_accuracy_transform_standalone,
                   "errors_pipeline": error_stats_pipe,
                   "errors_standalone": error_stats_standalone}, path=results_dir / "metrics.json")


if __name__ == "__main__":
    main()
