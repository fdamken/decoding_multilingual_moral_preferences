import traceback
from logging import Logger
from typing import Any, Optional

from tqdm import tqdm

import model
import moral_machine
from agent import Agent
from api_usage import APIUsage
from experiment import ex


def _run_game(game: moral_machine.Game, model_name: str) -> tuple[list[str], APIUsage]:
    agent = Agent(model_name)
    try:
        result = agent.play(game)
    except Exception:
        result = traceback.format_exc()
    return result, agent.report_api_usage()


@ex.automain
def main(model_name: str, language: str, game_indices: Optional[int | list[int]], _log: Logger) -> Any:
    assert model_name in model.get_available_models(), f"model '{model_name}' not available"
    assert language in moral_machine.get_available_languages(), f"language '{language}' not available"

    if game_indices is not None:
        if type(game_indices) is int:
            game_indices = [game_indices]
        _log.info(f"playing only games {game_indices}")

    answers: list[list[str]] = []
    api_usage: list[APIUsage] = []
    games = moral_machine.load_games(language)
    total = len(game_indices) if game_indices is not None else len(games)
    with tqdm(total=total) as pbar:
        for game_idx, game in enumerate(games):
            if game_idx is None or game_idx in game_indices:
                game_answers, game_api_usage = _run_game(game, model_name)
            else:
                game_answers, game_api_usage = f"skipped; only playing games {game_indices}", APIUsage(model_name, 0, 0, 0)
            answers.append(game_answers)
            api_usage.append(game_api_usage)
        api_usage_total = APIUsage.merge(*api_usage)
        pbar.update()

    return dict(
        answers=answers,
        api_usage=api_usage,
        api_usage_total=api_usage_total,
    )
