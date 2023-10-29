from abc import ABC, abstractmethod


class Model(ABC):
    """Abstract base class for LLMs."""

    @abstractmethod
    def prompt(self, prompt: str) -> str:
        """Prompts the model."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Reset the model (e.g., to start a new game)."""
        ...
