import collections
import logging

import hydra
from omegaconf import DictConfig

from llms4de.data import get_requests_dir, get_responses_dir, load_json, dump_json, dump_cfg
from llms4de.model.generic import execute_requests, extract_finish_reason_from_response

logger = logging.getLogger(__name__)

_openai_request_seed: int = 321164097


@hydra.main(version_base=None, config_name="config.yaml")  # specify config path via command line flag -cp
def main(cfg: DictConfig) -> None:
    requests_dir = get_requests_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    responses_dir = get_responses_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    requests = []
    request_names = []  # we need to remember these since sorting paths is not numerical
    for request_path in list(sorted(requests_dir.glob("*.json"))):
        requests.append(load_json(request_path))
        request_names.append(request_path.name)

    for request in requests:
        request["seed"] = _openai_request_seed

    responses = execute_requests(requests, cfg.api_name)

    num_failed = 0
    finish_reasons = collections.Counter()
    for response in responses:
        finish_reason = extract_finish_reason_from_response(response)
        if finish_reason is not None:
            finish_reasons[finish_reason] += 1
        else:
            num_failed += 1

    for key in finish_reasons.keys():
        if key != "stop":
            logger.warning(f"{finish_reasons[key]} generations were stopped due to {key}!")

    if num_failed > 0:
        logger.warning(f"{num_failed} requests failed!")

    for response, request_name in zip(responses, request_names):
        dump_json(response, responses_dir / request_name)

    dump_cfg(cfg, responses_dir / "config.cfg")


if __name__ == "__main__":
    main()
