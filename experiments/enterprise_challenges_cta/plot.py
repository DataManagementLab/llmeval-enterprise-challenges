import logging

import attrs
import hydra
import numpy as np
import pandas as pd
from hydra.core.config_store import ConfigStore
from matplotlib import pyplot as plt

from llms4de.data import get_experiments_path
from llms4de.plotting.colors import sort_idx, color, hatch
from llms4de.plotting.plot import prepare_plt, save_plt, FONT_SIZE, SUBPLOTS_ADJUST, grouped_bar_offsets, \
    VALUE_FONT_SIZE, VALUE_PAD, make_score_yaxis, LEGEND_Y_LOW, LEGEND_X, grouped_bar_xlim_padding
from llms4de.plotting.texts import text, score

logger = logging.getLogger(__name__)


@attrs.define
class Config:
    pass


ConfigStore.instance().store(name="config", node=Config)


@hydra.main(version_base=None, config_name="config")
def main(cfg: Config) -> None:
    res = pd.read_csv(
        get_experiments_path() / "enterprise_challenges_cta" / "f1_scores.csv",
        header=[0, 1],
        index_col=0
    )
    res.sort_index(key=lambda x: x.map(sort_idx), inplace=True)
    res.sort_index(axis=1, level=0, ascending=False, inplace=True)
    res.sort_index(axis=1, level=1, key=lambda x: x.map(sort_idx), inplace=True)
    res.columns = res.columns.droplevel(0)

    prepare_plt("single_column", "one_row")
    (width, height) = plt.rcParams["figure.figsize"]
    height += 0.2
    plt.rcParams["figure.figsize"] = (width, height)
    subplots_adjust = SUBPLOTS_ADJUST.copy()
    subplots_adjust["top"] = 0.85
    plt.subplots_adjust(**subplots_adjust)

    xs = list(range(1, len(res.columns) + 1))
    bar_width = 0.21
    for offset, (model, row) in zip(grouped_bar_offsets(4, bar_width), res.iterrows()):
        plt.bar(
            x=[x + offset for x in xs],
            height=res.loc[model].to_list(),
            width=bar_width,
            color=color(model),
            hatch=hatch(model),
            label=text(model)
        )
        for x, value in zip(xs, res.loc[model]):
            plt.text(
                x=x + offset,
                y=value + VALUE_PAD,
                s=score(value),
                color=color(model),
                ha="center",
                fontsize=VALUE_FONT_SIZE
            )

    plt.grid(axis="x")
    pad = grouped_bar_xlim_padding(4, bar_width, 0.5)
    plt.xlim((xs[0] - pad, xs[-1] + pad))
    labels_dict = {
        "public": f"{text("sportstables")}",
        "data": "SAPᴄᴛᴀ",
        "tasks": "+ Task\nChallenges",
        "knowledge": "+ Knowledge\nChallenges"
    }
    plt.xticks(xs, labels=[labels_dict[col] for col in res.columns])
    make_score_yaxis("F1 Score")
    plt.legend(loc="upper center", bbox_to_anchor=(LEGEND_X, LEGEND_Y_LOW + 0.04), ncol=len(res.index))

    plt.arrow(
        2, 0.74, 1.8, -0.4,
        head_width=0.05,
        head_length=0.1,
        fc="#E6001A",
        ec="#E6001A"
    )
    plt.text(
        3, 0.405,
        "Enterprise challenges cause\nperformance decrease!",
        ha="center",
        fontsize=FONT_SIZE,
        color="#E6001A",
        fontweight="bold",
        rotation=np.degrees(-np.arctan2(0.4, 1.8))
    )

    plt.text(1, 1.135, "Public Benchmark", ha="center", fontsize=FONT_SIZE + 1, color="#009D81", fontweight="bold")
    plt.text(3.1, 1.135, "Representative Customer Data from SAP", ha="center", fontsize=FONT_SIZE + 1, color="#E6001A",
             fontweight="bold")

    save_plt(get_experiments_path() / "enterprise_challenges_cta" / "headline_f1_scores.pdf")


if __name__ == "__main__":
    main()
