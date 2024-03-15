import json
import logging
import os
from abc import ABC, abstractmethod

import path_util
from api_usage import APIUsage
from experiment import ex


class Model(ABC):
    """Abstract base class for LLMs."""

    _system_prompt: str
    _num_input_tokens: int
    _num_output_tokens: int

    @ex.capture
    def __init__(self, language: str, _log: logging.Logger) -> None:
        self._dry_run = not bool(os.getenv("NO_DRY_RUN", False))
        if not self.dry_run:
            _log.warning(f"Running model NOT in dry mode! This will consume API tokens and may cost money. MAKE SURE TO RUN IN DRY MODE FIRST TO GET AN ESTIMATE!")

        with open(path_util.data_dir / "system_prompts.json") as f:
            system_prompts = json.load(f)
        system_prompt = system_prompts.get(language)
        assert system_prompt, f"no system prompt for language '{language}'"
        self._system_prompt = system_prompt

    @abstractmethod
    def prompt(self, prompt: str) -> str:
        """Prompts the model."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Reset the model (e.g., to start a new game)."""
        self._history = []
        self._num_input_tokens = 0
        self._num_output_tokens = 0

    @abstractmethod
    def report_api_usage(self) -> APIUsage:
        ...

    @property
    def dry_run(self) -> bool:
        return self._dry_run
