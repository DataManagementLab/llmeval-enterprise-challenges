########################################################################################################################
# Ollama API helpers version: 2025-02-10
#
# use the following methods:
# ollama_execute(...)      ==> execute API requests
########################################################################################################################
import dataclasses
import functools
import hashlib
import json
import logging
import threading
import time
from typing import Literal

import requests
import tqdm

from llms4de.data import get_data_path

logger = logging.getLogger(__name__)

OLLAMA_CACHE_PATH = get_data_path() / "ollama_cache"


def ollama_execute(
        requests: list[dict],
        *,
        silent: bool = False
) -> list[dict]:
    """Execute a list of requests against the Ollama API.

    This method also caches requests and responses and waits between requests to abide the thread limit.

    Args:
        requests: A list of API requests.
        silent: Whether to display log messages and progress bars.

    Returns:
        A list of API responses.
    """
    global _local_context, _local_semaphore
    context = _local_context
    semaphore = _local_semaphore

    with semaphore:
        if "num_running" not in context.keys():
            context["num_running"] = 0

    before = time.perf_counter()
    pairs = [_Pair(_Request(request)) for request in requests]
    if _do_benchmark:
        logger.info(f"created pairs in {time.perf_counter() - before} seconds")

    with _ProgressBar(total=len(pairs), desc="", disable=silent) as progress_bar:

        # create cache directory
        OLLAMA_CACHE_PATH.mkdir(parents=True, exist_ok=True)

        # load cached pairs
        before = time.perf_counter()
        pairs_to_execute = []
        progress_bar.set_description("load responses")
        progress_bar.reset(total=len(pairs))
        for pair in pairs:
            pair.response = pair.request.load_cached_response()
            if pair.response is None:
                pairs_to_execute.append(pair)
            else:
                progress_bar.cached += 1
            progress_bar.update()
        if _do_benchmark:
            logger.info(f"loaded responses in {time.perf_counter() - before} seconds")

        # in case some pairs were not cached, execute them
        if len(pairs_to_execute) > 0:

            progress_bar.clear()  # clear before printing/logging

            # check requests
            before = time.perf_counter()
            for pair in pairs_to_execute:
                pair.request.check()
            if _do_benchmark:
                logger.info(f"checked requests in {time.perf_counter() - before} seconds")

            # execute requests
            before = time.perf_counter()
            progress_bar.set_description("execute requests")
            progress_bar.reset(total=len(pairs))
            progress_bar.update(progress_bar.cached)
            while True:  # break if all(pair.status == "done" for pair in pairs_to_execute)
                logger.debug("repeatedly iterate through pairs until all are done")
                for pair in pairs_to_execute:
                    with semaphore:
                        if pair.status != "open":
                            continue
                        pair.status = "waiting"

                    while True:  # break if request is "running" in parallel execution
                        with semaphore:
                            if context["num_running"] < 200:  # max. num. of parallel requests
                                progress_bar.bottleneck = "P"

                                pair.status = "running"
                                context["num_running"] = context["num_running"] + 1
                                progress_bar.running = context["num_running"]
                                progress_bar.update_postfix()

                                def execute(p: _Pair, pb: _ProgressBar, c: dict, s: threading.Semaphore) -> None:
                                    http_response = p.request.execute()
                                    p.response = _Response(http_response.json())

                                    with s:
                                        c["num_running"] = c["num_running"] - 1
                                        pb.running = c["num_running"]

                                        match http_response.status_code:
                                            case 200:
                                                p.status = "done"
                                                pb.update()
                                            case _:
                                                p.status = "done"
                                                pb.failed += 1
                                                pb.update()

                                pair.thread = threading.Thread(
                                    target=execute,
                                    args=(pair, progress_bar, context, semaphore)
                                )
                                pair.thread.start()
                                break
                            else:
                                progress_bar.bottleneck = "T"
                                progress_bar.update_postfix()

                        time.sleep(0.05)  # sleep to wait for thread limit

                if all(pair.status == "done" for pair in pairs_to_execute):
                    break
                progress_bar.bottleneck = "Z"
                progress_bar.update_postfix()
                time.sleep(1)  # sleep to wait for stragglers and failures

            for pair in pairs_to_execute:
                if pair.thread is not None:
                    pair.thread.join()

            if _do_benchmark:
                logger.info(f"executed requests in {time.perf_counter() - before} seconds")

        return [pair.response.response for pair in pairs]


########################################################################################################################
# implementation
########################################################################################################################

_do_benchmark = False
_local_context = {}
_local_semaphore = threading.Semaphore()


class _Request:
    request: dict

    def __init__(self, request: dict) -> None:
        self.request = request

    @functools.cache
    def hash(self) -> str:
        return hashlib.sha256(bytes(json.dumps(self.request), "utf-8")).hexdigest()

    def check(self) -> None:
        if "model" not in self.request.keys():
            logger.error("missing field `model` in request!")
            raise AttributeError("missing field `model` in request!")

        if "messages" not in self.request.keys():
            logger.error("missing field `messages` in request!")
            raise AttributeError("missing field `messages` in request!")

        if "stream" not in self.request.keys() or self.request["stream"]:
            logger.error("request must set `stream` to `false`!")
            raise AttributeError("request must set `stream` to `false`!")

        if "options" not in self.request.keys() \
                or "temperature" not in self.request["options"].keys() \
                or self.request["options"]["temperature"] != 0:
            logger.warning("request's `temperature` not set to 0, which is required for reproducibility")
        if "options" not in self.request.keys() \
                or "seed" not in self.request["options"].keys():
            logger.warning("missing optional option `seed`, which is required for reproducibility")

    def load_cached_response(self):  # -> "_Response" | None
        path = OLLAMA_CACHE_PATH / f"{self.hash()}.json"
        if path.is_file():
            with open(path, "r", encoding="utf-8") as file:
                cached_pair = json.load(file)
            cached_request = _Request(cached_pair["request"])
            cached_response = _Response(cached_pair["response"])
            if self.request == cached_request.request:
                return cached_response
        return None

    def execute(self) -> requests.Response:
        http_response = requests.post(
            url="http://localhost:11434/api/chat",
            json=self.request
        )

        if http_response.status_code == 200:
            path = OLLAMA_CACHE_PATH / f"{self.hash()}.json"
            with open(path, "w", encoding="utf-8") as cache_file:
                json.dump({"request": self.request, "response": http_response.json()}, cache_file)
        else:
            logger.warning(f"request failed, no retry: {http_response.content}")

        return http_response


class _Response:
    response: dict

    def __init__(self, response: dict) -> None:
        self.response = response


@dataclasses.dataclass
class _Pair:
    request: _Request
    response: _Response | None = None
    status: Literal["open"] | Literal["waiting"] | Literal["running"] | Literal["done"] = "open"
    thread: threading.Thread | None = None


class _ProgressBar(tqdm.tqdm):
    running: int
    failed: int
    cached: int
    bottleneck: Literal["T"] | Literal["P"] | Literal["Z"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.running = 0
        self.failed = 0
        self.cached = 0
        self.bottleneck = "P"
        self.update_postfix()

    def __enter__(self):
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        return super().__exit__(exc_type, exc_value, traceback)

    def update(self, *args, **kwargs) -> None:
        self.update_postfix()
        super().update(*args, **kwargs)

    def update_postfix(self) -> None:
        self.set_postfix_str(
            f"{self.bottleneck}{self.running:03d}, failed={self.failed}, cached={self.cached}"
        )
