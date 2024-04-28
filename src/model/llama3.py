from logging import Logger

import torch
import transformers
from transformers import Conversation

from api_usage import APIUsage
from experiment import ex
from .model import Model


class Llama3Model(Model):
    _model_config = {
        "Meta-Llama-3-8B-Instruct": "meta-llama/Meta-Llama-3-8B-Instruct",
        "Meta-Llama-3-70B-Instruct": "meta-llama/Meta-Llama-3-70B-Instruct",
    }

    SUPPORTED_MODELS = set(_model_config.keys())

    _model_name: str

    _chatbot: transformers.Pipeline
    _conversation: Conversation

    def __init__(self, model_name: str):
        super().__init__()
        self._model_name = model_name
        self._init_model()

    def _init_model(self) -> None:
        self._chatbot = transformers.pipeline(
            task="conversation",
            model=self._model_config[self._model_name],
            model_kwargs={"torch_dtype": torch.bfloat16},
        )

    def prompt(self, prompt: str) -> str:
        self._conversation.add_message({"role": "user", "content": prompt})
        message = self._complete()
        return message

    @ex.capture
    def reset(self, _log: Logger) -> None:
        self._conversation = Conversation()
        self._conversation.add_message({"role": "system", "content": self.system_prompt})

    def _complete(self) -> str:
        self._chatbot(
            self._conversation,
            max_new_tokens=10,
            eos_token_id=[
                self._chatbot.tokenizer.eos_token_id,
                self._chatbot.tokenizer.convert_tokens_to_ids("<|eot_id|>")
            ],
            do_sample=False,
        )
        return self._conversation.messages[-1]["content"]

    def report_api_usage(self) -> APIUsage:
        return APIUsage(self._model_name, -1, -1, 0.)
