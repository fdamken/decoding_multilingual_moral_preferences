import json
from typing import Optional

import path_util
from model import get_available_models
from moral_machine import get_available_languages

expected_num_sessions = 500
expected_num_scenarios_per_session = 13
expected_answers = {1, 2}


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


def _validate_result(model: str, language: str) -> Optional[tuple[int, list[int], int, int, int]]:
    results_file = path_util.cleansed_experiment_results_dir / model / f"{language}.json"
    if not results_file.exists():
        _log_error(model, language, error="missing results")
        return None
    with open(results_file) as f:
        sessions = json.load(f)
    num_sessions = len(sessions)
    if num_sessions != expected_num_sessions:
        _log_error(model, language, error=f"unexpected number of sessions (is {num_sessions}, should be {expected_num_sessions})")
        return None
    erroneous_sessions = []
    num_missing_sessions = 0
    num_prompts_blocked = 0
    num_unexpected_answers = 0
    for session_idx, answers in enumerate(sessions):
        if answers is None:
            num_missing_sessions += 1
            continue
        if type(answers) is str:
            if answers.startswith("PROMPT BLOCKED"):
                num_prompts_blocked += 1
                continue
            if answers == "UNEXPECTED ANSWER":
                num_unexpected_answers += 1
                continue
        if type(answers) is not list:
            _log_error(model, language, session_idx, error=f"unexpected type of answer list (is {type(answers)}, should be list)")
            erroneous_sessions.append(session_idx)
            continue
        num_scenarios = len(answers)
        if num_scenarios != expected_num_scenarios_per_session:
            _log_error(
                model,
                language,
                session_idx,
                error=f"unexpected number of rounds (is {num_scenarios}, should be {expected_num_scenarios_per_session})"
            )
            erroneous_sessions.append(session_idx)
            continue
        unexpected_answers = [answer for answer in answers if answer not in expected_answers]
        if unexpected_answers:
            _log_error(model, language, session_idx, error=f"contains unexpected answers: {unexpected_answers}")
            erroneous_sessions.append(session_idx)
            continue
    return (num_sessions - num_missing_sessions, erroneous_sessions, num_missing_sessions, num_prompts_blocked,
            num_unexpected_answers)


def _validate_results() -> None:
    rerun_arguments = []
    for model in get_available_models():
        if model == "mock":
            continue
        if not (path_util.cleansed_experiment_results_dir / model).exists():
            _log_error(model, error="missing results")
            continue
        table_row = []
        total_invalid_sessions = 0
        total_num_sessions = 0
        for language in get_available_languages():
            validation_result = _validate_result(model, language)
            if validation_result is None:
                continue
            (num_sessions,
             erroneous_sessions,
             num_missing_sessions,
             num_prompts_blocked,
             num_unexpected_answers,
             ) = validation_result
            # _log_error(
            #  model,
            #     language,
            #     error=f"{len(erroneous_sessions)} erroneous sessions; {num_missing_sessions} missing sessions sessions; "
            #           f"{num_prompts_blocked} blocked prompts; {num_unexpected_answers} unexpected answers"
            #  )
            if num_missing_sessions > 0:
                cell_suffix = f" (-{num_missing_sessions})"
            else:
                cell_suffix = ""
            invalid_sessions = num_prompts_blocked + num_unexpected_answers
            total_invalid_sessions += invalid_sessions
            total_num_sessions += num_sessions
            table_row.append(f"{invalid_sessions / num_sessions * 100:.0f}{cell_suffix}")
            if len(erroneous_sessions) > 0:
                rerun_arguments.append(
                    f"with model_name={model} language={language} session_indices="
                    f"{','.join([str(session) for session in erroneous_sessions])}"
                )
        table_row.append(f"{total_invalid_sessions / total_num_sessions * 100:.0f}")
        print(f"{model}: {' & '.join(table_row)}")


def main() -> None:
    _validate_results()


if __name__ == "__main__":
    main()
