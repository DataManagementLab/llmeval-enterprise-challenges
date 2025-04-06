import logging

import pytest

from llms4de.prompting.template import fill_template, fill_chat_template, merge_messages_with_same_role

logger = logging.getLogger(__name__)

templates_variables_strings = [
    ("{{a}}", {"a": "val"}, "val"),
    ("{{a}} {{b}}", {"a": "val", "b": "ue"}, "val ue"),
    ("{{a}}", {"a": "{{b}}", "b": "c"}, "{{b}}"),  # value contains variable, which is not replaced
    ("{{a}}", {"a": "{{b}}"}, "{{b}}"),  # value contains missing variable, which is not considered
    ("{{a}}", {"a": "val", "unused": "u"}, "val"),  # does not raise in case of unneeded values
    ("{a}", {"a": "val"}, "{a}"),
    ("{{a", {"a": "val"}, "{{a")
]


@pytest.mark.parametrize("template,variables,s", templates_variables_strings)
def test_fill_template(template: str, variables: dict, s: str) -> None:
    assert fill_template(template, **variables) == s


def test_fill_template_raises() -> None:
    with pytest.raises(AssertionError):
        fill_template("{{a}}")  # missing value


def test_fill_chat_template() -> None:
    # fill string variable with string
    assert fill_chat_template([{"role": "a", "content": "{{b}}"}], b="b") == [{"role": "a", "content": "b"}]

    # fill message variable with message
    assert fill_chat_template(["{{a}}", {"role": "c", "content": "d"}], a={"role": "a", "content": "b"}) == \
           [{"role": "a", "content": "b"}, {"role": "c", "content": "d"}]

    # fill message variable with list of messages
    assert fill_chat_template(
        ["{{a}}", {"role": "e", "content": "f"}],
        a=[{"role": "a", "content": "b"}, {"role": "c", "content": "d"}]
    ) == [{"role": "a", "content": "b"}, {"role": "c", "content": "d"}, {"role": "e", "content": "f"}]

    # fill message variable with message, then fill string variable with string
    assert fill_chat_template(["{{a}}"], a={"role": "a", "content": "{{b}}"}, b="b") == \
           [{"role": "a", "content": "b"}]

    # fill message variable with list of messages, then fill message variable with message
    assert fill_chat_template(
        ["{{a}}"],
        a=[{"role": "a", "content": "b"}, "{{b}}"],
        b={"role": "c", "content": "d"}
    ) == [{"role": "a", "content": "b"}, {"role": "c", "content": "d"}]

    with pytest.raises(AssertionError):
        fill_chat_template(["{{a}}"])  # missing message variable

    with pytest.raises(AssertionError):
        fill_chat_template([{"role": "a", "content": "{{b}}"}])  # missing string variable

    with pytest.raises(AssertionError):
        # missing string variable in message value
        fill_chat_template(["{{a}}"], a={"role": "a", "content": "{{b}}"})


def test_merge_messages_with_same_role() -> None:
    assert merge_messages_with_same_role(
        [{"role": "user", "content": "abc"}, {"role": "user", "content": "def"}],
        separator=""
    ) == [{"role": "user", "content": "abcdef"}]

    assert merge_messages_with_same_role(
        [{"role": "user", "content": "a"}, {"role": "user", "content": "b"}, {"role": "user", "content": "c"}],
        separator="-"
    ) == [{"role": "user", "content": "a-b-c"}]
