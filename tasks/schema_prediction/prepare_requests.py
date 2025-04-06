import logging
import random

import hydra
import tqdm
from omegaconf import DictConfig, OmegaConf

from llms4de.data import get_instances_dir, get_requests_dir, load_json, load_str, dump_json, dump_cfg
from llms4de.model.generic import max_tokens_for_ground_truth
from llms4de.prompting.linearize import linearize_list
from llms4de.prompting.template import fill_chat_template

logger = logging.getLogger(__name__)

_prepare_requests_random = random.Random(859962185)


@hydra.main(version_base=None, config_path="../../config/schema_prediction", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    requests_dir = get_requests_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    # all_column_names = load_json(instances_dir / "table_header.json")

    instance_paths = list(sorted(instances_dir.glob("*/")))
    for path in tqdm.tqdm(instance_paths,
                          f"{cfg.task_name} - {cfg.dataset.dataset_name} - {cfg.exp_name} - prepare requests"):
        # load instance
        table_name = load_str(path / "table_name.txt")
        column_types = load_json(path / "table_header.json")
        inst_all_column_types = set(column_types)

        all_column_types = list(sorted(set(filter(lambda x: x is not None, inst_all_column_types))))
        linearized_all_column_types = linearize_list(all_column_types, **cfg.linearize_list)

        ground_truth = str(column_types)

        request = {
            "model": cfg.model,
            "max_tokens": max_tokens_for_ground_truth(
                ground_truth,
                cfg.api_name,
                cfg.model,
                cfg.max_tokens_over_ground_truth
            ),
            "temperature": cfg.temperature
        }

        request["messages"] = fill_chat_template(
            OmegaConf.to_container(cfg.prompt_chat_template),
            table=table_name,
            newline="\n"
        )

        dump_json(request, requests_dir / f"{path.name}.json")

    dump_cfg(cfg, requests_dir / "config.cfg")


if __name__ == "__main__":
    main()
