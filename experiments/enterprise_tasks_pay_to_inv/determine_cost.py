import json
import logging
import pathlib
import statistics

import attrs
import hydra
import pandas as pd
from hydra.core.config_store import ConfigStore

from llms4de.data import get_task_dir, get_experiments_path, dump_str
from llms4de.model._openai import MODEL_PARAMETERS

logger = logging.getLogger(__name__)


@attrs.define
class Config:
    pass


ConfigStore.instance().store(name="config", node=Config)


@hydra.main(version_base=None, config_name="config")
def main(cfg: Config) -> None:
    all_exp_paths = list(
        sorted(get_task_dir("entity_matching").glob(
            "pay_to_inv/experiments/enterprise-tasks-pay-to-inv_gpt-4o-2024-08-06_opaque_multi/")))
    all_res = pd.DataFrame({"path": all_exp_paths})
    all_res["response_paths"] = all_res["path"].apply(lambda p: list(sorted(p.joinpath("responses").glob("*.json"))))

    def response_path_to_costs(paths: list[pathlib.Path]) -> list[float]:
        costs = []
        for path in paths:
            with open(path, "r", encoding="utf-8") as file:
                response = json.load(file)
                costs.append(response["usage"]["prompt_tokens"] * MODEL_PARAMETERS["gpt-4o-2024-08-06"][
                    "cost_per_1k_input_tokens"] / 1_000
                             + response["usage"]["completion_tokens"] * MODEL_PARAMETERS["gpt-4o-2024-08-06"][
                                 "cost_per_1k_output_tokens"] / 1_000)
        return costs

    all_res["costs"] = all_res["response_paths"].apply(response_path_to_costs)
    all_res["avg_cost_per_pair"] = all_res["costs"].apply(statistics.mean)
    all_res["avg_cost_per_1M_pairs"] = all_res["avg_cost_per_pair"].apply(lambda c: round(c * 1_000 * 1_000))
    all_res["avg_cost_per_100M_pairs"] = all_res["avg_cost_per_pair"].apply(lambda c: round(c * 10_000 * 10_000))
    all_res["experiment"] = all_res["path"].apply(lambda p: p.name)
    all_res = all_res[["experiment", "avg_cost_per_1M_pairs", "avg_cost_per_100M_pairs"]]
    dump_str(str(all_res), get_experiments_path() / "enterprise_tasks_pay_to_inv" / "costs.txt")


if __name__ == "__main__":
    main()
