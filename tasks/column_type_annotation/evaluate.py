import collections
import logging
from typing import Any

import hydra
import pandas as pd
import tqdm
from omegaconf import DictConfig
from sklearn.metrics import classification_report

from llms4de.data import get_instances_dir, get_results_dir, load_json, dump_json, \
    get_predictions_dir, dump_cfg
from llms4de.evaluation.inspection import compute_cell_level_sparsity

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


@hydra.main(version_base=None, config_path="../../config/column_type_annotation", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    predictions_dir = get_predictions_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    results_dir = get_results_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    all_column_types = load_json(instances_dir / "all_column_types.json")
    all_column_types_set = set(all_column_types)

    errors = collections.Counter()
    all_true_column_types = []  # [['type-a', 'type-b', 'type-c'], ['type-x', 'type-z'], ...]
    all_pred_column_types = []  # [['type-a', 'type-b', 'type-c'], ['type-x', 'type-z'], ...]
    all_data_types = []  # [['numerical', 'non-numerical', 'non-numerical'], ['numerical', 'non-numerical'], ...]
    all_sparsities = []  # [[0.4, 0.4, 0.4], [0.7, 0.7], ...]
    all_num_columns = []  # [[3, 3, 3], [2, 2], ...]
    all_indices = []  # [[0, 1, 2], [0, 1]]
    all_column_names = []  # [['column-a', 'column-b', 'column-c'], ['column-x', 'column-z'], ...]

    instance_dirs = list(sorted(instances_dir.glob("*/")))
    for instance_dir in instance_dirs:
        prediction_dir = predictions_dir / instance_dir.name

        match cfg.task_mode:
            case "all" | "chunking":
                pred_column_types = load_json(prediction_dir / "column_types.json")
                if pred_column_types is None:
                    logger.warning("evaluation on failed prediction, interpret as empty list of column types")
                    pred_column_types = []
                all_pred_column_types.append(pred_column_types)
                true_column_types = load_json(instance_dir / "column_types.json")
                all_true_column_types.append(true_column_types)
                data_types = load_json(instance_dir / "data_types.json")
                all_data_types.append(data_types)
                df = pd.read_csv(instance_dir / "table.csv")
                sparsity = round(compute_cell_level_sparsity(df), cfg.bucketize_sparsity_decimal_points)
                all_sparsities.append([sparsity] * len(true_column_types))
                all_num_columns.append([len(true_column_types)] * len(true_column_types))
                all_indices.append(list(range(len(true_column_types))))
                column_names = df.columns.to_list()
                all_column_names.append(column_names)
            case "lookup-index" | "lookup-header":
                pred_column_type = load_json(prediction_dir / "column_type.json")
                if pred_column_type is None:
                    logger.warning("evaluation on failed prediction, interpret as empty list of column types")
                    all_pred_column_types.append([])
                else:
                    all_pred_column_types.append([pred_column_type])
                true_column_type = load_json(instance_dir / "column_type.json")
                all_true_column_types.append([true_column_type])
                data_type = load_json(instance_dir / "data_type.json")
                all_data_types.append([data_type])
                df = pd.read_csv(instance_dir / "table.csv")
                sparsity = round(compute_cell_level_sparsity(df), cfg.bucketize_sparsity_decimal_points)
                all_sparsities.append([sparsity])
                all_num_columns.append([len(df.columns)])
                index = load_json(instance_dir / "index.json")
                all_indices.append([index])
                column_name = df.columns.to_list()[index]
                all_column_names.append([column_name])
            case _:
                raise AssertionError(f"invalid task mode `{cfg.task_mode}`")

        errors[load_json(prediction_dir / "error.json")] += 1

    assert len(all_true_column_types) == len(all_pred_column_types)
    assert len(all_true_column_types) == len(all_data_types)
    assert len(all_true_column_types) == len(all_sparsities)
    assert len(all_true_column_types) == len(all_num_columns)
    assert len(all_true_column_types) == len(all_indices)
    assert len(all_true_column_types) == len(all_column_names)
    assert all(len(a) == len(b) for a, b in zip(all_true_column_types, all_data_types))
    assert all(len(a) == len(b) for a, b in zip(all_true_column_types, all_sparsities))
    assert all(len(a) == len(b) for a, b in zip(all_true_column_types, all_num_columns))
    assert all(len(a) == len(b) for a, b in zip(all_true_column_types, all_indices))
    assert all(len(a) == len(b) for a, b in zip(all_true_column_types, all_column_names))

    annotated_columns = collections.Counter()
    for inst_true_column_types in all_true_column_types:
        for column_type in inst_true_column_types:
            annotated_columns[column_type is not None] += 1

    dump_json(dict(annotated_columns), results_dir / "num_annotated_columns.json")
    dump_json(dict(errors), results_dir / "errors.json")

    num_columns_deviations = []
    not_even_a_column_type = []
    num_instances_with_column_at_idx = collections.Counter()
    flat_padded_true_values, flat_padded_pred_values = [], []
    flat_padded_true_values_by_idx = collections.defaultdict(list)
    flat_padded_pred_values_by_idx = collections.defaultdict(list)
    flat_padded_true_values_by_data_type = collections.defaultdict(list)
    flat_padded_pred_values_by_data_type = collections.defaultdict(list)
    flat_padded_true_values_by_sparsity = collections.defaultdict(list)
    flat_padded_pred_values_by_sparsity = collections.defaultdict(list)
    flat_padded_true_values_by_num_columns = collections.defaultdict(list)
    flat_padded_pred_values_by_num_columns = collections.defaultdict(list)
    for inst_true_values, inst_pred_values, inst_data_types, inst_sparsities, inst_num_columns, inst_indices, inst_column_names in tqdm.tqdm(
            zip(all_true_column_types, all_pred_column_types, all_data_types, all_sparsities, all_num_columns,
                all_indices, all_column_names),
            desc=f"{cfg.task_name} - {cfg.dataset.dataset_name} - {cfg.exp_name} - evaluate",
            total=len(all_true_column_types)
    ):
        num_columns_deviations.append(len(inst_pred_values) - len(inst_true_values))

        (inst_padded_true_values, inst_padded_data_types, inst_padded_sparsities, inst_padded_num_columns,
         inst_padded_indices, inst_padded_column_names), (
            inst_padded_pred_values,) = pad_sequences(
            [inst_true_values, inst_data_types, inst_sparsities, inst_num_columns, inst_indices, inst_column_names],
            [inst_pred_values]
        )
        for padded_true_value, padded_pred_value, padded_data_type, padded_sparsity, padded_num_column, padded_index, padded_column_name \
                in zip(inst_padded_true_values, inst_padded_pred_values, inst_padded_data_types, inst_padded_sparsities,
                       inst_padded_num_columns, inst_padded_indices, inst_padded_column_names):
            if not cfg.filter_zzz_columns or padded_column_name.upper().startswith("Z"):
                if padded_true_value is not None:  # ignore all columns for which the true value is None
                    flat_padded_true_values.append(padded_true_value)
                    flat_padded_pred_values.append(padded_pred_value)

                    if padded_pred_value not in all_column_types_set:
                        not_even_a_column_type.append(padded_pred_value)

                    if padded_true_value != "MISSING":
                        num_instances_with_column_at_idx[padded_index] += 1
                        flat_padded_true_values_by_idx[padded_index].append(padded_true_value)
                        flat_padded_pred_values_by_idx[padded_index].append(padded_pred_value)
                        flat_padded_true_values_by_data_type[padded_data_type].append(padded_true_value)
                        flat_padded_pred_values_by_data_type[padded_data_type].append(padded_pred_value)
                        flat_padded_true_values_by_sparsity[padded_sparsity].append(padded_true_value)
                        flat_padded_pred_values_by_sparsity[padded_sparsity].append(padded_pred_value)
                        flat_padded_true_values_by_num_columns[padded_num_column].append(padded_true_value)
                        flat_padded_pred_values_by_num_columns[padded_num_column].append(padded_pred_value)

    dump_json(dict(sorted(collections.Counter(num_columns_deviations).items())),
              results_dir / "num_columns_deviations.json")
    dump_json(dict(sorted(collections.Counter(not_even_a_column_type).items())),
              results_dir / "num_not_a_column_type.json")
    dump_json(dict(sorted(num_instances_with_column_at_idx.items())),
              results_dir / "num_instances_with_column_at_idx.json")

    classification_report = make_classification_report(
        flat_padded_true_values,
        flat_padded_pred_values,
        all_column_types
    )
    dump_json(classification_report, results_dir / "classification_report.json")

    classification_report_by_data_type = make_classification_report_by(
        flat_padded_true_values_by_data_type,
        flat_padded_pred_values_by_data_type,
        all_column_types
    )
    dump_json(classification_report_by_data_type, results_dir / "classification_report_by_data_type.json")

    classification_report_by_sparsity = make_classification_report_by(
        flat_padded_true_values_by_sparsity,
        flat_padded_pred_values_by_sparsity,
        all_column_types
    )
    dump_json(classification_report_by_sparsity, results_dir / "classification_report_by_sparsity.json")

    classification_report_by_num_columns = make_classification_report_by(
        flat_padded_true_values_by_num_columns,
        flat_padded_pred_values_by_num_columns,
        all_column_types
    )
    dump_json(classification_report_by_num_columns, results_dir / "classification_report_by_num_columns.json")

    classification_report_by_idx = make_classification_report_by(
        flat_padded_true_values_by_idx,
        flat_padded_pred_values_by_idx,
        all_column_types
    )
    dump_json(classification_report_by_idx, results_dir / "classification_report_by_idx.json")

    if errors.total() > 0:
        logger.warning(f"errors: {errors}")

    dump_cfg(cfg, results_dir / "config.cfg")


if __name__ == "__main__":
    main()
