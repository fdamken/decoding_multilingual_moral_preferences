from api_usage import APIUsage
from model import make_model
from moral_machine import Game, Scenario


class Agent:
    def __init__(self, model_name: str) -> None:
        self._model = make_model(model_name)

    def play(self, game: Game) -> list[str]:
        self._model.reset()
        return [self._model.prompt(self._make_prompt(scenario)) for scenario in game.scenarios]

    def report_api_usage(self) -> APIUsage:
        return self._model.report_api_usage()

    @staticmethod
    def _make_prompt(scenario: Scenario) -> str:
        return f"1: {scenario.desc_left}\n\n\n\n\n2: {scenario.desc_right}"
