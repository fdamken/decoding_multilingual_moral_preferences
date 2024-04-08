import json
import logging
import shutil

import path_util


def _preprocess(model: str, language: str, scenarios: list[dict]) -> None:
    with open(path_util.cleansed_experiment_results_dir / model / language / "run.json") as f:
        run = json.load(f)

    out_dir = path_util.preprocessed_experiment_results_dir / model
    out_dir.mkdir(exist_ok=True, parents=True)
    sessions = []
    for session_idx, session_answers in enumerate(run["result"]["answers"]):
        if type(session_answers) is not list:
            logging.info(f"{model}/{language}: session {session_idx} has unexpected type of answer list (is {type(session_answers)}, should be list); skipping")
            continue
        rounds = []
        for scenario_idx, answer in enumerate(session_answers):
            scenario_idx = session_idx * 13 + scenario_idx
            rounds.append(
                dict(
                    scenario_idx=scenario_idx,
                    scenario=scenarios[scenario_idx],
                    answer=int(answer) - 1,
                )
            )
        sessions.append(
            dict(
                session_idx=session_idx,
                rounds=rounds,
            )
        )
    with open(out_dir / f"{language}.json", "w") as f:
        json.dump(sessions, f, indent=2)


def main() -> None:
    if path_util.preprocessed_experiment_results_dir.exists():
        shutil.rmtree(path_util.preprocessed_experiment_results_dir)
    with open(path_util.data_dir / "raw" / "scenarios.json") as f:
        scenarios = json.load(f)
    for model in path_util.cleansed_experiment_results_dir.iterdir():
        for language in model.iterdir():
            _preprocess(model.name, language.name, scenarios)


if __name__ == "__main__":
    main()
