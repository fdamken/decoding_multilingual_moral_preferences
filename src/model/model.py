import logging
import os
from abc import ABC, abstractmethod

from api_usage import APIUsage
from experiment import ex


class Model(ABC):
    """Abstract base class for LLMs."""

    @ex.capture
    def __init__(self, _log: logging.Logger) -> None:
        self._dry_run = not bool(os.getenv("NO_DRY_RUN", False))
        if not self.dry_run:
            _log.warning(f"Running model NOT in dry mode! This will consume API tokens and may cost money. MAKE SURE TO RUN IN DRY MODE FIRST TO GET AN ESTIMATE!")

    @abstractmethod
    def prompt(self, prompt: str) -> str:
        """Prompts the model."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Reset the model (e.g., to start a new game)."""
        ...

    @abstractmethod
    def report_api_usage(self) -> APIUsage:
        ...

    @property
    def dry_run(self) -> bool:
        return self._dry_run
