import collections
import logging
import os
import re

import hydra
import tqdm
from omegaconf import DictConfig

from llms4de.data import get_responses_dir, get_predictions_dir, load_json, dump_str, dump_json, dump_cfg
from llms4de.model.generic import extract_text_from_response

logger = logging.getLogger(__name__)


def extract_sql_block(text):
    match = re.search(r'(?<=```sql\n)(.*?)(?=\n```)', text, re.DOTALL)
    if match:
        return match.group(1)
    match = re.search(r'(?<=```signal\n)(.*?)(?=\n```)', text, re.DOTALL)
    if match:
        return match.group(1)
    # If no SQL block is found, try extracting text between two newlines
    match = re.search(r'\n\n(.*?)\n\n', text, re.DOTALL)
    if match:
        return match.group(1)
    match = re.search(r'(?<=```\n)(.*?)(?=\n```)', text, re.DOTALL)
    if match:
        return match.group(1)

    if match:
        return match.group(1)
    match = re.sub(r'^.*?\n\n(?=SELECT\b)', '', text, flags=re.DOTALL)
    if match:
        return match
    return text


def remove_unwanted_chars(s):
    if s is None:
        return s
    # Characters to remove
    unwanted = ""
    for ch in unwanted:
        s = s.replace(ch, "")
    return s


@hydra.main(version_base=None, config_path="../../config/text2signal", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    responses_dir = get_responses_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    predictions_dir = get_predictions_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    errors = collections.Counter()
    response_paths = list(sorted(responses_dir.glob("*.json")))
    for path in tqdm.tqdm(response_paths,
                          f"{cfg.task_name} - {cfg.dataset.dataset_name} - {cfg.exp_name} - parse responses"):
        prediction_dir = predictions_dir / path.name[:-5]
        os.makedirs(prediction_dir)

        response = load_json(path)
        text_completion = extract_text_from_response(response)
        signal = text_completion
        signal = remove_unwanted_chars(signal)
        try:
            signal = extract_sql_block(signal)

        #    signal = signal.removeprefix("```sql")
        #    signal = signal.removesuffix("```")
        except Exception as e:
            logger.warning("Answer cannot be parsed")
        #   signal = signal.strip()

        if text_completion is None:
            logger.warning("api request failed")
            dump_json("api_request_failed", prediction_dir / "error.json")
            dump_str("api_request_failed", prediction_dir / "prediction.txt")
            errors["api_request_failed"] += 1
            continue

        if signal is None:
            logger.warning("parsing list failed")
            dump_json("failed_parse_list", prediction_dir / "error.json")
            dump_str("api_request_failed", prediction_dir / "prediction.txt")
            errors["parse_list_failed"] += 1
            continue
        #  signals = list(map(str, signal))
        dump_str(signal, prediction_dir / "prediction.txt")
        dump_json(None, prediction_dir / "error.json")

    if errors.total() > 0:
        logger.warning(f"errors: {errors}")

    dump_cfg(cfg, predictions_dir / "config.cfg")


if __name__ == "__main__":
    main()
