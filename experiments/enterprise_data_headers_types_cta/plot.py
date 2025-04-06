import logging

import attrs
import hydra
import pandas as pd
from hydra.core.config_store import ConfigStore
from matplotlib import pyplot as plt

from llms4de.data import get_experiments_path, dump_str
from llms4de.plotting.colors import sort_idx, color, hatch
from llms4de.plotting.plot import prepare_plt, grouped_bar_offsets, VALUE_PAD, VALUE_FONT_SIZE, \
    grouped_bar_xlim_padding, make_score_yaxis, LEGEND_X, LEGEND_Y, save_plt
from llms4de.plotting.texts import text, score

logger = logging.getLogger(__name__)


@attrs.define
class Config:
    pass


ConfigStore.instance().store(name="config", node=Config)


@hydra.main(version_base=None, config_name="config")
def main(cfg: Config) -> None:
    ####################################################################################################################
    # F1 scores with headers vs. without headers
    ####################################################################################################################
    table = pd.read_csv(
        get_experiments_path() / "enterprise_data_headers_types_cta" / "f1_scores_column_headers.csv",
        header=[0, 1],
        index_col=0
    )
    table.sort_index(key=lambda x: x.map(sort_idx), inplace=True)
    table.sort_index(axis=1, level=0, ascending=False, inplace=True)
    table.sort_index(axis=1, level=1, key=lambda x: x.map(sort_idx), inplace=True)

    latex_table = table.copy()
    latex_table = latex_table.map(score)
    latex_table.index = latex_table.index.map(text)

    latex = latex_table.to_latex()
    dump_str(latex, get_experiments_path() / "enterprise_data_headers_types_cta" / "f1_scores_column_headers.tex")

    table = pd.read_csv(
        get_experiments_path() / "enterprise_data_headers_types_cta" / "f1_scores_column_headers.csv",
        header=[0, 1],
        index_col=0
    )
    table_sap = pd.read_csv(
        get_experiments_path() / "enterprise_data_headers_types_cta" / "f1_scores_column_headers_sap.csv",
        header=[0, 1],
        index_col=0
    )
    for column in table_sap.columns:
        table[column] = table_sap[column]
    table.sort_index(key=lambda x: x.map(sort_idx), inplace=True)
    # table.sort_index(axis=1, level=0, key=lambda x: x.map(sort_idx), ascending=False, inplace=True)
    # table.sort_index(axis=1, level=1, key=lambda x: x.map(sort_idx), inplace=True)

    for HEADERS in ["with-headers", "without-headers"]:
        prepare_plt("single_column", "one_row")
        res = table[[(dataset, header) for dataset, header in table.columns if header == HEADERS]]
        res.columns = [dataset for dataset, header in res.columns]

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

        plt.xticks(xs, labels=[text(col) for col in res.columns])
        make_score_yaxis("F1 Score")
        plt.legend(loc="upper center", bbox_to_anchor=(LEGEND_X, LEGEND_Y), ncol=len(res.index))

        save_plt(get_experiments_path() / "enterprise_data_headers_types_cta" / f"f1_scores_{HEADERS}.pdf")

    ####################################################################################################################
    # F1 scores by data type
    ####################################################################################################################
    table = pd.read_csv(
        get_experiments_path() / "enterprise_data_headers_types_cta" / "f1_scores_by_data_types.csv",
        header=[0, 1],
        index_col=0
    )
    table.sort_index(key=lambda x: x.map(sort_idx), inplace=True)
    # table.sort_index(axis=1, level=0, ascending=False, inplace=True)
    table.sort_index(axis=1, level=1, key=lambda x: x.map(sort_idx), inplace=True)

    latex_table = table.copy()
    latex_table = latex_table.map(score)
    latex_table.index = latex_table.index.map(text)

    latex = latex_table.to_latex()
    dump_str(latex, get_experiments_path() / "enterprise_data_headers_types_cta" / "f1_scores_by_data_types.tex")


if __name__ == "__main__":
    main()
