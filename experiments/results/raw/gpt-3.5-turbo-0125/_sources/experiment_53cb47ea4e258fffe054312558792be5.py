import sacred
from sacred.observers import FileStorageObserver

import path_util

ex = sacred.Experiment("tinypaper")
ex.observers.append(FileStorageObserver(path_util.results_dir))


# noinspection PyUnusedLocal
@ex.config
def default_config():
    # name of the model to use, can be one of model_factory.get_available_models()
    model_name = None

    # language, can be one of moral_machine.get_available_languages()
    language = None

    # number of games to play, defaults to 100 games
    num_games = 100

    # play only the listed game indices; defaults to None (all)
    game_indices = None

    # number of scenarios per game, Moral Machine has 13 scenarios per game
    scenarios_per_game = 13
