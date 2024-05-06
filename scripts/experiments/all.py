import os
import sys

from model import get_available_models
from moral_machine import get_available_languages


def _expand_args_list(args_list: list[list[str]], key: str, values: list[str]) -> list[list[str]]:
    new_args_list = []
    for args in args_list:
        for value in values:
            new_args_list.append(args + [f"{key}={value}"])
    return new_args_list


def _add_session_slices(args_list: list[list[str]]) -> list[list[str]]:
    new_args_list = []
    for args in args_list:
        for i in range(10):
            new_args_list.append(args + [f"from_session_id={i * 50}", f"to_session_id={(i + 1) * 50}"])
    return new_args_list


def _run(args: list[str]) -> None:
    run_py = os.path.join(os.path.dirname(__file__), "run.py")
    command = f"python {run_py} {' '.join(args)}"
    print(f"running: {command}")
    os.system(command)


def main() -> None:
    args = sys.argv[1:]
    if len(args) == 0:
        args.append("with")
    model_given = False
    language_given = False
    for arg in args:
        model_given |= arg.startswith("model_name=")
        language_given |= arg.startswith("language=")
    args_list = [args]
    if not model_given:
        args_list = _expand_args_list(args_list, "model_name", get_available_models())
    if not language_given:
        args_list = _expand_args_list(args_list, "language", get_available_languages())
    args_list = _add_session_slices(args_list)
    for args in args_list:
        _run(args)


if __name__ == "__main__":
    main()
