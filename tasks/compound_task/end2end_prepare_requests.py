import logging
import random

import hydra
import pandas as pd
from omegaconf import DictConfig, OmegaConf

from llms4de.data import get_instances_dir, get_requests_dir, dump_json, dump_cfg
from llms4de.prompting.linearize import linearize_table
from llms4de.prompting.template import fill_chat_template

logger = logging.getLogger(__name__)

sample_examples_random = random.Random(613907351)


@hydra.main(version_base=None, config_path="../../config/compound_task", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    requests_dir = get_requests_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    # have only one instance for end2end

    # load instance data
    company_A_df = pd.read_csv(instances_dir / "company_A_data.csv", dtype=str, sep=";")
    company_B_info_df = pd.read_csv(instances_dir / "company_B_info_data.csv", dtype=str, sep=";")
    company_B_contact_df = pd.read_csv(instances_dir / "company_B_contact_data.csv", dtype=str, sep=";")

    assert len(company_B_contact_df) == len(company_B_info_df)

    # linearize the tables
    company_A_data_linearized = linearize_table(table=company_A_df, table_name="Customers", **cfg.linearize_table)
    company_B_info_data_linearized = linearize_table(table=company_B_info_df, table_name="Customer Information Table",
                                                     **cfg.linearize_table)
    company_B_contact_data_linearized = linearize_table(table=company_B_contact_df,
                                                        table_name="Customer Contact Details Table",
                                                        **cfg.linearize_table)

    # create_request
    request = {
        "model": cfg.model,
        "max_completion_tokens": None
    }

    if not "o1" in cfg.model:
        request["temperature"] = cfg.temperature

    ######## basic text request
    request["messages"] = fill_chat_template(
        OmegaConf.to_container(cfg.experiment.prompt_chat_template_text),
        company_A_table=company_A_data_linearized,
        company_B_info_table=company_B_info_data_linearized,
        company_B_contact_table=company_B_contact_data_linearized
    )

    dump_json(request, requests_dir / f"end2end_request_text.json")

    ################ steps request
    request["messages"] = fill_chat_template(
        OmegaConf.to_container(cfg.experiment.prompt_chat_template_steps),
        company_A_table=company_A_data_linearized,
        company_B_info_table=company_B_info_data_linearized,
        company_B_contact_table=company_B_contact_data_linearized
    )

    dump_json(request, requests_dir / f"end2end_request_steps.json")

    dump_cfg(cfg, requests_dir / "config.cfg")

    logger.debug("Done preparing requests")


if __name__ == "__main__":
    main()
