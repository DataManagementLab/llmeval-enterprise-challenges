import logging
import pathlib

import attrs
import hydra
import pandas as pd
from hydra.core.config_store import ConfigStore
from omegaconf import DictConfig

from llms4de.data import get_task_dir, load_json, get_experiments_path

logger = logging.getLogger(__name__)


@attrs.define
class Config:
    pass


ConfigStore.instance().store(name="config", node=Config)


@hydra.main(version_base=None, config_name="config")
def main(cfg: DictConfig) -> None:
    task_dir = get_task_dir("column_type_annotation")
    all_paths = list(
        sorted(filter(lambda p: "enterprise-challenges-cta" in p.name, task_dir.glob("*/experiments/*/"))))
    all_res = pd.DataFrame({"path": all_paths})
    all_res["cfg"] = all_res["path"].apply(lambda p: load_json(p / "results" / "config.cfg"))
    all_res["model"] = all_res["cfg"].apply(lambda cfg: cfg["model"])
    all_res["dataset"] = all_res["cfg"].apply(lambda cfg: cfg["dataset"]["dataset_name"])
    all_res["step"] = all_res["path"].apply(lambda p: p.name.split("_")[2])
    all_res["weighted avg f1-score"] = all_res["path"].apply(lambda p: load_score(p))

    ####################################################################################################################
    # F1 scores with headers vs. without headers
    ####################################################################################################################

    table = pd.pivot_table(all_res, values="weighted avg f1-score", index="model", columns=["dataset", "step"])
    table.to_csv(get_experiments_path() / "enterprise_challenges_cta" / "f1_scores.csv")


def load_score(path: pathlib.Path) -> float:
    return load_json(path / "results" / "classification_report.json")["weighted avg"]["f1-score"]


if __name__ == "__main__":
    main()
