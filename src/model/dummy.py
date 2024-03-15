from .model import Model


class DummyModel(Model):
    def __init__(self, answer: str) -> None:
        super().__init__()
        self._answer = answer

    def prompt(self, prompt: str) -> str:
        return self._answer

    def reset(self) -> None:
        pass

    def report_api_usage(self) -> str:
        return "dummy model; no API usage"
