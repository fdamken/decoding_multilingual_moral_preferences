import logging
import os
from enum import Enum
from logging import Logger
from typing import Final

import openai
import tiktoken
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from tenacity import retry, retry_if_exception_type, wait_random_exponential

from api_usage import APIUsage
from experiment import ex
from noop import NoOp
from rate_limit import RateLimit
from .model import Model


class OpenAIRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class OpenAIModel(Model):
    SUPPORTED_MODELS: Final[set[str]] = {
        # # https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo
        # "gpt-4-0125-preview",  # latest gpt-4-turbo with pinned version
        "gpt-4-0613",  # latest gpt-4 with pinned version
        # https://platform.openai.com/docs/models/gpt-3-5-turbo
        "gpt-3.5-turbo-0125",  # latest gpt-3.5-turbo with pinned version
    }

    _model_name: str

    _openai: OpenAI
    _history: list[ChatCompletionMessageParam]

    def __init__(self, model_name: str):
        super().__init__()
        self._model_name = model_name
        logging.getLogger("httpx").setLevel(logging.WARNING)  # reduce logging verbosity

    def prompt(self, prompt: str) -> str:
        self._add(OpenAIRole.USER, prompt)
        message = self._fetch()
        self._add(OpenAIRole.ASSISTANT, message)
        return message

    @ex.capture
    def reset(self, language: str) -> None:
        if self.dry_run:
            # make sure no real API calls are made in dry run
            # noinspection PyTypeChecker
            self._openai = NoOp()
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            assert api_key, "OPENAI_API_KEY environment variable not set or empty"
            self._openai = OpenAI(api_key=api_key)
        self._history = []
        self._add(OpenAIRole.SYSTEM, self.system_prompt)

    def report_api_usage(self) -> APIUsage:
        # input_token_cost and output_token_cost are $ / 1M tokens
        match self._model_name:
            case "gpt-4-0125-preview":
                input_token_cost = 30.
                output_token_cost = 60.
            case "gpt-4-0613":
                input_token_cost = 30.
                output_token_cost = 60.
            case "gpt-3.5-turbo-0125":
                input_token_cost = .5
                output_token_cost = 1.5
            case _:
                assert False, f"unsupported model: {self._model_name}"
        cost = (self._num_input_tokens * input_token_cost + self._num_output_tokens * output_token_cost) / 1_000_000
        return APIUsage(self._model_name, self._num_input_tokens, self._num_output_tokens, cost)

    @retry(wait=wait_random_exponential(min=1, max=60), retry=retry_if_exception_type(openai.RateLimitError))
    @ex.capture
    def _fetch(self, _log: Logger) -> str:
        if not self.dry_run:
            RateLimit.wait(500, 60)

        estimated_num_input_tokens, estimated_num_output_tokens = self._estimate_tokens()

        if self.dry_run:
            self._num_input_tokens += estimated_num_input_tokens
            self._num_output_tokens += estimated_num_output_tokens
            return "?"  # dry run, return a placeholder
        response = self._openai.chat.completions.create(
            messages=self._history,
            model=self._model_name,
            max_tokens=1,  # generate at most one token (we just want a single number, 1 or 2)
            n=1,  # generate a single completion
            temperature=0,
        )

        num_input_tokens = response.usage.prompt_tokens
        num_output_tokens = response.usage.completion_tokens
        if num_input_tokens != estimated_num_input_tokens:
            _log.warning(f"expected {estimated_num_input_tokens} input tokens, got {num_input_tokens}")
        if num_output_tokens != estimated_num_output_tokens:
            _log.warning(f"expected {estimated_num_output_tokens} output tokens, got {num_output_tokens}")

        self._num_input_tokens += num_input_tokens
        self._num_output_tokens += num_output_tokens

        return response.choices[0].message.content

    def _add(self, role: OpenAIRole, content: str) -> None:
        self._history.append(dict(role=role.value, content=content))

    def _estimate_tokens(self) -> tuple[int, int]:
        encoding = tiktoken.encoding_for_model(self._model_name)
        num_tokens = 0
        for message in self._history:
            num_tokens += 3
            for value in message.values():
                num_tokens += len(encoding.encode(value))
        return num_tokens + 3, 1
