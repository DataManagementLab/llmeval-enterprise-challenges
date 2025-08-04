import logging
import pathlib
import random
from typing import Any, Union, Literal

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

shuffle_instances_random = random.Random(803270735)


def shuffle_instances(
        instances: list[Any],
        *other_instances: list[Any]
) -> list[Any] | tuple[list[Any], ...]:
    """Shuffles instances inplace and returns the shuffled instances.

    Args:
        instances: The list of instances.
        other_instances: Other lists of instances to shuffle in unison.

    Returns:
        The shuffled list of instances.
    """
    if not other_instances:
        shuffle_instances_random.shuffle(instances)
        return instances
    else:
        all_instances = [instances, *other_instances]
        for instance in all_instances:
            assert len(instance) == len(instances), "all instances must have the same length"
        indices = list(range(len(instances)))
        shuffle_instances_random.shuffle(indices)
        return tuple([instance[i] for i in indices] for instance in all_instances)


shuffle_rows_random = np.random.default_rng(seed=149840118)


def shuffle_rows(
        table: pd.DataFrame,
        *other_tables: pd.DataFrame
) -> pd.DataFrame | tuple[pd.DataFrame, ...]:
    """Shuffle the rows of the given table. Resets the index.

    Args:
        table: The table to shuffle.
        *other_tables: Other tables to shuffle in unison.

    Returns:
        The shuffled table or tuple of tables.
    """
    if not other_tables:
        return table.sample(frac=1, axis=0, random_state=shuffle_rows_random, ignore_index=True)
    else:
        for other_table in other_tables:
            if len(other_table.index) != len(table.index):
                raise AssertionError("all tables must have the same number of rows")

        if len(table.index) == 0:
            return (table.copy(),) + tuple(df.copy() for df in other_tables)

        ids = shuffle_rows_random.permutation(len(table.index))
        l = [df.copy().iloc[ids] for df in (table,) + other_tables]
        for df in l:
            df.reset_index(drop=True, inplace=True)
        return tuple(l)


shuffle_columns_random = np.random.RandomState(48324329)


def shuffle_columns(
        table: pd.DataFrame,
        *other_tables: pd.DataFrame
) -> pd.DataFrame | tuple[pd.DataFrame, ...]:
    """Shuffle the columns of the given table.

    Args:
        table: The table to shuffle.
        *other_tables: Other tables to shuffle in unison.

    Returns:
        The shuffled table or tuple of tables.
    """
    if not other_tables:
        return table.sample(frac=1, axis=1, random_state=shuffle_columns_random)
    else:
        for other_table in other_tables:
            if len(other_table.columns) != len(table.columns):
                raise AssertionError("all tables must have the same number of columns")

        if len(table.columns) == 0:
            return (table.copy(),) + tuple(df.copy() for df in other_tables)

        all_columns = [df.columns for df in (table,) + other_tables]
        transposed = [list(row) for row in zip(*all_columns)]
        transposed = shuffle_columns_random.permutation(transposed)
        all_columns = [list(row) for row in zip(*transposed)]
        l = [df.copy()[columns] for df, columns in zip((table,) + other_tables, all_columns)]
        return tuple(l)


sample_examples_random = random.Random(613907351)


def sample_examples(
        instance_path: pathlib.Path,
        instance_paths: list[pathlib.Path],
        *,
        num_examples: int
) -> list[pathlib.Path]:
    """Sample instances paths from all other instance paths.

    Raises if there are not enough instances.

    Args:
        instance_path: The path of the current instance.
        instance_paths: All instance paths.
        num_examples: The number of examples.

    Returns:
        A list of instance paths.
    """
    instance_paths = instance_paths.copy()
    instance_paths.remove(instance_path)
    return sample_examples_random.sample(instance_paths, k=num_examples)


sample_rows_random = np.random.default_rng(seed=964183484)


