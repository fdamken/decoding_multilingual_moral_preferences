import logging
import os
from enum import Enum
from logging import Logger
from typing import Final

import google.generativeai as genai
from openai.types.chat import ChatCompletionMessageParam
from tenacity import retry, wait_random_exponential

from api_usage import APIUsage
from experiment import ex
from noop import NoOp
from .model import Model


class OpenAIRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class GoogleModel(Model):
    SUPPORTED_MODELS: Final[set[str]] = {
        # gpt-4 is way too expensive (roughly $7k for all languages combined)
        # # https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo
        # "gpt-4-0125-preview",  # latest gpt-4-turbo with pinned version
        # "gpt-4-0613",  # latest gpt-4 with pinned version
        # https://platform.openai.com/docs/models/gpt-3-5-turbo
        "gpt-3.5-turbo-0125",  # latest gpt-3.5-turbo with pinned version
    }

    _model_name: str

    _chat: genai.ChatSession
    _history: list[ChatCompletionMessageParam]

    def __init__(self, model_name: str):
        super().__init__()
        self._model_name = model_name
        logging.getLogger("httpx").setLevel(logging.WARNING)  # reduce logging verbosity

    def prompt(self, prompt: str) -> str:
        return self._fetch(prompt)

    @ex.capture
    def reset(self, language: str) -> None:
        if self.dry_run:
            # make sure no real API calls are made in dry run
            # noinspection PyTypeChecker
            self._chat = NoOp()
        else:
            api_key = os.getenv("GOOGLE_API_KEY")
            assert api_key, "GOOGLE_API_KEY environment variable not set or empty"
            genai.configure(api_key=api_key)
            self._chat = genai.GenerativeModel(
                self._model_name,
                generation_config=genai.GenerationConfig(
                    candidate_count=1,  # generate a single completion
                    max_output_tokens=1,  # generate at most one token (we just want a single number, 1 or 2)
                ),
            ).start_chat(
                history=[dict(
                    role="user",
                    parts=[self.system_prompt],
                )],
            )

    def report_api_usage(self) -> APIUsage:
        return APIUsage(f"google_{self._model_name}", 0, 0, 0.)

    @retry(wait=wait_random_exponential(min=1, max=60))
    @ex.capture
    def _fetch(self, prompt: str, _log: Logger) -> str:
        if self.dry_run:
            return "?"  # dry run, return a placeholder
        response = self._chat.send_message(prompt)
        return response.text
