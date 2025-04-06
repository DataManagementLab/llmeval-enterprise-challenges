import collections
import logging

import cattrs
import hydra
from omegaconf import DictConfig

from llms4de.data import get_instances_dir, get_results_dir, load_json, dump_json, \
    get_predictions_dir, dump_cfg
from llms4de.evaluation.metrics import ConfusionMatrix, ConfusionMatrixBy

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="../../config/entity_matching", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    predictions_dir = get_predictions_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    results_dir = get_results_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    errors = collections.Counter()
    confusion = ConfusionMatrix.empty()
    if cfg.dataset.dataset_name == "pay_to_inv":
        confusion_by_match = ConfusionMatrixBy.empty(("match_category", "clean_or_dirty"))
        confusion_by_perturbation = ConfusionMatrixBy.empty(("perturbation_category",))

    for instance_dir in list(sorted(instances_dir.glob("*/"))):
        prediction_dir = predictions_dir / instance_dir.name
        ground_truth = load_json(instance_dir / "ground_truth.json")
        prediction = load_json(prediction_dir / "prediction.json")
        error = load_json(prediction_dir / "error.json")

        if error is not None:
            logger.warning("evaluation on failed prediction, interpret as incorrect")
            prediction = {"rows_match": not ground_truth["rows_match"]}
            errors[error] += 1

        confusion.push(prediction=prediction["rows_match"], ground_truth=ground_truth["rows_match"])

        if cfg.dataset.dataset_name == "pay_to_inv":
            confusion_by_match.push(
                {
                    "match_category": ground_truth["match_category"],
                    "clean_or_dirty": "clean" if ground_truth["perturbation_categories"] == [] else "dirty"
                },
                prediction["rows_match"],
                ground_truth["rows_match"]
            )
            if ground_truth["perturbation_categories"] == []:
                confusion_by_perturbation.push(
                    {
                        "perturbation_category": "clean"
                    },
                    prediction["rows_match"],
                    ground_truth["rows_match"]
                )
            else:
                for perturbation_category in ground_truth["perturbation_categories"]:
                    confusion_by_perturbation.push(
                        {
                            "perturbation_category": perturbation_category
                        },
                        prediction["rows_match"],
                        ground_truth["rows_match"]
                    )

    if errors.total() > 0:
        logger.warning(f"errors: {errors}")

    dump_json(dict(errors), results_dir / "errors.json")
    dump_json(cattrs.unstructure(confusion), results_dir / "confusion.json")

    if cfg.dataset.dataset_name == "pay_to_inv":
        confusion_by_match_category = {}
        for k, v in confusion_by_match.group_by_key("match_category").items():
            confusion_by_match_category[k] = cattrs.unstructure(v)
        dump_json(confusion_by_match_category, results_dir / "confusion_by_match_category.json")

        clean_confusion_by_match_category = {}
        for k, v in confusion_by_match.group_by_key(
                "match_category",
                filter_key_values={"clean_or_dirty": "clean"}
        ).items():
            clean_confusion_by_match_category[k] = cattrs.unstructure(v)
        dump_json(clean_confusion_by_match_category, results_dir / "clean_confusion_by_match_category.json")

        dirty_confusion_by_match_category = {}
        for k, v in confusion_by_match.group_by_key(
                "match_category",
                filter_key_values={"clean_or_dirty": "dirty"}
        ).items():
            dirty_confusion_by_match_category[k] = cattrs.unstructure(v)
        dump_json(dirty_confusion_by_match_category, results_dir / "dirty_confusion_by_match_category.json")

        confusion_by_perturb_category = {}
        for k, v in confusion_by_perturbation.group_by_key("perturbation_category").items():
            confusion_by_perturb_category[k] = cattrs.unstructure(v)
        dump_json(confusion_by_perturb_category, results_dir / "confusion_by_perturbation_category.json")

    dump_cfg(cfg, results_dir / "config.cfg")


if __name__ == "__main__":
    main()
