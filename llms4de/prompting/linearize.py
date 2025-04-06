import json
import logging
from typing import Literal, Any

import pandas as pd

from llms4de.prompting.template import fill_template

logger = logging.getLogger(__name__)


def linearize_table(
        table: pd.DataFrame,
        table_name: str | None,
        *,
        template: str,
        mode: Literal["csv"] | Literal["markdown"] | Literal["key_value"] | Literal["matrix"],
        csv_params: dict | None = None,
        markdown_params: dict | None = None,
        matrix_params: dict | None = None,
        key_value_params: dict | None = None
) -> str:
    """Linearize the given table.

    Args:
        table: The table to linearize.
        table_name: The name of the table.
        template: The linearization template, which can contain {{table_name}}, {{table}}, and {{newline}}.
        mode: The linearization mode.
        csv_params: The parameters for the pandas to_csv method.
        markdown_params: The parameters for the pandas to_markdown method.
        matrix_params: The parameters for the matrix linearization.
        key_value_params: The parameters for the key value linearization.

    Returns:
        The linearized table string.
    """
    match mode:
        case "csv":
            lin_table = table.to_csv(**csv_params)
        case "markdown":
            lin_table = table.to_markdown(**markdown_params)
        case "key_value":
            lin_table = linearize_table_as_key_value(table, **key_value_params)
        case "matrix":
            lin_table = linearize_table_as_matrix(table, **matrix_params)
        case _:
            raise AssertionError(f"unsupported table linearization mode `{mode}`")

    return fill_template(template, newline="\n", table_name=table_name, table=lin_table)


def linearize_table_as_matrix(
        table: pd.DataFrame,
        *,
        template: str,
        major: Literal["row"] | Literal["col"],
        header: bool | Literal["dummy"]
) -> str:
    """Linearize the given table as a matrix.

    Args:
        table: The table to linearize.
        template: The linearization template, which can contain {{matrix}}, {{major}}, and {{newline}}.
        major: Whether to linearize in row-major or col-major.
        header: Whether to include normal headers, dummy headers, or no headers.

    Returns:
        The table linearized as a matrix.
    """
    match major:
        case "row":
            if header == "dummy":
                headers = ",".join(f"col{ix}" for ix in range(len(table.columns))) + "\n"
            elif header:
                headers = ",".join(list(map(str, table.columns))) + "\n"
            else:
                headers = ""
            values = "\n".join(",".join(list(map(str, row.tolist()))) for _, row in table.iterrows())
            lin_matrix = headers + values
            lin_major = "row-major"
        case "col":
            lines = []
            for ix, column in enumerate(table.columns):
                line = ",".join(list(map(str, table[column])))
                if header == "dummy":
                    lines.append(f"col{ix}: {line}")
                elif header:
                    lines.append(f"{column}: {line}")
                else:
                    lines.append(line)
            lin_matrix = "\n".join(lines)
            lin_major = "column-major"
        case _:
            raise AssertionError(f"unsupported matrix major mode `{major}`")

    return fill_template(template, newline="\n", major=lin_major, matrix=lin_matrix)


def linearize_table_as_key_value(
        table: pd.DataFrame,
        *,
        replace_na: str | None
) -> str:
    """Linearize the given table as 'key: value' assignments.

    Args:
        table: The table to linearize.
        replace_na: Replacement value for na values, or None if na values should not be replaced.

    Returns:
        The table linearized as a matrix.
    """
    if replace_na is not None:
        mask = table.isna()
        table = table.where(~mask, replace_na)

    return "\n".join(
        ", ".join(f"{k}: {v}" for k, v in zip(table.columns, row)) for row in table.itertuples(index=False))


def linearize_list(
        l: list[Any],
        *,
        mode: Literal["json_list"],
) -> str:
    """Linearize the given list.

    Args:
        l: The list to linearize.
        mode: The linearization mode.

    Returns:
        The linearized list string.
    """
    match mode:
        case "json_list":
            return json.dumps(l)
        case _:
            raise AssertionError(f"unknown list serialization mode `{mode}`")
