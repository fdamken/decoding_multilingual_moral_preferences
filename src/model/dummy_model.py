from model.model import Model


class DummyModel(Model):
    def __init__(self, answer: str) -> None:
        self._answer = answer

    def prompt(self, prompt: str) -> str:
        return self._answer

    def reset(self) -> None:
        pass
