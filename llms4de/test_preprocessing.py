import logging
import pathlib

import pandas as pd
import pytest

from llms4de.preprocessing import shuffle_instances, shuffle_columns, filter_table_size, \
    distribute_budget_across_instances, sample_rows, sample_examples, shuffle_rows

logger = logging.getLogger(__name__)


def test_shuffle_instances() -> None:
    # note that shuffling instances should be deterministic
    assert shuffle_instances(["a", "b", "c"]) == ["a", "b", "c"]
    assert shuffle_instances(["a", "b", "c"]) == ["a", "b", "c"]
    assert shuffle_instances(["a", "b", "c"]) == ["b", "c", "a"]

    assert shuffle_instances(["a", "b", "c"], [1, 2, 3]) == (["b", "c", "a"], [2, 3, 1])

    assert shuffle_instances([]) == []

    with pytest.raises(AssertionError):
        shuffle_instances(["a", "b", "c"], [1, 2])


def test_shuffle_rows() -> None:
    # note that shuffling rows should be deterministic
    a = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    b = pd.DataFrame({"a": [2, 1, 3], "b": [5, 4, 6]})
    assert shuffle_rows(a).equals(b)
    assert a.equals(pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}))
    assert shuffle_rows(pd.DataFrame({})).equals(pd.DataFrame({}))

    a_1 = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    a_2 = pd.DataFrame({"A": [10, 20, 30], "B": [40, 50, 60]})
    b_1 = pd.DataFrame({"a": [3, 2, 1], "b": [6, 5, 4]})
    b_2 = pd.DataFrame({"A": [30, 20, 10], "B": [60, 50, 40]})
    s_1, s_2 = shuffle_rows(a_1, a_2)
    assert s_1.equals(b_1)
    assert s_2.equals(b_2)
    assert a_1.equals(pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}))
    assert a_2.equals(pd.DataFrame({"A": [10, 20, 30], "B": [40, 50, 60]}))

    a_1 = pd.DataFrame({})
    a_2 = pd.DataFrame({})
    b_1 = pd.DataFrame({})
    b_2 = pd.DataFrame({})
    s_1, s_2 = shuffle_rows(a_1, a_2)
    assert s_1.equals(b_1)
    assert s_2.equals(b_2)

    with pytest.raises(AssertionError):
        shuffle_rows(pd.DataFrame({"a": [1]}), pd.DataFrame({"b": [1, 2]}))


def test_shuffle_columns() -> None:
    # note that shuffling columns should be deterministic
    a = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
    b = pd.DataFrame({"c": [5, 6], "b": [3, 4], "a": [1, 2]})
    assert shuffle_columns(a).equals(b)
    assert a.equals(pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]}))
    assert shuffle_columns(pd.DataFrame({})).equals(pd.DataFrame({}))

    shuffle_columns(a)  # this shuffle leaves the table unchanged...
    shuffle_columns(a)  # this shuffle leaves the table unchanged...

    a_1 = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
    a_2 = pd.DataFrame({"A": [10, 20], "B": [30, 40], "C": [50, 60]})
    b_1 = pd.DataFrame({"a": [1, 2], "c": [5, 6], "b": [3, 4]})
    b_2 = pd.DataFrame({"A": [10, 20], "C": [50, 60], "B": [30, 40]})
    s_1, s_2 = shuffle_columns(a_1, a_2)
    print(s_1)
    assert s_1.equals(b_1)
    assert s_2.equals(b_2)
    assert a_1.equals(pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]}))
    assert a_2.equals(pd.DataFrame({"A": [10, 20], "B": [30, 40], "C": [50, 60]}))

    a_1 = pd.DataFrame({})
    a_2 = pd.DataFrame({})
    b_1 = pd.DataFrame({})
    b_2 = pd.DataFrame({})
    s_1, s_2 = shuffle_columns(a_1, a_2)
    assert s_1.equals(b_1)
    assert s_2.equals(b_2)

    with pytest.raises(AssertionError):
        shuffle_columns(pd.DataFrame({"a": [1]}), pd.DataFrame({"b": [2], "c": [3]}))


