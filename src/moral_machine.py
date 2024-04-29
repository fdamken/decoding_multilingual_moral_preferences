from dataclasses import dataclass

import pandas as pd

import path_util
from experiment import ex

_languages = [
    "ar",
    "de",
    "en",
    "es",
    "fr",
    "ja",
    "kr",
    "pt",
    "ru",
    "zh",
]


def get_available_languages() -> list[str]:
    return list(_languages)


@dataclass
class Scenario:
    profile_left: str
    profile_right: str
    left_right_swapped: int


@dataclass
class Session:
    scenarios: list[Scenario]


@ex.capture
def load_sessions(language: str, from_session_id: int, to_session_id: int) -> list[Session]:
    assert language in get_available_languages(), f"language '{language}' not available"
    language = language.split("-")[0]  # strip region to load the dataset in correct language
    df = pd.read_csv(path_util.get_data_path(language))
    sessions = []
    scenarios = []
    for _, row in df.iterrows():
        profile_left, profile_right, left_right_swapped = row["desc_left"], row["desc_right"], row["left_right_swapped"]
        scenarios.append(Scenario(profile_left, profile_right, left_right_swapped))
        if len(scenarios) == 13:
            sessions.append(Session(scenarios))
            scenarios = []
    return sessions[from_session_id:to_session_id]
