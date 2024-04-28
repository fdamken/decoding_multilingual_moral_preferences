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


class Llama3Model(Model):
    _model_config = {
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
            device_map="auto",
        )

    def prompt(self, prompt: str) -> str:
        self._history.append(ChatMessage(ChatRole.USER, prompt))
        complete = self._complete()
        print("complete:", repr(complete))
        quit()
        self._history.append(ChatMessage(ChatRole.ASSISTANT, message))
        return message

    @ex.capture
    def reset(self, _log: Logger) -> None:
        self._history = [ChatMessage(ChatRole.SYSTEM, self.system_prompt)]

    def _complete(self) -> str:
        prompt = self._pipe.tokenizer.apply_chat_template(
            [msg.to_dict() for msg in self._history],
            tokenize=False,
            add_generation_prompt=True
        )
        return self._pipe(
            prompt,
            max_new_tokens=10,
            eos_token_id=[
                self._pipe.tokenizer.eos_token_id,
                self._pipe.tokenizer.convert_tokens_to_ids("<|eot_id|>")
            ],
            do_sample=True,
            temperature=0.,
            top_p=.9,
        )[0]["generated_text"]

    def report_api_usage(self) -> APIUsage:
        return APIUsage(self._model_name, -1, -1, 0.)
