import logging
import pathlib

import attrs
import hydra
import pandas as pd
from hydra.core.config_store import ConfigStore
from omegaconf import DictConfig

from llms4de.data import get_task_dir, load_json, get_experiments_path
from llms4de.model.generic import compute_cost_for_response

logger = logging.getLogger(__name__)


@attrs.define
class Config:
    pass


ConfigStore.instance().store(name="config", node=Config)


@hydra.main(version_base=None, config_name="config")
def main(cfg: DictConfig) -> None:
    task_dir = get_task_dir("column_type_annotation")
    all_paths = list(
        sorted(filter(lambda p: "enterprise-data-rows-ablations-cta" in p.name, task_dir.glob("*/experiments/*/"))))
    all_res = pd.DataFrame({"path": all_paths})
    all_res["cfg"] = all_res["path"].apply(lambda p: load_json(p / "results" / "config.cfg"))
    all_res["model"] = all_res["cfg"].apply(lambda cfg: cfg["model"])
    all_res["dataset"] = all_res["cfg"].apply(lambda cfg: cfg["dataset"]["dataset_name"])
    all_res["header"] = all_res["path"].apply(lambda p: p.name.split("_")[2])
    all_res["num_rows"] = all_res["cfg"].apply(lambda cfg: cfg["sample_rows"]["num_rows"])
    all_res["weighted avg f1-score"] = all_res["path"].apply(lambda p: load_score(p))
    all_res["total costs"] = all_res["path"].apply(lambda p: determine_cost(p / "responses"))

    table = pd.pivot_table(all_res, values=["weighted avg f1-score", "total costs"], index="model",
                           columns=["dataset", "header", "num_rows"])
    table.to_csv(
        get_experiments_path() / "enterprise_data_rows_ablations_cta" / "f1_scores_column_headers_rows.csv")


def load_score(path: pathlib.Path) -> float:
    return load_json(path / "results" / "classification_report.json")["weighted avg"]["f1-score"]


def determine_cost(path: pathlib.Path) -> float:
    total_cost = 0
    for res_path in path.glob("*.json"):
        response = load_json(res_path)
        total_cost += compute_cost_for_response(response)
    return total_cost


if __name__ == "__main__":
    main()
