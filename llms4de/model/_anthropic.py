########################################################################################################################
# Anthropic API helpers version: 2025-02-04
#
# use the following methods:
# anthropic_model(...)        ==> get model info
# anthropic_execute(...)      ==> execute API requests
#
# You must store your Anthropic API key in an environment variable, for example using:
# export ANTHROPIC_API_KEY="<your-key>"
########################################################################################################################
import dataclasses
import functools
import hashlib
import json
import logging
import os
import threading
import time
from typing import Literal, Any

import requests
import tqdm

from llms4de.data import get_data_path

logger = logging.getLogger(__name__)

CACHE_PATH = get_data_path() / "anthropic_cache"

# see https://docs.anthropic.com/en/docs/about-claude/models and https://www.anthropic.com/pricing#anthropic-api
MODEL_PARAMETERS = {
    "claude-3-5-sonnet-20240620": {
        "cost_per_1k_input_tokens": 0.0030,
        "cost_per_1k_output_tokens": 0.0150,
        "cost_per_1k_cache_creation_input_tokens": 0.00375,
        "cost_per_1k_cache_read_input_tokens": 0.0003,
        "max_context": 200_000,
        "max_output_tokens": 8_192
    },
    "claude-3-5-sonnet-20241022": {
        "cost_per_1k_input_tokens": 0.0030,
        "cost_per_1k_output_tokens": 0.0150,
        "cost_per_1k_cache_creation_input_tokens": 0.00375,
        "cost_per_1k_cache_read_input_tokens": 0.0003,
        "max_context": 200_000,
        "max_output_tokens": 8_192
    },
    "claude-3-5-haiku-20241022": {
        "cost_per_1k_input_tokens": 0.0008,
        "cost_per_1k_output_tokens": 0.0040,
        "cost_per_1k_cache_creation_input_tokens": 0.001,
        "cost_per_1k_cache_read_input_tokens": 0.00008,
        "max_context": 200_000,
        "max_output_tokens": 8_192
    }
}


########################################################################################################################
# API
########################################################################################################################


def anthropic_model(
        model: str
) -> dict:
    """Get information about the Anthropic model.

    Args:
        model: The name of the model.

    Returns:
        A dictionary with information about the Anthropic model.
    """
    return _get_model_params(model)


