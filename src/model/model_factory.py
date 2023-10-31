from logging import Logger
from typing import Callable

from experiment import ex
from model.dummy_model import DummyModel
from model.model import Model
from model.openai_model import OpenAIModel

_model_maker_registry: dict[str, Callable[[], Model]] = {}


def get_available_models() -> list[str]:
    return list(_model_maker_registry.keys())


@ex.capture
def make_model(name: str, *, _log: Logger) -> Model:
    assert name in _model_maker_registry, f"model '{name}' not available"
    _log.info(f"creating model '{name}'")
    return _model_maker_registry[name]()


def model_maker(name: str) -> Callable[[Callable[[], Model]], Callable[[], Model]]:
    def model_maker_decorator(func: Callable[[], Model]) -> Callable[[], Model]:
        # this code is run before the experiment starts, so ex.logger is not available yet
        print(f"registering model '{name}'")
        _model_maker_registry[name] = func
        return func

    return model_maker_decorator


@model_maker("dummy")
def make_dummy():
    return DummyModel("1")


for _model_name in ["gpt-3.5-turbo"]:
    @model_maker(_model_name)
    @ex.capture
    def make_openai_model(_log: Logger) -> OpenAIModel:
        OpenAIModel.authenticate()  # authenticate first to fail fast
        _log.info(f"creating openai-model '{_model_name}'")
        return OpenAIModel(_model_name)
