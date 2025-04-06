import logging
import re

import hydra
import pandas as pd
from omegaconf import DictConfig
from pydantic import ValidationError

from llms4de.data import dump_json, get_instances_dir, get_results_dir, load_json, get_responses_dir
from llms4de.evaluation.compound_task_metric import table_accuracy_alternative_names
from llms4de.model.generic import extract_text_from_response, extract_finish_reason_from_response

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="../../config/compound_task", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    logger.debug("Starting evaluation")
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    responses_dir = get_responses_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    results_dir = get_results_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    # load ground truth table
    ground_truth_df = pd.read_csv(instances_dir / "end2end_final_table.csv", dtype=str, sep=";")
    ground_truth_df = ground_truth_df[ground_truth_df.columns[~ground_truth_df.columns.str.startswith("info_")]]

    for template_name in ["text", "steps"]:
        response = load_json(responses_dir / f"end2end_request_{template_name}.json")

        finish_reason = extract_finish_reason_from_response(response)
        print(finish_reason)

        if finish_reason == "length":
            final_accuracy = 0
            error_stats = "response not evaluated, token limit reached"
            logger.error(f"Response was not finished due to length")
        else:
            response_text = extract_text_from_response(response)

            print(f"Got repsonse text: {len(response_text)}")

            # clean response text:
            response_text = response_text.strip("```").strip().replace('"', "")
            response_text = re.sub(r"^csv|csv$", "", response_text)

            try:
                # delete rows from response text that have a inconsistent number of columns
                rows = response_text.strip().split("\n")
                print(f"Got rows: {len(rows)}")
                # Extract header and data rows
                header, data_rows = rows[0], rows[1:]
                header_count = len(header.split(";"))
                column_counts = [len(row.split(";")) for row in data_rows]
                filtered_rows = [row for row, count in zip(data_rows, column_counts) if
                                 count <= header_count and count > 0.75 * header_count]
                if len(filtered_rows) < len(data_rows):
                    logger.info(f"Cleaned output table, from {len(data_rows)} kept only {len(filtered_rows)}")
                cleaned_response_table = "\n".join([header] + filtered_rows) + "\n"

                with open(results_dir / f'output_table_{template_name}.csv', 'w') as f:
                    f.write(cleaned_response_table)

                print("Wrote output table")

                try:
                    predicted_output_table_df = pd.read_csv(results_dir / f'output_table_{template_name}.csv', sep=';',
                                                            dtype=str)
                    print("Parsing successful")
                    predicted_output_table_df = predicted_output_table_df.map(lambda x: str(x) if pd.notna(x) else x)

                    # print(len(predicted_output_table_df), "rows, gt has", len(ground_truth_df))

                    final_accuracy, error_stats = table_accuracy_alternative_names(cfg, predicted_output_table_df,
                                                                                   ground_truth_df,
                                                                                   primary_column="NAME1")
                except pd.errors.ParserError as e:
                    print(e)
                    final_accuracy = 0
                    error_stats = f"Parse error: {e}"
                    logger.error(f"Couldn't parse table of {template_name} template, setting accuracy to 0")

            except ValidationError as e:
                logger.error(e)
                final_accuracy = 0
                logger.error(f"Error in response, setting accuracy to 0")

        logger.info(f"Final end2end accuracy with {template_name} template is {final_accuracy}")

        dump_json(obj={f"accuracy_{template_name}": final_accuracy,
                       "error_stats": error_stats},
                  path=results_dir / f"metrics_{template_name}_template.json")


if __name__ == "__main__":
    main()
