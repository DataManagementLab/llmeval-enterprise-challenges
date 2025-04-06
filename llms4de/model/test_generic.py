import logging
import os
import pathlib

import pytest
import requests

from llms4de.model.generic import num_tokens, execute_requests, extract_text_from_response, \
    extract_finish_reason_from_response, max_tokens_for_ground_truth, prepare_for_anthropic, prepare_for_ollama

logger = logging.getLogger(__name__)

openai_available = "OPENAI_API_KEY" in os.environ.keys()
anthropic_available = "ANTHROPIC_API_KEY" in os.environ.keys()
hf_available = "HF_TOKEN" in os.environ.keys()
aicore_available = pathlib.Path("key.json").is_file()

try:
    requests.post(url="http://localhost:11434/api/chat", timeout=1)
    ollama_available = True
except requests.exceptions.ConnectionError:
    ollama_available = False
except:
    ollama_available = True


def test_prepare_for_anthropic() -> None:
    request = {"model": "claude-3-5-sonnet-20241022", "max_tokens": None}
    assert prepare_for_anthropic(request) == {"model": "claude-3-5-sonnet-20241022", "max_tokens": 8_192}

    request = {"model": "claude-3-5-sonnet-20241022"}
    assert prepare_for_anthropic(request) == {"model": "claude-3-5-sonnet-20241022", "max_tokens": 8_192}

    with pytest.raises(AssertionError):
        prepare_for_anthropic({"model": "gpt-4o-mini-2024-07-18", "max_tokens": None})


def test_prepare_for_ollama() -> None:
    request = {"model": "llama3.1:70b-instruct-fp16", "max_tokens": 100}
    out = {"model": "llama3.1:70b-instruct-fp16", "options": {"num_predict": 100, "num_ctx": 128_000}, "stream": False}
    assert prepare_for_ollama(request) == out

    request = {"model": "llama3.1:70b-instruct-fp16", "max_completion_tokens": 100}
    out = {"model": "llama3.1:70b-instruct-fp16", "options": {"num_predict": 100, "num_ctx": 128_000}, "stream": False}
    assert prepare_for_ollama(request) == out

    request = {"model": "llama3.1:70b-instruct-fp16", "max_tokens": None}
    out = {"model": "llama3.1:70b-instruct-fp16", "options": {"num_ctx": 128_000}, "stream": False}
    assert prepare_for_ollama(request) == out

    request = {"model": "llama3.1:70b-instruct-fp16", "seed": 1234}
    out = {"model": "llama3.1:70b-instruct-fp16", "options": {"seed": 1234, "num_ctx": 128_000}, "stream": False}
    assert prepare_for_ollama(request) == out

    request = {"model": "llama3.1:70b-instruct-fp16", "temperature": 0}
    out = {"model": "llama3.1:70b-instruct-fp16", "options": {"temperature": 0, "num_ctx": 128_000}, "stream": False}
    assert prepare_for_ollama(request) == out


models_api_names = [
    pytest.param(
        "gpt-4o-mini-2024-07-18", "openai",
        marks=pytest.mark.xfail(not openai_available, reason="cannot execute without openai")
    ),
    pytest.param(
        "gpt-4o-2024-08-06", "openai",
        marks=pytest.mark.xfail(not openai_available, reason="cannot execute without openai")
    ),
    pytest.param(
        "claude-3-5-haiku-20241022", "anthropic",
        marks=pytest.mark.xfail(not anthropic_available, reason="cannot execute without anthropic")
    ),
    pytest.param(
        "claude-3-5-sonnet-20241022", "anthropic",
        marks=pytest.mark.xfail(not anthropic_available, reason="cannot execute without anthropic")
    ),
    pytest.param(
        "llama3.1:8b-instruct-fp16", "ollama",
        marks=pytest.mark.xfail(
            not (ollama_available and hf_available),
            reason="cannot execute without ollama and huggingface"
        )
    ),
    pytest.param(
        "llama3.1:70b-instruct-fp16", "ollama",
        marks=pytest.mark.xfail(
            not (ollama_available and hf_available),
            reason="cannot execute without ollama and huggingface"
        )
    ),
    pytest.param(
        "gpt-4o-mini-2024-07-18", "aicore",
        marks=pytest.mark.xfail(not aicore_available, reason="cannot execute without aicore")
    ),
    pytest.param(
        "gpt-4o-2024-08-06", "aicore",
        marks=pytest.mark.xfail(not aicore_available, reason="cannot execute without aicore")
    ),
    pytest.param(
        "claude-3-5-haiku-20241022", "aicore",
        marks=pytest.mark.xfail(not aicore_available, reason="cannot execute without aicore")
    ),
    pytest.param(
        "claude-3-5-sonnet-20241022", "aicore",
        marks=pytest.mark.xfail(not aicore_available, reason="cannot execute without aicore")
    ),
    pytest.param(
        "llama3.1:8b-instruct-fp16", "aicore",
        marks=pytest.mark.xfail(
            not (aicore_available and hf_available),
            reason="cannot execute without aicore and huggingface"
        )
    ),
    pytest.param(
        "llama3.1:70b-instruct-fp16", "aicore",
        marks=pytest.mark.xfail(
            not (aicore_available and hf_available),
            reason="cannot execute without aicore and huggingface"
        )
    )
]


