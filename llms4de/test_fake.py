import logging

import pytest

from llms4de.fake import fake_hex, unique

logger = logging.getLogger(__name__)


def test_fake_hex() -> None:
    # note that the hexadecimal strings should be deterministic
    assert fake_hex(4) == "b62c"
    assert fake_hex(10) == "780e10b2ec"
    assert fake_hex(0) == ""


def test_unique() -> None:
    idx = 0

    def generator() -> int:
        nonlocal idx
        idx += 1
        return idx

    assert unique(generator, []) == 1
    idx = 0
    assert unique(generator, [1]) == 2
    idx = 0
    with pytest.raises(AssertionError):
        unique(generator, [1, 2, 3, 4], num_tries=2)
