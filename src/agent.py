from model import model_factory
from moral_machine import Game, Scenario


class Agent:
    def __init__(self, model_name: str) -> None:
        self._model = model_factory.make_model(model_name)

    def play(self, game: Game) -> list[str]:
        self._model.reset()
        return [self._model.prompt(self._make_prompt(scenario)) for scenario in game.scenarios]

    @staticmethod
    def _make_prompt(scenario: Scenario) -> str:
        return f"1: {scenario.desc_left}\n\n\n\n\n2: {scenario.desc_right}"
