import collections
import logging
from typing import Any

import cattrs
import hydra
import tqdm
from omegaconf import DictConfig
from sklearn.metrics import classification_report

from llms4de.data import get_instances_dir, get_results_dir, load_json, dump_json, \
    get_predictions_dir, dump_cfg, load_str
from llms4de.evaluation.metrics import ConfusionMatrixBy

logger = logging.getLogger(__name__)


def pad_sequences(
        a: list[list[str]],
        b: list[list[str]],
) -> tuple[list[list[str]], list[list[str]]]:
    """Pad the shorter lists by appending "MISSING"."""
    assert len(set(map(len, a))) == 1
    assert len(set(map(len, b))) == 1

    if len(a[0]) < len(b[0]):
        diff = len(b[0]) - len(a[0])
        for ix in range(len(a)):
            a[ix] = a[ix] + ["MISSING"] * diff
    else:
        diff = len(a[0]) - len(b[0])
        for ix in range(len(b)):
            b[ix] = b[ix] + ["MISSING"] * diff

    return a, b


def make_classification_report(
        flat_true_values: list[str],
        flat_pred_values: list[str],
        labels: list[str]
) -> dict:
    return classification_report(
        [str(v) for v in flat_true_values],
        [str(v) for v in flat_pred_values],
        output_dict=True,
        zero_division=0.0,
        labels=labels
    )


def make_classification_report_by(
        flat_true_values_by: dict[Any, list[str]],
        flat_pred_values_by: dict[Any, list[str]],
        labels
) -> dict[Any, dict]:
    classification_reports_by = {}
    for by in flat_true_values_by.keys():
        classification_reports_by[by] = make_classification_report(
            flat_true_values_by[by],
            flat_pred_values_by[by],
            labels
        )
    return classification_reports_by


@hydra.main(version_base=None, config_path="../../config/schema_prediction", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    predictions_dir = get_predictions_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    results_dir = get_results_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)
    all_column_names = load_json(instances_dir / "all_column_names.json")

    errors = collections.Counter()

    # confusion matrix that measures only if the column name is included in the model prediction regardless of position
    # we measure this for each column_name individually so that we can later group by column names
    set_confusion = ConfusionMatrixBy.empty(("column_name",))

    all_true_column_types = []  # [['type-a', 'type-b', 'type-c'], ['type-x', 'type-z'], ...]
    all_pred_column_types = []  # [['type-a', 'type-b', 'type-c'], ['type-x', 'type-z'], ...]
    all_indices = []  # [[0, 1, 2], [0, 1]]
    instance_dirs = list(sorted(instances_dir.glob("*/")))
    for instance_dir in instance_dirs:
        prediction_dir = predictions_dir / instance_dir.name

        pred_column_types = load_json(prediction_dir / "table_header.json")
        if pred_column_types is None:
            logger.warning("evaluation on failed prediction, interpret as empty list of column types")
            pred_column_types = []

        all_pred_column_types.append(pred_column_types)
        table_name = load_str(instance_dir / "table_name.txt")
        true_column_types = load_json(instance_dir / "table_header.json")
        all_true_column_types.append(true_column_types)
        all_indices.append(list(range(len(true_column_types))))

        errors[load_json(prediction_dir / "error.json")] += 1

        set_true_column_names = set(true_column_types)
        set_pred_column_names = set(pred_column_types)
        for column_name in all_column_names:
            set_confusion.push(
                key_values={"column_name": f"Z{column_name}" if table_name.upper().startswith("Z") else column_name},
                prediction=column_name in set_pred_column_names,
                ground_truth=column_name in set_true_column_names
            )

    # save set confusion across all column names
    dump_json(cattrs.unstructure(set_confusion.all), results_dir / "set_confusion_all.json")
    dump_json(set_confusion.all.f1_score, results_dir / "set_f1_score_all.json")

    # save set confusion for each column name
    set_conf_by_col_name = set_confusion.group_by_key("column_name")
    # sort column names by f1 score
    set_conf_by_col_name = dict(sorted(set_conf_by_col_name.items(), key=lambda item: item[1].f1_score, reverse=True))
    dump_json(
        {k: cattrs.unstructure(v) for k, v in set_conf_by_col_name.items()},
        results_dir / "set_confusion_by_column_name.json"
    )
    dump_json(
        {k: v.f1_score for k, v in set_conf_by_col_name.items()},
        results_dir / "set_f1_score_by_column_name.json"
    )

    assert len(all_true_column_types) == len(all_pred_column_types)
    assert len(all_true_column_types) == len(all_indices)
    assert all(len(a) == len(b) for a, b in zip(all_true_column_types, all_indices))

    annotated_columns = collections.Counter()
    for inst_true_column_types in all_true_column_types:
        for column_type in inst_true_column_types:
            annotated_columns[column_type is not None] += 1

    dump_json(dict(annotated_columns), results_dir / "num_annotated_columns.json")
    dump_json(dict(errors), results_dir / "errors.json")

    num_columns_deviations = []
    num_instances_with_column_at_idx = collections.Counter()
    flat_padded_true_values, flat_padded_pred_values = [], []
    flat_padded_true_values_by_idx = collections.defaultdict(list)
    flat_padded_pred_values_by_idx = collections.defaultdict(list)
    for inst_true_values, inst_pred_values, inst_indices in tqdm.tqdm(
            zip(all_true_column_types, all_pred_column_types,
                all_indices),
            desc=f"{cfg.task_name} - {cfg.dataset.dataset_name} - {cfg.exp_name} - evaluate",
            total=len(all_true_column_types)
    ):
        num_columns_deviations.append(len(inst_pred_values) - len(inst_true_values))

        (inst_padded_true_values,
         inst_padded_indices), (
            inst_padded_pred_values,) = pad_sequences(
            [inst_true_values, inst_indices],
            [inst_pred_values]
        )
        for padded_true_value, padded_pred_value, padded_index \
                in zip(inst_padded_true_values, inst_padded_pred_values, inst_padded_indices):
            if padded_true_value is not None:  # ignore all columns for which the true value is None
                flat_padded_true_values.append(padded_true_value)
                flat_padded_pred_values.append(padded_pred_value)

                if padded_true_value != "MISSING":
                    num_instances_with_column_at_idx[padded_index] += 1
                    flat_padded_true_values_by_idx[padded_index].append(padded_true_value)
                    flat_padded_pred_values_by_idx[padded_index].append(padded_pred_value)

    dump_json(dict(sorted(collections.Counter(num_columns_deviations).items())),
              results_dir / "num_columns_deviations.json")
    dump_json(dict(sorted(num_instances_with_column_at_idx.items())),
              results_dir / "num_instances_with_column_at_idx.json")

    classification_report = make_classification_report(
        flat_padded_true_values,
        flat_padded_pred_values, all_column_names
    )
    dump_json(classification_report, results_dir / "classification_report.json")

    classification_report_by_idx = make_classification_report_by(
        flat_padded_true_values_by_idx,
        flat_padded_pred_values_by_idx, all_column_names
    )
    dump_json(classification_report_by_idx, results_dir / "classification_report_by_idx.json")

    if errors.total() > 0:
        logger.warning(f"errors: {errors}")

    dump_cfg(cfg, results_dir / "config.cfg")


if __name__ == "__main__":
    main()
