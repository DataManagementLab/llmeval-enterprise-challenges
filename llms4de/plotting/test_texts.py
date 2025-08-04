import logging

from llms4de.plotting.texts import text, short_text, score

logger = logging.getLogger(__name__)


def test_text() -> None:
    assert text("gpt-4o-mini-2024-07-18") == "GPT-4o-Mini"
    assert text("gpt-4o-2024-05-13") == "GPT-4o"
    assert text("gpt-3.5-turbo-1106") == "GPT-3.5-Turbo"
    assert text("gpt-4-0613") == "GPT-4"
    assert text("o1-2024-12-17") == "o1"
    assert text("anthropic.claude-3-5-sonnet-20241022-v2:0") == "Claude 3.5 Sonnet (v2)"
    assert text("anthropic.claude-3-5-sonnet-20240620-v1:0") == "Claude 3.5 Sonnet"
    assert text("meta.llama3-1-70b-instruct-v1:0") == "Llama 3.1 Instruct"
    assert text("llama3.1:70b-instruct-fp16") == "Llama 3.1 Instruct"
    assert text("gittablesCTA") == "GitTablesCTA"
    assert text("sportstables") == "SportsTables"
    assert text("lookup-index") == "lookup by index"
    assert text("lookup-header") == "lookup by header"
    assert text("syntax") == "Syntax Error"
    assert text("content") == "Semantic Error"
    assert text("incorrect_result") == "Incorrect Result"
    assert text("correct_result") == "Correct Result"
    assert text("asdf") == "asdf"


def test_short_text() -> None:
    assert short_text("lookup-index") == "by index"
    assert short_text("lookup-header") == "by header"
    assert short_text("asdf") == "asdf"


def test_score() -> None:
    assert score(0.115) == "0.12"
    assert score(0.114) == "0.11"
