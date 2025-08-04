import ast
import json
import logging
import os
import random
import statistics
from pathlib import Path

import hydra
import pandas as pd
import tqdm
from omegaconf import DictConfig

from llms4de.data import get_download_dir, get_instances_dir, dump_json, dump_cfg

pd.options.mode.chained_assignment = None  # default='warn'
logger = logging.getLogger(__name__)

_random = random.Random(218411488)


def save_source_rows(invoices_tables: list[pd.DataFrame], invoice_id: int, instance_dir: Path):
    """
    Saves the invoice id row from every dataframe in invoices to disk
    """
    if len(invoices_tables) == 1:
        source_row = invoices_tables[0][invoices_tables[0]["invoice_id"] == invoice_id]
        source_row.drop("invoice_id", axis=1, inplace=True)
        source_row.to_csv(instance_dir / "source_row.csv", index=False)
    elif len(invoices_tables) == 3:
        # BKPF
        invoices_tables[0]["invoice_id"] = invoices_tables[0]["invoice_id"].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        source_row_BKPF = invoices_tables[0][
            invoices_tables[0]["invoice_id"].apply(lambda x: isinstance(x, list) and invoice_id in x)]
        source_row_BKPF.drop("invoice_id", axis=1, inplace=True)
        source_row_BKPF.to_csv(instance_dir / "source_row_BKPF.csv", index=False)
        # BSEG
        invoices_tables[1]["invoice_id"] = invoices_tables[1]["invoice_id"].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        source_row_BSEG = invoices_tables[1][
            invoices_tables[1]["invoice_id"].apply(lambda x: isinstance(x, list) and invoice_id in x)]
        source_row_BSEG.drop("invoice_id", axis=1, inplace=True)
        source_row_BSEG.to_csv(instance_dir / "source_row_BSEG.csv", index=False)
        # KNA
        source_row_KNA = invoices_tables[2].copy()
        source_row_KNA.drop("invoice_id", axis=1, inplace=True)
        source_row_KNA.drop("LAND1", axis=1, inplace=True)
        source_row_KNA.to_csv(instance_dir / "source_row_KNA.csv", index=False)
    else:
        raise NotImplementedError(f"Supporting only 1 or 3 invoice tables ")


