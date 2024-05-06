from pathlib import Path
from typing import Final

project_root_dir: Final[Path] = Path(__file__).parent.parent
data_dir: Final[Path] = project_root_dir / "data"
results_local_dir: Final[Path] = project_root_dir / "results_local"
results_dir: Final[Path] = project_root_dir / "results"
cleansed_experiment_results_dir: Final[Path] = results_dir / "cleansed"
preprocessed_experiment_results_dir: Final[Path] = results_dir / "preprocessed"
prepared_experiment_results_dir: Final[Path] = results_dir / "prepared"


def get_data_path(language: str) -> Path:
    path = data_dir / "preprocessed" / f"dataset_{language}.csv"
    assert path.exists(), f"dataset for language '{language}' not found"
    return path
