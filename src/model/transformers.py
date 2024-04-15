from dataclasses import dataclass
from enum import StrEnum
from logging import Logger
from typing import Optional

import transformers

from api_usage import APIUsage
from experiment import ex
from .model import Model


class ChatRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class ChatMessage:
    role: ChatRole
    message: Optional[str]

    def __str__(self) -> str:
        prefix = f"<|im_start|>{self.role}"
        if self.message is None:
            return f"{prefix}\n\n"
        return f"{prefix}\n{self.message}<|im_end|>\n"


class TransformersModel(Model):
    _model_config = {
        "Llama-2-7b-chat-hf": "meta-llama/Llama-2-7b-chat-hf",
        "Llama-2-13b-chat-hf": "meta-llama/Llama-2-13b-chat-hf",
        "Llama-2-70b-chat-hf": "meta-llama/Llama-2-70b-chat-hf",
    }

    SUPPORTED_MODELS = set(_model_config.keys())

    _model_name: str

    _pipe: transformers.Pipeline
    _history: list[ChatMessage]

    def __init__(self, model_name: str):
        super().__init__()
        self._model_name = model_name
        self._init_model()

    def _init_model(self) -> None:
        self._pipe = transformers.pipeline("text-generation", self._model_config[self._model_name], trust_remote_code=True)

    def prompt(self, prompt: str) -> str:
        self._history.append(ChatMessage(ChatRole.USER, prompt + f"\n\n{self.reinforcement_prompt}"))
        message = self._complete().split("<|im_start|>assistant")[-1].split("<|im_end|>")[0].strip()
        print("message:", repr(message))
        quit()
        self._history.append(ChatMessage(ChatRole.ASSISTANT, message))
        return message

    @ex.capture
    def reset(self, _log: Logger) -> None:
        self._history = [ChatMessage(ChatRole.SYSTEM, self.system_prompt)]

    def _complete(self) -> str:
        return self._pipe(
            "\n".join([str(message) for message in self._history + [ChatMessage(ChatRole.ASSISTANT, None)]]),
            max_new_tokens=10,
            do_sample=True,
            use_cache=True,
        )[0]["generated_text"]

    def report_api_usage(self) -> APIUsage:
        return APIUsage(self._model_name, -1, -1, 0.)
