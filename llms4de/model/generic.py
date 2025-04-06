import copy
import logging
import os

import requests

logger = logging.getLogger(__name__)

FORCE: float | None = 0.01

HF_TOKENIZER_CACHE: dict = {}


def prepare_for_anthropic(request: dict) -> dict:
    """Prepare Anthropic API request.

    Args:
        request: The API request.

    Returns:
        The API request prepared for the Anthropic API.
    """
    from llms4de.model import _anthropic
    request = copy.deepcopy(request)
    if request["model"] not in _anthropic.MODEL_PARAMETERS.keys():
        raise AssertionError(f"`{request['model']}` is not an anthropic model")

    # Anthropic does not support `seed`
    if "seed" in request.keys():
        del request["seed"]

    # Anthropic requires (not optional) `max_tokens` and does not support `max_completion_tokens`
    if "max_completion_tokens" in request.keys():
        request["max_tokens"] = request["max_completion_tokens"]
        del request["max_completion_tokens"]
    if "max_tokens" not in request.keys() or request["max_tokens"] is None:
        request["max_tokens"] = _anthropic.MODEL_PARAMETERS[request["model"]]["max_output_tokens"]

    return request


def prepare_for_ollama(request: dict) -> dict:
    """Prepare Ollama API request.

    Args:
        request: The API request.

    Returns:
        The API request prepared for the Ollama API.
    """
    request = copy.deepcopy(request)

    # move `seed` to options
    if "seed" in request.keys():
        if "options" not in request.keys():
            request["options"] = {}
        request["options"]["seed"] = request["seed"]
        del request["seed"]

    # move `temperature` to options
    if "temperature" in request.keys():
        if "options" not in request.keys():
            request["options"] = {}
        request["options"]["temperature"] = request["temperature"]
        del request["temperature"]

    # move `max_tokens` to options as `num_predict`
    max_tokens = None
    if "max_completion_tokens" in request.keys():
        max_tokens = request["max_completion_tokens"]
        del request["max_completion_tokens"]
    elif "max_tokens" in request.keys():
        max_tokens = request["max_tokens"]
        del request["max_tokens"]

    if max_tokens is not None:
        if "options" not in request.keys():
            request["options"] = {}
        request["options"]["num_predict"] = max_tokens

    # set `stream` to False
    request["stream"] = False

    if "options" not in request.keys():
        request["options"] = {}
    request["options"]["num_ctx"] = 128_000

    return request


def num_tokens(
        text: str,
        model: str,
        api_name: str
) -> int:
    """Compute the number of tokens of the text.

    Args:
        text: The given text.
        model: The name of the model.
        api_name: The name of the API to use.

    Returns:
        The number of tokens.
    """
    match api_name:
        case "openai":
            import tiktoken
            from llms4de.model import _openai
            assert model in _openai.MODEL_PARAMETERS.keys(), f"`{model}` is not an openai model"
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        case "anthropic":
            from llms4de.model import _anthropic
            assert model in _anthropic.MODEL_PARAMETERS.keys(), f"`{model}` is not an anthropic model"
            if "ANTHROPIC_API_KEY" not in os.environ.keys():
                raise AssertionError("missing `ANTHROPIC_API_KEY` in environment variables")
            if text == "":
                return 0
            http_response = requests.post(
                url="https://api.anthropic.com/v1/messages/count_tokens",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": text}]
                },
                headers={
                    "content-type": "application/json",
                    "x-api-key": f"{os.environ['ANTHROPIC_API_KEY']}",
                    "anthropic-version": "2023-06-01"
                }
            )
            return max(1, http_response.json()["input_tokens"] - 7)  # there seem to be 7 'structural' tokens
        case "ollama":
            import tokenizers
            if "HF_TOKEN" not in os.environ.keys():
                raise AssertionError("missing `HF_TOKEN` in environment variables")
            ollama_to_hf_model = {
                "llama3.1:8b-instruct-fp16": "meta-llama/Llama-3.1-8B-Instruct",
                "llama3.1:70b-instruct-fp16": "meta-llama/Llama-3.1-70B-Instruct"
            }
            if model not in ollama_to_hf_model.keys():
                raise AssertionError(f"`cannot translate ollama model `{model}` to hugging face model")
            if ollama_to_hf_model[model] in HF_TOKENIZER_CACHE.keys():
                tokenizer = HF_TOKENIZER_CACHE[ollama_to_hf_model[model]]
            else:
                tokenizer = tokenizers.Tokenizer.from_pretrained(ollama_to_hf_model[model])
                HF_TOKENIZER_CACHE[ollama_to_hf_model[model]] = tokenizer
            return len(tokenizer.encode(text, add_special_tokens=False).tokens)
        case "aicore":
            import tiktoken
            from llms4de.model import _openai, _anthropic
            if model in _openai.MODEL_PARAMETERS.keys():
                encoding = tiktoken.encoding_for_model(model)
                return len(encoding.encode(text))
            elif model in _anthropic.MODEL_PARAMETERS.keys():
                raise AssertionError(f"cannot compute tokens for anthropic model `{model}` with aicore")
            else:  # assume Ollama model
                raise AssertionError(f"cannot compute tokens for ollama model `{model}` with aicore")
        case _:
            raise AssertionError(f"unknown api_name `{api_name}`")


