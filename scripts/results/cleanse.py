import json
import shutil
import sys
from pathlib import Path

import path_util


def _cleanse(model: str, language: str, model_language_dir: Path) -> None:
    print(f"cleansing {model}/{language}", file=sys.stderr)

    sessions = [None for _ in range(500)]  # 500 sessions
    for results_dir in model_language_dir.iterdir():
        with (open(results_dir / "config.json") as f_config, open(results_dir / "run.json") as f_run):
            config = json.load(f_config)
            from_session_id = config.get("from_session_id", 0)
            to_session_id = config.get("to_session_id", None) or config.get("num_sessions", None)
            assert to_session_id is not None, "one of 'to_session_id' or 'num_sessions' must be set"
            print(f"  - processing {results_dir.name} ({from_session_id}:{to_session_id})", file=sys.stderr)
            for session_idx_offset, session in enumerate(json.load(f_run)["result"]["answers"]):
                if isinstance(session, str) and "UnexpectedAnswerException" in session:
                    session = "UNEXPECTED_ANSWER"
                sessions[from_session_id + session_idx_offset] = session
            assert from_session_id + session_idx_offset + 1 == to_session_id, "session IDs do not match"

    out_dir = path_util.cleansed_experiment_results_dir / model
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / f"{language}.json", "w") as f:
        json.dump(sessions, f, indent=2)


def main() -> None:
    if path_util.cleansed_experiment_results_dir.exists():
        shutil.rmtree(path_util.cleansed_experiment_results_dir)
    for model_dir in path_util.raw_experiment_results_dir.iterdir():
        if model_dir.name == "_sources":
            continue
        for language_dir in model_dir.iterdir():
            _cleanse(model_dir.name, language_dir.name, language_dir)


if __name__ == "__main__":
    main()
