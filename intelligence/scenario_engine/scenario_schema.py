"""Internal scenario-domain contracts independent of transport schemas."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WeightedSignal:
    name: str
    weight: float

    def __post_init__(self) -> None:
        if not 0 < self.weight <= 1:
            raise ValueError("signal weight must be in the range (0, 1]")
