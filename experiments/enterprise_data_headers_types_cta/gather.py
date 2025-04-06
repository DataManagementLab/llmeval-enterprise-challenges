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
        sorted(filter(lambda p: "enterprise-data-headers-types-cta" in p.name, task_dir.glob("*/experiments/*/"))))
    all_res = pd.DataFrame({"path": all_paths})
    all_res["cfg"] = all_res["path"].apply(lambda p: load_json(p / "results" / "config.cfg"))
    all_res["model"] = all_res["cfg"].apply(lambda cfg: cfg["model"])
    all_res["dataset"] = all_res["cfg"].apply(lambda cfg: cfg["dataset"]["dataset_name"])
    all_res["header"] = all_res["path"].apply(lambda p: p.name.split("_")[2])
    all_res["weighted avg f1-score"] = all_res["path"].apply(lambda p: load_score(p))

    ####################################################################################################################
    # F1 scores with headers vs. without headers
    ####################################################################################################################

    table = pd.pivot_table(all_res, values="weighted avg f1-score", index="model", columns=["dataset", "header"])
    table.to_csv(get_experiments_path() / "enterprise_data_headers_types_cta" / "f1_scores_column_headers.csv")

    ####################################################################################################################
    # F1 scores by data type
    ####################################################################################################################

    df_non_num = all_res.copy()
    df_non_num["data_type"] = "non-numerical"
    df_non_num["weighted avg f1-score"] = df_non_num["path"].apply(lambda p: load_score_non_numerical(p))

    df_num = all_res.copy()
    df_num["data_type"] = "numerical"
    df_num["weighted avg f1-score"] = df_num["path"].apply(lambda p: load_score_numerical(p))
    df_all = pd.concat((df_non_num, df_num), ignore_index=True)
    df_all = df_all[df_all["header"] == "with-headers"]

    table = pd.pivot_table(df_all, values="weighted avg f1-score", index="model", columns=["dataset", "data_type"])
    table.to_csv(get_experiments_path() / "enterprise_data_headers_types_cta" / "f1_scores_by_data_types.csv")


def load_score(path: pathlib.Path) -> float:
    return load_json(path / "results" / "classification_report.json")["weighted avg"]["f1-score"]


def load_score_numerical(path: pathlib.Path) -> float:
    report = load_json(path / "results" / "classification_report_by_data_type.json")
    return report["numerical"]["weighted avg"]["f1-score"]


def load_score_non_numerical(path: pathlib.Path) -> float:
    report = load_json(path / "results" / "classification_report_by_data_type.json")
    return report["non-numerical"]["weighted avg"]["f1-score"]


if __name__ == "__main__":
    main()
