import json
import os.path
from csv import DictWriter
from pathlib import Path

from tqdm import tqdm

THIS_DIR = Path(os.path.dirname(__file__))


def load_dataset(dataset_file: Path) -> list[list[str]]:
    with open(dataset_file, "r") as f:
        return json.load(f)


def preprocess_description(description: str) -> str:
    return description \
        .replace("<br>", "\n\n") \
        .replace("<ul>", "\n") \
        .replace("</ul>", "\n") \
        .replace("<li>", "* ") \
        .replace("</li>", "\n") \
        .strip()


def preprocess_dataset(dataset_file: Path, scenarios: list[dict]) -> None:
    with open(THIS_DIR / "preprocessed" / f"{dataset_file.stem}.csv", "w") as f:
        csv = DictWriter(f, ["desc_left", "desc_right", "left_right_swapped"])
        csv.writeheader()
        for (desc_left, desc_right), scenario in tqdm(zip(load_dataset(dataset_file), scenarios), desc=dataset_file.stem):
            left_right_swapped = scenario["_id"] % 2 == 0
            if left_right_swapped:
                desc_left, desc_right = desc_right, desc_left
            csv.writerow(
                dict(
                    desc_left=preprocess_description(desc_left),
                    desc_right=preprocess_description(desc_right),
                    left_right_swapped=1 if left_right_swapped else 0,
                )
            )


def main() -> None:
    with open(THIS_DIR / "raw" / "scenarios.json", "r") as f:
        scenarios = json.load(f)
    for dataset_file in (THIS_DIR / "raw").iterdir():
        if dataset_file.name.startswith("dataset_"):
            preprocess_dataset(dataset_file, scenarios)


if __name__ == "__main__":
    main()
