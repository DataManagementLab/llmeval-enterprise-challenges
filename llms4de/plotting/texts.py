import logging

logger = logging.getLogger(__name__)


def text(name: str) -> str:
    """Return the text assigned to the given name. Default is the name itself.

    Args:
        name: The given name.

    Returns:
        The text.
    """
    if "gpt-3.5-turbo" in name or "gpt-35-turbo" in name:
        return "GPT-3.5-Turbo"
    elif "gpt-4o-mini" in name:
        return "GPT-4o-Mini"
    elif "gpt-4-" in name:
        return "GPT-4"
    elif "gpt-4o-" in name:
        return "GPT-4o"
    elif "o1" in name:
        return "o1"
    elif "claude-3-5-sonnet" in name:
        return "Claude 3.5 Sonnet"
    elif "llama" in name and "instruct" in name and ("3.1" in name or "3-1" in name):
        return "Llama 3.1 Instruct"

    match name:
        case "gittablesCTA":
            return "GitTablesCTA"
        case "sportstables":
            return "SportsTables"
        case "enterprisetables_cta":
            return "SAPᴄᴛᴀ"
        case "lookup-index":
            return "lookup by index"
        case "lookup-header":
            return "lookup by header"
        case "syntax":
            return "Syntax Error"
        case "content":
            return "Semantic Error"
        case "incorrect_result":
            return "Incorrect Result"
        case "correct_result":
            return "Correct Result"
        case _:
            return name


def short_text(name: str) -> str:
    """Return the short text assigned to the given name. Default is the normal text.

    Args:
        name: The given name.

    Returns:
        The short text.
    """
    match name:
        case "lookup-index":
            return "by index"
        case "lookup-header":
            return "by header"
        case _:
            return name


def score(value: float) -> str:
    """Return the value formatted as a score.

    Args:
        value: The value to format.

    Returns:
        The formatted score.
    """
    return f"{round(value, 2):0.2f}"
