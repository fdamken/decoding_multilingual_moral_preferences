import numpy as np

from api_usage import APIUsage
from .model import Model


class MockModel(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._generator = np.random.default_rng(seed=0)

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def prompt(self, prompt: str) -> str:
        return self._generator.choice(["1", "2"])

    def reset(self) -> None:
        pass

    def report_api_usage(self) -> APIUsage:
        return APIUsage("mock", 0, 0, 0.)
