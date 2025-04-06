import logging

import pandas as pd

from llms4de.evaluation.inspection import compute_cell_level_sparsity, find_row_in_table, find_column_in_table, \
    find_value_in_table

logger = logging.getLogger(__name__)


def test_compute_cell_level_sparsity() -> None:
    assert compute_cell_level_sparsity(pd.DataFrame({"a": [1, None], "b": [None, 2]})) == 0.5
    assert compute_cell_level_sparsity(pd.DataFrame({"a": [None, None], "b": [None, None]})) == 1.0
    assert compute_cell_level_sparsity(pd.DataFrame({"a": [1, 2], "b": [3, 4]})) == 0.0


def test_find_row_in_table() -> None:
    df = pd.DataFrame({"a": [1, "c"], "b": [2, 3]})
    assert find_row_in_table(df, ["1", "2"]) == [0]
    assert find_row_in_table(df, ["1", 2]) == [0]
    assert find_row_in_table(df, ["a", "2"]) == []


def test_find_column_in_table() -> None:
    df = pd.DataFrame({"a": [1, "c"], "b": [2, 3]})
    assert find_column_in_table(df, ["2", "3"]) == [1]
    assert find_column_in_table(df, ["2", 3]) == [1]
    assert find_row_in_table(df, ["f", "a"]) == []


def test_find_value_in_table() -> None:
    df = pd.DataFrame({"a": [1, "c"], "b": [2, 3]})
    assert find_value_in_table(df, "1") == [(0, 0)]
    # noinspection PyTypeChecker
    assert find_value_in_table(df, 1) == [(0, 0)]
    assert find_value_in_table(df, "asdf") == []
