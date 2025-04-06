import logging
import pathlib
from typing import Literal

from matplotlib import pyplot as plt

logger = logging.getLogger(__name__)

FONT_SIZE: float = 6.5
VALUE_FONT_SIZE: float = 4.5
VALUE_PAD: float = 0.05
LEGEND_X: float = 0.45
LEGEND_Y: float = -0.15
LEGEND_Y_LOW: float = -0.3
LEGEND_COL_SPACING: float = 1.35
HATCH_LINE_WIDTH: float = 0.3
BAR_DIST_FRAC: float = 1 / 15
BAR_XLIM_PADDING_FRAC: float = 1
TOP_TEXT_Y: float = 1.1
SUBPLOTS_ADJUST: dict[str, float] = {
    "left": 0.1,
    "top": 0.88,
    "bottom": 0.3,
    "right": 0.985
}


def prepare_plt(
        width: Literal["double_column"] | Literal["single_column"] | float,
        height: Literal["one_row"] | Literal["two_row"] | float
) -> None:
    """Prepare matplotlib to create a plot.

    Args:
        width: The width of the plot in the paper.
        height: The height of the plot in the paper.
    """
    plt.style.use("seaborn-v0_8-whitegrid")

    if width == "double_column":
        width = 8
    elif width == "single_column":
        width = 4

    if height == "one_row":
        height = 1.35
    elif height == "two_row":
        height = 2.7

    plt.rcParams["figure.figsize"] = (width, height)
    plt.rcParams["font.size"] = FONT_SIZE
    plt.rcParams["hatch.linewidth"] = HATCH_LINE_WIDTH
    plt.rcParams["legend.columnspacing"] = LEGEND_COL_SPACING


def save_plt(
        path: pathlib.Path
) -> None:
    """Save the plot at the given path.

    Args:
        path: The path at which to save the plot.
    """
    plt.savefig(path)
    plt.clf()


def make_score_yaxis(label: str | None) -> None:
    """Prepare the y-axis for scores.

    Args:
        label: The column label
    """
    ticks = [0, 0.25, 0.5, 0.75, 1]
    labels = [f"{ticks[0]}", "", f"{ticks[2]}", "", f"{ticks[4]}"]
    max_decimals = max(len(l.partition(".")[2]) if "." in l else 0 for l in labels)
    labels = labels[:1] + [l if l == "" else f"{float(l):.{max_decimals}f}" for l in labels[1:]]
    plt.yticks(ticks, labels=labels)
    plt.ylim((0, 1.0))
    if label is not None:
        plt.ylabel(label)


def grouped_bar_offsets(bars_per_group: int, bar_width: float) -> list[float]:
    """Compute offsets for grouped bar charts.
    
    Args:
        bars_per_group: The number of bars per group.
        bar_width: The width of each bar.

    Returns:
        The offsets for the bar centers.
    """
    bar_dist = bar_width * BAR_DIST_FRAC

    if bars_per_group % 2 == 1:
        side = [(bar_width + bar_dist) * (n + 1) for n in range((bars_per_group - 1) // 2)]
        return [-v for v in reversed(side)] + [0] + side
    else:
        side = [(bar_width + bar_dist) * (n + 0.5) for n in range(bars_per_group // 2)]
        return [-v for v in reversed(side)] + side


def grouped_bar_xlim_padding(
        bars_per_group: int,
        bar_width: float,
        bar_xlim_padding_frac: float | None = None
) -> float:
    """Compute the xlim padding for grouped bar charts.

    Args:
        bars_per_group: The number of bars per group.
        bar_width: The width of each bar.
        bar_xlim_padding_frac: The padding from outermost bar to the plot border.

    Returns:
        The padding.
    """
    if bar_xlim_padding_frac is None:
        bar_xlim_padding_frac = BAR_XLIM_PADDING_FRAC

    return grouped_bar_offsets(bars_per_group, bar_width)[-1] + ((0.5 + bar_xlim_padding_frac) * bar_width)