@pytest.mark.parametrize("model,api_name", models_api_names)
def test_num_tokens(model: str, api_name: str) -> None:
    assert num_tokens("", model, api_name) == 0
    assert num_tokens("the", model, api_name) == 1


def test_num_tokens_wrong_model_api() -> None:
    with pytest.raises(AssertionError):
        num_tokens("", "asdf", "openai")

    with pytest.raises(AssertionError):
        num_tokens("", "asdf", "anthropic")

    with pytest.raises(AssertionError):
        num_tokens("", "asdf", "ollama")

    with pytest.raises(AssertionError):
        num_tokens("", "asdf", "asdf")


@pytest.mark.parametrize("model,api_name", models_api_names)
def test_max_tokens_for_ground_truth(model: str, api_name: str) -> None:
    assert max_tokens_for_ground_truth("", api_name, model, None) is None
    assert max_tokens_for_ground_truth("", api_name, model, 10) == 10
    assert max_tokens_for_ground_truth("hello", api_name, model, 10) == 11


requests_api_names = []
for param in models_api_names:
    request_1 = {
        "model": param.values[0],
        "max_tokens": 10,
        "temperature": 0,
        "messages": [{"role": "user", "content": "Name all prime numbers below 10!"}],
        "seed": 321164097
    }
    request_2 = {
        "model": param.values[0],
        "max_completion_tokens": 10,
        "temperature": 0,
        "messages": [{"role": "user", "content": "Name all prime numbers below 10!"}],
        "seed": 321164097
    }
    requests_api_names.append(pytest.param([request_1, request_2], param.values[1], marks=param.marks))


@pytest.mark.parametrize("requests,api_name", requests_api_names)
def test_execute_requests(requests: list[dict], api_name: str) -> None:
    responses = execute_requests(requests, api_name)
    assert isinstance(responses, list)
    assert isinstance(extract_text_from_response(responses[0]), str)  # check that request was successful


def test_execute_requests_unknown_api() -> None:
    with pytest.raises(AssertionError):
        execute_requests([], api_name="asdf")


def test_extract_text_from_response() -> None:
    # OpenAI response
    assert extract_text_from_response({
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4o-mini",
        "system_fingerprint": "fp_44709d6fcb",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "This is the response.",
            },
            "logprobs": None,
            "finish_reason": "stop"
        }],
        "service_tier": "default",
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21,
            "completion_tokens_details": {
                "reasoning_tokens": 0,
                "accepted_prediction_tokens": 0,
                "rejected_prediction_tokens": 0
            }
        }
    }) == "This is the response."

    # Anthropic response
    assert extract_text_from_response({
        "content": [
            {
                "text": "This is the response.",
                "type": "text"
            }
        ],
        "id": "msg_013Zva2CMHLNnXjNJJKqJ2EF",
        "model": "claude-3-5-sonnet-20241022",
        "role": "assistant",
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "type": "message",
        "usage": {
            "input_tokens": 2095,
            "output_tokens": 503
        }
    }) == "This is the response."

    # Ollama response
    assert extract_text_from_response({
        "model": "llama3.1:8b-instruct-fp16",
        "created_at": "2025-02-10T09:39:16.328944308Z",
        "message":
            {
                "role": "assistant",
                "content": "This is the response."
            },
        "done_reason": "length",
        "done": True,
        "total_duration": 3148156471,
        "load_duration": 23135820,
        "prompt_eval_count": 18,
        "prompt_eval_duration": 70000000,
        "eval_count": 100,
        "eval_duration": 1992000000
    }) == "This is the response."

    # AWS Bedrock response
    assert extract_text_from_response({
        "output": {
            "message": {
                "content": [
                    {
                        "text": "This is the response."
                    }
                ],
                "role": "assistant"
            }
        },
        "stopReason": "end_turn",
        "usage": {
            "inputTokens": 30,
            "outputTokens": 628,
            "totalTokens": 658
        },
        "metrics": {
            "latencyMs": 1275
        }
    }) == "This is the response."

    # failed response
    assert extract_text_from_response({}) is None


