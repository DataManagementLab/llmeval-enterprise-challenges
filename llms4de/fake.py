import logging
import random
from typing import Any, Callable

logger = logging.getLogger(__name__)

fake_hex_random = random.Random(69230915)


def fake_hex(length: int) -> str:
    """Generates a random hexadecimal string of the given length.

    Args:
        length: The length of the string.

    Returns:
        The random hexadecimal string.
    """
    return "".join(fake_hex_random.choice("0123456789abcdef") for _ in range(length))


def unique(generator: Callable, prev_values: list[Any], *, num_tries: int = 10_000) -> Any:
    """Calls the generator function until a new value is generated.

    Raises if no new value is generated in the specified number of tries.

    Args:
        generator: The generator function, which receives no arguments.
        prev_values: The list of previous values.
        num_tries: The number of tries to generate a new value.

    Returns:
        The new value.
    """
    prev_values = set(prev_values)
    for _ in range(num_tries):
        value = generator()
        if value not in prev_values:
            return value
    raise AssertionError(f"Unable to generate a unique value in {num_tries} tries.")
