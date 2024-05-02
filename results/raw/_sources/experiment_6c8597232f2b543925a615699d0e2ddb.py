import sacred
from sacred.observers import FileStorageObserver

import path_util

ex = sacred.Experiment("tinypaper")
ex.observers.append(FileStorageObserver(path_util.results_local_dir))


# noinspection PyUnusedLocal
@ex.config
def default_config():
    # name of the model to use, can be one of model_factory.get_available_models()
    model_name = None

    # language, can be one of moral_machine.get_available_languages()
    language = None

    # number of sessions to play, defaults to 100
    num_sessions = 100

    # play only the listed session indices; defaults to None (all)
    session_indices = None
