import collections
import logging
import statistics

import attrs
import cattrs
import hydra
import numpy as np
import pandas as pd
from hydra.core.config_store import ConfigStore

from llms4de.data import load_json, get_task_dir, get_experiments_path
from llms4de.evaluation.metrics import ConfusionMatrix

logger = logging.getLogger(__name__)


@attrs.define
class Config:
    pass


ConfigStore.instance().store(name="config", node=Config)


@hydra.main(version_base=None, config_name="config")
def main(cfg: Config) -> None:
    # load all results
    task_dir = get_task_dir("schema_prediction")
    all_exp_paths = list(
        sorted(filter(lambda p: "enterprise-knowledge-schema-prediction" in p.name, task_dir.glob("*/experiments/*/"))))
    all_res = pd.DataFrame({"path": all_exp_paths})
    all_res["cfg"] = all_res["path"].apply(lambda p: load_json(p / "results" / "config.cfg"))
    all_res["model"] = all_res["cfg"].apply(lambda cfg: cfg["model"])
    all_res["errors"] = all_res["path"].apply(lambda p: load_json(p / "results" / "errors.json"))
    all_res["confusion_all"] = all_res["path"].apply(
        lambda p: cattrs.structure(load_json(p / "results" / "set_confusion_all.json"), ConfusionMatrix)
    )

    all_res["confusion_all_columns"] = all_res["path"].apply(
        lambda p: {
            k: cattrs.structure(v, ConfusionMatrix) for k, v in
            load_json(p / "results" / "set_confusion_by_column_name.json").items()
        }
    )

    all_res["f1_score_by_count_sap"] = all_res["confusion_all_columns"].apply(
        lambda c: make_f1_score_by_count(c, False))
    all_res["f1_score_by_count_zzz"] = all_res["confusion_all_columns"].apply(
        lambda c: make_f1_score_by_count(c, True))

    table_sap = all_res.copy()[["model", "f1_score_by_count_sap"]]
    for count in list(sorted(table_sap.iloc[0]["f1_score_by_count_sap"].keys())):
        table_sap[count] = table_sap["f1_score_by_count_sap"].apply(lambda f1c: f1c.get(count, np.nan))
    table_sap.to_csv(get_experiments_path() / "enterprise_knowledge_schema_prediction" / "f1_score_by_count_sap.csv")

    table_zzz = all_res.copy()[["model", "f1_score_by_count_zzz"]]
    for count in list(sorted(table_zzz.iloc[0]["f1_score_by_count_zzz"].keys())):
        table_zzz[count] = table_zzz["f1_score_by_count_zzz"].apply(lambda f1c: f1c.get(count, np.nan))
    table_zzz.to_csv(get_experiments_path() / "enterprise_knowledge_schema_prediction" / "f1_score_by_count_zzz.csv")


def make_f1_score_by_count(confusion_by_name: dict[str, ConfusionMatrix], zzz: bool) -> dict[int, tuple[float, int]]:
    f1_scores_by_count = collections.defaultdict(list)
    for column_name, confusion in confusion_by_name.items():
        if zzz == column_name.upper().startswith("Z"):
            f1_scores_by_count[discretize_count(confusion.FN + confusion.TP)].append(confusion.f1_score)

    f1_score_by_count = {}
    for count, f1_scores in f1_scores_by_count.items():
        f1_score_by_count[count] = (statistics.mean(f1_scores), len(f1_scores))

    return f1_score_by_count


def discretize_count(count: int) -> int:
    return count


if __name__ == "__main__":
    main()