def max_tokens_for_ground_truth(
        ground_truth: str,
        api_name: str,
        model: str,
        max_tokens_over_ground_truth: int | None
) -> int | None:
    """Compute max_tokens based on the length of the ground truth and max_tokens_over_ground_truth.

    Args:
        ground_truth: The ground truth string.
        api_name: The name of the API.
        model: The model name.
        max_tokens_over_ground_truth: How many additional tokens should be allowed.

    Returns:
        The value for max_tokens.
    """
    if max_tokens_over_ground_truth is None:
        return None
    else:
        ground_truth_len = num_tokens(ground_truth, model, api_name)
        return ground_truth_len + max_tokens_over_ground_truth


def execute_requests(
        requests: list[dict],
        api_name: str
) -> list[dict]:
    """Execute the list of requests against the specified API.

    Args:
        requests: The list of API requests.
        api_name: The name of the API.

    Returns:
        The list of API responses.
    """
    match api_name:
        case "openai":
            from llms4de.model import _openai
            return _openai.openai_execute(requests, force=FORCE)
        case "anthropic":
            from llms4de.model import _anthropic
            requests = [prepare_for_anthropic(request) for request in requests]
            return _anthropic.anthropic_execute(requests, force=FORCE)
        case "ollama":
            from llms4de.model import _ollama
            requests = [prepare_for_ollama(request) for request in requests]
            return _ollama.ollama_execute(requests)
        case "aicore":
            from llms4de.model import _aicore
            return _aicore.aicore_execute(requests, force=FORCE)
        case _:
            raise AssertionError(f"unknown api_name `{api_name}`")


def extract_text_from_response(response: dict) -> str | None:
    """Extract the text from an API response.

    Args:
        response: The API response.

    Returns:
        The generated text or None if the API request failed.
    """
    if "choices" in response.keys():  # OpenAI response
        return response["choices"][0]["message"]["content"]
    elif "content" in response.keys():  # Anthropic response
        return response["content"][0]["text"]
    elif "message" in response.keys():  # Ollama response
        return response["message"]["content"]
    elif "output" in response.keys():  # AWS Bedrock response
        return response["output"]["message"]["content"][0]["text"]
    else:
        return None


def extract_finish_reason_from_response(response: dict) -> str | None:
    """Extract the finish reason from an API response.

    Args:
        response: The API response.

    Returns:
        The finish reason for the generated text or None if the API request failed.
    """
    if "choices" in response.keys():  # OpenAI response
        return response["choices"][0]["finish_reason"]
    elif "stop_reason" in response.keys():  # Anthropic response
        match response["stop_reason"]:
            case "end_turn" | "stop_sequence":
                return "stop"
            case "max_tokens":
                return "length"
            case "tool_use":
                return "tool_calls"
            case _:
                raise AssertionError(f"unknown anthropic stop_reason `{response['stop_reason']}`")
    elif "done_reason" in response.keys():  # Ollama response
        match response["done_reason"]:
            case "length":
                return "length"
            case "stop":
                return "stop"
            case _:
                raise AssertionError(f"unknown ollama done_reason `{response['done_reason']}`")
    elif "stopReason" in response.keys():  # AWS Bedrock response
        match response["stopReason"]:
            case "end_turn" | "stop_sequence":
                return "stop"
            case "max_tokens":
                return "length"
            case "tool_use":
                return "tool_calls"
            case _:
                raise AssertionError(f"unknown aws bedrock stopReason `{response['stopReason']}`")
    else:
        return None
