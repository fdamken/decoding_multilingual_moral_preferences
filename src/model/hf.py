import os
from logging import Logger
from typing import Final

import requests
import transformers

from api_usage import APIUsage
from experiment import ex
from .model import Model


class HFModel(Model):
    _model_config = {
        # https://huggingface.co/meta-llama/Llama-2-7b-chat-hf
        "Llama-2-7b-chat-hf": dict(organization="meta-llama", model="Llama-2-7b-chat-hf"),
        # https://huggingface.co/meta-llama/Llama-2-13b-chat-hf
        "Llama-2-13b-chat-hf": dict(organization="meta-llama", model="Llama-2-13b-chat-hf"),
        # https://huggingface.co/meta-llama/Llama-2-70b-chat-hf
        "Llama-2-70b-chat-hf": dict(organization="meta-llama", model="Llama-2-70b-chat-hf"),
    }

    SUPPORTED_MODELS: Final[set[str]] = set(_model_config.keys())

    _organization: str
    _model_name: str

    _api_key: str
    _history: list[str]

    def __init__(self, model_name: str):
        super().__init__()

        self._organization = self._model_config[model_name]["organization"]
        self._model_name = self._model_config[model_name]["model"]

        api_key = os.getenv("HUGGINGFACE_API_KEY")
        assert api_key, "HUGGINGFACE_API_KEY environment variable not set or empty"
        self._api_key = api_key

    def prompt(self, prompt: str) -> str:
        self._history.append(prompt)
        message = self._complete()
        self._history.append(message)
        return message

    @ex.capture
    def reset(self, _log: Logger) -> None:
        self._history = []

    def _complete(self) -> str:
        result = requests.post(
            f"https://api-inference.huggingface.co/models/{self._organization}/{self._model_name}",
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={
                "inputs": "abc",
            }
        ).json()
        return result

    def report_api_usage(self) -> APIUsage:
        return APIUsage(self._model_name, -1, -1, 0.)
