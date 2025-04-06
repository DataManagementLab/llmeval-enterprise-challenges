import logging

import attrs
import hana_ml.dataframe as hdf
import hydra
from hydra.core.config_store import ConfigStore

from llms4de.data import get_experiments_path, dump_json

logger = logging.getLogger(__name__)


@attrs.define
class Config:
    user: str = ""
    system: str = ""
    port: str = ""
    num_tables: int = 10_000


ConfigStore.instance().store(name="config", node=Config)


@hydra.main(version_base=None, config_name="config")
def main(cfg: Config) -> None:
    user = cfg.user  # change this to your own user for the customer system
    conn = hdf.ConnectionContext(address=cfg.system, port=cfg.port, user=user)

    # crawl random table names
    sql_statement_names = f'select TABNAME from SAPSR3.DD02L where TABCLASS = \'TRANSP\' ORDER BY RAND()'
    all_table_names = select_data_SQL(sql_statement=sql_statement_names, conn=conn).values.flatten().tolist()
    logger.info(f"total number of tables: {len(all_table_names)}")

    num_cells = 0
    num_tables = 0
    for table_name in all_table_names[:cfg.num_tables]:  # query only cfg.num_tables tables
        logger.info(f"determine cells for `{table_name}`")
        sql_statement_num_rows = f'select count(*) from "SAPSR3"."{table_name}"'
        df_num_rows = select_data_SQL(sql_statement=sql_statement_num_rows, conn=conn)
        num_rows = df_num_rows.values.flatten().tolist()

        sql_statement_num_cols = f'select COUNT(*) FROM "SYS"."TABLE_COLUMNS" where "SYS"."TABLE_COLUMNS"."TABLE_NAME"= \'{table_name}\''
        df_num_cols = select_data_SQL(sql_statement=sql_statement_num_cols, conn=conn)
        num_cols = df_num_cols.values.flatten().tolist()

        num_cells += num_rows[0] * num_cols[0]
        num_tables += 1

    dump_json(
        {
            "total_number_of_tables": len(all_table_names),
            "subset_num_tables": num_tables,
            "subset_num_cells": num_cells
        },
        get_experiments_path() / "costs_imdb_wikipedia_enterprisetables" / "total_num_cells.json"
    )


def select_data_SQL(sql_statement, conn):
    df = conn.sql(sql_statement)
    df = df.collect()
    return df


if __name__ == "__main__":
    main()
