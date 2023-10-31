import uuid
from dataclasses import dataclass
from typing import Iterable, Optional

import pandas as pd

import path_util
from experiment import ex

_languages = ["ar", "de", "en", "es", "fr", "ja", "kr", "pt", "ru", "zh"]


def get_available_languages() -> list[str]:
    return list(_languages)


@dataclass
class Scenario:
    id: str
    desc_left: str
    desc_right: str


@dataclass
class Game:
    id: str
    scenarios: list[Scenario]


@ex.capture
def load_games(language: str, num_games: Optional[int], scenarios_per_game: int) -> list[Game]:
    assert language in get_available_languages(), f"language '{language}' not available"
    df = pd.read_csv(path_util.get_data_path(language))
    games = []
    scenarios = []
    for _, row in df.iterrows():
        scenario_id, desc_left, desc_right = row["id"], row["desc_left"], row["desc_right"]
        scenarios.append(Scenario(scenario_id, desc_left, desc_right))
        if len(scenarios) == scenarios_per_game:
            games.append(Game(str(uuid.uuid4()), scenarios))
            scenarios = []
        if num_games is not None and len(games) == num_games:
            break
    return games
