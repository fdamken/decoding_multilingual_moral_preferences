import logging

from tenacity import after_log, before_sleep_log, retry, retry_if_exception_type, stop_after_attempt

from api_usage import APIUsage
from model import make_model
from moral_machine import Game, Scenario


class UnexpectedAnswerException(Exception):
    pass


class Agent:
    def __init__(self, model_name: str) -> None:
        self._model = make_model(model_name)

    @retry(
        after=after_log(logging.root, logging.WARNING),
        before_sleep=before_sleep_log(logging.root, logging.INFO),
        retry=retry_if_exception_type(UnexpectedAnswerException),
        stop=stop_after_attempt(10),
    )
    def play(self, game: Game) -> list[str]:
        self._model.reset()
        return [self._prompt(self._make_prompt(scenario)) for scenario in game.scenarios]

    def report_api_usage(self) -> APIUsage:
        return self._model.report_api_usage()

    def _prompt(self, prompt) -> str:
        result = self._model.prompt(prompt)
        if result not in {"1", "2"}:
            raise UnexpectedAnswerException(f"expected 1 or 2, got {result}")
        return result

    @staticmethod
    def _make_prompt(scenario: Scenario) -> str:
        return f"1: {scenario.desc_left}\n\n\n\n\n2: {scenario.desc_right}"
