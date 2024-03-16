from pathlib import Path
from typing import Final

data_dir: Final[Path] = Path(__file__).parent.parent / "data"
results_dir: Final[Path] = Path(__file__).parent.parent / "results"


def get_data_path(language: str) -> Path:
    path = data_dir / "preprocessed" / f"dataset_{language}.csv"
    assert path.exists(), f"dataset for language '{language}' not found"
    return path
