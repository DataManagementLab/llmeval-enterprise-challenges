import logging
import re
from copy import deepcopy

logger = logging.getLogger(__name__)


def fill_template(template: str, **args) -> str:
    """Replace {{variables}} in the template with the given values.

    Args:
        template: The given template string, which may contain {{variables}}.
        **args: The values for the variables.

    Raises in case of missing values, but not in case of unneeded values.

    Returns:
        The template string with {{variables}} replaced by values.
    """

    def replace_variable(match) -> str:
        variable = match.group(1)
        if variable not in args.keys():
            raise AssertionError(f"Missing value for template string variable {variable}!")
        return args[variable]

    return re.sub(r"\{\{([^{}]+)\}\}", replace_variable, template)


def fill_chat_template(
        template: list[dict[str, str] | str],
        **args
) -> list[dict[str, str]]:
    """Replace {{variables}} in the chat template with the given values.

    A value can be a list of messages, a message, or a string, and replacement happens in that order.

    Raises in case of missing values, but not in case of unneeded values.

    Args:
        template: List of template messages containing {{variables}}.
        **args: The given string, message, or list of messages as values for the variables.

    Returns:
        The filled-out template.
    """
    template = deepcopy(template)

    # replace message variables with lists of messages
    for key, value in args.items():
        template_key = "{{" + key + "}}"
        if isinstance(value, list):
            new_template = []
            for message in template:
                if message == template_key:
                    new_template += value
                else:
                    new_template.append(message)
            template = new_template

    # replace message variables with messages
    for key, value in args.items():
        template_key = "{{" + key + "}}"
        if isinstance(value, dict):
            new_template = []
            for message in template:
                if message == template_key:
                    new_template.append(value)
                else:
                    new_template.append(message)
            template = new_template

    # check for missing message values
    for message in template:
        if isinstance(message, str):
            raise AssertionError(f"Missing values for template message variable {message}!")

    # replace string variables with strings, which already checks for missing string values
    str_args = {k: v for k, v in args.items() if isinstance(v, str)}
    for message in template:
        message["content"] = fill_template(message["content"], **str_args)

    return template


def merge_messages_with_same_role(messages: list[dict[str, str]], separator: str = "\n\n") -> list[dict[str, str]]:
    """Merge consecutive messages from the same role.

    Args:
        messages: A list of messages.
        separator: The seperator string to place between merged message contents.

    Returns:
        The list of merged messages.


    """
    merged_messages = []
    for message in messages:
        if merged_messages != [] and message["role"] == merged_messages[-1]["role"]:
            merged_messages[-1]["content"] += separator + message["content"]
        else:
            merged_messages.append(message)
    return merged_messages
