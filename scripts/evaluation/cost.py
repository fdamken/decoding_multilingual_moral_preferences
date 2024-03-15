import json
from argparse import ArgumentParser
from pathlib import Path

import pandas as pd

_results_dir = Path(__file__).parent.parent.parent / "results"


def _load_run(experiment: int) -> tuple[dict, dict]:
    exp_dir = _results_dir / str(experiment)
    with open(exp_dir / "config.json", "r") as f:
        config = json.load(f)
    with open(exp_dir / "run.json", "r") as f:
        run = json.load(f)
    return config, run


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("-e", "--experiments", required=True)
    args = parser.parse_args()
    if args.experiments == "all":
        experiments = [int(d.name) for d in _results_dir.iterdir() if d.name.isnumeric()]
    else:
        experiments = [int(e) for e in args.experiments.split(",")]

    df_data = []
    for experiment_id, (config, run) in ((e, _load_run(e)) for e in experiments):
        df_data.append(dict(
            experiment_id=experiment_id,
            model_name=config["model_name"],
            language=config["language"],
            cost=run["result"]["api_usage_total"]["cost"],
        ))
    df = pd.DataFrame.from_records(df_data, index="experiment_id")

    for key, item in df.groupby("model_name"):
        print(f"\n\n### Model '{key}' ###")
        print(item[["language", "cost"]])
        print(f"Total: {item['cost'].sum():.2f}")


if __name__ == "__main__":
    main()
