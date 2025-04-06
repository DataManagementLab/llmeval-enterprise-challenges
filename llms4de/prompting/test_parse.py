import logging

import pytest

from llms4de.prompting.parse import parse_list_from_csv, parse_list_from_json, parse_list

logger = logging.getLogger(__name__)


def test_parse_list() -> None:
    # CSV
    assert parse_list("a,b", mode="csv", csv_params={"sep": ",", "strip": True}) == ["a", "b"]
    with pytest.raises(TypeError):
        parse_list("a,b", mode="csv", csv_params=None)

    # JSON list
    assert parse_list("[\"a\", \"b\"]", mode="json_list", json_params={"strip": True, "strict": True}) == ["a", "b"]
    with pytest.raises(TypeError):
        parse_list("a,b", mode="json_list", json_params=None)

    # invalid mode
    with pytest.raises(AssertionError):
        # noinspection PyTypeChecker
        parse_list("a,b", mode="asdf")


csv_strings_lists_params = [
    ("a,b,c", ["a", "b", "c"], {"sep": ",", "strip": False}),
    ("a,b ,c", ["a", "b ", "c"], {"sep": ",", "strip": False}),
    ("a,b ,c", ["a", "b", "c"], {"sep": ",", "strip": True}),
    ("a,b,c\nd", ["a", "b", "c\nd"], {"sep": ",", "strip": True}),
]


@pytest.mark.parametrize("s,l,params", csv_strings_lists_params)
def test_parse_list_from_csv(s: str, l: list[str], params: dict) -> None:
    assert parse_list_from_csv(s, **params) == l


json_strings_lists_params = [
    ("[\"a\", \"b\", \"c\"]", ["a", "b", "c"], {"strip": False, "strict": True}),
    ("[\"a\", 1, \"c\"]", ["a", "1", "c"], {"strip": False, "strict": True}),  # parsing always converts to list of STR
    ("[\"a\", \"b\", \"c \"]", ["a", "b", "c "], {"strip": False, "strict": True}),  # without strip
    ("[\"a\", \"b\", \"c \"]", ["a", "b", "c"], {"strip": True, "strict": True}),  # with strip
    ("{}", None, {"strip": False, "strict": True}),  # JSON dict is not a list
    ("", None, {"strip": False, "strict": True}),  # unparsable
    ("", None, {"strip": False, "strict": False}),  # unparsable
    ("[\"a\", \"b\", \"c\"", None, {"strip": False, "strict": True}),  # not parsable if strict
    ("[\"a\", \"b\", \"c\"", ["a", "b", "c"], {"strip": False, "strict": False}),  # parsable if not strict
    ("[\"a\", \"b\", \"c", ["a", "b", "c"], {"strip": False, "strict": False}),  # parsable if not strict
    ("[\"a\", \"b\", \"c\",", ["a", "b", "c", ""], {"strip": False, "strict": False}),  # parsable if not strict
    ("asdf[\"a\", \"b\", \"c\"]", ["a", "b", "c"], {"strip": False, "strict": False}),  # parsable if not strict
    ("[\"a\", \"b\", \"c\"]asdf", ["a", "b", "c"], {"strip": False, "strict": False}),  # parsable if not strict
    ("asdf[\"a\", \"b\", \"c\"]asdf", ["a", "b", "c"], {"strip": False, "strict": False}),  # parsable if not strict
]


@pytest.mark.parametrize("s,l,params", json_strings_lists_params)
def test_parse_list_from_json(s: str, l: list[str], params: dict) -> None:
    assert parse_list_from_json(s, **params) == l
