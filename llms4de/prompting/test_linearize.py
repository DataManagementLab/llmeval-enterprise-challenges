import logging

import pandas as pd
import pytest

from llms4de.prompting.linearize import linearize_table_as_matrix, linearize_list, linearize_table, \
    linearize_table_as_key_value

logger = logging.getLogger(__name__)


def test_linearize_table() -> None:
    table = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    table_name = "my_table"

    # CSV
    assert linearize_table(
        table,
        table_name,
        mode="csv",
        template="{{table}}",
        csv_params={"index": False, "header": True}
    ) == "a,b\n1,3\n2,4\n"

    assert linearize_table(
        table,
        table_name,
        mode="csv",
        template="{{table}}",
        csv_params={"index": False, "header": False}
    ) == "1,3\n2,4\n"

    assert linearize_table(
        table,
        table_name,
        mode="csv",
        template="{{table}}",
        csv_params={}
    ) == ",a,b\n0,1,3\n1,2,4\n"

    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        linearize_table(table, table_name, template="{{table}}", mode="csv", csv_params=None)

    # Markdown
    assert linearize_table(
        table,
        table_name,
        mode="markdown",
        template="{{table}}",
        markdown_params={"index": False}
    ) == "|   a |   b |\n|----:|----:|\n|   1 |   3 |\n|   2 |   4 |"

    assert linearize_table(
        table,
        table_name,
        mode="markdown",
        template="{{table}}",
        markdown_params={"index": True}
    ) == "|    |   a |   b |\n|---:|----:|----:|\n|  0 |   1 |   3 |\n|  1 |   2 |   4 |"

    assert linearize_table(
        table,
        table_name,
        mode="markdown",
        template="{{table}}",
        markdown_params={}
    ) == "|    |   a |   b |\n|---:|----:|----:|\n|  0 |   1 |   3 |\n|  1 |   2 |   4 |"

    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        linearize_table(table, table_name, template="{{table}}", mode="markdown", markdown_params=None)

    # matrix
    assert linearize_table(
        table,
        table_name,
        mode="matrix",
        template="{{table}}",
        matrix_params={"template": "{{matrix}}", "major": "row", "header": True}
    ) == "a,b\n1,3\n2,4"

    # key value
    assert linearize_table(
        table,
        table_name,
        mode="key_value",
        template="{{table}}",
        key_value_params={"replace_na": None}
    ) == "a: 1, b: 3\na: 2, b: 4"

    # invalid mode
    with pytest.raises(AssertionError):
        # noinspection PyTypeChecker
        linearize_table(table, table_name, template="{{table}}", mode="asdf")

    # test template
    assert linearize_table(table, table_name, template="{{table_name}}", mode="csv", csv_params={}) == "my_table"
    assert linearize_table(table, table_name, template="{{newline}}", mode="csv", csv_params={}) == "\n"


def test_linearize_table_as_matrix() -> None:
    table = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    assert linearize_table_as_matrix(table, template="{{matrix}}", major="row", header=True) == "a,b\n1,3\n2,4"
    assert linearize_table_as_matrix(table, template="{{matrix}}", major="row", header=False) == "1,3\n2,4"
    assert linearize_table_as_matrix(table, template="{{matrix}}", major="row", header="dummy") == "col0,col1\n1,3\n2,4"

    assert linearize_table_as_matrix(table, template="{{matrix}}", major="col", header=True) == "a: 1,2\nb: 3,4"
    assert linearize_table_as_matrix(table, template="{{matrix}}", major="col", header=False) == "1,2\n3,4"
    assert linearize_table_as_matrix(table, template="{{matrix}}", major="col",
                                     header="dummy") == "col0: 1,2\ncol1: 3,4"

    # invalid mode
    with pytest.raises(AssertionError):
        # noinspection PyTypeChecker
        linearize_table_as_matrix(table, template="{{matrix}}", major="asdf", header=True)

    # test template
    assert linearize_table_as_matrix(table, template="{{newline}}", major="col", header=True) == "\n"
    assert linearize_table_as_matrix(table, template="{{major}}", major="row", header=True) == "row-major"
    assert linearize_table_as_matrix(table, template="{{major}}", major="col", header=True) == "column-major"


def test_linearize_table_as_key_value() -> None:
    table = pd.DataFrame({"a": ["c", 2], "b": [3, None]})
    assert linearize_table_as_key_value(table, replace_na=None) == "a: c, b: 3.0\na: 2, b: nan"
    assert linearize_table_as_key_value(table, replace_na="null") == "a: c, b: 3.0\na: 2, b: null"


def test_linearize_list() -> None:
    l = ["a", 1, "b"]

    # JSON list
    assert linearize_list(l, mode="json_list") == "[\"a\", 1, \"b\"]"

    # invalid mode
    with pytest.raises(AssertionError):
        # noinspection PyTypeChecker
        linearize_list(l, mode="asdf")
