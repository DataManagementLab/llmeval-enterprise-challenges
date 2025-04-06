import logging

import hydra
import pandas as pd
from omegaconf import DictConfig
from pydantic import BaseModel

from llms4de.data import get_download_dir, get_instances_dir, get_results_dir, load_json, get_responses_dir, dump_json
from llms4de.evaluation.metrics import ConfusionMatrix
from llms4de.model.generic import extract_text_from_response

logger = logging.getLogger(__name__)


class End2endResponse(BaseModel):
    output_table: str
    comments: str


def fill_schema(cfg: DictConfig, predicted_schema: dict):
    #### Fill schema with data
    download_dir = get_download_dir(cfg.task_name, cfg.dataset.dataset_name)
    # load customers B data
    company_B_df = pd.read_csv(download_dir / cfg.sub_dataset / "company_B_table_joined.csv", dtype=str, sep=";")

    # create list of dictionaries
    table_B_in_predicted_schema = []
    for index, company_B_row in company_B_df.iterrows():
        new_row = {}
        for key, value in predicted_schema.items():
            if len(value) == 0:
                new_row[key] = None
            elif len(value) == 1:
                new_row[key] = str(company_B_row[value[0]])
            else:  # len(value) > 1:
                column_value = ""
                for v in value:
                    column_value += str(company_B_row[v]) + " "
                new_row[key] = column_value

        new_row["info_internal_id"] = company_B_row["info_internal_id"]
        new_row["info_is_altered"] = company_B_row["info_is_altered"]
        new_row["info_altering"] = company_B_row["info_altering"]
        table_B_in_predicted_schema.append(new_row)

    table_B_in_predicted_schema = pd.DataFrame(table_B_in_predicted_schema)

    return table_B_in_predicted_schema


@hydra.main(version_base=None, config_path="../../config/compound_task", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    logger.debug("Starting evaluation")
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    responses_dir = get_responses_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    results_dir = get_results_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    # load ground truth table
    ground_truth = load_json(instances_dir / "schema_matching_ground_truth.json")
    assert type(ground_truth) == dict

    confusion = ConfusionMatrix.empty()

    all_predictions = {key: [] for key in ground_truth.keys()}

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
            all_predictions[instance_data["col_A"]].append(instance_data["col_B"])
        elif "no" in response_text.lower():
            pred = False
        else:
            logger.error(f"Response not yes/no: {response_text}")
            raise NotImplementedError

        confusion.push(prediction=pred, ground_truth=instance_data["match"])

    # print(f"Confusion:", confusion)

    # print(f"Have {gt_matches} gt matches in dataset")

    print("Mistakes are: (column_A, gt, pred)")

    correct_mappings = 0
    for key, gt_value in ground_truth.items():
        if set(all_predictions[key]) == set(gt_value):
            correct_mappings += 1
        else:
            pass
            print(key, gt_value, all_predictions[key])

    accuracy = correct_mappings / len(ground_truth.keys())
    logger.info(f"Final Schema Matching accuracy: {accuracy}")

    dump_json(obj={"accuracy": accuracy}, path=results_dir / "metrics.json")
    dump_json(obj=all_predictions, path=results_dir / "predicted_schema.json")

    table_B_in_predicted_schema = fill_schema(cfg=cfg, predicted_schema=all_predictions)
    table_B_in_predicted_schema.to_csv(path_or_buf=results_dir / "table_B_in_predicted_schema.csv", index=False,
                                       sep=";")

    table_B_in_gt_schema = fill_schema(cfg=cfg, predicted_schema=ground_truth)
    table_B_in_gt_schema.to_csv(path_or_buf=results_dir / "table_B_in_gt_schema.csv", index=False, sep=";")


if __name__ == "__main__":
    main()
