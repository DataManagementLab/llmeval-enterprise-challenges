import logging

import attrs
import hydra
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from hydra.core.config_store import ConfigStore
from matplotlib.patches import Patch

from llms4de.data import load_json, get_task_dir

logger = logging.getLogger(__name__)


@attrs.define
class Config:
    pass


ConfigStore.instance().store(name="config", node=Config)


# -----------------------------
# 2. Define a Function to Count Statuses
# -----------------------------
# This function takes a JSON structure (a dict) and returns a new dict counting
# how many times each status occurs.


def count_statuses(result):
    counts = {}
    for key, value in result.items():
        status = value.get('status')
        if status:
            counts[status] = counts.get(status, 0) + 1
    return counts

#config_path="../../config/text2signal", config_name="config.yaml"
@hydra.main(version_base=None, config_name="config")
def main(cfg: Config) -> None:
    # load all results
    all_exp_paths = list(
        sorted(get_task_dir("signal_validation").glob("signavio/experiments/enterprise-knowledge-text2signal*/")))
    #print(all_exp_paths)
    all_res = pd.DataFrame({"path": all_exp_paths})
    #print("PATH", all_res["path"])
    all_res["cfg"] = all_res["path"].apply(lambda p: load_json(p / "results" / "config.cfg"))

    print("LL", all_res[cfg])
    all_res["model"] = all_res["cfg"].apply(lambda cfg: cfg["model"])
    all_res["mode"] = all_res["cfg"].apply(lambda cfg: cfg["mode"])
    #  all_res["errors"] = all_res["path"].apply(lambda p: load_json(p / "results" / "errors.json"))
    all_res["results"] = all_res["path"].apply(lambda p: load_json(p / "results" / "results.json"))  #
    print(all_res)
    all_res.to_csv("experiments/enterprise_knowledge_text2signal/all_signal_results.csv")

    # -----------------------------
    # 3. Expand the 'results' Column into Separate Count Columns
    # -----------------------------
    # Apply the counting function and expand the resulting dictionary into columns.
    counts_series = all_res['results'].apply(count_statuses)
    counts_df = counts_series.apply(pd.Series).fillna(0)  # fill missing statuses with 0

    # Merge with the original DataFrame (keeping 'path' and 'cfg' for later, though they are ignored).
    df_expanded = pd.concat([all_res.drop(columns='results'), counts_df], axis=1)

    # -----------------------------
    # 4. Identify Status Columns (Ignoring 'model', 'mode', 'path', and 'cfg')
    # -----------------------------
    status_cols = [col for col in df_expanded.columns if col not in ['model', 'mode', 'path', 'cfg']]

    # -----------------------------
    # 5. Define x-Positions Grouped by Model
    # -----------------------------
    # Sort by model and mode.
    df_expanded = df_expanded.sort_values(['model', 'mode'])
    bar_positions = []  # x position for each (model, mode) bar
    group_centers = {}  # center x position of each model group for labeling
    current_x = 0

    for model, group in df_expanded.groupby('model'):
        n = len(group)
        positions = np.arange(current_x, current_x + n)
        group_centers[model] = np.mean(positions)
        bar_positions.extend(positions)
        current_x += n + 1  # add a gap between different model groups

    # -----------------------------
    # 6. Create a Color Mapping for Each Status
    # -----------------------------
    cmap = cm.get_cmap('Set1', len(status_cols))
    status_colors = {status: cmap(i) for i, status in enumerate(status_cols)}

    # -----------------------------
    # 7. Plot the Stacked Bar Chart with Annotations
    # -----------------------------
    fig, ax = plt.subplots(figsize=(12, 10))  # Increased figure size

    for i, (_, row) in enumerate(df_expanded.iterrows()):
        x = bar_positions[i]
        bottom = 0
        for status in status_cols:
            try:
                count = int(row[status])
            except Exception:
                count = 0
            if count > 0:
                # Draw the bar segment
                ax.bar(x, count, bottom=bottom, color=status_colors[status], width=0.8)
                # Annotate the segment with its absolute number (centered vertically)
                ax.text(x, bottom + count / 2, str(count),
                        ha='center', va='center', fontsize=10, color='white')
                bottom += count

    # Set x-axis ticks to show the 'mode' for each bar.
    ax.set_xticks(bar_positions)
    ax.set_xticklabels(df_expanded['mode'])

    # Retrieve y-limits for proper placement of model labels.
    ymin, ymax = ax.get_ylim()
    # Place the model names below the chart.
    for model, center in group_centers.items():
        ax.text(center, ymin - 0.05 * (ymax - ymin), model,
                ha='center', va='top', fontsize=12, fontweight='bold',
                transform=ax.get_xaxis_transform())

    # Adjust the y-axis upper limit to provide extra space.
    max_stack = df_expanded[status_cols].sum(axis=1).max()
   # ax.set_ylim(0, max_stack * 1.2)

    # Create the legend and move it further to the right.
    legend_elements = [Patch(facecolor=status_colors[s], label=s) for s in status_cols]
    ax.legend(handles=legend_elements, title="Status", bbox_to_anchor=(1.25, 1), loc='upper left')

    ax.set_ylabel("Count", fontsize=12)
    ax.set_title("Stacked Bar Chart with Absolute Numbers,\nLegend and Model Names", fontsize=14)

    # Adjust subplot parameters:
    # - Increase the bottom margin so model names are visible.
    # - Reduce the width of the plotting area so that the legend has more space.
    plt.subplots_adjust(bottom=0.2, right=0.65)
    # Use tight_layout with a rect parameter to reserve space for the legend.
    #  plt.tight_layout(rect=[0, 0, 0.65, 1])
    plt.show()


#  save_plt(get_experiments_path() / "enterprise_knowledge_text2signal" / "table.pdf")


if __name__ == "__main__":
    main()
