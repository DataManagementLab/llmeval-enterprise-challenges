import logging
import random

import hydra
from omegaconf import DictConfig, OmegaConf

from llms4de.data import get_instances_dir, get_requests_dir, dump_json, load_json
from llms4de.prompting.template import fill_chat_template

logger = logging.getLogger(__name__)

sample_examples_random = random.Random(613907351)


def create_request(cfg: DictConfig, instance_data: dict):
    # create_request
    request = {
        "model": cfg.model,
        "max_completion_tokens": 10,
        "temperature": cfg.temperature,
    }

    request["messages"] = fill_chat_template(
        OmegaConf.to_container(cfg.experiment.prompt_chat_template),
        company_A_row=instance_data["row_A"],
        company_B_row=instance_data["row_B"],
    )

    return request


@hydra.main(version_base=None, config_path="../../config/compound_task", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    requests_dir = get_requests_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    request_idx = 0
    for idx in range(len(list(instances_dir.glob("*.json")))):
        # create pairwise requests (pair every column from A with every column from B)
        try:
            instance_data = load_json(instances_dir / f"{idx}.json")
        except FileNotFoundError as e:
            print(e)
            continue

        request = create_request(cfg=cfg, instance_data=instance_data)
        dump_json(request, requests_dir / f"{request_idx}.json")
        request_idx += 1

    logger.debug("Done preparing requests")


if __name__ == "__main__":
    main()
