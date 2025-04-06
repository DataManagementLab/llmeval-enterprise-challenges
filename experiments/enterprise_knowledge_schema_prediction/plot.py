import logging
import logging
import statistics

import attrs
import hydra
import pandas as pd
from hydra.core.config_store import ConfigStore
from matplotlib import pyplot as plt

from llms4de.data import get_experiments_path
from llms4de.plotting.colors import color, sort_idx, hatch
from llms4de.plotting.plot import save_plt, prepare_plt, SUBPLOTS_ADJUST, LEGEND_Y_LOW, grouped_bar_offsets, VALUE_PAD, \
    VALUE_FONT_SIZE, grouped_bar_xlim_padding
from llms4de.plotting.texts import text, score

logger = logging.getLogger(__name__)


@attrs.define
class Config:
    pass


ConfigStore.instance().store(name="config", node=Config)


@hydra.main(version_base=None, config_name="config")
def main(cfg: Config) -> None:
    res_sap = pd.read_csv(
        get_experiments_path() / "enterprise_knowledge_schema_prediction" / "f1_score_by_count_sap.csv",
        index_col="model")
    res_sap.sort_index(key=lambda x: x.map(sort_idx), inplace=True)
    res_zzz = pd.read_csv(
        get_experiments_path() / "enterprise_knowledge_schema_prediction" / "f1_score_by_count_zzz.csv",
        index_col="model")
    res_zzz.sort_index(key=lambda x: x.map(sort_idx), inplace=True)

    mappings = {
        "1": map_1,
        "2-9": map_2_9,
        "≥10": map_10
    }

    for k, m in mappings.items():
        res_sap[k] = res_sap["f1_score_by_count_sap"].apply(eval).apply(m)
        res_zzz[k] = res_zzz["f1_score_by_count_zzz"].apply(eval).apply(m)

    res_sap = res_sap[list(mappings.keys())]
    res_zzz = res_zzz[list(mappings.keys())]

    prepare_plt("single_column", "one_row")
    figure, axis = plt.subplots(1, 2, sharex=False, sharey=False)
    subplots_adjust = SUBPLOTS_ADJUST.copy()
    subplots_adjust["right"] = 0.98
    subplots_adjust["left"] = 0.13
    figure.subplots_adjust(wspace=0.37, hspace=None, **subplots_adjust)

    xs = [1, 2, 3]
    bar_width = 0.2
    for offset, (model, row) in zip(grouped_bar_offsets(4, bar_width), res_sap.iterrows()):
        axis[0].bar(
            x=[x + offset for x in xs],
            height=[row[k] for k in mappings.keys()],
            width=bar_width,
            color=color(model),
            label=text(model),
            hatch=hatch(model)
        )
        axis[0].text(x=1 + offset, y=row[list(mappings.keys())[0]] + VALUE_PAD - 0.04,
                     s=score(row[list(mappings.keys())[0]])[-3:],
                     color=color(model), ha="center", fontsize=VALUE_FONT_SIZE - 1)
        axis[0].text(x=2 + offset, y=row[list(mappings.keys())[1]] + VALUE_PAD - 0.04,
                     s=score(row[list(mappings.keys())[1]])[-3:],
                     color=color(model), ha="center", fontsize=VALUE_FONT_SIZE - 1)
        axis[0].text(x=3 + offset, y=row[list(mappings.keys())[2]] + VALUE_PAD - 0.04,
                     s=score(row[list(mappings.keys())[2]])[-3:],
                     color=color(model), ha="center", fontsize=VALUE_FONT_SIZE - 1)

    axis[0].grid(axis="x")
    pad = grouped_bar_xlim_padding(4, bar_width, 0.5)
    axis[0].set_xlim((xs[0] - pad, xs[-1] + pad))
    axis[0].set_xticks([1, 2, 3], labels=list(mappings.keys()))

    axis[0].set_ylim((0, 0.25))
    axis[0].set_yticks((0, 0.0625, 0.125, 0.1875, 0.25), labels=["0", "", "0.125", "", "0.250"])
    axis[0].set_ylabel("F1 Score")
    axis[0].set_xlabel("Standard SAP Columns", labelpad=-77, fontweight="bold")

    for label in axis[0].get_yticklabels():
        if label.get_text() == "0.250":
            label.set_fontweight("bold")
            label.set_fontstyle("italic")

    xs = [1, 2, 3]
    bar_width = 0.2
    for offset, (model, row) in zip(grouped_bar_offsets(4, bar_width), res_zzz.iterrows()):
        axis[1].bar(
            x=[x + offset for x in xs],
            height=[row[k] for k in mappings.keys()],
            width=bar_width,
            color=color(model),
            label=text(model),
            hatch=hatch(model)
        )
        axis[1].text(x=1 + offset, y=row[list(mappings.keys())[0]] + VALUE_PAD - 0.04,
                     s=score(row[list(mappings.keys())[0]])[-3:],
                     color=color(model), ha="center", fontsize=VALUE_FONT_SIZE - 1)
        axis[1].text(x=2 + offset, y=row[list(mappings.keys())[1]] + VALUE_PAD - 0.04,
                     s=score(row[list(mappings.keys())[1]])[-3:],
                     color=color(model), ha="center", fontsize=VALUE_FONT_SIZE - 1)
        axis[1].text(x=3 + offset, y=row[list(mappings.keys())[2]] + VALUE_PAD - 0.04,
                     s=score(row[list(mappings.keys())[2]])[-3:],
                     color=color(model), ha="center", fontsize=VALUE_FONT_SIZE - 1)

    axis[1].grid(axis="x")
    pad = grouped_bar_xlim_padding(4, bar_width, 0.5)
    axis[1].set_xlim((xs[0] - pad, xs[-1] + pad))
    axis[1].set_xticks([1, 2, 3], labels=list(mappings.keys()))

    axis[1].set_ylim((0, 0.25))
    axis[1].set_yticks((0, 0.0625, 0.125, 0.1875, 0.25), labels=["0", "", "0.125", "", "0.250"])
    axis[1].set_xlabel("Customer-defined Columns", labelpad=-77, fontweight="bold")

    for label in axis[1].get_yticklabels():
        if label.get_text() == "0.250":
            label.set_fontweight("bold")
            label.set_fontstyle("italic")

    figure.text(0.535, 0.12, "How Often Column Appears In Schema", ha="center")

    plt.legend(loc="upper center", bbox_to_anchor=(-0.33, LEGEND_Y_LOW), ncol=len(res_sap.index))

    save_plt(get_experiments_path() / "enterprise_knowledge_schema_prediction" / "knowledge_header_recall.pdf")


def is_int(s: str) -> bool:
    try:
        int(s)
        return True
    except:
        return False


def map_1(d: dict) -> float:
    f1_scores = []
    for k, v in d.items():
        if k == 1:
            f1_scores += [v[0]] * v[1]
    return statistics.mean(f1_scores)


def map_2_9(d: dict) -> float:
    f1_scores = []
    for k, v in d.items():
        if 2 <= k <= 9:
            f1_scores += [v[0]] * v[1]
    return statistics.mean(f1_scores)


def map_10(d: dict) -> float:
    f1_scores = []
    for k, v in d.items():
        if k >= 10:
            f1_scores += [v[0]] * v[1]
    return statistics.mean(f1_scores)


if __name__ == "__main__":
    main()