def test_distribute_budget_across_instances() -> None:
    # note that distributing budget should be deterministic
    assert distribute_budget_across_instances([], 0) == []
    assert distribute_budget_across_instances([2, 4, 3], 7) == [2, 3, 2]
    assert distribute_budget_across_instances([2, 4, 3], 7) == [2, 2, 3]

    with pytest.raises(AssertionError):
        distribute_budget_across_instances([0, 1, 0], 2)


def test_sample_examples() -> None:
    # note that the sampled paths should be deterministic
    assert sample_examples(
        pathlib.Path("a"),
        [pathlib.Path("a"), pathlib.Path("b"), pathlib.Path("c")],
        num_examples=1
    ) == [pathlib.Path("c")]

    assert sample_examples(
        pathlib.Path("a"),
        [pathlib.Path("a"), pathlib.Path("b"), pathlib.Path("c")],
        num_examples=1
    ) == [pathlib.Path("b")]

    assert sample_examples(
        pathlib.Path("a"),
        [pathlib.Path("a"), pathlib.Path("b"), pathlib.Path("c")],
        num_examples=2
    ) == [pathlib.Path("b"), pathlib.Path("c")]

    assert sample_examples(
        pathlib.Path("a"),
        [pathlib.Path("a")],
        num_examples=0
    ) == []

    # not enough instances
    with pytest.raises(ValueError):
        sample_examples(
            pathlib.Path("a"),
            [pathlib.Path("a"), pathlib.Path("b"), pathlib.Path("c")],
            num_examples=3
        )


def test_sample_rows() -> None:
    # note that the sampled rows should be deterministic
    table = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    other_table_a = pd.DataFrame({"a": ["a", "b", "c"], "b": ["d", "e", "f"]})

    assert sample_rows(table, num_rows=2, mode="random").equals(pd.DataFrame({"a": [2, 3], "b": [5, 6]}))

    t, a = sample_rows(table, other_table_a, num_rows=1, mode="random")
    assert t.equals(pd.DataFrame({"a": [3], "b": [6]}))
    assert a.equals(pd.DataFrame({"a": ["c"], "b": ["f"]}))

    assert sample_rows(table, num_rows=10, mode="random").equals(pd.DataFrame({"a": [2, 1, 3], "b": [5, 4, 6]}))

    t, a = sample_rows(table, other_table_a, num_rows=10, mode="random")
    assert t.equals(pd.DataFrame({"a": [3, 2, 1], "b": [6, 5, 4]}))
    assert a.equals(pd.DataFrame({"a": ["c", "b", "a"], "b": ["f", "e", "d"]}))

    table = pd.DataFrame({"a": [1, None, None], "b": [4, 5, None]})
    assert sample_rows(table, num_rows=10, mode="full").equals(pd.DataFrame({"a": [1, None, None], "b": [4, 5, None]}))

    t, a = sample_rows(table, other_table_a, num_rows=10, mode="full")
    assert t.equals(pd.DataFrame({"a": [1, None, None], "b": [4, 5, None]}))
    assert a.equals(pd.DataFrame({"a": ["a", "b", "c"], "b": ["d", "e", "f"]}))

    # invalid mode
    with pytest.raises(AssertionError):
        # noinspection PyTypeChecker
        sample_rows(table, num_rows=10, mode="asdf")


def test_filter_table_size() -> None:
    table = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})

    assert filter_table_size(table)
    assert filter_table_size(table, min_num_rows=2)
    assert not filter_table_size(table, min_num_rows=3)
    assert filter_table_size(table, max_num_rows=2)
    assert not filter_table_size(table, max_num_rows=1)
    assert filter_table_size(table, min_num_cols=2)
    assert not filter_table_size(table, min_num_cols=4)
    assert filter_table_size(table, max_num_cols=3)
    assert not filter_table_size(table, max_num_cols=2)
    assert filter_table_size(table, min_num_cells=3)
    assert not filter_table_size(table, min_num_cells=100)
    assert filter_table_size(table, max_num_cells=100)
    assert not filter_table_size(table, max_num_cells=3)
