import logging

import attrs
import hydra
import pandas as pd
from hydra.core.config_store import ConfigStore
from matplotlib import pyplot as plt

from llms4de.data import get_experiments_path
from llms4de.plotting.colors import color, sort_idx, marker, gradient
from llms4de.plotting.plot import save_plt, prepare_plt, SUBPLOTS_ADJUST, LEGEND_Y_LOW
from llms4de.plotting.texts import text

logger = logging.getLogger(__name__)


@attrs.define
class Config:
    pass


ConfigStore.instance().store(name="config", node=Config)


@hydra.main(version_base=None, config_name="config")
def main(cfg: Config) -> None:
    ####################################################################################################################
    # ablation for sparsity
    ####################################################################################################################

    res = pd.read_csv(
        get_experiments_path() / "enterprise_data_sparsity_width_cta" / "f1_scores_by_sparsity.csv",
        index_col="model"
    )
    res.sort_index(key=lambda x: x.map(sort_idx), inplace=True)

    prepare_plt("single_column", "one_row")
    figure, axis = plt.subplots(1, 2, sharex=False, sharey=False)
    subplots_adjust = SUBPLOTS_ADJUST.copy()
    subplots_adjust["right"] = 0.98
    figure.subplots_adjust(wspace=0.35, hspace=None, **subplots_adjust)

    sparsities = list(sorted(map(float, filter(is_float, res.columns))))
    for model, row in res.iterrows():
        if row["header"] == "with-headers":
            axis[0].plot(sparsities, [row[str(s)] for s in sparsities], mew=1.75,
                         color=gradient(model)[1], marker=marker(model), mfc=color(model), mec=color(model),
                         label=text(model))
    axis[0].set_xlim((0, 1))
    axis[0].set_xticks((0, 0.25, 0.50, 0.75, 1.00), labels=("0", "", "0.5", "", "1.0"))
    axis[0].set_ylim((0, 1))
    axis[0].set_yticks((0, 0.25, 0.5, 0.75, 1), labels=["0", "", "0.5", "", "1.0"])
    axis[0].set_ylabel("F1 Score")
    axis[0].set_xlabel("With Column Names", labelpad=-77, fontweight="bold")

    for model, row in res.iterrows():
        if row["header"] == "without-headers":
            axis[1].plot(sparsities, [row[str(s)] for s in sparsities], mew=1.75,
                         color=gradient(model)[1], marker=marker(model), mfc=color(model), mec=color(model),
                         label=text(model))
    axis[1].set_xlim((0, 1))
    axis[1].set_xticks((0, 0.25, 0.50, 0.75, 1.00), labels=("0", "", "0.5", "", "1.0"))
    axis[1].set_ylim((0, 0.1))
    axis[1].set_yticks((0, 0.025, 0.05, 0.075, 0.1), labels=["0", "", "0.05", "", "0.10"])
    axis[1].set_xlabel("Without Column Names", labelpad=-77, fontweight="bold")

    for label in axis[1].get_yticklabels():
        if label.get_text() == "0.10":
            label.set_fontweight("bold")
            label.set_fontstyle("italic")

    figure.text(0.535, 0.12, "Fraction of Empty Cells", ha="center")

    plt.legend(loc="upper center", bbox_to_anchor=(-0.28, LEGEND_Y_LOW), ncol=len(res.index))

    save_plt(get_experiments_path() / "enterprise_data_sparsity_width_cta" / "data_f1_scores_by_sparsity.pdf")

    ####################################################################################################################
    # ablation for table width
    ####################################################################################################################

    res = pd.read_csv(
        get_experiments_path() / "enterprise_data_sparsity_width_cta" / "f1_scores_by_num_columns.csv",
        index_col="model"
    )
    res.sort_index(key=lambda x: x.map(sort_idx), inplace=True)

    prepare_plt("single_column", "one_row")
    figure, axis = plt.subplots(1, 2, sharex=False, sharey=False)
    subplots_adjust = SUBPLOTS_ADJUST.copy()
    subplots_adjust["right"] = 0.98
    figure.subplots_adjust(wspace=0.35, hspace=None, **subplots_adjust)

    num_columnss = list(sorted(map(int, filter(is_int, res.columns))))
    for model, row in res.iterrows():
        if row["header"] == "with-headers":
            axis[0].plot(num_columnss, [row[str(s)] for s in num_columnss], mew=1.75,
                         color=gradient(model)[1], marker=marker(model), mfc=color(model), mec=color(model),
                         label=text(model))
    axis[0].set_xlim((0, 100))
    axis[0].set_xticks((0, 25, 50, 75, 100), labels=("0", "", "50", "", "100"))
    axis[0].set_ylim((0, 1))
    axis[0].set_yticks((0, 0.25, 0.5, 0.75, 1), labels=["0", "", "0.5", "", "1.0"])
    axis[0].set_ylabel("F1 Score")
    axis[0].set_xlabel("With Column Names", labelpad=-77, fontweight="bold")

    for model, row in res.iterrows():
        if row["header"] == "without-headers":
            axis[1].plot(num_columnss, [row[str(s)] for s in num_columnss], mew=1.75,
                         color=gradient(model)[1], marker=marker(model), mfc=color(model), mec=color(model),
                         label=text(model))
    axis[1].set_xlim((0, 100))
    axis[1].set_xticks((0, 25, 50, 75, 100), labels=("0", "", "50", "", "100"))
    axis[1].set_ylim((0, 0.1))
    axis[1].set_yticks((0, 0.025, 0.05, 0.075, 0.1), labels=["0", "", "0.05", "", "0.10"])
    axis[1].set_xlabel("Without Column Names", labelpad=-77, fontweight="bold")

    for label in axis[1].get_yticklabels():
        if label.get_text() == "0.10":
            label.set_fontweight("bold")
            label.set_fontstyle("italic")

    figure.text(0.535, 0.12, "Number of Columns", ha="center")

    plt.legend(loc="upper center", bbox_to_anchor=(-0.28, LEGEND_Y_LOW), ncol=len(res.index))

    save_plt(get_experiments_path() / "enterprise_data_sparsity_width_cta" / "data_f1_scores_by_num_columns.pdf")


def is_float(s: str) -> bool:
    try:
        float(s)
        return True
    except:
        return False


def is_int(s: str) -> bool:
    try:
        int(s)
        return True
    except:
        return False


if __name__ == "__main__":
    main()
