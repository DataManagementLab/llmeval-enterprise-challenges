import logging
import random

import hydra
import pandas as pd
import tqdm
from omegaconf import DictConfig, OmegaConf

from llms4de.data import get_instances_dir, get_requests_dir, dump_json, load_json, dump_cfg
from llms4de.model.generic import max_tokens_for_ground_truth
from llms4de.prompting.linearize import linearize_table
from llms4de.prompting.template import fill_chat_template

logger = logging.getLogger(__name__)

sample_examples_random = random.Random(613907351)


def get_ground_truth_string(ground_truth: bool):
    if ground_truth:
        return "Yes"
    else:
        return "No"


@hydra.main(version_base=None, config_path="../../config/entity_matching", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    requests_dir = get_requests_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    instance_paths = list(sorted(instances_dir.glob("*/")))
    for path in tqdm.tqdm(instance_paths,
                          f"{cfg.task_name} - {cfg.dataset.dataset_name} - {cfg.exp_name} - prepare requests"):
        if not path.is_dir():
            continue
        instance_idx = int(path.parts[-1])

        # load instance data
        if cfg.dataset.dataset_name == "pay_to_inv" and cfg.dataset.schema_mode == "multi-table":
            source_rows = []
            for file in list(sorted(path.glob("*.csv"))):
                if "source" in file.name:
                    source_rows.append(pd.read_csv(file))
        else:
            source_row = pd.read_csv(path / "source_row.csv")
        target_row = pd.read_csv(path / "target_row.csv")
        ground_truth = load_json(path / "ground_truth.json")["rows_match"]
        ground_truth = get_ground_truth_string(ground_truth)

        # linearize each table
        if cfg.dataset.dataset_name == "pay_to_inv" and cfg.dataset.schema_mode == "multi-table":
            linearized_source_rows = []
            for s in source_rows:
                linearized_source_rows.append(linearize_table(s, table_name=None, **cfg.linearize_table))
            linearized_source_row = "   ".join(linearized_source_rows)
        else:
            linearized_source_row = linearize_table(source_row, table_name=None, **cfg.linearize_table)
        linearized_target_row = linearize_table(target_row, table_name=None, **cfg.linearize_table)

        examples = []
        # load examples (create lists of positive/negative ones during preprocessing?)
        pos_neg_indices = load_json(instances_dir / "examples_pos_neg.json")

        if cfg.sample_examples.num_examples > 0:
            k = cfg.sample_examples.num_examples

            # randomly choose a positive example and a negative one
            if instance_idx in pos_neg_indices["positive"]:
                pos_neg_indices["positive"].remove(instance_idx)
            elif instance_idx in pos_neg_indices["negative"]:
                pos_neg_indices["negative"].remove(instance_idx)

            chosen_pos_indices = sample_examples_random.sample(pos_neg_indices["positive"], k=k)
            chosen_neg_indices = sample_examples_random.sample(pos_neg_indices["negative"], k=k)

            example_instances = chosen_neg_indices + chosen_pos_indices
            sample_examples_random.shuffle(example_instances)

            for ex_idx in example_instances:
                ex_path = instances_dir / str(ex_idx)
                # Load example data
                if cfg.dataset.dataset_name == "pay_to_inv" and cfg.dataset.schema_mode == "multi-table":
                    ex_source_rows = []
                    for file in list(sorted(ex_path.glob("*.csv"))):
                        if "source" in file.name:
                            ex_source_rows.append(pd.read_csv(file))
                else:
                    ex_source_row = pd.read_csv(ex_path / "source_row.csv")
                ex_target_row = pd.read_csv(ex_path / "target_row.csv")
                ex_ground_truth = load_json(ex_path / "ground_truth.json")["rows_match"]

                # linearize example dfs
                if cfg.dataset.dataset_name == "pay_to_inv" and cfg.dataset.schema_mode == "multi-table":
                    ex_linearized_source_rows = []
                    for s in source_rows:
                        ex_linearized_source_rows.append(linearize_table(s, table_name=None, **cfg.linearize_table))
                    ex_linearized_source_row = "   ".join(ex_linearized_source_rows)
                else:
                    ex_linearized_source_row = linearize_table(ex_source_row, table_name=None, **cfg.linearize_table)
                ex_linearized_target_row = linearize_table(ex_target_row, table_name=None, **cfg.linearize_table)

                examples.append(
                    {
                        "first_table_row": ex_linearized_source_row,
                        "second_table_row": ex_linearized_target_row,
                        "ground_truth": get_ground_truth_string(ex_ground_truth)
                    }
                )

        request = {
            "model": cfg.model,
            "max_tokens": max_tokens_for_ground_truth(ground_truth, cfg.api_name, cfg.model,
                                                      cfg.max_tokens_over_ground_truth),
            "temperature": cfg.temperature
        }

        example_messages = []
        for example in examples:
            example_messages += fill_chat_template(OmegaConf.to_container(cfg.example_chat_template), **example)
        request["messages"] = fill_chat_template(
            OmegaConf.to_container(cfg.prompt_chat_template),
            examples=example_messages,
            first_table_row=linearized_source_row,
            second_table_row=linearized_target_row,
            ground_truth=ground_truth
        )

        dump_json(request, requests_dir / f"{path.name}.json")

    dump_cfg(cfg, requests_dir / "config.cfg")


if __name__ == "__main__":
    main()
