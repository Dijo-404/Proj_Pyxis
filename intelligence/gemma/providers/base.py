"""Runtime-independent interface for local Gemma inference."""

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence


class GemmaProvider(ABC):
    """Contract implemented by every local inference runtime."""

    @abstractmethod
    async def generate(
        self,
        *,
        system_prompt: str,
        messages: Sequence[Mapping[str, str]],
    ) -> str:
        """Return raw model output for subsequent schema validation."""
