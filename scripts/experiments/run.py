import traceback
from logging import Logger
from typing import Any

from tqdm import tqdm

import model
import moral_machine
from agent import Agent
from api_usage import APIUsage
from experiment import ex


def _run_game(game: moral_machine.Game, model_name: str) -> tuple[list[str], APIUsage]:
    agent = Agent(model_name)
    # try:
    result = agent.play(game)
    # except Exception:
    #     result = traceback.format_exc()
    return result, agent.report_api_usage()


@ex.automain
def main(model_name: str, language: str, _log: Logger) -> Any:
    assert model_name in model.get_available_models(), f"model '{model_name}' not available"
    assert language in moral_machine.get_available_languages(), f"language '{language}' not available"

    answers: list[list[str]] = []
    api_usage: list[APIUsage] = []
    for game in tqdm(moral_machine.load_games(language)):
        game_answers, game_api_usage = _run_game(game, model_name)
        answers.append(game_answers)
        api_usage.append(game_api_usage)
    api_usage_total = APIUsage.merge(*api_usage)

    return dict(
        answers=answers,
        api_usage=api_usage,
        api_usage_total=api_usage_total,
    )
