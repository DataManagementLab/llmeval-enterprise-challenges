import logging

import attrs
import hydra
import pandas as pd
from hydra.core.config_store import ConfigStore
from matplotlib import pyplot as plt

from llms4de.data import dump_str, get_experiments_path
from llms4de.plotting.colors import hatch, color, sort_idx
from llms4de.plotting.plot import save_plt, prepare_plt, SUBPLOTS_ADJUST, grouped_bar_offsets, VALUE_FONT_SIZE, \
    VALUE_PAD, make_score_yaxis, grouped_bar_xlim_padding, LEGEND_Y, LEGEND_X, LEGEND_Y_LOW, TOP_TEXT_Y
from llms4de.plotting.texts import text, score

logger = logging.getLogger(__name__)


@attrs.define
class Config:
    pass


ConfigStore.instance().store(name="config", node=Config)


@hydra.main(version_base=None, config_name="config")
def main(cfg: Config) -> None:
    ####################################################################################################################
    # F1 scores at increasing difficulties
    ####################################################################################################################

    table = pd.read_csv(
        get_experiments_path() / "enterprise_tasks_pay_to_inv" / "tasks_pay_to_inv_increasing_difficulty.csv",
        index_col="model"
    )
    table.sort_index(key=lambda x: x.map(sort_idx), inplace=True)
    table = table.map(score)
    table.reset_index(inplace=True)
    table["model"] = table["model"].apply(text)
    latex = table.to_latex(column_format="l" + "r" * (len(table.columns) - 1), index=False)
    latex_lines = latex.splitlines()
    latex_lines[2] = " & ".join(r"\textbf{" + part + "}" for part in latex_lines[2][:-3].split(" & ")) + r" \\"
    latex = "\n".join(latex_lines)
    dump_str(latex,
             get_experiments_path() / "enterprise_tasks_pay_to_inv" / "tasks_pay_to_inv_increasing_difficulty.tex")

    ####################################################################################################################
    # precision and recall for +multi-matches scenario
    ####################################################################################################################

    res = pd.read_csv(
        get_experiments_path() / "enterprise_tasks_pay_to_inv" / "tasks_pay_to_inv_precision_recall.csv",
        index_col="model"
    )
    res.sort_index(key=lambda x: x.map(sort_idx), inplace=True)

    prepare_plt("single_column", "one_row")
    (width, height) = plt.rcParams["figure.figsize"]
    height *= 1.03
    plt.rcParams["figure.figsize"] = (width, height)

    subplots_adjust = SUBPLOTS_ADJUST.copy()
    subplots_adjust["top"] = 0.85
    subplots_adjust["left"] = 0.05
    plt.subplots_adjust(**subplots_adjust)

    xs = [1, 2, 3]
    bar_width = 0.175
    for offset, (model, row) in zip(grouped_bar_offsets(4, bar_width), res.iterrows()):
        plt.bar(
            x=[x + offset for x in xs],
            height=[row["f1_score"], row["precision"], row["recall"]],
            width=bar_width,
            color=color(model),
            label=text(model),
            hatch=hatch(model)
        )
        plt.text(x=1 + offset, y=row["f1_score"] + VALUE_PAD, s=score(row["f1_score"]),
                 color=color(model), ha="center", fontsize=VALUE_FONT_SIZE)
        plt.text(x=2 + offset, y=row["precision"] + VALUE_PAD, s=score(row["precision"]),
                 color=color(model), ha="center", fontsize=VALUE_FONT_SIZE)
        plt.text(x=3 + offset, y=row["recall"] + VALUE_PAD, s=score(row["recall"]),
                 color=color(model), ha="center", fontsize=VALUE_FONT_SIZE)

    plt.grid(axis="x")
    pad = grouped_bar_xlim_padding(4, bar_width)
    plt.xlim((xs[0] - pad, xs[-1] + pad))
    plt.xticks([1, 2, 3], labels=["F1 Score", "Precision", "Recall"])
    make_score_yaxis(None)
    plt.legend(loc="upper center", bbox_to_anchor=(0.48, LEGEND_Y), ncol=len(res.index))

    plt.text(
        2.5,
        TOP_TEXT_Y + 0.05,
        "F1 scores depend only on recall",
        ha="center",
        fontweight="bold"
    )

    save_plt(get_experiments_path() / "enterprise_tasks_pay_to_inv" / "tasks_pay_to_inv_precision_recall.pdf")

    ####################################################################################################################
    # F1 scores for typical error categories
    ####################################################################################################################

    res = pd.read_csv(
        get_experiments_path() / "enterprise_tasks_pay_to_inv" / "tasks_pay_to_inv_error_categories.csv",
        index_col="model"
    )
    res.sort_index(key=lambda x: x.map(sort_idx), inplace=True)
    res.sort_index(axis=1, key=lambda x: x.map(sort_idx), inplace=True)

    prepare_plt("single_column", "one_row")
    (width, height) = plt.rcParams["figure.figsize"]
    height *= 1.03
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
        "initial (clean)": "Clean",
        "assignment number": "Assignment\nNumber",
        "billing number": "Billing\nNumber",
        "deduction ≤ $0.1": "Deduction\n≤ $0.1",
        "partner name": "Partner\nName"
    }
    plt.xticks(xs, labels=[labels_dict[col] for col in res.columns])
    make_score_yaxis("F1 Score")
    plt.legend(loc="upper center", bbox_to_anchor=(LEGEND_X, LEGEND_Y_LOW), ncol=len(res.index))

    plt.text(
        (xs[2] + xs[3]) / 2,
        TOP_TEXT_Y + 0.05,
        "Failures caused mainly by errors in textual attributes",
        ha="center",
        fontweight="bold"
    )

    save_plt(get_experiments_path() / "enterprise_tasks_pay_to_inv" / "tasks_pay_to_inv_error_categories.pdf")


if __name__ == "__main__":
    main()
