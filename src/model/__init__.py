from logging import Logger
from typing import Callable

from experiment import ex
from .dummy import DummyModel
from .model import Model
from .openai import OpenAIModel

_model_maker_registry: dict[str, Callable[[], Model]] = {}


def get_available_models() -> list[str]:
    return list(_model_maker_registry.keys())


@ex.capture
def make_model(name: str, *, _log: Logger) -> Model:
    assert name in _model_maker_registry, f"model '{name}' not available"
    _log.debug(f"creating model '{name}'")
    return _model_maker_registry[name]()


def model_maker(name: str) -> Callable[[Callable[[], Model]], Callable[[], Model]]:
    def model_maker_decorator(func: Callable[[], Model]) -> Callable[[], Model]:
        # this code is run before the experiment starts, so ex.logger is not available yet
        _model_maker_registry[name] = func
        return func

    return model_maker_decorator


@model_maker("dummy")
def make_dummy():
    return DummyModel("1")


def _register_openai_model(model_name: str) -> None:
    @model_maker(model_name)
    @ex.capture
    def make_openai_model(_log: Logger) -> OpenAIModel:
        _log.debug(f"creating OpenAI model '{model_name}'")
        return OpenAIModel(model_name)


for _model_name in OpenAIModel.SUPPORTED_MODELS:
    _register_openai_model(_model_name)

__all__ = [
    "Model",
    "get_available_models",
    "make_model",
]
