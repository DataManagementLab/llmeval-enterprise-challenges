import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def table_accuracy_alternative_names(cfg, pred_table: pd.DataFrame, ground_truth_table: pd.DataFrame,
                                     primary_column: str) -> float:
    """Compute the accuracy of the predicted table with respect to the ground truth table.

    Columns are matched based on their names, and rows are matched based on the value in the primary column.

    Args:
        pred_table: The predicted table.
        ground_truth_table: The ground truth table.
        primary_column: The primary column by which to match between rows.

    Returns:
        The accuracy.

    Raises:
        AssertionError: If the primary column is missing in the predicted or ground truth table.
        AssertionError: If any value in the predicted or ground truth table is neither na, None, or of type str.
        AssertionError: If the column names in the ground truth table are not unique.
        AssertionError: If the values in the primary column of the ground truth table are not unique.
    """
    if primary_column not in pred_table.columns:
        raise AssertionError(f"primary column {primary_column} not in predicted table")

    if primary_column not in ground_truth_table.columns:
        raise AssertionError(f"primary column {primary_column} not in ground truth table")

    assert len(set(ground_truth_table.columns)) == len(ground_truth_table.columns)
    assert ground_truth_table[primary_column].is_unique
    assert pred_table.map(lambda x: pd.isna(x) or isinstance(x, str) or x is None).all().all()
    assert ground_truth_table.map(lambda x: pd.isna(x) or isinstance(x, str) or x is None).all().all()

    pred_table = pred_table.copy()
    ground_truth_table = ground_truth_table.copy()
    pred_table.reset_index(drop=True, inplace=True)
    ground_truth_table.reset_index(drop=True, inplace=True)

    correct_df = pd.DataFrame(index=pred_table.index, columns=list(set(pred_table.columns)), data=True)

    error_statistics = {"duplicate row": 0, "row not in GT": 0, "row from GT not in pred": 0, "incorrect cell": 0}

    # evaluate column presence
    gt_checks = {column: False for column in ground_truth_table.columns}
    for column in pred_table.columns:
        if column in gt_checks.keys():
            if gt_checks[column]:
                correct_df[column] = False  # predicted second column with that name ==> incorrect
            else:
                # correct_df[column] stays True
                gt_checks[column] = True  # predicted column in ground truth ==> correct
        else:
            correct_df[column] = False  # predicted column not in ground truth ==> incorrect

    for gt_column, exists in gt_checks.items():
        if not exists:
            correct_df[gt_column] = False  # ground truth column not predicted ==> incorrect

    # evaluate row presence
    gt_checks = {
        row[primary_column]: {"true_row_ix": row_ix, "pred_row_ix": None}
        for row_ix, row in ground_truth_table.iterrows()
    }

    for pred_row_ix, row in pred_table.iterrows():
        cell_value = row[primary_column]
        if primary_column == "NAME1":
            if not row[primary_column] in gt_checks.keys():
                # find true value based on row[primary_column]
                for locale in cfg.dataset.customer_details.locales:
                    for company in locale.companies:
                        if company.previous_name == row[primary_column]:
                            cell_value = company.name
        if cell_value in gt_checks.keys():  # (matches based on strict equality)
            if gt_checks[cell_value]["pred_row_ix"] is not None:
                # delete the row
                correct_df.loc[pred_row_ix] = "del"  # predicted second matching row ==> incorrect (uses first match)
                error_statistics["duplicate row"] += 1
                # need to set all cell values in first found row also to false
                row_ix_first_occurance = gt_checks[cell_value]["pred_row_ix"]
                correct_df.loc[row_ix_first_occurance] = False
            else:
                # correct_df[pred_row_ix] stays True
                gt_checks[cell_value]["pred_row_ix"] = pred_row_ix  # predicted row in ground truth ==> correct
        else:
            correct_df.loc[pred_row_ix] = False  # predicted row not in ground truth ==> incorrect
            error_statistics["row not in GT"] += 1

    for gt_row_name, gt_row_indexes in gt_checks.items():
        if gt_row_indexes["pred_row_ix"] is None:
            new_row = pd.DataFrame(columns=correct_df.columns, index=[len(correct_df.index)], data=False)
            correct_df = pd.concat([correct_df, new_row])  # ground truth row not predicted
            error_statistics["row from GT not in pred"] += 1

    row_pred_to_gt_matches = {
        check["pred_row_ix"]: check["true_row_ix"] for check in gt_checks.values() if check["pred_row_ix"] is not None
    }

    # evaluate cell values
    for pred_row_ix, row in pred_table.iterrows():
        # loop through columns
        for col_name, pred_cell_value in row.items():
            if correct_df.at[pred_row_ix, col_name] == True:
                # need to find cell value in correct_df
                gt_row_idx = row_pred_to_gt_matches[pred_row_ix]
                gt_cell_value = ground_truth_table.at[gt_row_idx, col_name]

                if (pd.notna(gt_cell_value) or pd.notna(pred_cell_value)) and gt_cell_value != pred_cell_value:
                    correct_df.at[pred_row_ix, col_name] = False
                    error_statistics["incorrect cell"] += 1

    # count number of true values in correct dataframe
    num_correct_values = correct_df.apply(lambda x: x == True).values.sum()
    num_incorrect_values = correct_df.apply(lambda x: x == False).values.sum()
    num_none_values = correct_df.apply(lambda x: x == "del").values.sum()
    total_cells = ground_truth_table.size  # num_correct_values + num_incorrect_values

    logger.info(
        f"GT table has {len(ground_truth_table)} rows and {len(ground_truth_table.columns)} cols, in total {total_cells} cells")
    logger.info(
        f"Predicted table has {len(pred_table)} rows and {len(pred_table.columns)} cols, in total {pred_table.size} cells")
    logger.info(
        f"Correct check table has {len(correct_df)} rows and {len(correct_df.columns)} cols, in total {correct_df.size} cells")
    logger.info(error_statistics)
    logger.info(
        f"table accuracy: {num_correct_values} correct cells and {num_incorrect_values} incorrect cells {num_none_values} None values")

    if total_cells == 0 and num_incorrect_values == 0:
        return 1.0
    elif total_cells == 0 and num_incorrect_values != 0:
        return 0.0
    else:
        calc_string = f"MAX(1-({num_incorrect_values}/{total_cells}), 0)"
        logger.info(calc_string)
        error_statistics["result_calculation"] = calc_string
        return max(1 - (num_incorrect_values / total_cells), 0), error_statistics