def anthropic_execute(
        requests: list[dict],
        *,
        force: float | None = None,
        silent: bool = False
) -> list[dict]:
    """Execute a list of requests against the Anthropic API.

    This method also estimates the maximum cost incurred by the requests, caches requests and responses, and waits
    between requests to abide the API limits.

    Args:
        requests: A list of API requests.
        force: An optional float specifying the cost below or equal to which no confirmation should be required.
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
        if "num_counting" not in context.keys():
            context["num_counting"] = 0

    before = time.perf_counter()
    pairs = [_Pair(_Request(request)) for request in requests]
    if _do_benchmark:
        logger.info(f"created pairs in {time.perf_counter() - before} seconds")

    with _ProgressBar(total=len(pairs), desc="", disable=silent) as progress_bar:

        # create cache directory
        CACHE_PATH.mkdir(parents=True, exist_ok=True)

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

            if "ANTHROPIC_API_KEY" not in os.environ.keys():
                raise AssertionError(f"Missing `ANTHROPIC_API_KEY` in environment variables!")

            # count tokens
            before = time.perf_counter()
            progress_bar.set_description("count tokens")
            progress_bar.reset(total=len(pairs))
            progress_bar.update(progress_bar.cached)
            for pair in pairs_to_execute:
                while True:
                    with semaphore:
                        if context["num_counting"] < 20:  # max. num. of parallel count token requests
                            context["num_counting"] = context["num_counting"] + 1
                            progress_bar.bottleneck = "P"
                            progress_bar.running = context["num_counting"]
                            progress_bar.update_postfix()

                            def execute(p: _Pair, pb: _ProgressBar, c: dict, s: threading.Semaphore) -> None:
                                http_response = p.request.count_tokens()
                                if http_response.status_code != 200:
                                    logger.error(f"count_tokens error: {http_response.content}")
                                    http_response.raise_for_status()
                                    exit()

                                p.request.num_input_tokens = http_response.json()["input_tokens"]

                                with s:
                                    c["num_counting"] = c["num_counting"] - 1
                                    pb.running = c["num_counting"]
                                    pb.update()

                            pair.thread = threading.Thread(
                                target=execute,
                                args=(pair, progress_bar, context, semaphore)
                            )
                            pair.thread.start()
                            break

                    progress_bar.bottleneck = "T"
                    progress_bar.update_postfix()
                    time.sleep(0.05)  # sleep to wait for thread limit budget

            progress_bar.bottleneck = "Z"
            progress_bar.update_postfix()
            for pair in pairs_to_execute:
                if pair.thread is not None:
                    pair.thread.join()
                    pair.thread = None
            if _do_benchmark:
                logger.info(f"counted tokens in {time.perf_counter() - before} seconds")

            progress_bar.clear()  # clear before printing/logging

            # check requests
            before = time.perf_counter()
            for pair in pairs_to_execute:
                pair.request.check()
            if _do_benchmark:
                logger.info(f"checked requests in {time.perf_counter() - before} seconds")

            # estimate maximum cost
            before = time.perf_counter()
            total_max_cost = sum(pair.request.max_cost() for pair in pairs_to_execute)
            if _do_benchmark:
                logger.info(f"estimated maximum cost in {time.perf_counter() - before} seconds")

            if force is None or total_max_cost > force:
                logger.info(f"press enter to continue and spend up to around ${total_max_cost:.2f}")
                input()
            elif not silent:
                logger.info(f"spending up to around ${total_max_cost:.2f}")

            # sort requests to execute longest requests first, put one short request first to quickly obtain HTTP header
            before = time.perf_counter()
            pairs_to_execute.sort(key=lambda p: p.request.max_total_usage(), reverse=True)
            pairs_to_execute = pairs_to_execute[-1:] + pairs_to_execute[:-1]
            if _do_benchmark:
                logger.info(f"sorted requests in {time.perf_counter() - before} seconds")

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

                        if pair.request.model not in context.keys():
                            context[pair.request.model] = _ModelBudgetState.new()

                    while True:  # break if request is "done" in sequential execution or "running" in parallel execution
                        with semaphore:
                            context[pair.request.model] = context[pair.request.model].consider_time()

                            if context[pair.request.model].is_enough_for_request(pair.request):
                                match context[pair.request.model].mode:
                                    case "sequential" if context["num_running"] == 0:
                                        logger.debug(f"sequential execution for `{pair.request.model}`: execute")
                                        progress_bar.bottleneck = "S"

                                        pair.status = "running"
                                        context["num_running"] = context["num_running"] + 1
                                        progress_bar.running = context["num_running"]
                                        progress_bar.update_postfix()

                                        context[pair.request.model] = context[pair.request.model].decrease_by_request(
                                            pair.request
                                        )

                                        http_response = pair.request.execute()
                                        pair.response = _Response(http_response.json())

                                        context[pair.request.model] = context[pair.request.model].set_from_headers(
                                            http_response.headers
                                        )

                                        context["num_running"] = context["num_running"] - 1
                                        progress_bar.running = context["num_running"]
                                        progress_bar.cost += pair.response.total_cost()

                                        match http_response.status_code:
                                            case 200:
                                                context[pair.request.model] = context[pair.request.model].to_parallel()
                                                pair.status = "done"
                                                progress_bar.update()
                                                break
                                            case 429:
                                                pair.status = "open"
                                                progress_bar.update_postfix()  # not done -> update only postfix
                                            case _:
                                                pair.status = "done"
                                                progress_bar.failed += 1
                                                progress_bar.update()
                                                break
                                    case "parallel" if context["num_running"] < 20:  # max. num. of parallel requests
                                        logger.debug(f"parallel execution for `{pair.request.model}`: execute")
                                        progress_bar.bottleneck = "P"

                                        pair.status = "running"
                                        context["num_running"] = context["num_running"] + 1
                                        progress_bar.running = context["num_running"]
                                        progress_bar.update_postfix()

                                        context[pair.request.model] = context[pair.request.model].decrease_by_request(
                                            pair.request
                                        )

                                        def execute(p: _Pair, pb: _ProgressBar, c: dict,
                                                    s: threading.Semaphore) -> None:
                                            http_response = p.request.execute()
                                            p.response = _Response(http_response.json())

                                            with s:
                                                c[pair.request.model] = c[p.request.model].set_from_headers(
                                                    http_response.headers
                                                )

                                                c["num_running"] = c["num_running"] - 1
                                                pb.running = c["num_running"]
                                                pb.cost += p.response.total_cost()

                                                match http_response.status_code:
                                                    case 200:
                                                        c[p.request.model] = c[p.request.model].increase_by_response(
                                                            p.request,
                                                            p.response
                                                        )
                                                        p.status = "done"
                                                        pb.update()
                                                    case 429:
                                                        logger.debug(
                                                            f"parallel execution for `{p.request.model}`: "
                                                            f"rate limit error -> switch to sequential execution"
                                                        )
                                                        p.status = "open"
                                                        c[p.request.model] = c[p.request.model].to_sequential()
                                                        pb.update_postfix()  # not done -> update only postfix
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
                                    case _:
                                        progress_bar.bottleneck = "T"
                                        progress_bar.update_postfix()
                            else:
                                progress_bar.bottleneck = "L"
                                progress_bar.update_postfix()

                        time.sleep(0.05)  # sleep to wait for thread limit or rate limit budget

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


@functools.cache
def _get_model_params(model: str) -> dict:
    if model not in MODEL_PARAMETERS.keys():
        raise AssertionError(f"Unknown model `{model}`!")
    else:
        return MODEL_PARAMETERS[model]


class _Request:
    request: dict
    num_input_tokens: int | None

    def __init__(self, request: dict) -> None:
        self.request = request
        self.num_input_tokens = None

    @functools.cached_property
    def model(self) -> str:
        if "model" not in self.request.keys():
            raise AttributeError("Missing field `model` in request!")
        return self.request["model"]

    @functools.cached_property
    def messages(self) -> list[dict]:
        if "messages" not in self.request.keys():
            raise AttributeError("Missing field `messages` in request!")
        return self.request["messages"]

    @functools.cached_property
    def max_tokens(self) -> int:
        if "max_tokens" not in self.request.keys():
            raise AttributeError("Missing field `max_tokens` in request!")
        return self.request["max_tokens"]

    @functools.cache
    def max_input_usage(self) -> int:
        return self.num_input_tokens

    @functools.cache
    def max_output_usage(self) -> int:
        return self.max_tokens

    @functools.cache
    def max_total_usage(self) -> int:
        return self.max_input_usage() + self.max_output_usage()

    @functools.cache
    def max_cost(self) -> float:
        model_params = _get_model_params(self.model)
        input_cost = self.max_input_usage() * (model_params["cost_per_1k_input_tokens"] / 1000)
        output_cost = self.max_output_usage() * (model_params["cost_per_1k_output_tokens"] / 1000)
        return input_cost + output_cost

    @functools.cache
    def hash(self) -> str:
        return hashlib.sha256(bytes(json.dumps(self.request), "utf-8")).hexdigest()

    def check(self) -> None:
        model_params = _get_model_params(self.model)

        if self.num_input_tokens > model_params["max_context"]:
            logger.warning("request's number of input tokens exceeds model's `max_context`")

        if self.max_tokens > model_params["max_output_tokens"]:
            logger.warning("request's `max_tokens` exceeds model's `max_output_tokens`")

        if self.num_input_tokens + self.max_tokens > model_params["max_context"]:
            logger.warning("request's input tokens + `max_tokens` exceeds model's `max_context`")

        if "temperature" not in self.request.keys() or self.request["temperature"] != 0:
            logger.warning("request's `temperature` not set to 0, which is required for reproducibility")

    def load_cached_response(self):  # -> "_Response" | None
        path = CACHE_PATH / f"{self.hash()}.json"
        if path.is_file():
            with open(path, "r", encoding="utf-8") as file:
                cached_pair = json.load(file)
            cached_request = _Request(cached_pair["request"])
            cached_response = _Response(cached_pair["response"])
            if self.request == cached_request.request:
                return cached_response
        return None

    def count_tokens(self) -> requests.Response:
        req = {k: v for k, v in self.request.items() if k in {"messages", "model", "system", "tool_choice", "tools"}}
        while True:
            before = time.time()
            http_response = requests.post(
                url="https://api.anthropic.com/v1/messages/count_tokens",
                json=req,
                headers={
                    "content-type": "application/json",
                    "x-api-key": f"{os.environ['ANTHROPIC_API_KEY']}",
                    "anthropic-version": "2023-06-01"
                }
            )
            after = time.time()
            time.sleep(max(0.0, (60 / 4_000 - (after - before)) * 20 * 1.1))
            match http_response.status_code:
                case 200:
                    return http_response
                case _:
                    logger.error(f"count_tokens error, retry: {http_response.content}")

    def execute(self) -> requests.Response:
        http_response = requests.post(
            url="https://api.anthropic.com/v1/messages",
            json=self.request,
            headers={
                "content-type": "application/json",
                "x-api-key": f"{os.environ['ANTHROPIC_API_KEY']}",
                "anthropic-version": "2023-06-01"
            }
        )

        if http_response.status_code == 200:
            path = CACHE_PATH / f"{self.hash()}.json"
            with open(path, "w", encoding="utf-8") as cache_file:
                json.dump({"request": self.request, "response": http_response.json()}, cache_file)
        elif http_response.status_code == 429:
            logger.info("retry request due to rate limit error")
        else:
            logger.warning(f"request failed, no retry: {http_response.content}")

        return http_response


class _Response:
    response: dict

    def __init__(self, response: dict) -> None:
        self.response = response

    @functools.cache
    def was_successful(self) -> bool:  # use type to determine if request was successful
        return self.response["type"] == "message"

    @functools.cached_property
    def model(self) -> str:
        if "model" not in self.response.keys():
            raise AttributeError("Missing field `model` in response, which is required for successful requests!")
        return self.response["model"]

    @functools.cached_property
    def usage(self) -> dict:
        if "usage" not in self.response.keys():
            raise AttributeError("Missing field `usage` in response, which is required for successful requests!")
        return self.response["usage"]

    @functools.cache
    def input_usage(self) -> int:
        if self.was_successful():
            total_usage = 0
            if self.usage["cache_creation_input_tokens"] is not None:
                total_usage += self.usage["cache_creation_input_tokens"]
            if self.usage["cache_read_input_tokens"] is not None:
                total_usage += self.usage["cache_read_input_tokens"]
            total_usage += self.usage["input_tokens"]
            return total_usage
        else:
            return 0

    @functools.cache
    def output_usage(self) -> int:
        if self.was_successful():
            return self.usage["output_tokens"]
        else:
            return 0

    @functools.cache
    def total_usage(self) -> int:
        return self.input_usage() + self.output_usage()

    @functools.cache
    def total_cost(self) -> float:
        if self.was_successful():
            model_params = _get_model_params(self.model)
            total_cost = 0
            if self.usage["cache_creation_input_tokens"] is not None:
                total_cost += self.usage["cache_creation_input_tokens"] * (
                        model_params["cost_per_1k_cache_creation_input_tokens"] / 1000)
            if self.usage["cache_read_input_tokens"] is not None:
                total_cost += self.usage["cache_read_input_tokens"] * (
                        model_params["cost_per_1k_cache_read_input_tokens"] / 1000)

            total_cost += self.usage["input_tokens"] * (model_params["cost_per_1k_input_tokens"] / 1000)
            total_cost += self.usage["output_tokens"] * (model_params["cost_per_1k_output_tokens"] / 1000)
            return total_cost
        else:
            return 0


@dataclasses.dataclass
class _Pair:
    request: _Request
    response: _Response | None = None
    status: Literal["open"] | Literal["waiting"] | Literal["running"] | Literal["done"] = "open"
    thread: threading.Thread | None = None


@dataclasses.dataclass
class _ModelBudgetState:
    mode: Literal["sequential"] | Literal["parallel"]
    rpm: int | None
    tpm: int | None
    itpm: int | None
    otpm: int | None
    r: int | None
    t: int | None
    it: int | None
    ot: int | None
    last_update: float

    @classmethod
    def new(cls) -> "_ModelBudgetState":
        return cls("sequential", None, None, None, None, None, None, None, None, time.time())

    def is_enough_for_request(self, request: _Request) -> bool:
        return (
                (self.r is None or self.r >= 1)
                and (self.t is None or self.t >= request.max_total_usage())
                and (self.it is None or self.it >= request.max_input_usage())
                and (self.ot is None or self.ot >= request.max_output_usage())
        )

    def consider_time(self) -> "_ModelBudgetState":
        now = time.time()
        delta = now - self.last_update
        if self.rpm is not None and self.r is not None:
            self.r = min(self.rpm, int(self.r + self.rpm * delta / 60))
        if self.tpm is not None and self.t is not None:
            self.t = min(self.tpm, int(self.t + self.tpm * delta / 60))
        if self.itpm is not None and self.it is not None:
            self.it = min(self.itpm, int(self.it + self.itpm * delta / 60))
        if self.otpm is not None and self.ot is not None:
            self.ot = min(self.otpm, int(self.ot + self.otpm * delta / 60))
        self.last_update = now
        return self

    def decrease_by_request(self, request: _Request) -> "_ModelBudgetState":
        if self.r is not None:
            self.r -= 1
        if self.t is not None:
            self.t -= request.max_total_usage()
        if self.it is not None:
            self.it -= request.max_input_usage()
        if self.ot is not None:
            self.ot -= request.max_output_usage()
        return self

    def increase_by_response(self, request: _Request, response: _Response) -> "_ModelBudgetState":
        if response.total_usage() < request.max_total_usage():
            self.t = min(self.tpm, int(self.t + request.max_total_usage() - response.total_usage()))
        if response.input_usage() < request.max_input_usage():
            self.it = min(self.itpm, int(self.it + request.max_input_usage() - response.input_usage()))
        if response.output_usage() < request.max_output_usage():
            self.ot = min(self.otpm, int(self.ot + request.max_output_usage() - response.output_usage()))
        return self

    def set_from_headers(self, headers: dict[str, Any]) -> "_ModelBudgetState":
        if "anthropic-ratelimit-requests-limit" in headers.keys():
            self.rpm = int(headers["anthropic-ratelimit-requests-limit"])
        if "anthropic-ratelimit-tokens-limit" in headers.keys():
            self.tpm = int(headers["anthropic-ratelimit-tokens-limit"])
        if "anthropic-ratelimit-input-tokens-limit" in headers.keys():
            self.itpm = int(headers["anthropic-ratelimit-input-tokens-limit"])
        if "anthropic-ratelimit-output-tokens-limit" in headers.keys():
            self.otpm = int(headers["anthropic-ratelimit-output-tokens-limit"])
        if "anthropic-ratelimit-requests-remaining" in headers.keys():
            header_r = int(headers["anthropic-ratelimit-requests-remaining"])
            if self.r is None or self.r > header_r:
                self.r = header_r
        if "anthropic-ratelimit-tokens-remaining" in headers.keys():
            header_t = int(headers["anthropic-ratelimit-tokens-remaining"])
            if self.t is None or self.t > header_t:
                self.t = header_t
        if "anthropic-ratelimit-input-tokens-remaining" in headers.keys():
            header_it = int(headers["anthropic-ratelimit-input-tokens-remaining"])
            if self.it is None or self.it > header_it:
                self.it = header_it
        if "anthropic-ratelimit-output-tokens-remaining" in headers.keys():
            header_ot = int(headers["anthropic-ratelimit-output-tokens-remaining"])
            if self.ot is None or self.ot > header_ot:
                self.ot = header_ot
        return self

    def to_parallel(self) -> "_ModelBudgetState":
        self.mode = "parallel"
        return self

    def to_sequential(self) -> "_ModelBudgetState":
        self.mode = "sequential"
        return self


class _ProgressBar(tqdm.tqdm):
    running: int
    failed: int
    cached: int
    cost: float
    bottleneck: Literal["T"] | Literal["L"] | Literal["P"] | Literal["Z"] | Literal["S"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.running = 0
        self.failed = 0
        self.cached = 0
        self.cost = 0
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
            f"{self.bottleneck}{self.running:03d}, failed={self.failed}, cached={self.cached}, cost=${self.cost:.2f}"
        )
