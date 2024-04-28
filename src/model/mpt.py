from dataclasses import dataclass
from enum import StrEnum
from logging import Logger

import torch
import transformers
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

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


class MptModel(Model):
    _model_config = {
        "mpt-7b-8k-chat": "mosaicml/mpt-7b-8k-chat",
        "mpt-7b-chat": "mosaicml/mpt-7b-chat",
        "mpt-30b-instruct": "mosaicml/mpt-30b-instruct",
        "mpt-30b-chat": "mosaicml/mpt-30b-chat",
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
        model_name = self._model_config[self._model_name]
        config = AutoConfig.from_pretrained(model_name, trust_remote_code=True)
        config.max_seq_len = 16384
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            config=config,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
        )
        tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="left")
        tokenizer.chat_template = (
            "{% for message in messages %}"
            "{{'<|im_start|>' + message['role'] + '\n' + message['content'] + '<|im_end|>' + '\n'}}"
            "{% endfor %}"
            "{% if add_generation_prompt %}"
            "{{ '<|im_start|>assistant\n' }}"
            "{% endif %}"
        )
        self._pipe = transformers.pipeline("text-generation", model=model, tokenizer=tokenizer)

    def prompt(self, prompt: str) -> str:
        self._history.append(ChatMessage(ChatRole.USER, prompt))
        message = self._complete()
        print("message:", repr(message))
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
        print("prompt:", repr(prompt))
        eos_token_id = [self._pipe.tokenizer.eos_token_id]
        return self._pipe(
            prompt,
            max_new_tokens=50,
            eos_token_id=eos_token_id,
            do_sample=False,
        )[0]["generated_text"][len(prompt):]

    def report_api_usage(self) -> APIUsage:
        return APIUsage(self._model_name, -1, -1, 0.)
