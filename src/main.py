import multiprocessing as mp
from functools import partial
from typing import Optional

import moral_machine
from agent import Agent
from experiment import ex
from model import model_factory


def _run_game(game: moral_machine.Game, model: str) -> any:
    return Agent(model).play(game)


@ex.automain
def main(model: str, language: str, num_workers: Optional[int]) -> None:
    assert model in model_factory.get_available_models(), f"model '{model}' not available"
    assert language in moral_machine.get_available_languages(), f"language '{language}' not available"

    games = moral_machine.load_games()
    with mp.Pool(num_workers) as pool:
        return pool.map(partial(_run_game, model=model), games)
