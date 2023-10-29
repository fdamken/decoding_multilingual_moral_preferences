from typing import Callable, Final, Type

from model.dummy_model import DummyModel
from model.model import Model

_model_maker_registry: dict[str, Callable[[], Model]] = {}


def get_available_models() -> list[str]:
    return list(_model_maker_registry.keys())


def make_model(name: str) -> Model:
    assert name in _model_maker_registry, f"model '{name}' not available"
    return _model_maker_registry[name]()


def model_maker(name: str) -> Callable[[Callable[[], Model]], Model]:
    def model_maker_decorator(func: Callable[[], Model]) -> Model:
        _model_maker_registry[name] = func
        return func()

    return model_maker_decorator


@model_maker("dummy")
def make_dummy():
    return DummyModel("1")
