from logging import Logger
from typing import Final

import torch
import transformers

from api_usage import APIUsage
from experiment import ex
from .model import Model


class MPTModel(Model):
    _model_config = {
        # https://huggingface.co/mosaicml/mpt-7b-8k-chat
        "mpt-7b-8k-chat": dict(tokenizer="mosaicml/mpt-7b-8k", model="mosaicml/mpt-7b-chat-8k"),
        # https://huggingface.co/mosaicml/mpt-30b-chat
        "mpt-30b-chat": dict(tokenizer="mosaicml/mpt-30b", model="mosaicml/mpt-30b-chat"),
    }

    SUPPORTED_MODELS: Final[set[str]] = set(_model_config.keys())

    _model_name: str

    _pipe: transformers.Pipeline
    _history: list[str]

    def __init__(self, model_name: str):
        super().__init__()

        self._model_name = model_name

        self._device = "cuda"

        config = transformers.AutoConfig.from_pretrained(
            self._model_config[self._model_name]["model"],
            trust_remote_code=True,
        )
        config.init_device = self._device
        config.max_seq_len = 16384
        model = transformers.AutoModelForCausalLM.from_pretrained(
            self._model_config[self._model_name]["model"],
            config=config,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
        )
        tokenizer = transformers.AutoTokenizer.from_pretrained(self._model_config[self._model_name]["tokenizer"])
        self._pipe = transformers.pipeline("text-generation", model=model, tokenizer=tokenizer, device=self._device)

    def prompt(self, prompt: str) -> str:
        self._history.append(prompt)
        message = self._complete()
        self._history.append(message)
        return message

    @ex.capture
    def reset(self, _log: Logger) -> None:
        self._history = [self.system_prompt]

    def _complete(self) -> str:
        with torch.autocast(self._device, dtype=torch.bfloat16):
            result = self._pipe(
                "\n\n".join(self._history),
                max_new_tokens=1,
                do_sample=True,
                use_cache=True,
            )
        return result

    def report_api_usage(self) -> APIUsage:
        return APIUsage(self._model_name, -1, -1, 0.)
