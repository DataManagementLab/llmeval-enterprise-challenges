import logging

import pytest

from llms4de.plotting import colors
from llms4de.plotting.colors import color, gradient, value_to_color, hatch, sort_idx, marker

logger = logging.getLogger(__name__)


def test_color() -> None:
    assert color("gpt-4o-mini-2024-07-18") == colors.COLOR_7A
    assert color("gpt-4o-2024-05-13") == colors.COLOR_9A
    assert color("gpt-3.5-turbo-1106") == colors.COLOR_1A
    assert color("anthropic.claude-3-5-sonnet-20241022-v2:0") == colors.COLOR_3A
    assert color("meta.llama3-1-70b-instruct-v1:0") == colors.COLOR_1A
    assert color("llama3.1:70b-instruct-fp16") == colors.COLOR_1A
    assert color("o1-2024-12-17") == colors.COLOR_11A
    assert color("syntax") == colors.COLOR_8A
    assert color("content") == colors.COLOR_7A
    assert color("incorrect_result") == colors.COLOR_6A
    assert color("correct_result") == colors.COLOR_4A
    assert color("asdf") == colors.COLOR_BLACK


def test_gradient() -> None:
    assert gradient("gpt-4o-mini-2024-07-18") == colors.GRADIENT_7A_LIGHT
    assert gradient("gpt-4o-2024-05-13") == colors.GRADIENT_9A_LIGHT
    assert gradient("gpt-3.5-turbo-1106") == colors.GRADIENT_1A_LIGHT
    assert gradient("anthropic.claude-3-5-sonnet-20241022-v2:0") == colors.GRADIENT_3A_LIGHT
    assert gradient("meta.llama3-1-70b-instruct-v1:0") == colors.GRADIENT_1A_LIGHT
    assert gradient("llama3.1:70b-instruct-fp16") == colors.GRADIENT_1A_LIGHT
    assert gradient("o1-2024-12-17") == colors.GRADIENT_11A_LIGHT
    assert gradient("asdf") == colors.GRADIENT_BLACK_LIGHT


def test_hatch() -> None:
    assert hatch("gpt-4o-mini-2024-07-18") == "////"
    assert hatch("gpt-4o-2024-05-13") == "\\\\\\\\"
    assert hatch("gpt-3.5-turbo-1106") == "xxx"
    assert hatch("anthropic.claude-3-5-sonnet-20241022-v2:0") == "ooo"
    assert hatch("meta.llama3-1-70b-instruct-v1:0") == "+++"
    assert hatch("llama3.1:70b-instruct-fp16") == "+++"
    assert hatch("o1-2024-12-17") == "xxxx"
    assert hatch("asdf") is None


def test_marker() -> None:
    assert marker("gpt-4o-mini-2024-07-18") == "1"
    assert marker("gpt-4o-2024-05-13") == "2"
    assert marker("gpt-3.5-turbo-1106") == "x"
    assert marker("anthropic.claude-3-5-sonnet-20241022-v2:0") == "."
    assert marker("meta.llama3-1-70b-instruct-v1:0") == "+"
    assert marker("llama3.1:70b-instruct-fp16") == "+"
    assert marker("o1-2024-12-17") == "x"
    assert marker("asdf") is None


def test_sort_idx() -> None:
    assert sort_idx("gpt-3.5-turbo-1106") == 0
    assert sort_idx("gpt-4o-mini-2024-07-18") == 1
    assert sort_idx("gpt-4o-2024-05-13") == 2
    assert sort_idx("o1-2024-12-17") == 3
    assert sort_idx("anthropic.claude-3-5-sonnet-20241022-v2:0") == 4
    assert sort_idx("meta.llama3-1-70b-instruct-v1:0") == 5
    assert sort_idx("llama3.1:70b-instruct-fp16") == 5
    assert sort_idx("gittablesCTA") == 1
    assert sort_idx("sportstables") == 2
    assert sort_idx("enterprisetables_cta") == 3
    assert sort_idx("public") == 0
    assert sort_idx("data") == 1
    assert sort_idx("task") == 2
    assert sort_idx("knowledge") == 3
    assert sort_idx("zero_shot") == 1
    assert sort_idx("one_shot") == 2
    assert sort_idx("few_shot") == 3
    assert sort_idx("RAG") == 4
    assert sort_idx("few_and_docu") == 5
    assert sort_idx("initial (clean)") == 1
    assert sort_idx("assignment number") == 3
    assert sort_idx("billing number") == 4
    assert sort_idx("deduction ≤ $0.1") == 2
    assert sort_idx("partner name") == 5
    assert sort_idx("asdf") == 0


def test_value_to_color() -> None:
    assert value_to_color(0, ("a", "b", "c", "d", "e")) == "a"
    assert value_to_color(0.3, ("a", "b", "c", "d", "e")) == "b"
    assert value_to_color(1, ("a", "b", "c", "d", "e")) == "e"
    assert value_to_color(-3, ("a", "b", "c", "d", "e")) == "a"
    assert value_to_color(3, ("a", "b", "c", "d", "e")) == "e"
    assert value_to_color(0, ("a", "b", "c", "d", "e"), reverse=True) == "e"
    assert value_to_color(0.3, ("a", "b", "c", "d", "e"), reverse=True) == "d"
    assert value_to_color(1, ("a", "b", "c", "d", "e"), reverse=True) == "a"

    with pytest.raises(AssertionError):
        value_to_color(0, tuple())

    with pytest.raises(AssertionError):
        value_to_color(0, tuple(), reverse=True)
