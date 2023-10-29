import json
import os.path
import shutil
import uuid
from csv import DictWriter
from pathlib import Path

from markdownify import markdownify
from tqdm import tqdm

THIS_DIR = Path(os.path.dirname(__file__))


def load_dataset(language: str) -> list[list[str]]:
    with open(THIS_DIR / ".." / "raw" / f"dataset_{language}.json", "r") as f:
        return json.load(f)


def preprocess_description(description: str) -> str:
    return markdownify(description)


def preprocess_dataset(language: str, *, out_dir: Path) -> None:
    with open(out_dir / f"dataset_{language}.csv", "w") as f:
        csv = DictWriter(f, ["id", "desc_left", "desc_right"])
        csv.writeheader()
        for desc_left, desc_right in tqdm(load_dataset(language), desc=language):
            csv.writerow({"id": uuid.uuid4(), "desc_left": preprocess_description(desc_left), "desc_right": preprocess_description(desc_right)})


def main() -> None:
    for language in ["ar", "de", "en", "es", "fr", "ja", "kr", "pt", "ru", "zh"]:
        preprocess_dataset(language, out_dir=THIS_DIR)


if __name__ == "__main__":
    main()
