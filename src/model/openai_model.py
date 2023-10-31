import json
import os
from enum import Enum
from typing import Final

import openai

import path_util
from experiment import ex
from model.model import Model


class OpenAIRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class OpenAIModel(Model):
    def __init__(self, model_name: str):
        super().__init__()
        self._model_name = model_name
        self._system_prompt = self._load_system_prompt()
        self._history = []

    @staticmethod
    def authenticate() -> None:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        assert openai_api_key, "OPENAI_API_KEY environment variable not set"
        openai.api_key = openai_api_key

    def prompt(self, prompt: str) -> str:
        self._add(OpenAIRole.USER, prompt)
        message = openai.ChatCompletion.create(
            model=self._model_name,
            messages=self._history,
            temperature=.5,  # TODO: What is a good temperature value?
        ).choices[0].message.content
        self._add(OpenAIRole.ASSISTANT, message)
        return message

    @ex.capture
    def reset(self, language: str) -> None:
        self._history = []
        self._add(OpenAIRole.SYSTEM, self._system_prompt)

    def _add(self, role: OpenAIRole, content: str) -> None:
        self._history.append(dict(role=role.value, content=content))

    @ex.capture
    def _load_system_prompt(self, language: str) -> str:
        with open(path_util.data_dir / "system_prompts.json") as f:
            system_prompts = json.load(f)
        system_prompt = system_prompts.get(language)
        assert system_prompt, f"no system prompt for language '{language}'"
        return system_prompt