def sample_rows(
        table: pd.DataFrame,
        *other_tables: pd.DataFrame,
        num_rows: int,
        mode: Literal["random"] | Literal["full"] | Literal["full_columns"]
) -> Union[pd.DataFrame, tuple[pd.DataFrame, ...]]:
    """Sample rows from a pd.DataFrame.

    Does NOT raise if there are not enough rows.

    Args:
        table: The table to sample from.
        num_rows: The number of rows to sample.
        mode: Whether to sample *random* rows or prefer *full* rows.

    Returns:
        A pd.DataFrame with the sampled rows.
    """
    num_rows = min(num_rows, len(table.index))
    match mode:
        case "random":
            if not other_tables:
                return table.sample(n=num_rows, axis=0, random_state=sample_rows_random, ignore_index=True)
            else:
                ids = sample_rows_random.choice(len(table.index), num_rows, replace=False)
                l = [df.copy().iloc[ids] for df in (table,) + other_tables]
                for df in l:
                    df.reset_index(drop=True, inplace=True)
                return tuple(l)
        case "full":
            ids = list(range(len(table.index)))
            sparsities = [row.isna().sum() / len(row.index) for _, row in table.iterrows()]
            sample_rows_random.shuffle(ids)
            ids.sort(key=lambda ix: sparsities[ix])
            ids = ids[:num_rows]
            if not other_tables:
                df = table.copy().iloc[ids]
                df.reset_index(drop=True, inplace=True)
                return df
            else:
                l = [df.copy().iloc[ids] for df in (table,) + other_tables]
                for df in l:
                    df.reset_index(drop=True, inplace=True)
                return tuple(l)
        case "full_columns":
            assert not other_tables, "cannot use sampling mode `full_columns` if there are other_tables"
            data = {}
            for column in table.columns:
                col_data = table[column].dropna().to_list()
                sample_rows_random.shuffle(col_data)
                col_data = col_data[:num_rows]
                if len(col_data) < num_rows:
                    logger.warning(
                        f"there are fewer than num_rows={num_rows} non-NaN values in column `{column}`, fill with NaN")
                    col_data = col_data + [None] * (num_rows - len(col_data))
                data[column] = col_data
            return pd.DataFrame(data)
        case _:
            raise AssertionError(f"invalid sample_rows mode `{mode}`")


def filter_table_size(
        df: pd.DataFrame,
        *,
        min_num_rows: int | None = None,
        max_num_rows: int | None = None,
        min_num_cols: int | None = None,
        max_num_cols: int | None = None,
        min_num_cells: int | None = None,
        max_num_cells: int | None = None
) -> bool:
    """Returns True if the given table fits the size requirements.

    Args:
        df: The given table.
        min_num_rows: The minimum number of rows.
        max_num_rows: The maximum number of rows.
        min_num_cols: The minimum number of columns.
        max_num_cols: The maximum number of columns.
        min_num_cells: The minimum number of cells.
        max_num_cells: The maximum number of cells.

    Returns:
        Whether the table fits the size requirements.
    """
    if min_num_rows is not None and len(df.index) < min_num_rows:
        return False
    if max_num_rows is not None and len(df.index) > max_num_rows:
        return False
    if min_num_cols is not None and len(df.columns) < min_num_cols:
        return False
    if max_num_cols is not None and len(df.columns) > max_num_cols:
        return False
    if min_num_cells is not None and len(df.index) * len(df.columns) < min_num_cells:
        return False
    if max_num_cells is not None and len(df.index) * len(df.columns) > max_num_cells:
        return False
    return True


distribute_budget_across_instances_random = random.Random(165098809)


def distribute_budget_across_instances(
        budget_per_instance: list[int],
        total_budget: int
) -> list[int]:
    """Randomly distribute the total budget across all instances while not exceeding their individual budgets.

    Raises if the individual instance budgets are not enough to fulfill the total budget.

    Args:
        budget_per_instance: The list of individual instance budgets.
        total_budget: The total budget to distribute

    Returns:
        The list of assigned instance budgets.
    """
    if total_budget > sum(budget_per_instance):
        raise AssertionError(f"The individual instance budgets are not enough to fulfill the total budget.")

    budget_per_instance = budget_per_instance.copy()
    assigned_budget_per_instance = [0 for _ in budget_per_instance]
    while total_budget > 0:
        instances_with_budget = [idx for idx, budget in enumerate(budget_per_instance) if budget > 0]
        instance = distribute_budget_across_instances_random.choice(instances_with_budget)
        total_budget -= 1
        budget_per_instance[instance] -= 1
        assigned_budget_per_instance[instance] += 1

    return assigned_budget_per_instance
