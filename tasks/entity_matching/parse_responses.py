import collections
import logging

import hydra
import tqdm
from omegaconf import DictConfig

from llms4de.data import get_responses_dir, get_predictions_dir, load_json, dump_json, dump_cfg
from llms4de.model.generic import extract_text_from_response

logger = logging.getLogger(__name__)


def get_ground_truth_boolean(response: str) -> bool | None:
    response_parts = response.lower().split()
    if "yes" in response_parts or len(response_parts) >= 1 and response_parts[0].startswith("yes"):
        if "no" in response_parts or len(response_parts) >= 1 and response_parts[0].startswith("no"):
            logger.warning(f"`yes` and `no` in yes/no response `{response}`")
            return None
        return True
    elif "no" in response_parts or len(response_parts) >= 1 and response_parts[0].startswith("no"):
        return False
    else:
        logger.warning(f"neither `yes` nor `no` in yes/no response `{response}`")
        return None


@hydra.main(version_base=None, config_path="../../config/entity_matching", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    responses_dir = get_responses_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    predictions_dir = get_predictions_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    errors = collections.Counter()
    response_paths = list(sorted(responses_dir.glob("*.json")))
    for response_path in tqdm.tqdm(response_paths,
                                   f"{cfg.task_name} - {cfg.dataset.dataset_name} - {cfg.exp_name} - parse responses"):
        prediction_dir = predictions_dir / response_path.name[:-5]
        prediction_dir.mkdir(parents=True)

        response = load_json(response_path)
        text_completion = extract_text_from_response(response)

        if text_completion is None:
            logger.warning("api request failed")
            dump_json(None, prediction_dir / "prediction.json")
            dump_json("api_request_failed", prediction_dir / "error.json")
            errors["api_request_failed"] += 1
            continue

        prediction = get_ground_truth_boolean(text_completion)

        if prediction is None:
            logger.warning(f"parsing yes/no response `{prediction}` failed")
            dump_json(None, prediction_dir / "prediction.json")
            dump_json("parse_yes_no_failed", prediction_dir / "error.json")
            errors["parse_yes_no_failed"] += 1
            continue

        dump_json({"rows_match": prediction}, prediction_dir / "prediction.json")
        dump_json(None, prediction_dir / "error.json")

    if errors.total() > 0:
        logger.warning(f"errors: {errors}")

    dump_cfg(cfg, predictions_dir / "config.cfg")


if __name__ == "__main__":
    main()
