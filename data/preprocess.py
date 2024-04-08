import json
import os.path
import random
import uuid
from csv import DictWriter
from pathlib import Path

from markdownify import markdownify
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


def preprocess_dataset(dataset_file: Path) -> None:
    with open(THIS_DIR / "preprocessed" / f"{dataset_file.stem}.csv", "w") as f:
        csv = DictWriter(f, ["desc_left", "desc_right", "left_right_swapped"])
        csv.writeheader()
        for desc_left, desc_right in tqdm(load_dataset(dataset_file), desc=dataset_file.stem):
            if left_right_swapped := random.choice([True, False]):
                desc_left, desc_right = desc_right, desc_left
            csv.writerow(
                dict(
                    desc_left=preprocess_description(desc_left),
                    desc_right=preprocess_description(desc_right),
                    left_right_swapped=1 if left_right_swapped else 0,
                )
            )


def main() -> None:
    for dataset_file in (THIS_DIR / "raw").iterdir():
        if dataset_file.name.startswith("dataset_"):
            preprocess_dataset(dataset_file)


if __name__ == "__main__":
    main()
