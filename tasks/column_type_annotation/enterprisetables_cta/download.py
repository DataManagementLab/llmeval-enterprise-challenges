import logging

import hana_ml.dataframe as hdf
import hydra
from omegaconf import DictConfig

from llms4de.data import get_download_dir, dump_json, dump_cfg
from llms4de.evaluation.inspection import compute_cell_level_sparsity

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="../../../config/column_type_annotation", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    assert cfg.dataset.dataset_name == "enterprisetables_cta", "This script is dataset-specific."
    download_dir = get_download_dir(cfg.task_name, cfg.dataset.dataset_name, clear=True)

    num_rows_export = cfg.dataset.num_rows_export
    user = cfg.dataset.user  # change this to your own user for the customer system
    conn = hdf.ConnectionContext(address=cfg.dataset.system, port=cfg.dataset.port, user=user)

    stats = {
        "num_tables": None,
        "num_cols": [],
        "num_rows": [],
        "sparsity": [],
        "num_numerical_cols": 0,
        "num_non_numerical_cols": 0,
        "data_type_mapping": {},
        "data_types": []
    }
    logger.info(f"Processing tables: {cfg.dataset.tables}")
    for table_name in cfg.dataset.tables:
        logger.info(f"Processing table: {table_name}")

        sql_statement_columns = f'select DISTINCT "SYS"."TABLE_COLUMNS"."COLUMN_NAME", "SYS"."TABLE_COLUMNS"."DATA_TYPE_NAME", "SAPSR3"."DD03M"."DDTEXT", "SAPSR3"."DD03M"."FIELDNAME" FROM "SYS"."TABLE_COLUMNS" join "SAPSR3"."DD03M" on "SYS"."TABLE_COLUMNS"."COLUMN_NAME" = "SAPSR3"."DD03M"."FIELDNAME" and "SYS"."TABLE_COLUMNS"."TABLE_NAME" = "SAPSR3"."DD03M"."TABNAME" where "SYS"."TABLE_COLUMNS"."TABLE_NAME"= \'{table_name}\' and "SAPSR3"."DD03M"."DDLANGUAGE" = \'E\''
        sql_statement_data = f'select * from "SAPSR3"."{table_name}" order by rand() limit {num_rows_export}'  # retrieves random rows
        sql_statement_num_rows = f'select COUNT(*) from "SAPSR3"."{table_name}"'

        df = select_data_SQL(sql_statement=sql_statement_columns, conn=conn)
        df_data = select_data_SQL(sql_statement=sql_statement_data, conn=conn)
        df_num_rows = select_data_SQL(sql_statement=sql_statement_num_rows, conn=conn)

        stats["num_rows"].append(df_num_rows.to_json())
        stats["num_cols"].append(len(df_data.columns))

        # creating new df with NaN value for sparsity analysis
        df_nan = df_data
        nan_value = float("NaN")
        df_nan.replace("", nan_value, inplace=True)
        stats["sparsity"].append(compute_cell_level_sparsity(df_nan))

        df_data.to_csv(download_dir / f"{table_name}.csv", index=False)

        numerical_types = ["REAL", "SMALLINT", "INTEGER", "TINYINT", "SMALLDECIMAL", "DOUBLE", "BIGINT", "DECIMAL"]

        all_numerical_cols = []
        all_textual_cols = []
        mapping_header_to_column_type = {}

        for ind in df.index:
            mapping_header_to_column_type[df["COLUMN_NAME"][ind]] = df["DDTEXT"][ind]

            stats["data_types"].append(df["DATA_TYPE_NAME"][ind])
            if df["DATA_TYPE_NAME"][ind] in numerical_types:
                # all_numerical_cols.append(df["DDTEXT"][ind])
                stats["data_type_mapping"][df["DATA_TYPE_NAME"][ind]] = "numerical"
            else:
                # all_textual_cols.append(df["DDTEXT"][ind])
                stats["data_type_mapping"][df["DATA_TYPE_NAME"][ind]] = "non-numerical"

        # use pandas to determine data types
        for col, dtype in zip(df_data.columns.to_list(), df_data.dtypes.to_list()):
            if dtype.kind in ("i", "f", "u"):
                if col in mapping_header_to_column_type.keys():
                    all_numerical_cols.append(mapping_header_to_column_type[col])
                else:
                    logger.warning(f"column `{col}` has no column type, so no data type is saved")
            else:
                if col in mapping_header_to_column_type.keys():
                    all_textual_cols.append(mapping_header_to_column_type[col])
                else:
                    logger.warning(f"column `{col}` has no column type, so no data type is saved")

        all_column_types_by_data_type = {
            "numerical": all_numerical_cols,
            "non-numerical": all_textual_cols
        }
        stats["num_numerical_cols"] += len(all_numerical_cols)
        stats["num_non_numerical_cols"] += len(all_textual_cols)
        all_column_types_by_data_type["non-numerical"].append(None)
        dump_json(all_column_types_by_data_type, download_dir / f"{table_name}_metadata.json")
        dump_json(mapping_header_to_column_type, download_dir / f"{table_name}_mapping.json")

    dump_json(stats, download_dir / "stats.json")
    dump_cfg(cfg, download_dir / "config.cfg")


def select_data_SQL(sql_statement, conn):
    df = conn.sql(sql_statement)
    df = df.collect()
    return df


if __name__ == "__main__":
    main()
