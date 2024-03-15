import logging
import os
from logging import Logger
from typing import Final

import google.generativeai as genai
from google.generativeai.types import HarmBlockThreshold, HarmCategory

from api_usage import APIUsage
from experiment import ex
from noop import NoOp
from rate_limit import RateLimit
from .model import Model


class GoogleModel(Model):
    SUPPORTED_MODELS: Final[set[str]] = {
        # https://ai.google.dev/models/gemini
        "gemini-1.0-pro-001",  # latest gemini-pro with pinned version
    }

    _model_name: str

    _chat: genai.ChatSession

    def __init__(self, model_name: str):
        super().__init__()
        self._model_name = model_name
        logging.getLogger("httpx").setLevel(logging.WARNING)  # reduce logging verbosity

    def prompt(self, prompt: str) -> str:
        return self._fetch(prompt)

    @ex.capture
    def reset(self, language: str, _log: Logger) -> None:
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
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                },
                generation_config=genai.GenerationConfig(
                    candidate_count=1,  # generate a single completion
                    max_output_tokens=2,  # generate at most one token (we just want a single number, 1 or 2)
                ),
            ).start_chat()
        system_prompt_response = self._fetch(self.system_prompt)
        _log.debug(f"system prompt response: {system_prompt_response}")

    def report_api_usage(self) -> APIUsage:
        return APIUsage(f"google_{self._model_name}", -1, -1, -1.)

    @ex.capture
    def _fetch(self, prompt: str, _log: Logger) -> str:
        RateLimit.wait(60, 60)
        if self.dry_run:
            return "?"  # dry run, return a placeholder
        return self._chat.send_message(prompt).text
