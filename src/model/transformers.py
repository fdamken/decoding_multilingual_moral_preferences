from logging import Logger
from typing import Final

import transformers

from api_usage import APIUsage
from experiment import ex
from .model import Model


class TransformersModel(Model):
    _model_config = {
        "Llama-2-7b-chat-hf": "meta-llama/Llama-2-7b-chat-hf",
        "Llama-2-13b-chat-hf": "meta-llama/Llama-2-13b-chat-hf",
        "Llama-2-70b-chat-hf": "meta-llama/Llama-2-70b-chat-hf",
    }

    SUPPORTED_MODELS: Final[set[str]] = set(_model_config.keys())

    _model_name: str

    _pipe: transformers.Pipeline
    _history: list[str]

    def __init__(self, model_name: str):
        super().__init__()
        self._model_name = model_name
        self._pipe = transformers.pipeline("text-generation", self._model_config[self._model_name], trust_remote_code=True)

    def prompt(self, prompt: str) -> str:
        self._history.append(prompt)
        message = self._complete()
        self._history.append(message)
        return message

    @ex.capture
    def reset(self, _log: Logger) -> None:
        self._history = [self.system_prompt]

    def _complete(self) -> str:
        return self._pipe(
            "\n\n".join(self._history),
            max_new_tokens=1,
            do_sample=True,
            use_cache=True,
        )

    def report_api_usage(self) -> APIUsage:
        return APIUsage(self._model_name, -1, -1, 0.)
