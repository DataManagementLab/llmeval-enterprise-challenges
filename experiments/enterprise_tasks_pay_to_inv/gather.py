import logging

import attrs
import cattrs
import hydra
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
    all_exp_paths = list(
        sorted(get_task_dir("entity_matching").glob("pay_to_inv/experiments/enterprise-tasks-pay-to-inv*/")))
    all_res = pd.DataFrame({"path": all_exp_paths})
    all_res["cfg"] = all_res["path"].apply(lambda p: load_json(p / "results" / "config.cfg"))
    all_res["model"] = all_res["cfg"].apply(lambda cfg: cfg["model"])
    all_res["schema_mode"] = all_res["cfg"].apply(lambda cfg: cfg["dataset"]["schema_mode"])
    all_res["perturbation_mode"] = all_res["cfg"].apply(lambda cfg: cfg["dataset"]["perturbation_mode"])
    all_res["errors"] = all_res["path"].apply(lambda p: load_json(p / "results" / "errors.json"))
    all_res["confusion"] = all_res["path"].apply(
        lambda p: cattrs.structure(load_json(p / "results" / "confusion.json"), ConfusionMatrix)
    )
    all_res["confusion_by_match_category"] = all_res["path"].apply(
        lambda p: {
            k: cattrs.structure(v, ConfusionMatrix) for k, v in
            load_json(p / "results" / "confusion_by_match_category.json").items()
        }
    )
    all_res["clean_confusion_by_match_category"] = all_res["path"].apply(
        lambda p: {
            k: cattrs.structure(v, ConfusionMatrix) for k, v in
            load_json(p / "results" / "clean_confusion_by_match_category.json").items()
        }
    )
    all_res["dirty_confusion_by_match_category"] = all_res["path"].apply(
        lambda p: {
            k: cattrs.structure(v, ConfusionMatrix) for k, v in
            load_json(p / "results" / "dirty_confusion_by_match_category.json").items()
        }
    )
    all_res["confusion_by_perturbation_category"] = all_res["path"].apply(
        lambda p: {
            k: cattrs.structure(v, ConfusionMatrix) for k, v in
            load_json(p / "results" / "confusion_by_perturbation_category.json").items()
        }
    )

    ####################################################################################################################
    # F1 scores at increasing difficulties
    ####################################################################################################################

    table = pd.DataFrame(
        index=all_res["model"].unique().tolist(),
        columns=["initial data", "+ errors", "+ multi-matches", "+ multiple tables"]
    )
    for model in table.index:
        # initial data
        res = all_res.loc[
            (all_res["model"] == model)
            & (all_res["schema_mode"] == "opaque")
            & (all_res["perturbation_mode"] == "multi")
            ]
        assert len(res.index) == 1
        res = res.iloc[0]
        confusion = res["clean_confusion_by_match_category"]["one_pay_one_inv"]
        table.at[model, "initial data"] = [confusion.f1_score, confusion.bootstrap_f1_score_standard_error()]

        # + errors
        res = all_res.loc[
            (all_res["model"] == model)
            & (all_res["schema_mode"] == "opaque")
            & (all_res["perturbation_mode"] == "multi")
            ]
        assert len(res.index) == 1
        res = res.iloc[0]
        confusion = res["dirty_confusion_by_match_category"]["one_pay_one_inv"]
        table.at[model, "+ errors"] = [confusion.f1_score, confusion.bootstrap_f1_score_standard_error()]

        # + multi-matches
        res = all_res.loc[
            (all_res["model"] == model)
            & (all_res["schema_mode"] == "opaque")
            & (all_res["perturbation_mode"] == "multi")
            ]
        assert len(res.index) == 1
        res = res.iloc[0]
        confusion = res["dirty_confusion_by_match_category"]["one_pay_multi_inv"]
        confusion = confusion + res["dirty_confusion_by_match_category"]["multi_pay_one_inv"]
        table.at[model, "+ multi-matches"] = [confusion.f1_score, confusion.bootstrap_f1_score_standard_error()]

        # + multiple tables
        res = all_res.loc[
            (all_res["model"] == model)
            & (all_res["schema_mode"] == "multi-table")
            & (all_res["perturbation_mode"] == "multi")
            ]
        assert len(res.index) == 1
        res = res.iloc[0]
        confusion = res["dirty_confusion_by_match_category"]["one_pay_multi_inv"]
        confusion = confusion + res["dirty_confusion_by_match_category"]["multi_pay_one_inv"]
        table.at[model, "+ multiple tables"] = [confusion.f1_score, confusion.bootstrap_f1_score_standard_error()]

    table.index.name = "model"
    table.to_csv(get_experiments_path() / "enterprise_tasks_pay_to_inv" / "tasks_pay_to_inv_increasing_difficulty.csv")

    ####################################################################################################################
    # precision and recall for +multi-matches scenario
    ####################################################################################################################

    res = all_res.loc[
        (all_res["schema_mode"] == "opaque")
        & (all_res["perturbation_mode"] == "multi")
        ]
    res = res.copy()

    res["f1_score"] = res["dirty_confusion_by_match_category"].apply(
        lambda d: (d["multi_pay_one_inv"] + d["one_pay_multi_inv"]).f1_score
    )
    res["precision"] = res["dirty_confusion_by_match_category"].apply(
        lambda d: (d["multi_pay_one_inv"] + d["one_pay_multi_inv"]).precision
    )
    res["recall"] = res["dirty_confusion_by_match_category"].apply(
        lambda d: (d["multi_pay_one_inv"] + d["one_pay_multi_inv"]).recall
    )

    res = res[["model", "f1_score", "precision", "recall"]]
    res.set_index("model", inplace=True)
    res.to_csv(get_experiments_path() / "enterprise_tasks_pay_to_inv" / "tasks_pay_to_inv_precision_recall.csv")

    ####################################################################################################################
    # F1 scores for typical error categories
    ####################################################################################################################

    res = all_res.loc[
        (all_res["schema_mode"] == "opaque")
        & (all_res["perturbation_mode"] == "single")
        ]
    res = res.copy()

    res["initial (clean)"] = res["confusion_by_perturbation_category"].apply(
        lambda d: d["clean"].f1_score
    )
    res["assignment number"] = res["confusion_by_perturbation_category"].apply(
        lambda d: d["perturbed_assignment_number"].f1_score
    )
    res["billing number"] = res["confusion_by_perturbation_category"].apply(
        lambda d: d["perturbed_billing_number"].f1_score
    )
    res["partner name"] = res["confusion_by_perturbation_category"].apply(
        lambda d: d["perturbed_business_partner"].f1_score
    )
    res["deduction ≤ $0.1"] = res["confusion_by_perturbation_category"].apply(
        lambda d: d["small_deduction"].f1_score
    )

    res = res[["model", "initial (clean)", "assignment number", "billing number", "partner name", "deduction ≤ $0.1"]]
    res.set_index("model", inplace=True)
    res.to_csv(get_experiments_path() / "enterprise_tasks_pay_to_inv" / "tasks_pay_to_inv_error_categories.csv")


if __name__ == "__main__":
    main()
