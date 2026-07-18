"""Hugging Face Transformers implementation of the Gemma provider boundary."""

from collections.abc import Mapping, Sequence

from intelligence.gemma.providers.base import GemmaProvider


class TransformersGemmaProvider(GemmaProvider):
    """Placeholder until local model-loading policy is implemented."""

    async def generate(
        self,
        *,
        system_prompt: str,
        messages: Sequence[Mapping[str, str]],
    ) -> str:
        raise RuntimeError("Transformers Gemma runtime is not configured")
