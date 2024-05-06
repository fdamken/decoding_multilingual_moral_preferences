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

    # which sessions to play (from inclusive, to exclusive); defaults to 0-500 (all)
    from_session_id = 0
    to_session_id = 500

    # play only the listed session indices; defaults to None (all)
    session_indices = None
