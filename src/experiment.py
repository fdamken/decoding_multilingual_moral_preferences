import sacred
from sacred.observers import FileStorageObserver

import path_util

ex = sacred.Experiment("tinypaper")
ex.observers.append(FileStorageObserver(path_util.results_dir))


# noinspection PyUnusedLocal
@ex.config
def default_config():
    model = None
    language = "en"
    num_games = None
    scenarios_per_game = 13
    num_workers = None
    openai_api_key = None
