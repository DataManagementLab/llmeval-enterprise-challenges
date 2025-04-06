import logging

import pandas as pd

logger = logging.getLogger(__name__)


def compute_cell_level_sparsity(table: pd.DataFrame) -> float:
    """Compute the sparsity of the given table as the fraction of cell values that are nan.

    Args:
        table: The given table.

    Returns:
        The table sparsity.
    """
    return table.isna().sum().sum() / (len(table.index) * len(table.columns))


def find_row_in_table(table: pd.DataFrame, row: list[str]) -> list[int]:
    """Return all indices of rows in the given table that are equal to the given row.

    Converts all values to strings.

    Args:
        table: The given table.
        row: The given row.

    Returns:
        The list of indices.
    """
    row = list(map(str, row))
    indices = []
    for ix, r in enumerate(table.itertuples(index=False)):
        if list(map(str, r)) == row:
            indices.append(ix)
    return indices


def find_column_in_table(table: pd.DataFrame, column: list[str]) -> list[int]:
    """Return all indices of columns in the given table that are equal to the given column.

    Converts all values to strings.

    Args:
        table: The given table.
        column: The given column.

    Returns:
        The list of indices.
    """
    column = list(map(str, column))
    indices = []
    for ix, col in enumerate(table.columns):
        if list(map(str, table[col].to_list())) == column:
            indices.append(ix)
    return indices


def find_value_in_table(table: pd.DataFrame, value: str) -> list[tuple[int, int]]:
    """Return (row, column) index pairs of all cells in the given table that are equal to the given value.

    Converts all values to strings.

    Args:
        table: The given table.
        value: The given value.

    Returns:
        The list of index pairs.
    """
    value = str(value)
    indices = []
    for row_ix in range(len(table.index)):
        for col_ix in range(len(table.columns)):
            if str(table.iat[row_ix, col_ix]) == value:
                indices.append((row_ix, col_ix))
    return indices
