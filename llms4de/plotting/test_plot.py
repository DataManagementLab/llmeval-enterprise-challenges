import logging
import os

from matplotlib import pyplot as plt

from llms4de.data import get_data_path
from llms4de.plotting.plot import prepare_plt, save_plt, grouped_bar_offsets, grouped_bar_xlim_padding

logger = logging.getLogger(__name__)


def test_prepare_plt() -> None:
    prepare_plt("double_column", "one_row")
    prepare_plt("double_column", "two_row")
    prepare_plt("single_column", "one_row")
    prepare_plt("single_column", "two_row")


def test_save_plt() -> None:
    prepare_plt("double_column", "one_row")

    plt.plot([1, 2, 3], [1, 2, 3])

    path = get_data_path() / "tmp.pdf"
    save_plt(path)
    assert path.is_file()
    os.remove(path)


def test_grouped_bar_offsets() -> None:
    assert grouped_bar_offsets(3, 0.15) == [-0.16, 0, 0.16]
    assert grouped_bar_offsets(4, 0.15) == [-0.24, -0.08, 0.08, 0.24]


def test_grouped_bar_padding() -> None:
    assert round(grouped_bar_xlim_padding(3, 0.15), 3) == 0.385
    assert round(grouped_bar_xlim_padding(4, 0.15), 3) == 0.465