@hydra.main(version_base=None, config_path="../../../config/entity_matching", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    assert cfg.dataset.dataset_name == "pay_to_inv", "This script is dataset-specific."
    download_dir = get_download_dir(cfg.task_name, cfg.dataset.dataset_name)
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    # load invoices
    if cfg.dataset.schema_mode in ["descriptive", "opaque"]:
        invoices = [
            pd.read_csv(download_dir / cfg.dataset.perturbation_mode / cfg.dataset.schema_mode / "invoices.csv")]
        payments = pd.read_csv(download_dir / cfg.dataset.perturbation_mode / cfg.dataset.schema_mode / "payments.csv")
    elif cfg.dataset.schema_mode == "multi-table":
        invoices_BKPF = pd.read_csv(
            download_dir / cfg.dataset.perturbation_mode / cfg.dataset.schema_mode / "invoices_BKPF.csv")
        invoices_BSEG = pd.read_csv(
            download_dir / cfg.dataset.perturbation_mode / cfg.dataset.schema_mode / "invoices_BSEG.csv")
        invoices_KNA = pd.read_csv(
            download_dir / cfg.dataset.perturbation_mode / cfg.dataset.schema_mode / "invoices_KNA-1.csv")
        invoices = [invoices_BKPF, invoices_BSEG, invoices_KNA]
        payments = pd.read_csv(
            download_dir / cfg.dataset.perturbation_mode / cfg.dataset.schema_mode / "payments_FEBEP.csv")

    else:
        raise AssertionError(f"Invalid dataset schema_mode `{cfg.dataset.schema_mode}`!")
    matches = pd.read_csv(download_dir / cfg.dataset.perturbation_mode / cfg.dataset.schema_mode / "matches.csv")

    ix = 0
    # save the ground truth
    positive_instances = []
    negative_instances = []

    # loop through all true matches
    all_involved_invoice_ids, all_involved_payment_ids = set(), set()
    all_in_match_invoice_ids, all_in_match_payment_ids = set(), set()
    nums_invoices_in_match, nums_payments_in_match = [], []
    for _, match in tqdm.tqdm(matches.iterrows(),
                              desc=f"{cfg.task_name} - {cfg.dataset.dataset_name} - {cfg.exp_name} - preprocess",
                              total=len(matches.index)):
        if ix >= cfg.limit_instances:
            break

        invoice_ids = json.loads(match["invoice_ids"])
        payment_ids = json.loads(match["payment_ids"])
        nums_invoices_in_match.append(len(invoice_ids))
        nums_payments_in_match.append(len(payment_ids))
        if cfg.dataset.schema_mode == "multi-table":
            payments["payment_id"] = payments["payment_id"].apply(
                lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
            payments["payment_id"] = payments["payment_id"].apply(lambda x: x[0] if isinstance(x, list) else x)
        perturbation_categories = json.loads(match["perturbation_categories"])

        # save match as instance
        for invoice_id in invoice_ids:
            all_involved_invoice_ids.add(invoice_id)
            instance_dir = instances_dir / f"{ix}"
            os.makedirs(instance_dir, exist_ok=True)

            # create a non-matching pair for the invoice
            save_source_rows(invoices_tables=invoices, invoice_id=invoice_id, instance_dir=instance_dir)
            payment_id = _random.choice(list(set(payments["payment_id"].to_list()) - set(payment_ids)))
            target_row = payments[payments["payment_id"] == payment_id]
            target_row.drop("payment_id", axis=1, inplace=True)

            target_row.to_csv(instance_dir / "target_row.csv", index=False)
            dump_json({"rows_match": False, "match_category": match["match_category"],
                       "perturbation_categories": perturbation_categories, "kind": "invoice_driven"},
                      instance_dir / "ground_truth.json")
            negative_instances.append(ix)
            ix += 1

            # loop through all payment ids of the match (is only 1 for 1:1 row matches)
            for payment_id in payment_ids:
                all_involved_payment_ids.add(payment_id)
                all_in_match_invoice_ids.add(invoice_id)
                all_in_match_payment_ids.add(payment_id)
                instance_dir = instances_dir / f"{ix}"
                os.makedirs(instance_dir, exist_ok=True)

                save_source_rows(invoices_tables=invoices, invoice_id=invoice_id, instance_dir=instance_dir)
                target_row = payments[payments["payment_id"] == payment_id]
                target_row.drop("payment_id", axis=1, inplace=True)

                target_row.to_csv(instance_dir / "target_row.csv", index=False)
                dump_json({"rows_match": True, "match_category": match["match_category"],
                           "perturbation_categories": perturbation_categories, "kind": "match",
                           "match_id": match["match_id"]},
                          instance_dir / "ground_truth.json")
                positive_instances.append(ix)
                ix += 1

        # create a non-matching pair for each of the payment in the match
        for payment_id in payment_ids:
            instance_dir = instances_dir / f"{ix}"
            os.makedirs(instance_dir, exist_ok=True)

            if cfg.dataset.schema_mode == "multi-table":
                all_invoice_ids = [x[0] for x in invoices[0]["invoice_id"]]
                invoice_id = _random.choice(list(set(all_invoice_ids) - set(invoice_ids)))
            else:
                invoice_id = _random.choice(list(set(invoices[0]["invoice_id"].to_list()) - set(invoice_ids)))
            all_involved_invoice_ids.add(invoice_id)
            save_source_rows(invoices_tables=invoices, invoice_id=invoice_id, instance_dir=instance_dir)
            target_row = payments[payments["payment_id"] == payment_id]
            target_row.drop("payment_id", axis=1, inplace=True)

            target_row.to_csv(instance_dir / "target_row.csv", index=False)
            dump_json({"rows_match": False, "match_category": match["match_category"],
                       "perturbation_categories": perturbation_categories, "kind": "payment_driven"},
                      instance_dir / "ground_truth.json")
            negative_instances.append(ix)
            ix += 1

    logger.info(f"{len(all_involved_invoice_ids)} invoices and {len(all_involved_payment_ids)} payments")
    logger.info(
        f"{statistics.mean(nums_invoices_in_match)} invoices per match and {statistics.mean(nums_payments_in_match)} payments per match")
    logger.info(
        f"{(len(all_involved_invoice_ids) - len(all_in_match_invoice_ids)) / len(all_involved_invoice_ids)} invoices not in any match")
    logger.info(
        f"{(len(all_involved_payment_ids) - len(all_in_match_payment_ids)) / len(all_involved_payment_ids)} payments not in any match")
    dump_json({"positive": positive_instances, "negative": negative_instances}, instances_dir / "examples_pos_neg.json")
    dump_cfg(cfg, instances_dir / "config.cfg")
    logger.info(f"Saved {len(positive_instances)} positive and {len(negative_instances)} negative instances!")


if __name__ == "__main__":
    main()
