import torch
import transformers

from .transformers import TransformersModel


class MPTModel(TransformersModel):
    _model_config = {
        "mpt-7b-8k-chat": dict(tokenizer="mosaicml/mpt-7b-8k", model="mosaicml/mpt-7b-chat-8k"),
        "mpt-30b-chat": dict(tokenizer="mosaicml/mpt-30b", model="mosaicml/mpt-30b-chat"),
    }

    SUPPORTED_MODELS = set(_model_config.keys())

    def _init_model(self) -> None:
        config = transformers.AutoConfig.from_pretrained(
            self._model_config[self._model_name]["model"],
            trust_remote_code=True,
        )
        config.max_seq_len = 16384
        model = transformers.AutoModelForCausalLM.from_pretrained(
            self._model_config[self._model_name]["model"],
            config=config,
            torch_dtype=torch.float32,
            trust_remote_code=True,
        )
        tokenizer = transformers.AutoTokenizer.from_pretrained(self._model_config[self._model_name]["tokenizer"])
        self._pipe = transformers.pipeline("text-generation", model=model, tokenizer=tokenizer)
