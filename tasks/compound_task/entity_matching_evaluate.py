import logging

import hydra
import pandas as pd
from omegaconf import DictConfig
from pydantic import BaseModel

from llms4de.data import get_data_path, get_download_dir, get_instances_dir, get_results_dir, load_json, \
    get_responses_dir, dump_json
from llms4de.evaluation.metrics import ConfusionMatrix
from llms4de.model.generic import extract_text_from_response

logger = logging.getLogger(__name__)


class End2endResponse(BaseModel):
    output_table: str
    comments: str


@hydra.main(version_base=None, config_path="../../config/compound_task", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    logger.debug("Starting evaluation")
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    responses_dir = get_responses_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    results_dir = get_results_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    confusion = ConfusionMatrix.empty()

    predicted_matches = []
    predicted_match_ids = set()

    gt_matches = 0
    for idx in range(len(list(responses_dir.glob("*.json")))):
        # load instance data
        try:
            instance_data = load_json(instances_dir / f"{idx}.json")
        except FileNotFoundError as e:
            # print(e)
            continue

        if instance_data["match"]:
            gt_matches += 1

        response = load_json(responses_dir / f"{idx}.json")
        response_text = extract_text_from_response(response)

        # parse response
        if "yes" in response_text.lower():
            pred = True
            predicted_matches.append(
                {"internal_id_A": instance_data["row_A_idx"], "internal_id_B": instance_data["row_B_idx"]})
            predicted_match_ids.add(instance_data["row_A_idx"])
            predicted_match_ids.add(instance_data["row_B_idx"])
            # all_predictions[instance_data["col_A"]].append(instance_data["col_B"])
        elif "no" in response_text.lower():
            pred = False
        else:
            logger.error(f"Response not yes/no: {response_text}")
            raise NotImplementedError

        confusion.push(prediction=pred, ground_truth=instance_data["match"])

    # print(f"Confusion:", confusion, "F1", confusion.f1_score, "Acc", confusion.accuracy)

    # print(f"Have {gt_matches} gt matches in dataset")

    # print(predicted_matches)

    # save predicted matches seperately!
    dump_json(obj=predicted_matches, path=results_dir / "predicted_matches.json")

    # create predicted output table

    # load data from A
    download_dir = get_download_dir(task_name=cfg.task_name, dataset_name=cfg.dataset.dataset_name)
    company_A_df = pd.read_csv(download_dir / cfg.sub_dataset / "company_A_table.csv", dtype=str, sep=";")

    # load data from B (output of schema matching)
    schema_matching_exp_name = "schema_matching-" + cfg.sub_dataset + "-" + cfg.model
    schema_matching_results_dir = get_data_path() / cfg.task_name / cfg.dataset.dataset_name / "experiments" / schema_matching_exp_name / "results"

    company_B_df_predicted = pd.read_csv(schema_matching_results_dir / "table_B_in_predicted_schema.csv", dtype=str,
                                         sep=";")
    schema_matching_accuracy = load_json(schema_matching_results_dir / "metrics.json")["accuracy"]

    # take all rows that were not identified in the matches
    filtered_A_df = company_A_df[~company_A_df["info_internal_id"].isin(predicted_match_ids)]
    filtered_B_df = company_B_df_predicted[~company_B_df_predicted["info_internal_id"].isin(predicted_match_ids)]

    # take only one of the rows that were identified to match (fill cells with placeholder)
    entity_matching_output_df = pd.concat((filtered_A_df, filtered_B_df), ignore_index=True)
    match_temp_rows_df = pd.DataFrame(index=range(len(predicted_match_ids)), columns=entity_matching_output_df.columns,
                                      data="merge placeholder row")
    for index, i in enumerate(predicted_match_ids):
        match_temp_rows_df.loc[index, "info_internal_id"] = i
    entity_matching_output_df = pd.concat((entity_matching_output_df, match_temp_rows_df), ignore_index=True)

    entity_matching_output_df.to_csv(results_dir / "entity_matching_predicted_output_table.csv", index=False, sep=";")

    # load ground truth
    ground_truth_df = pd.read_csv(download_dir / cfg.sub_dataset / "ground_truth_table.csv", dtype=str, sep=";")

    # Evaluate how many rows are correct (count mistakes)
    num_mistakes = 0
    gt_checks = set()  # collect internal IDs that were seen in output already to detect duplicates
    for out_row_ix, row in entity_matching_output_df.iterrows():
        # predicted row is in ground truth?
        if row["info_internal_id"] in list(ground_truth_df["info_internal_id"]):
            if row["info_internal_id"] in gt_checks:
                num_mistakes += 1  # is a duplicate row --> incorrect
            else:
                gt_checks.add(row["info_internal_id"])
        else:
            num_mistakes += 1  # not in GT --> incorrect (should not really occur?)
    assert ground_truth_df.info_internal_id.is_unique
    for gt_row_ix, row in ground_truth_df.iterrows():
        if row["info_internal_id"] not in gt_checks:
            num_mistakes += 1  # row from GT not in prediction --> incorrect

    entity_matching_accuracy = max(1 - (num_mistakes / len(ground_truth_df)), 0)
    final_accuracy = schema_matching_accuracy * entity_matching_accuracy

    # load accuracy from schema matching step and multiply!

    logger.info(f"Had {num_mistakes} mistakes in entity matching")

    logger.info(
        f"Final Entity Matching Pipeline Accuracy: {final_accuracy}, Standalone Accuracy: {entity_matching_accuracy}")
    dump_json(obj={"accuracy_pipeline": final_accuracy, "accuracy_standalone": entity_matching_accuracy},
              path=results_dir / "metrics.json")

    filtered_A_df.to_csv(results_dir / "entity_matching_rows_A_keep.csv", index=False, sep=";")
    filtered_B_df.to_csv(results_dir / "entity_matching_rows_B_transform.csv", index=False, sep=";")


if __name__ == "__main__":
    main()
