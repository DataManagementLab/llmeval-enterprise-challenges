import collections
import logging
import os

import hydra
import tqdm
from omegaconf import DictConfig

from llms4de.data import get_responses_dir, get_predictions_dir, load_json, dump_json, dump_cfg
from llms4de.model.generic import extract_text_from_response
from llms4de.prompting.parse import parse_list

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="../../config/column_type_annotation", config_name="config.yaml")
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

        if text_completion is None:
            logger.warning("api request failed")
            match cfg.task_mode:
                case "all":
                    dump_json(None, prediction_dir / "column_types.json")
                case "lookup-index" | "lookup-header":
                    dump_json(None, prediction_dir / "column_type.json")
                case _:
                    raise AssertionError(f"invalid task mode `{cfg.task_mode}`")
            dump_json("api_request_failed", prediction_dir / "error.json")
            errors["api_request_failed"] += 1
            continue

        match cfg.task_mode:
            case "all":
                column_types = parse_list(text_completion, **cfg.parse_list)
                if column_types is None:
                    logger.warning("parsing list failed")
                    dump_json(None, prediction_dir / "column_types.json")
                    dump_json("failed_parse_list", prediction_dir / "error.json")
                    errors["parse_list_failed"] += 1
                    continue
                column_types = list(map(str, column_types))
                dump_json(column_types, prediction_dir / "column_types.json")
                dump_json(None, prediction_dir / "error.json")
            case "lookup-index" | "lookup-header":
                dump_json(text_completion, prediction_dir / "column_type.json")
                dump_json(None, prediction_dir / "error.json")
            case _:
                raise AssertionError(f"invalid task mode `{cfg.task_mode}`")

    if errors.total() > 0:
        logger.warning(f"errors: {errors}")

    dump_cfg(cfg, predictions_dir / "config.cfg")


if __name__ == "__main__":
    main()
