"""llama.cpp implementation of the Gemma provider boundary."""

from collections.abc import Mapping, Sequence

from intelligence.gemma.providers.base import GemmaProvider


class LlamaCppGemmaProvider(GemmaProvider):
    """Placeholder until the local GGUF runtime is configured."""

    async def generate(
        self,
        *,
        system_prompt: str,
        messages: Sequence[Mapping[str, str]],
    ) -> str:
        raise RuntimeError("llama.cpp Gemma runtime is not configured")
