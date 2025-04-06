import json
import logging
from typing import Literal

logger = logging.getLogger(__name__)


def parse_list(
        s: str,
        *,
        mode: Literal["csv"] | Literal["json_list"],
        csv_params: dict | None = None,
        json_params: dict | None = None
) -> list[str] | None:
    """Parse the given string into a list.

    Args:
        s: The string to parse.
        mode: The parsing mode.
        csv_params: The parameters for the CSV parsing mode.
        json_params: The parameters for the JSON parsing mode.

    Returns:
        The parsed list.
    """
    match mode:
        case "csv":
            return parse_list_from_csv(s, **csv_params)
        case "json_list":
            return parse_list_from_json(s, **json_params)
        case _:
            raise AssertionError(f"unknown list parsing mode `{mode}`")


def parse_list_from_csv(
        s: str,
        *,
        sep: str,
        strip: bool
) -> list[str] | None:
    """Parse the given CSV string into a list.

    Args:
        s: The string to parse.
        sep: The separator string.
        strip: Whether to strip the individual values.

    Returns:
        The parsed list.
    """
    l = s.split(sep)
    if strip:
        l = [s.strip() for s in l]
    return l


def parse_list_from_json(
        s: str,
        *,
        strip: bool,
        strict: bool
) -> list[str] | None:
    """Parse the given JSON string into a list.

    Args:
        s: The string to parse.
        strip: Whether to strip the individual values.
        strict: Whether to only consider valid JSON.

    Returns:
        The parsed list.
    """
    try:
        s = s.removeprefix("```json")
        s = s.removesuffix("```")
        s = s.strip()
        l = json.loads(s)
    except:
        if s is None:
            return None
        if strict:
            logger.warning(f"JSON parsing failed, not parsable: '{s}'")
            return None
        if "[" in s:
            s = s[s.index("["):]
        if "]" in s:
            s = s[:s.index("]") + 1]
        try:
            l = json.loads(s)
        except:
            try:
                s_new = f"{s}]"  # add ]
                l = json.loads(s_new)
            except:
                try:
                    s_new = f"{s}\"]"  # add "]
                    l = json.loads(s_new)
                except:
                    try:
                        s_new = f"{s}\"\"]"  # add ""]
                        l = json.loads(s_new)
                    except:
                        logger.warning(f"JSON parsing failed, not parsable: '{s}'")
                        return None

    if not isinstance(l, list):
        logger.warning(f"JSON parsing failed, not a list: '{s}'")
        return None

    l = [str(s) for s in l]
    if strip:
        l = [s.strip() for s in l]
    return l
