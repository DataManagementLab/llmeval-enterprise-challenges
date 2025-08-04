import collections
import logging

import attrs
import hydra
import pandas as pd
from hydra.core.config_store import ConfigStore
from matplotlib import pyplot as plt

from llms4de.data import get_experiments_path
from llms4de.plotting.colors import hatch, color, sort_idx, COLOR_GREY, COLOR_BLACK
from llms4de.plotting.plot import save_plt, prepare_plt, SUBPLOTS_ADJUST, grouped_bar_offsets, VALUE_PAD, \
    VALUE_FONT_SIZE, grouped_bar_xlim_padding, make_score_yaxis, LEGEND_X, LEGEND_Y_LOW, LEGEND_Y, FONT_SIZE, TOP_TEXT_Y
from llms4de.plotting.texts import text, score

logger = logging.getLogger(__name__)


@attrs.define
class Config:
    pass


ConfigStore.instance().store(name="config", node=Config)


@hydra.main(version_base=None, config_name="config")
def main(cfg: Config) -> None:
    res = pd.read_csv(get_experiments_path() / "enterprise_knowledge_text2signal" / "all_signal_results.csv",
                      index_col="model")
    res.sort_index(key=lambda x: x.map(sort_idx), inplace=True)
    res["results"] = res["results"].apply(eval)
    res["codes"] = res["results"].apply(lambda r: collections.Counter(v["status"] for v in r.values()))
    all_codes = list(sorted(set(code for codes in res["codes"].to_list() for code in codes.keys())))
    res["num_correct"] = res["codes"].apply(lambda c: c["valid query correct result"])
    res["num_incorrect"] = res["codes"].apply(lambda c: c.total() - c["valid query correct result"])
    res["accuracy"] = res["codes"].apply(lambda c: c["valid query correct result"] / c.total() if c.total() > 0 else 0)

    ####################################################################################################################
    # scores
    ####################################################################################################################

    table = res.pivot(columns="mode", values="accuracy")
    table.sort_index(key=lambda x: x.map(sort_idx), inplace=True)
    if "one_shot" in table.columns:
        del table["one_shot"]
    if "RAG" in table.columns:
        del table["RAG"]
    table.sort_index(axis=1, key=lambda x: [sort_idx(c) for c in x], inplace=True)

    prepare_plt("single_column", "one_row")
    (width, height) = plt.rcParams["figure.figsize"]
    height *= 1.03
    plt.rcParams["figure.figsize"] = (width, height)

    subplots_adjust = SUBPLOTS_ADJUST.copy()
    subplots_adjust["top"] = 0.85
    plt.subplots_adjust(**subplots_adjust)

    xs = [1, 2, 3]
    bar_width = 0.215
    for offset, (model, row) in zip(grouped_bar_offsets(4, bar_width), table.iterrows()):
        plt.bar(
            x=[x + offset for x in xs],
            height=row.to_list(),
            width=bar_width,
            color=color(model),
            hatch=hatch(model),
            label=text(model)
        )
        for x, value in zip(xs, row.to_list()):
            plt.text(
                x=x + offset,
                y=value + VALUE_PAD,
                s=score(value),
                color=color(model),
                ha="center",
                fontsize=VALUE_FONT_SIZE
            )

    bar_width_r = 0.25
    leaderboard_scores = [
        0.866,  # https://yale-lily.github.io/spider 20.02.2025
        0.7563  # https://bird-bench.github.io
    ]
    plt.bar(
        x=[4.15 - 0.18, 4.15 + 0.18],
        height=leaderboard_scores,
        width=bar_width_r,
        color=COLOR_GREY
    )
    for x, value in zip([4.15 - 0.18, 4.15 + 0.18], leaderboard_scores):
        plt.text(x=x, y=value + VALUE_PAD, s=score(value), color=COLOR_GREY, ha="center", fontsize=VALUE_FONT_SIZE)

    plt.grid(axis="x")
    pad_l = grouped_bar_xlim_padding(4, bar_width, 0.75)
    pad_r = grouped_bar_xlim_padding(1, bar_width_r)
    plt.xlim((1 - pad_l, 4.15 + 0.11 + pad_r))
    labels_dict = {
        "zero_shot": "Zero-shot",
        "one_shot": "One-shot",
        "few_shot": "+ Examples\n in Prompt",
        "RAG": "With Documentation",
        "few_and_docu": "+ Documentation\n in Prompt"
    }
    plt.xticks(xs + [4.15 - 0.18, 4.15, 4.15 + 0.18],
               labels=[labels_dict[col] for col in table.columns] + ["Spider", "\nTop of Leaderboard", "BIRD"])
    make_score_yaxis("Execution Accuracy")
    plt.legend(loc="upper center", bbox_to_anchor=(LEGEND_X, LEGEND_Y_LOW), ncol=len(res.index))

    plt.text(
        xs[1],
        TOP_TEXT_Y,
        "Text-to-SIGNAL fails out of the box",
        ha="center",
        fontweight="bold"
    )

    save_plt(get_experiments_path() / "enterprise_knowledge_text2signal" / "knowledge_signal_scores.pdf")

    ####################################################################################################################
    # error categories
    ####################################################################################################################

    code_mapping = {
        "syntax": ["SyntaxError", "LiteralError", "NestedAggregationsDisallowed",
                   "FillTimeSeriesMustBeCaseLevelTimestamp"],
        "content": ["ColumnNotFound", "InvalidArguments", "MissingDataSourceError", "SemanticColumnNotFound",
                    "FillNeedOrderByGroupColumnFollowedByAscendingTimeseries", "NoSuchFunction", "InvalidDatePart",
                    "MatchesOnNonNestedDataError", "ColumnsHaveToBeSelectedOnce", "NeedsNestedColumnInput"],
        "incorrect_result": ["valid query wrong result", "TooManyRowsInResponse"],
        "correct_result": ["valid query correct result"]
    }
    covered_codes = set(v for value in code_mapping.values() for v in value)
    for code in all_codes:
        if code not in covered_codes:
            logger.error(code)
            # assert False, code

    table = res.loc["gpt-4o-2024-08-06"][["mode", "codes"]]
    table = table.loc[table["mode"] != "one_shot"]
    table = table.loc[table["mode"] != "RAG"]
    table.set_index("mode", inplace=True)
    table.sort_index(key=lambda x: x.map(sort_idx), inplace=True)
    for new_code, codes in code_mapping.items():
        table[new_code] = table["codes"].apply(lambda x: sum(x[c] for c in codes))
    del table["codes"]

    table = table.transpose()
    table[table.columns] = table[table.columns].cumsum()
    table = table.iloc[::-1]

    prepare_plt("single_column", "one_row")
    (width, height) = plt.rcParams["figure.figsize"]
    height *= 1.05
    plt.rcParams["figure.figsize"] = (width, height)
    figure, axis = plt.subplots(1, 2, sharex=False, sharey=False)
    subplots_adjust = SUBPLOTS_ADJUST.copy()
    subplots_adjust["right"] = 0.98
    subplots_adjust["bottom"] = 0.35
    figure.subplots_adjust(wspace=0.37, hspace=None, **subplots_adjust)

    xs = [1, 2, 3]
    bar_width = 0.61
    for error, row in table.iterrows():
        for x in xs:
            axis[0].plot([x - bar_width / 2, x + bar_width / 2], [row.to_list()[x - 1]] * 2, color=COLOR_BLACK,
                         linewidth=0.6, solid_capstyle="butt")

        axis[0].bar(
            x=xs,
            height=row.to_list(),
            width=bar_width,
            color=color(error),
            label=text(error),
            hatch=[None, None, None if error != "syntax" else "xxx"],
            edgecolor=COLOR_GREY,
            linewidth=0
        )

    plt.grid(axis="x")
    pad = grouped_bar_xlim_padding(1, bar_width, 0.3)
    axis[0].set_xlim((xs[0] - pad, xs[-1] + pad))
    labels_dict = {
        "zero_shot": "Zero-shot\n ",  # \n for x_label placement
        "one_shot": "One-shot",
        "few_shot": "+Examples",
        "RAG": "With Documentation",
        "few_and_docu": "+Docs"
    }
    axis[0].set_xticks(xs, labels=[labels_dict[col] for col in table.columns], fontsize=5.5)
    axis[0].set_xlabel("Most queries fail to execute", labelpad=-82, fontweight="bold")
    m = table.max().max()
    axis[0].set_ylim((0, m))
    axis[0].set_yticks([0, m / 4, m / 2, m * 3 / 4, m], labels=["0", "", f"{int(m / 2)}", "", f"{int(m)}"])
    axis[0].set_ylabel("Number Of Errors")
    lh = axis[0].get_legend_handles_labels()[0]
    assert len(lh) == 4
    lh = [lh[3], lh[1], lh[2], lh[0]]
    axis[0].legend(
        handles=lh,
        loc="upper center",
        bbox_to_anchor=(0.45, LEGEND_Y),
        ncol=2
    )

    xs = [1, 2, 3]

    axis[1].set_xlabel("Many syntax errors related to SQL        ", labelpad=-82, fontweight="bold")

    axis[1].set_xticks(xs, labels=["GROUP BY\nUsing Names", "Invalid\nCharacter", "Incorrect\nStructure"], fontsize=5.5)
    pad = grouped_bar_xlim_padding(1, bar_width, 0.3)
    axis[1].set_xlim((xs[0] - pad, xs[-1] + pad))

    error_values = [50, 14, 11]
    for x, value in enumerate(error_values):
        axis[1].bar(
            x=[x + 1],
            height=value,
            width=bar_width,
            color=color("syntax"),
            label=value,
            hatch="xxx",
            edgecolor=COLOR_GREY,
            linewidth=0
        )
        axis[1].text(x=x + 1, y=value + 5,
                     s=str(int(value)),
                     color=COLOR_BLACK, ha="center", fontsize=FONT_SIZE - 1)

    #   m = table.max().max()

    m = 75
    axis[1].set_ylabel("Number Of Errors")
    axis[1].set_ylim((0, m))
    axis[1].set_yticks([0, m / 4, m / 2, m * 3 / 4, m], labels=["0", "", f"{int(m / 2)}", "", f"{int(m)}"])

    save_plt(get_experiments_path() / "enterprise_knowledge_text2signal" / "knowledge_signal_errors.pdf")


if __name__ == "__main__":
    main()
