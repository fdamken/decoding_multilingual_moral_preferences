import json
import shutil
from csv import DictWriter
from typing import Final
from uuid import uuid4

import pandas as pd

import path_util

TILE_TYPES: Final[list[tuple[str, str]]] = [
    (0, "Man"),
    (1, "Woman"),
    (2, "Pregnant"),
    (3, "Stroller"),
    (4, "OldMan"),
    (5, "OldWoman"),
    (6, "Boy"),
    (7, "Girl"),
    (8, "Homeless"),
    (9, "LargeWoman"),
    (10, "LargeMan"),
    (11, "Criminal"),
    (12, "MaleExecutive"),
    (13, "FemaleExecutive"),
    (14, "FemaleAthlete"),
    (15, "MaleAthlete"),
    (16, "FemaleDoctor"),
    (17, "MaleDoctor"),
    (20, "Dog"),
    (21, "Cat"),
]


def extract_tile_for_outcome(tiles, outcome):
    assert outcome in {0, 1}, f"unexpected outcome {outcome}"
    for tile in tiles:
        if tile["outcome"] == outcome:
            return tile
    return None


def compute_number_of_characters(tiles):
    outcomes = []
    for outcome in {0, 1}:
        result = {}
        for type_in_tile, type_in_out in TILE_TYPES:
            result[type_in_out] = 0
            for tile in tiles:
                if tile["outcome"] != outcome:
                    continue
                if tile["tile_type"] == type_in_tile:
                    result[type_in_out] += 1
        result["NumberOfCharacters"] = sum(result.values())
        outcomes.append(result)
    for outcome in outcomes:
        outcome["DiffNumberOFCharacters"] = abs(outcomes[0]["NumberOfCharacters"] - outcomes[1]["NumberOfCharacters"])
    return outcomes


def determine_attribute_level(scenario_type, number_of_characters, number_of_characters_other):
    existing_character_types = {key for key, value in number_of_characters.items() if value > 0}
    match scenario_type:
        case "Utilitarian":
            if sum(number_of_characters.values()) < sum(number_of_characters_other.values()):
                return "Less"
            return "More"
        case "Gender":
            if any(
                key in {"Man", "OldMan", "Boy", "LargeMan", "MaleExecutive", "MaleAthlete", "MaleDoctor"} for key in
                existing_character_types
            ):
                return "Male"
            if any(
                key in {"Woman", "OldWoman", "Girl", "LargeWoman", "FemaleExecutive", "FemaleAthlete", "FemaleDoctor"} for key in
                existing_character_types
            ):
                return "Female"
            assert False, f"unexpected gender scenario: {number_of_characters}"
        case "Fitness":
            if any(key in {"FemaleAthlete", "MaleAthlete"} for key in existing_character_types):
                return "Fit"
            return "Fat"
        case "Age":
            if any(key in {"Boy", "Girl"} for key in existing_character_types):
                return "Young"
            return "Old"
        case "Social Status":
            if any(key in {"MaleExecutive", "FemaleExecutive"} for key in existing_character_types):
                return "High"
            return "Low"
        case "Species":
            if all(key not in {"Dog", "Cat"} for key in existing_character_types):
                return "Hoomans"
            if any(key in {"Dog", "Cat"} for key in existing_character_types):
                return "Pets"
            assert False, f"unexpected species scenario: {number_of_characters}"
        case "Random":
            return "Rand"
        case _:
            assert False, f"unknown scenario type: {scenario_type}"


