"""LiteRT-LM implementation of the optional edge Gemma provider boundary."""

from collections.abc import Mapping, Sequence

from intelligence.gemma.providers.base import GemmaProvider


class LiteRTGemmaProvider(GemmaProvider):
    """Placeholder for the optional on-device deployment mode."""

    async def generate(
        self,
        *,
        system_prompt: str,
        messages: Sequence[Mapping[str, str]],
    ) -> str:
        raise RuntimeError("LiteRT-LM Gemma runtime is not configured")
