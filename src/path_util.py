import logging
from datetime import datetime
from pathlib import Path
from typing import Final, Optional

_data_dir: Final[Path] = Path(__file__).parent.parent / "data"
_results_dir: Final[Path] = Path(__file__).parent.parent / "results"


def create_experiment_dir(extra_info: Optional[str] = None) -> Path:
    datetime_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_name = datetime_str
    if extra_info:
        dir_name += f"--{extra_info}"
    experiment_dir = _results_dir / dir_name
    logging.info(f"Creating experiment directory: {experiment_dir}")
    experiment_dir.mkdir(parents=True, exist_ok=False)
    return experiment_dir


def get_data_path(language: str) -> Path:
    path = _data_dir / "preprocessed" / f"dataset_{language}.csv"
    assert path.exists(), f"dataset for language '{language}' not found"
    return path
