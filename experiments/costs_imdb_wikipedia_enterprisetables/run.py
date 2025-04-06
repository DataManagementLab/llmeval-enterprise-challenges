import collections
import logging

import attrs
import datasets
import hana_ml.dataframe as hdf
import hydra
import pandas as pd
import tiktoken
from hydra.core.config_store import ConfigStore

from llms4de.data import get_download_dir, load_str, get_experiments_path, dump_json
from llms4de.model._openai import openai_model

logger = logging.getLogger(__name__)


@attrs.define
class Config:
    models: list[str] = ["gpt-4o-mini-2024-07-18", "gpt-4o-2024-08-06", "o1-2024-12-17"]
    tsv_chunk_len: int = 128_000
    num_threads: int = 16
    user: str = ""
    system: str = ""
    port: str = ""
    num_rows_export: str = "20"
    num_tables: int = 1000


ConfigStore.instance().store(name="config", node=Config)


@hydra.main(version_base=None, config_name="config")
def main(cfg: Config) -> None:
    measure_imdb(cfg)
    measure_wikipedia(cfg)
    measure_enterprisetables(cfg)
    measure_random_enterprisetables(cfg)


def measure_imdb(cfg: Config) -> None:
    logger.info("measure imdb dataset")
    download_dir = get_download_dir("other_datasets", "imdb")
    table_paths = list(sorted(download_dir.glob("*.tsv")))

    num_bytes = 0
    tokens = collections.Counter()
    cost = {}
    for model in cfg.models:
        logger.info(f"processing with model `{model}`")
        num_bytes = 0
        for path in table_paths:
            logger.info(f"determine tokens for `{path.name}`")
            encoding = tiktoken.encoding_for_model(model)
            table_str = load_str(path)
            table_chunks = [table_str[0 + i:cfg.tsv_chunk_len + i] for i in range(0, len(table_str), cfg.tsv_chunk_len)]
            num_bytes += sum(map(lambda s: len(s.encode("utf-8")), table_chunks))
            tokens[model] += sum(map(len, encoding.encode_batch(table_chunks, num_threads=cfg.num_threads)))
        cost[model] = determine_cost(tokens[model], model)

    results = make_result_dataframe(num_bytes, tokens, cost)
    results.to_csv(get_experiments_path() / "costs_imdb_wikipedia_enterprisetables" / "costs_imdb.csv")


def measure_wikipedia(cfg: Config) -> None:
    logger.info("measure wikipedia")
    download_dir = get_download_dir("other_datasets", "wikipedia")

    dataset = datasets.load_dataset("wikipedia", "20220301.en", cache_dir=str(download_dir))
    dataset = dataset["train"]
    texts = dataset["text"]

    num_bytes = sum(map(lambda s: len(s.encode("utf-8")), texts))
    tokens = {}
    cost = {}
    for model in cfg.models:
        logger.info(f"processing with model `{model}`")
        encoding = tiktoken.encoding_for_model(model)
        tokens[model] = sum(map(len, encoding.encode_batch(texts, num_threads=cfg.num_threads)))
        cost[model] = determine_cost(tokens[model], model)

    results = make_result_dataframe(num_bytes, tokens, cost)
    results.to_csv(get_experiments_path() / "costs_imdb_wikipedia_enterprisetables" / "costs_wikipedia.csv")


def measure_enterprisetables(cfg: Config) -> None:
    logger.info("measure enterprisetables dataset")
    download_dir = get_download_dir("column_type_annotation", "enterprisetables_cta")
    table_paths = list(sorted(download_dir.glob("*.csv")))

    num_bytes = 0
    tokens = collections.Counter()
    cost = {}
    for model in cfg.models:
        logger.info(f"processing with model `{model}`")
        num_bytes = 0
        for path in table_paths:
            logger.info(f"determine tokens for `{path.name}`")
            encoding = tiktoken.encoding_for_model(model)
            table_str = load_str(path)
            table_chunks = [table_str[0 + i:cfg.tsv_chunk_len + i] for i in range(0, len(table_str), cfg.tsv_chunk_len)]
            num_bytes += sum(map(lambda s: len(s.encode("utf-8")), table_chunks))
            tokens[model] += sum(map(len, encoding.encode_batch(table_chunks, num_threads=cfg.num_threads)))
        cost[model] = determine_cost(tokens[model], model)

    results = make_result_dataframe(num_bytes, tokens, cost)
    results.to_csv(get_experiments_path() / "costs_imdb_wikipedia_enterprisetables" / "costs_enterprisetables.csv")


def measure_random_enterprisetables(cfg: Config) -> None:
    logger.info("measure random enterprisetables dataset")

    user = cfg.user  # change this to your own user for the customer system
    conn = hdf.ConnectionContext(address=cfg.system, port=cfg.port, user=user)

    # crawl random table names
    sql_statement_names = f'select TABNAME  from SAPSR3.DD02L where TABCLASS = \'TRANSP\' ORDER BY RAND() LIMIT {cfg.num_tables}'
    random_table_names = select_data_SQL(sql_statement=sql_statement_names, conn=conn).values.flatten().tolist()

    num_bytes = 0
    num_cells = 0
    tokens = collections.Counter()
    cost = {}
    for model in cfg.models:
        logger.info(f"processing with model `{model}`")
        num_bytes = 0
        num_cells = 0

        for table_name in random_table_names:
            logger.info(f"determine tokens for `{table_name}`")
            sql_statement_data = f'select * from "SAPSR3"."{table_name}" order by rand() limit {cfg.num_rows_export}'
            df_data = select_data_SQL(sql_statement=sql_statement_data, conn=conn)
            nan_value = float("NaN")
            df_data.replace("", nan_value, inplace=True)
            table_str = df_data.to_csv(index=False)
            encoding = tiktoken.encoding_for_model(model)
            num_cells += df_data.size + len(df_data.columns)  # treat headers as "normal" cells
            table_chunks = [table_str[0 + i:cfg.tsv_chunk_len + i] for i in range(0, len(table_str), cfg.tsv_chunk_len)]
            num_bytes += sum(map(lambda s: len(s.encode("utf-8")), table_chunks))
            tokens[model] += sum(map(len, encoding.encode_batch(table_chunks, num_threads=cfg.num_threads)))
        cost[model] = determine_cost(tokens[model], model)

    results = make_result_dataframe(num_bytes, tokens, cost)
    results.to_csv(
        get_experiments_path() / "costs_imdb_wikipedia_enterprisetables" / "costs_random_enterprisetables.csv")
    dump_json(
        {"number_of_cells": num_cells},
        get_experiments_path() / "costs_imdb_wikipedia_enterprisetables" / "num_cells.json"
    )


def make_result_dataframe(num_bytes: int, tokens: dict[str, int], cost: dict[str, float]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            tokens,
            cost,
            {model: num_bytes for model in tokens.keys()},
            {model: t / num_bytes for model, t in tokens.items()},
            {model: (c / num_bytes) * 1_000_000_000 for model, c in cost.items()}
        ],
        index=["tokens", "cost", "bytes", "tokens per byte", "cost per GB"]
    )


def determine_cost(tokens: int, model: str) -> float:
    return tokens * openai_model(model)["cost_per_1k_input_tokens"] / 1000


def select_data_SQL(sql_statement, conn):
    df = conn.sql(sql_statement)
    df = df.collect()
    return df


if __name__ == "__main__":
    main()
