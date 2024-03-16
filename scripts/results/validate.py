import json
from typing import Optional

import path_util
from model import get_available_models
from moral_machine import get_available_languages

expected_num_games = 100
expected_num_scenarios_per_game = 13
expected_answers = {"1", "2"}


def _log_error(
    model: Optional[str] = None,
    language: Optional[str] = None,
    game_idx: Optional[int] = None,
    round_idx: Optional[int] = None,
    /,
    *,
    error: str,
) -> None:
    prefix = ""
    if model is not None:
        prefix += f"model {model}"
    if language is not None:
        assert model is not None, "language requires model"
        prefix += f", language {language}"
    if game_idx is not None:
        assert language is not None, "game_idx requires language"
        prefix += f", game {game_idx:3d}"
    if round_idx is not None:
        assert game_idx is not None, "round_idx requires game_idx"
        prefix += f", round {round_idx:2d}"
    if prefix:
        print(f"{prefix}: {error}")
    else:
        print(error)


def _validate_result(model: str, language: str) -> Optional[list[int]]:
    result_dir = path_util.cleansed_experiment_results_dir / model / language
    if not result_dir.exists():
        _log_error(model, language, error="missing results")
        return None
    with open(result_dir / "config.json") as f:
        config = json.load(f)
    if config["model_name"] != model:
        _log_error(model, language, error=f"model name mismatch (is {config['model_name']}, should be {model})")
        return None
    if config["language"] != language:
        _log_error(model, language, error=f"language mismatch (is {config['language']}, should be {language})")
        return None
    with open(result_dir / "run.json") as f:
        run = json.load(f)
    games = run["result"]["answers"]
    num_games = len(games)
    if num_games != expected_num_games:
        _log_error(model, language, error=f"unexpected number of games (is {num_games}, should be {expected_num_games})")
        return None
    erroneous_games = []
    for game_idx, answers in enumerate(games):
        if type(answers) is not list:
            _log_error(model, language, game_idx, error=f"unexpected type of answer list (is {type(answers)}, should be list)")
            erroneous_games.append(game_idx)
            continue
        num_scenarios = len(answers)
        if num_scenarios != expected_num_scenarios_per_game:
            _log_error(model, language, game_idx, error=f"unexpected number of rounds (is {num_scenarios}, should be {expected_num_scenarios_per_game})")
            erroneous_games.append(game_idx)
            continue
        unexpected_answers = [answer for answer in answers if answer not in expected_answers]
        if unexpected_answers:
            _log_error(model, language, game_idx, error=f"contains unexpected answers: {unexpected_answers}")
            erroneous_games.append(game_idx)
            continue
    return erroneous_games


def _validate_results() -> None:
    total_erroneous_games = []
    rerun_arguments = []
    for model in get_available_models():
        if not (path_util.cleansed_experiment_results_dir / model).exists():
            _log_error(model, error="missing results")
            continue
        for language in get_available_languages():
            erroneous_games = _validate_result(model, language)
            if erroneous_games is not None:
                total_erroneous_games += erroneous_games
                if erroneous_games:
                    rerun_arguments.append(f"with model_name={model} language={language} game_indices={','.join([str(game) for game in erroneous_games])}")
    if total_erroneous_games:
        rerun_arguments_str = '\n'.join(rerun_arguments)
        print(f"found {len(total_erroneous_games)} erroneous games\nrerun with the following arguments:\n{rerun_arguments_str}")
    else:
        print("all results are valid")


def main() -> None:
    _validate_results()


if __name__ == "__main__":
    main()