def test_extract_finish_reason_from_response() -> None:
    # OpenAI response
    assert extract_finish_reason_from_response({
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4o-mini",
        "system_fingerprint": "fp_44709d6fcb",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "This is the response.",
            },
            "logprobs": None,
            "finish_reason": "stop"
        }],
        "service_tier": "default",
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21,
            "completion_tokens_details": {
                "reasoning_tokens": 0,
                "accepted_prediction_tokens": 0,
                "rejected_prediction_tokens": 0
            }
        }
    }) == "stop"

    # Anthropic response
    assert extract_finish_reason_from_response({
        "content": [
            {
                "text": "This is the response.",
                "type": "text"
            }
        ],
        "id": "msg_013Zva2CMHLNnXjNJJKqJ2EF",
        "model": "claude-3-5-sonnet-20241022",
        "role": "assistant",
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "type": "message",
        "usage": {
            "input_tokens": 2095,
            "output_tokens": 503
        }
    }) == "stop"

    # test Anthropic mapping to OpenAI
    assert extract_finish_reason_from_response({"stop_reason": "end_turn"}) == "stop"
    assert extract_finish_reason_from_response({"stop_reason": "max_tokens"}) == "length"
    assert extract_finish_reason_from_response({"stop_reason": "stop_sequence"}) == "stop"
    assert extract_finish_reason_from_response({"stop_reason": "tool_use"}) == "tool_calls"

    with pytest.raises(AssertionError):
        extract_finish_reason_from_response({"stop_reason": "asdf"})

    # Ollama response
    assert extract_finish_reason_from_response({
        "model": "llama3.1:8b-instruct-fp16",
        "created_at": "2025-02-10T09:39:16.328944308Z",
        "message":
            {
                "role": "assistant",
                "content": "This is the response."
            },
        "done_reason": "length",
        "done": True,
        "total_duration": 3148156471,
        "load_duration": 23135820,
        "prompt_eval_count": 18,
        "prompt_eval_duration": 70000000,
        "eval_count": 100,
        "eval_duration": 1992000000
    }) == "length"

    # test Ollama mapping to OpenAI
    assert extract_finish_reason_from_response({"done_reason": "length"}) == "length"
    assert extract_finish_reason_from_response({"done_reason": "stop"}) == "stop"

    with pytest.raises(AssertionError):
        extract_finish_reason_from_response({"done_reason": "asdf"})

    # AWS Bedrock response
    assert extract_finish_reason_from_response({
        "output": {
            "message": {
                "content": [
                    {
                        "text": "<text generated by the model>"
                    }
                ],
                "role": "assistant"
            }
        },
        "stopReason": "end_turn",
        "usage": {
            "inputTokens": 30,
            "outputTokens": 628,
            "totalTokens": 658
        },
        "metrics": {
            "latencyMs": 1275
        }
    }) == "stop"

    # test AWS Bedrock mapping to OpenAI
    assert extract_finish_reason_from_response({"stopReason": "end_turn"}) == "stop"
    assert extract_finish_reason_from_response({"stopReason": "max_tokens"}) == "length"
    assert extract_finish_reason_from_response({"stopReason": "stop_sequence"}) == "stop"
    assert extract_finish_reason_from_response({"stopReason": "tool_use"}) == "tool_calls"

    with pytest.raises(AssertionError):
        extract_finish_reason_from_response({"stop_reason": "asdf"})

    # failed response
    assert extract_finish_reason_from_response({}) is None
