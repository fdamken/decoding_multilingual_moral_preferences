import json
from typing import Optional

import path_util
from model import get_available_models
from moral_machine import get_available_languages

expected_num_sessions = 100
expected_num_scenarios_per_session = 13
expected_answers = {"1", "2"}


def _log_error(
    model: Optional[str] = None,
    language: Optional[str] = None,
    session_idx: Optional[int] = None,
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
    if session_idx is not None:
        assert language is not None, "session_idx requires language"
        prefix += f", session {session_idx:3d}"
    if round_idx is not None:
        assert session_idx is not None, "round_idx requires session_idx"
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
    sessions = run["result"]["answers"]
    num_sessions = len(sessions)
    if num_sessions != expected_num_sessions:
        _log_error(model, language, error=f"unexpected number of sessions (is {num_sessions}, should be {expected_num_sessions})")
        return None
    erroneous_sessions = []
    for session_idx, answers in enumerate(sessions):
        if type(answers) is str and answers.startswith("PROMPT BLOCKED"):
            _log_error(model, language, session_idx, error="prompt blocked")
            continue
        if type(answers) is not list:
            _log_error(model, language, session_idx, error=f"unexpected type of answer list (is {type(answers)}, should be list)")
            erroneous_sessions.append(session_idx)
            continue
        num_scenarios = len(answers)
        if num_scenarios != expected_num_scenarios_per_session:
            _log_error(model, language, session_idx, error=f"unexpected number of rounds (is {num_scenarios}, should be {expected_num_scenarios_per_session})")
            erroneous_sessions.append(session_idx)
            continue
        unexpected_answers = [answer for answer in answers if answer not in expected_answers]
        if unexpected_answers:
            _log_error(model, language, session_idx, error=f"contains unexpected answers: {unexpected_answers}")
            erroneous_sessions.append(session_idx)
            continue
    return erroneous_sessions


def _validate_results() -> None:
    total_erroneous_sessions = []
    rerun_arguments = []
    for model in get_available_models():
        if not (path_util.cleansed_experiment_results_dir / model).exists():
            _log_error(model, error="missing results")
            continue
        for language in get_available_languages():
            erroneous_sessions = _validate_result(model, language)
            if erroneous_sessions is not None:
                total_erroneous_sessions += erroneous_sessions
                if erroneous_sessions:
                    rerun_arguments.append(f"with model_name={model} language={language} session_indices={','.join([str(session) for session in erroneous_sessions])}")
    if total_erroneous_sessions:
        rerun_arguments_str = '\n'.join(rerun_arguments)
        print(f"found {len(total_erroneous_sessions)} erroneous sessions\nrerun with the following arguments:\n{rerun_arguments_str}")
    else:
        print("all results are valid")


def main() -> None:
    _validate_results()


if __name__ == "__main__":
    main()
