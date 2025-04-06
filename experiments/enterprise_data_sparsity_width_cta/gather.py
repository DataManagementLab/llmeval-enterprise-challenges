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

    ####################################################################################################################
    # ablation for sparsity
    ####################################################################################################################
    all_paths = list(
        sorted(filter(lambda p: "enterprise-data-sparsity-width-cta" in p.name,
                      task_dir.glob("*/experiments/*_sparsity/"))))
    all_res = pd.DataFrame({"path": all_paths})
    all_res["cfg"] = all_res["path"].apply(lambda p: load_json(p / "results" / "config.cfg"))
    all_res["model"] = all_res["cfg"].apply(lambda cfg: cfg["model"])
    all_res["dataset"] = all_res["cfg"].apply(lambda cfg: cfg["dataset"]["dataset_name"])
    all_res["header"] = all_res["path"].apply(lambda p: p.name.split("_")[2])
    all_res["classification_report_by_sparsity"] = all_res["path"].apply(lambda p: load_cr_sparsity(p))

    table = all_res.copy()
    sparsities = list(sorted(table.iloc[0]["classification_report_by_sparsity"].keys()))
    for sparsity in sparsities:
        table[sparsity] = table["classification_report_by_sparsity"].apply(
            lambda r: r[sparsity]["weighted avg"]["f1-score"])
    del table["classification_report_by_sparsity"]
    table.to_csv(get_experiments_path() / "enterprise_data_sparsity_width_cta" / "f1_scores_by_sparsity.csv")

    ####################################################################################################################
    # ablation for table width
    ####################################################################################################################
    all_paths = list(
        sorted(filter(lambda p: "enterprise-data-sparsity-width-cta" in p.name,
                      task_dir.glob("*/experiments/*_num_columns/"))))
    all_res = pd.DataFrame({"path": all_paths})
    all_res["cfg"] = all_res["path"].apply(lambda p: load_json(p / "results" / "config.cfg"))
    all_res["model"] = all_res["cfg"].apply(lambda cfg: cfg["model"])
    all_res["dataset"] = all_res["cfg"].apply(lambda cfg: cfg["dataset"]["dataset_name"])
    all_res["header"] = all_res["path"].apply(lambda p: p.name.split("_")[2])
    all_res["classification_report_by_num_columns"] = all_res["path"].apply(lambda p: load_cr_width(p))

    table = all_res.copy()
    num_columnss = list(sorted(table.iloc[0]["classification_report_by_num_columns"].keys()))
    for num_columns in num_columnss:
        table[num_columns] = table["classification_report_by_num_columns"].apply(
            lambda r: r[num_columns]["weighted avg"]["f1-score"])

    del table["classification_report_by_num_columns"]
    table.to_csv(get_experiments_path() / "enterprise_data_sparsity_width_cta" / "f1_scores_by_num_columns.csv")


def load_cr_width(path: pathlib.Path) -> float:
    return load_json(path / "results" / "classification_report_by_num_columns.json")


def load_cr_sparsity(path: pathlib.Path) -> float:
    return load_json(path / "results" / "classification_report_by_sparsity.json")


if __name__ == "__main__":
    main()