def prepare_round(responde_id, extended_session_id, user_id, language, round_idx, round):
    scenario = round["scenario"]
    scenario_type_idx = scenario["i"]
    crossing_signal = scenario["options"]["crossing_signal"]
    barrier = scenario["options"]["barrier"]
    tiles = scenario["tiles"]
    left_right_swapped = scenario["_id"] % 2 == 0
    answer = round["answer"]
    if scenario_type_idx in {0, 1}:
        scenario_type = "Utilitarian"
    elif scenario_type_idx in {2, 3}:
        scenario_type = "Gender"
    elif scenario_type_idx in {4, 5}:
        scenario_type = "Fitness"
    elif scenario_type_idx in {6, 7}:
        scenario_type = "Age"
    elif scenario_type_idx in {8, 9}:
        scenario_type = "Social Status"
    elif scenario_type_idx in {10, 11}:
        scenario_type = "Species"
    elif scenario_type_idx == 13:
        scenario_type = "Random"
    else:
        assert False, f"unknown scenario type index: {scenario_type_idx}"
    default_choice = {
        "Gender": "Male", "Fitness": "Fit", "Age": "Young", "Social Status": "High", "Species": "Hoomans", "Utilitarian": "More",
        "Random": None
    }[scenario_type]
    non_default_choice = {
        "Gender": "Female", "Fitness": "Fat", "Age": "Old", "Social Status": "Old", "Species": "Pets", "Utilitarian": "Less",
        "Random": None
    }[scenario_type]
    shared_info = {
        "ResponseID": responde_id,
        "ExtendedSessionID": extended_session_id,
        "UserID": user_id,
        "ScenarioOrder": str(round_idx + 1),
        "PedPed": 1 if barrier == -1 else 0,
        "Template": "llm",
        "DescriptionShown": 1,
        "UserCountry3": language,  # exploit the country-handling of the MM code
        "ScenarioType": scenario_type,
        "ScenarioTypeStrict": scenario_type,
        "DefaultChoice": default_choice,
        "NonDefaultChoice": non_default_choice,
    }
    outcomes = [{}, {}]
    number_of_characters = compute_number_of_characters(tiles)
    for outcome_idx in {0, 1}:
        if crossing_signal == "no":
            crossing_signal_int = 0
        elif barrier == -1:
            # this is PedPed and the crossing light always gives the color for
            # outcome 0
            if outcome_idx == 0:
                crossing_signal_int = 1 if crossing_signal == "green" else 2
            else:
                crossing_signal_int = 2 if crossing_signal == "green" else 1
        elif barrier == 0:
            # barrier is affecting outcome 0
            if outcome_idx == 0:
                crossing_signal_int = 0
            else:
                crossing_signal_int = 1 if crossing_signal == "green" else 2
        elif barrier == 1:
            # barrier is affecting outcome 1
            if outcome_idx == 1:
                crossing_signal_int = 0
            else:
                crossing_signal_int = 1 if crossing_signal == "green" else 2
        else:
            assert False, f"unexpected barrier value: {barrier}"
        outcomes[outcome_idx] |= shared_info
        outcomes[outcome_idx] |= number_of_characters[outcome_idx]
        attribute_level = determine_attribute_level(
            scenario_type,
            number_of_characters[outcome_idx],
            number_of_characters[1 - outcome_idx]
        )
        outcomes[outcome_idx] |= {
            "Barrier": 1 if barrier == outcome_idx else 0,
            "AttributeLevel": attribute_level,
            "Intervention": outcome_idx,  # outcome 1 is always the swerving one
            "Saved": 1 if answer == outcome_idx else 0,
            # usually 0 is left, but if left/right are swapped, 0 is right
            "LeftHand": outcome_idx if left_right_swapped else (1 - outcome_idx),
            "CrossingSignal": crossing_signal_int,
            "DefaultChoiceIsOmission": outcome_idx if attribute_level == default_choice else 1 - outcome_idx,
        }
    return outcomes


def prepare(language, sessions):
    rows = []
    for session in sessions:
        session_id = str(uuid4())
        user_id = str(uuid4())
        for round_idx, round_ in enumerate(session["rounds"]):
            rows += prepare_round(str(uuid4()), session_id, user_id, language, round_idx, round_)
    return rows


def _find_missing_characters(csv_file_name):
    df = pd.read_csv(csv_file_name)
    # we exclude "Age", "Fitness", "Social Status", "Species", "Gender" because we have too little data
    characters = ["OldMan", "OldWoman", "Boy", "Girl", "LargeMan", "LargeWoman", "MaleAthlete", "FemaleAthlete", "MaleDoctor",
                  "FemaleDoctor", "MaleExecutive", "FemaleExecutive", "Pregnant", "Stroller", "Homeless", "Criminal", "Dog",
                  "Cat"]
    df_filtered = df.loc[
        (df["ScenarioType"] == "Random") & (df["ScenarioTypeStrict"] == "Random") & (df["NumberOfCharacters"] == 1)]
    relevant_columns_sum = df_filtered[characters].sum()
    return list(relevant_columns_sum[relevant_columns_sum == 0].index)


def main():
    if path_util.prepared_experiment_results_dir.exists():
        shutil.rmtree(path_util.prepared_experiment_results_dir)
    path_util.prepared_experiment_results_dir.mkdir(exist_ok=True, parents=True)

    for model in path_util.preprocessed_experiment_results_dir.iterdir():
        rows = []
        missing_languages = []
        for file_path in model.iterdir():
            with open(file_path, "r") as f:
                language = file_path.stem
                sessions = json.load(f)
                if len(sessions) > 0:
                    rows += prepare(language, sessions)
                else:
                    missing_languages.append(language)

        csv_file_name = path_util.prepared_experiment_results_dir / f"{model.name}.csv"
        with open(csv_file_name, "w") as f:
            csv = DictWriter(
                f,
                ["ResponseID", "ExtendedSessionID", "UserID", "ScenarioOrder", "Intervention", "PedPed", "Barrier",
                 "CrossingSignal", "AttributeLevel", "ScenarioTypeStrict",
                 "ScenarioType", "DefaultChoice", "NonDefaultChoice", "DefaultChoiceIsOmission", "NumberOfCharacters",
                 "DiffNumberOFCharacters", "Saved", "Template",
                 "DescriptionShown", "LeftHand", "UserCountry3", "Man", "Woman", "Pregnant", "Stroller", "OldMan", "OldWoman",
                 "Boy", "Girl", "Homeless", "LargeWoman", "LargeMan",
                 "Criminal", "MaleExecutive", "FemaleExecutive", "FemaleAthlete", "MaleAthlete", "FemaleDoctor", "MaleDoctor",
                 "Dog", "Cat"
                 ],
                lineterminator="\n"
            )
            csv.writeheader()
            for row in rows:
                csv.writerow(row)

        status = []
        missing_characters = _find_missing_characters(csv_file_name)
        if missing_languages:
            status.append(f"missing languages: {', '.join(missing_languages)}")
        if missing_characters:
            status.append(f"missing characters: {', '.join(missing_characters)}")
        if not missing_languages and not missing_characters:
            status.append("valid")
        print(f"{model.name}: {'; '.join(status)}")


if __name__ == "__main__":
    main()
