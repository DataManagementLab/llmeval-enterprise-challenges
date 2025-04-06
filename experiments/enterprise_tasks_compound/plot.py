import logging

import attrs
import hydra
import numpy as np
import pandas as pd
from hydra.core.config_store import ConfigStore
from matplotlib import pyplot as plt
from matplotlib.patches import Patch

from llms4de.data import get_experiments_path
from llms4de.plotting.colors import hatch, color, sort_idx, COLOR_10A, COLOR_11A, COLOR_BLACK
from llms4de.plotting.plot import save_plt, prepare_plt, grouped_bar_offsets, VALUE_FONT_SIZE, VALUE_PAD, \
    grouped_bar_xlim_padding, make_score_yaxis, LEGEND_Y, LEGEND_Y_LOW, LEGEND_X, TOP_TEXT_Y, \
    SUBPLOTS_ADJUST
from llms4de.plotting.texts import text, score

logger = logging.getLogger(__name__)


@attrs.define
class Config:
    pass


ConfigStore.instance().store(name="config", node=Config)


@hydra.main(version_base=None, config_name="config")
def main(cfg: Config) -> None:
    ####################################################################################################################
    # Accuracy scores for pipeline vs. end2end
    ####################################################################################################################

    res = pd.read_csv(get_experiments_path() / "enterprise_tasks_compound" / "pipeline_end2end.csv", index_col="model")
    res.sort_index(key=lambda x: x.map(sort_idx), inplace=True)

    prepare_plt("single_column", "one_row")
    plt.subplots_adjust(**SUBPLOTS_ADJUST)

    xs = [0.5, 1.7, 2.8]
    bar_width = 0.19
    offsets_p = grouped_bar_offsets(4, bar_width)
    offsets_p.insert(len(offsets_p) // 2, 0)
    offsets_e = grouped_bar_offsets(5, bar_width)
    for offset_p, offset_e, (model, row) in zip(offsets_p, offsets_e, res.iterrows()):
        plt.bar(
            x=[x + offset_p for x in xs[:1]] + [x + offset_e for x in xs[1:]],
            height=res.loc[model].to_list(),
            width=bar_width,
            color=color(model),
            hatch=hatch(model),
            label=text(model)
        )
        for x, value in zip(xs[:1], res.loc[model][:1]):
            plt.text(
                x=x + offset_p,
                y=value + VALUE_PAD,
                s=score(value),
                color=color(model),
                ha="center",
                fontsize=VALUE_FONT_SIZE
            )

        for x, value in zip(xs[1:], res.loc[model][1:]):
            plt.text(
                x=x + offset_e,
                y=value + VALUE_PAD,
                s=score(value),
                color=color(model),
                ha="center",
                fontsize=VALUE_FONT_SIZE
            )

    plt.grid(axis="x")
    padding_p = grouped_bar_xlim_padding(4, bar_width, 0.5)
    padding_e = grouped_bar_xlim_padding(5, bar_width, 0.5)
    plt.xlim((xs[0] - padding_p, xs[-1] + padding_e))
    labels_dict = {
        "pipeline": "Pipeline",
        "end2end_text": "End2End (w/out Steps)",
        "end2end_steps": "End2End (with Steps)"
    }
    plt.xticks(xs, labels=[labels_dict[col] for col in res.columns])
    make_score_yaxis("Accuracy")
    plt.legend(
        loc="upper center",
        bbox_to_anchor=(LEGEND_X, LEGEND_Y),
        ncol=len(res.index),
        columnspacing=1.0,
        fontsize=6.0
    )

    save_plt(get_experiments_path() / "enterprise_tasks_compound" / "tasks_compound_pipeline_end2end.pdf")

    ####################################################################################################################
    # Accuracy scores end2end scale
    ####################################################################################################################

    res = pd.read_csv(get_experiments_path() / "enterprise_tasks_compound" / "end2end_scale.csv", index_col="model")
    res.sort_index(key=lambda x: x.map(sort_idx), inplace=True)

    prepare_plt("single_column", "one_row")
    plt.subplots_adjust(**SUBPLOTS_ADJUST)

    xs = [1, 2, 3, 4, 5]
    bar_width = 0.3
    for offset, (model_mode, row) in zip(grouped_bar_offsets(2, bar_width), res.iterrows()):
        model, mode = model_mode.split(" ")
        c = color(model) if mode == "text" else COLOR_10A
        plt.bar(
            x=[x + offset for x in xs],
            height=res.loc[model_mode].to_list(),
            width=bar_width,
            color=c,
            hatch=hatch(model) if mode == "text" else "...",
            label=f"{text(model)} (End2End w/out Steps)" if mode == "text" else f"{text(model)} (End2End with Steps)"
        )
        for x, value in zip(xs, res.loc[model_mode]):
            plt.text(x=x + offset, y=value + VALUE_PAD, s=score(value), color=c, ha="center", fontsize=VALUE_FONT_SIZE)

    plt.text(x=5, y=0.035, s="'Sorry, but I\ncan't fulfill that.'", color=COLOR_11A, ha="center", fontsize=5.5,
             fontstyle="oblique", fontweight="bold")

    plt.arrow(
        2.35, 0.75, 2.7, -0.4,
        head_width=0.05,
        head_length=0.12,
        fc=COLOR_BLACK,
        ec=COLOR_BLACK
    )
    plt.text(3.75, 0.435,
             "Larger datasets decrease accuracy",
             ha="center",
             fontweight="bold",
             rotation=np.degrees(-np.arctan2(0.4, 2.27))
             )

    plt.grid(axis="x")
    pad = grouped_bar_xlim_padding(2, bar_width)
    plt.xlim((xs[0] - pad, xs[-1] + pad))
    plt.xticks(xs, labels=res.columns)
    plt.xlabel("Number of Customers", labelpad=1.3)
    make_score_yaxis("Accuracy")
    plt.legend(loc="upper center", bbox_to_anchor=(LEGEND_X, LEGEND_Y_LOW), ncol=len(res.index), columnspacing=1.5)

    save_plt(get_experiments_path() / "enterprise_tasks_compound" / "tasks_compound_end2end_scale.pdf")

    ####################################################################################################################
    # Task Accuracy scores pipeline vs. standalone
    ####################################################################################################################

    res = pd.read_csv(
        get_experiments_path() / "enterprise_tasks_compound" / "pipeline_standalone.csv",
        index_col="model"
    )
    res.sort_index(key=lambda x: x.map(sort_idx), inplace=True)

    prepare_plt("single_column", "one_row")
    plt.subplots_adjust(**SUBPLOTS_ADJUST)

    xs = [1, 2, 3]
    bar_width = 0.16
    for offset, (model, row) in zip(grouped_bar_offsets(4, bar_width), res.iterrows()):
        # Extract pipeline and standalone values
        pipeline_cols = [col for col in res.columns if "pipeline" in col]
        standalone_cols = [col for col in res.columns if "standalone" in col]
        pipeline_vals = row[pipeline_cols].to_list()
        standalone_vals = row[standalone_cols].to_list()

        # Plot standalone bars
        plt.bar(
            x=[x + offset for x in xs],
            height=standalone_vals,
            width=bar_width - 0.011,  # offset the linewidth
            facecolor="none",  # Transparent fill
            edgecolor=color(model),  # Colored border
            linewidth=1,  # Border thickness
            # hatch=hatch(model),
            # label="Standalone"
        )

        # Plot pipeline bars
        plt.bar(
            x=[x + offset for x in xs],
            height=pipeline_vals,
            width=bar_width,
            color=color(model),
            hatch=hatch(model),
            label=text(model)
        )

        # Overlay standalone stars
        plt.scatter(
            x=[x + offset for x in xs[:1]],
            y=standalone_vals[:1],
            color=COLOR_BLACK,
            edgecolor=COLOR_BLACK,
            s=15,
            zorder=5,
            marker="_"
        )
        plt.scatter(
            x=[x + offset for x in xs[1:]],
            y=standalone_vals[1:],
            color=COLOR_BLACK,
            edgecolor=COLOR_BLACK,
            s=15,
            zorder=5,
            marker=11
        )

        # Add text labels for both pipeline bars and standalone points
        for i, (x, p_val, s_val) in enumerate(zip(xs, pipeline_vals, standalone_vals)):
            s = score(p_val)
            if s not in ["0.84", "0.87"] and not (s == "0.72" and i == len(xs) - 1):
                # Pipeline score label
                plt.text(
                    x=x + offset,
                    y=p_val + VALUE_PAD,
                    s=score(p_val),
                    color=color(model),
                    ha="center",
                    fontsize=VALUE_FONT_SIZE
                )
            # Standalone score label
            plt.text(
                x=x + offset,
                y=s_val + VALUE_PAD,
                s=f"{score(s_val)}",
                color=color(model),
                ha="center",
                fontsize=VALUE_FONT_SIZE
            )

    plt.grid(axis="x")
    pad = grouped_bar_xlim_padding(4, bar_width)
    plt.xlim((xs[0] - pad, xs[-1] + pad))

    # Custom legend handles
    pipeline_legend = Patch(
        facecolor="gray",
        edgecolor="gray",
        label="Pipeline",
        linewidth=1
    )

    standalone_legend = Patch(
        facecolor="none",  # Transparent fill
        edgecolor="gray",
        label="Standalone",
        linewidth=1,
        # hatch=7
    )

    labels_dict = {
        "sm_pipeline": "Schema Matching",
        "em_pipeline": "Entity Matching",
        "di_pipeline": "Data Integration",
    }
    plt.xticks(xs, labels=[labels_dict[col] for col in pipeline_cols])
    make_score_yaxis("Task Accuracy")

    # Get existing handles and labels for model entries
    model_handles, model_labels = plt.gca().get_legend_handles_labels()

    # Top row: Pipeline and Standalone
    first_legend = plt.legend(
        handles=[pipeline_legend, standalone_legend],
        loc="upper center",
        bbox_to_anchor=(0.5, LEGEND_Y + 0.02),
        ncol=2,
        columnspacing=1.5
    )

    # Second row: Model-specific labels
    second_legend = plt.legend(
        handles=model_handles,
        labels=model_labels,
        loc="lower center",
        ncol=len(model_labels)
    )

    # Ensure both legends are shown
    plt.gca().add_artist(first_legend)

    plt.text(
        (xs[-2] + xs[-1]) / 2,
        TOP_TEXT_Y,
        "▼ Errors propagate in task pipeline",
        ha="center",
        fontweight="bold"
    )

    plt.legend(
        loc="upper center",
        bbox_to_anchor=(LEGEND_X, LEGEND_Y_LOW),
        ncol=len(model_labels) + 2
    )

    save_plt(get_experiments_path() / "enterprise_tasks_compound" / "tasks_compound_pipeline_standalone.pdf")

    ####################################################################################################################
    # Task Accuracy scores standalone
    ####################################################################################################################

    res = pd.read_csv(
        get_experiments_path() / "enterprise_tasks_compound" / "pipeline_standalone.csv",
        index_col="model"
    )
    res.sort_index(key=lambda x: x.map(sort_idx), inplace=True)

    prepare_plt("single_column", "one_row")
    plt.subplots_adjust(**SUBPLOTS_ADJUST)

    xs = [1, 2, 3]
    bar_width = 0.16
    for offset, (model, row) in zip(grouped_bar_offsets(4, bar_width), res.iterrows()):
        # Extract pipeline and standalone values
        pipeline_cols = [col for col in res.columns if "pipeline" in col]
        standalone_cols = [col for col in res.columns if "standalone" in col]
        pipeline_vals = row[pipeline_cols].to_list()
        standalone_vals = row[standalone_cols].to_list()

        # Plot standalone bars
        plt.bar(
            x=[x + offset for x in xs],
            height=standalone_vals,
            width=bar_width - 0.011,  # offset the linewidth
            facecolor="none",  # Transparent fill
            edgecolor=color(model),  # Colored border
            linewidth=1,  # Border thickness
            # hatch=hatch(model),
            # label="Standalone"
        )

        # Add text labels for both pipeline bars and standalone points
        for i, (x, p_val, s_val) in enumerate(zip(xs, pipeline_vals, standalone_vals)):
            # Standalone score label
            plt.text(
                x=x + offset,
                y=s_val + VALUE_PAD,
                s=f"{score(s_val)}",
                color=color(model),
                ha="center",
                fontsize=VALUE_FONT_SIZE
            )

    plt.grid(axis="x")
    pad = grouped_bar_xlim_padding(4, bar_width)
    plt.xlim((xs[0] - pad, xs[-1] + pad))

    # Custom legend handles
    pipeline_legend = Patch(
        facecolor="gray",
        edgecolor="gray",
        label="Pipeline",
        linewidth=1
    )

    standalone_legend = Patch(
        facecolor="none",  # Transparent fill
        edgecolor="gray",
        label="Standalone",
        linewidth=1,
        # hatch=7
    )

    labels_dict = {
        "sm_pipeline": "Schema Matching",
        "em_pipeline": "Entity Matching",
        "di_pipeline": "Data Integration",
    }
    plt.xticks(xs, labels=[labels_dict[col] for col in pipeline_cols])
    make_score_yaxis("Task Accuracy")

    # Get existing handles and labels for model entries
    model_handles, model_labels = plt.gca().get_legend_handles_labels()

    # Top row: Pipeline and Standalone
    first_legend = plt.legend(
        handles=[pipeline_legend, standalone_legend],
        loc="upper center",
        bbox_to_anchor=(0.5, LEGEND_Y + 0.02),
        ncol=2,
        columnspacing=1.5
    )

    # Ensure both legends are shown
    plt.gca().add_artist(first_legend)

    plt.legend(
        loc="upper center",
        bbox_to_anchor=(LEGEND_X, LEGEND_Y_LOW),
        ncol=len(model_labels) + 2
    )

    save_plt(get_experiments_path() / "enterprise_tasks_compound" / "tasks_compound_pipeline_standalone_partial.pdf")


if __name__ == "__main__":
    main()
