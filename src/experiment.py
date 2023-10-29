import argparse
import json
from functools import partial
from pathlib import Path
import multiprocessing as mp

import moral_machine
import path_util
from agent import Agent
from model import model_factory


def _run_game(game: moral_machine.Game, *, args) -> any:
    return Agent(args.model).play(game)


def _run(args, experiment_dir: Path) -> None:
    games = moral_machine.load_games(args.language)
    with mp.Pool(args.num_workers) as pool:
        raw_results = pool.map(partial(_run_game, args=args), games)
    with open(experiment_dir / "raw_results.json", "w") as f:
        json.dump(raw_results, f)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", "-m", type=str, required=True, choices=model_factory.get_available_models(), help="model to query")
    parser.add_argument("--language", "-l", type=str, required=True, choices=moral_machine.get_available_languages(), help="language to query")
    parser.add_argument("--num_games", "-n", type=int, required=False, help="number of games to play; defaults to all")
    parser.add_argument("--num_workers", "-w", type=int, required=False, help="number of workers to use; defaults to all")
    args = parser.parse_args()
    experiment_dir = path_util.create_experiment_dir(f"{args.model}_{args.language}")
    _run(args, experiment_dir)


if __name__ == "__main__":
    main()
