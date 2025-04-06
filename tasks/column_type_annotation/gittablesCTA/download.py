import io
import json
import logging
import os
import pathlib
import shutil
import zipfile

import hydra
import pandas as pd
import requests
import tqdm
from omegaconf import DictConfig

from llms4de.data import get_download_dir, download_url, dump_cfg

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="../../../config/column_type_annotation", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    assert cfg.dataset.dataset_name == "gittablesCTA", "This script is dataset-specific."
    download_dir = get_download_dir(cfg.task_name, cfg.dataset.dataset_name, clear=True)

    logger.info("Downloading the data for GitTablesCTA.")
    download_url(url=cfg.dataset.url, path=download_dir, unzip=True)
    with zipfile.ZipFile(download_dir / "tables.zip", "r") as file:
        file.extractall(path=download_dir)
    os.remove(download_dir / "tables.zip")

    logger.info("Downloading the original GitTables dataset.")
    with open(pathlib.Path(os.path.dirname(__file__)).resolve() / "zenodo_csv_meta.json", "r",
              encoding="utf-8") as file:
        csv_meta = json.load(file)

    for file in tqdm.tqdm(csv_meta["files"], f"download csv files"):
        url = file["links"]["self"]
        logger.info(f"Download and extract {url}")
        response = requests.get(url)
        zip_data = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_data, "r") as zip_ref:
            zip_ref.extractall(download_dir / "gittables_1m_csv" / file["key"][:-4])

    logger.info("Augment GitTablesCTA tables with column headers from the original GitTables dataset.")
    shutil.move(download_dir / "tables", download_dir / "tables_without_column_names")
    os.mkdir(download_dir / "tables")

    # load all GitTablesCTA tables
    cta_tables = sorted(os.listdir(download_dir / "tables_without_column_names"))
    cta_dataframes = []
    for i, cta_table in enumerate(cta_tables):
        df = pd.read_csv(download_dir / "tables_without_column_names" / cta_table)
        df = df.drop(columns=["Unnamed: 0"])
        df.columns = ["empty"] * len(df.columns)
        cta_dataframes.append((i, df))

    cta_lengths = {(len(x[1]), len(x[1].columns)): [] for x in cta_dataframes}
    for i, c in cta_dataframes:
        cta_lengths[(len(c), len(c.columns))].append((i, c))

    # gather matches of GitTables CTA tables and original GitTables tables
    matches = {}
    for gittables_folder in os.listdir(download_dir / "gittables_1m_csv"):
        logger.info(f"%%%%%%%%%%%%%%%%%% {gittables_folder} %%%%%%%%%%%%%%%%%%%%%%%")
        folder_tables = os.listdir(download_dir / "gittables_1m_csv" / gittables_folder)
        for table in tqdm.tqdm(folder_tables):
            remove = []
            table_path = download_dir / "gittables_1m_csv" / pathlib.Path(gittables_folder) / pathlib.Path(table)
            try:
                df = pd.read_csv(table_path)
            except:
                continue
            if (len(df), len(df.columns)) in cta_lengths.keys():
                # replace all column names with empty
                df.columns = ["empty"] * len(df.columns)
                for i, cta_df in cta_lengths[(len(df), len(df.columns))]:
                    if df.equals(cta_df):
                        matches[i] = (table_path, cta_tables[i])
                        remove.append(((len(df), len(df.columns)), (i, cta_df)))
                for key, value in remove:
                    cta_dataframes.remove(value)
                    cta_lengths[key].remove(value)
            if len(cta_dataframes) == 0:
                break
        logger.info(f"Still looking for {len(cta_dataframes)} tables")
        if len(cta_dataframes) == 0:
            break

    # copy tables for matches
    matches_formatted_local = [{"table_idx": key, "gittables_all": value[0], "gittables_cta": value[1]} for key, value
                               in matches.items()]
    for x in matches_formatted_local:
        orig_file = x["gittables_all"]
        table_name = str(orig_file).split("1m_csv/")[-1].replace("/", "---")
        new_filename = str(pathlib.Path(x["gittables_cta"]).stem) + "---" + table_name
        new_filename = new_filename[:14] + ".csv"
        shutil.copyfile(orig_file, download_dir / "tables" / pathlib.Path(new_filename))

    # write "tables-have-no-index-column.txt" indicator file
    with open(download_dir / "tables-have-no-index-column.txt", "w", encoding="utf-8") as file:
        file.write("...")

    # delete original GitTables dataset
    shutil.rmtree(download_dir / "gittables_1m_csv")
    dump_cfg(cfg, download_dir / "config.cfg")


if __name__ == "__main__":
    main()
