from dataclasses import dataclass
from enum import StrEnum
from logging import Logger

import torch
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
    content: str

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}


class TransformersModel(Model):
    _model_config = {
        "falcon-7b-instruct": "tiiuae/falcon-7b-instruct",
        "falcon-40b-instruct": "tiiuae/falcon-40b-instruct",
        "falcon-180B-chat": "tiiuae/falcon-180B-chat",
        "Llama-2-7b-chat-hf": "meta-llama/Llama-2-7b-chat-hf",
        "Llama-2-13b-chat-hf": "meta-llama/Llama-2-13b-chat-hf",
        "Llama-2-70b-chat-hf": "meta-llama/Llama-2-70b-chat-hf",
        "Meta-Llama-3-8B-Instruct": "meta-llama/Meta-Llama-3-8B-Instruct",
        "Meta-Llama-3-70B-Instruct": "meta-llama/Meta-Llama-3-70B-Instruct",
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
        self._pipe = transformers.pipeline(
            "text-generation",
            model=self._model_config[self._model_name],
            model_kwargs={"torch_dtype": torch.bfloat16},
            trust_remote_code=True,
        )

    def prompt(self, prompt: str) -> str:
        self._history.append(ChatMessage(ChatRole.USER, prompt))
        message = self._complete()
        self._history.append(ChatMessage(ChatRole.ASSISTANT, message))
        return message

    @ex.capture
    def reset(self, _log: Logger) -> None:
        self._history = [ChatMessage(ChatRole.SYSTEM, self.system_prompt)]

    def _complete(self) -> str:
        prompt = self._pipe.tokenizer.apply_chat_template(
            [msg.to_dict() for msg in self._history],
            tokenize=False,
            add_generation_prompt=True,
        )
        eos_token_id = [self._pipe.tokenizer.eos_token_id]
        if eot_id := self._pipe.tokenizer.convert_tokens_to_ids("<|eot_id|>"):
            eos_token_id.append(eot_id)
        return self._pipe(
            prompt,
            max_new_tokens=1,
            eos_token_id=eos_token_id,
            do_sample=False,
        )[0]["generated_text"][len(prompt):]

    def report_api_usage(self) -> APIUsage:
        return APIUsage(self._model_name, -1, -1, 0.)
