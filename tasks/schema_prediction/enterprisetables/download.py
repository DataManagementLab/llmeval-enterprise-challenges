import logging

import hana_ml.dataframe as hdf
import hydra
from omegaconf import DictConfig

from llms4de.data import get_download_dir, dump_str

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="../../../config/schema_prediction", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    assert cfg.dataset.dataset_name == "enterprisetables", "This script is dataset-specific."
    download_dir = get_download_dir(cfg.task_name, cfg.dataset.dataset_name, clear=True)

    user = cfg.dataset.user  # change this to your own user for the customer system
    conn = hdf.ConnectionContext(address=cfg.dataset.system, port=cfg.dataset.port, user=user)
    table_names = []
    if cfg.dataset.random_tables:
        sql_statement_names = f'select TABNAME  from SAPSR3.DD02L where TABCLASS = \'TRANSP\' AND TABNAME NOT LIKE \'%/%\' AND TABNAME NOT LIKE \'Z%\' ORDER BY RAND() LIMIT {cfg.dataset.no_extract_tablenames}'
        df_names1 = select_data_SQL(sql_statement=sql_statement_names, conn=conn)
        sql_statement_names = f'select TABNAME  from SAPSR3.DD02L where TABCLASS = \'TRANSP\' AND TABNAME NOT LIKE \'%/%\' AND TABNAME LIKE \'Z%\' ORDER BY RAND() LIMIT {cfg.dataset.no_extract_tablenames}'
        df_names2 = select_data_SQL(sql_statement=sql_statement_names, conn=conn)

        table_names = df_names1.values.flatten().tolist()
        table_names += df_names2.values.flatten().tolist()

        print(table_names)
        print(cfg.dataset.tables)
    else:
        table_names = cfg.dataset.tables

    for table_name in table_names:
        logger.info(f"Processing table: {table_name}")

        #     sql_statement_columns = f'select DISTINCT "SYS"."TABLE_COLUMNS"."COLUMN_NAME", "SYS"."TABLE_COLUMNS"."DATA_TYPE_NAME", "SAPSR3"."DD03M"."DDTEXT", "SAPSR3"."DD03M"."FIELDNAME" FROM "SYS"."TABLE_COLUMNS" join "SAPSR3"."DD03M" on "SYS"."TABLE_COLUMNS"."COLUMN_NAME" = "SAPSR3"."DD03M"."FIELDNAME" and "SYS"."TABLE_COLUMNS"."TABLE_NAME" = "SAPSR3"."DD03M"."TABNAME" where "SYS"."TABLE_COLUMNS"."TABLE_NAME"= \'{table_name}\' and "SAPSR3"."DD03M"."DDLANGUAGE" = \'E  \''
        sql_statement_columns = f'select SYS.TABLE_COLUMNS.COLUMN_NAME FROM SYS.TABLE_COLUMNS where SYS.TABLE_COLUMNS.TABLE_NAME= \'{table_name}\''
        df = select_data_SQL(sql_statement=sql_statement_columns, conn=conn)

        dump_str(df.to_json(), download_dir / f"{table_name}_header.json")


def select_data_SQL(sql_statement, conn):
    df = conn.sql(sql_statement)
    df = df.collect()
    return df


if __name__ == "__main__":
    main()
