import json
import logging
import os
from enum import Enum
from functools import cached_property
from logging import Logger
from typing import Final

import tiktoken
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from tenacity import retry, wait_random_exponential

import path_util
from api_usage import APIUsage
from experiment import ex
from .model import Model


class DryRunOpenAI(OpenAI):
    # noinspection PyMissingConstructor
    def __init__(self):
        pass

    def __getattr__(self, *args, **kwargs) -> None:
        raise NotImplementedError(f"__setattr__ in dry run ({args}, {kwargs})")

    def __setattr__(self, *args, **kwargs) -> None:
        raise NotImplementedError(f"__setattr__ in dry run ({args}, {kwargs})")


class OpenAIRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class OpenAIModel(Model):
    SUPPORTED_MODELS: Final[set[str]] = {
        # gpt-4 is way too expensive (roughly $7k for all languages combined)
        # # https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo
        # "gpt-4-0125-preview",  # latest gpt-4-turbo with pinned version
        # "gpt-4-0613",  # latest gpt-4 with pinned version
        # https://platform.openai.com/docs/models/gpt-3-5-turbo
        "gpt-3.5-turbo-0125",  # latest gpt-3.5-turbo with pinned version
    }

    _model_name: str
    _system_prompt: str
    _history: list[ChatCompletionMessageParam]
    _num_input_tokens: int
    _num_output_tokens: int

    _openai: OpenAI

    def __init__(self, model_name: str):
        super().__init__()

        self._model_name = model_name
        self._system_prompt = self._load_system_prompt()
        self._history = []
        self._num_input_tokens = 0
        self._num_output_tokens = 0

        # reduce logging verbosity
        logging.getLogger("httpx").setLevel(logging.WARNING)

    def prompt(self, prompt: str) -> str:
        self._add(OpenAIRole.USER, prompt)
        message = self._fetch()
        self._add(OpenAIRole.ASSISTANT, message)
        return message

    @ex.capture
    def reset(self, language: str) -> None:
        if self.dry_run:
            # replace OpenAI with a dry-run implementation to make sure no real
            # API calls are made
            self._openai = DryRunOpenAI()
        else:
            self._openai = OpenAI(api_key=self._api_key)
        self._history = []
        self._add(OpenAIRole.SYSTEM, self._system_prompt)

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
        return APIUsage(
            f"openai_{self._model_name}",
            self._num_input_tokens,
            self._num_output_tokens,
            cost,
        )

    @retry(wait=wait_random_exponential(min=1, max=60))
    @ex.capture
    def _fetch(self, _log: Logger) -> str:
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
        num_tokens = 0
        for message in self._history:
            num_tokens += 3
            for value in message.values():
                num_tokens += len(self._token_encoding.encode(value))
        return num_tokens + 3, 1

    @ex.capture
    def _load_system_prompt(self, language: str) -> str:
        with open(path_util.data_dir / "system_prompts.json") as f:
            system_prompts = json.load(f)
        system_prompt = system_prompts.get(language)
        assert system_prompt, f"no system prompt for language '{language}'"
        return system_prompt

    @cached_property
    def _token_encoding(self) -> tiktoken.Encoding:
        return tiktoken.encoding_for_model(self._model_name)

    @cached_property
    def _api_key(self) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        assert api_key, "OPENAI_API_KEY environment variable not set or empty"
        return api_key
