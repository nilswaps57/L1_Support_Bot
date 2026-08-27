"""Embedding value objects and compatibility identity."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EmbeddingVector:
    values: tuple[float, ...]
    model_id: str

    def __post_init__(self) -> None:
        if not self.values or not self.model_id.strip():
            raise ValueError("Embedding vectors require values and a model identity")

    @property
    def dimensions(self) -> int:
        return len(self.values)
