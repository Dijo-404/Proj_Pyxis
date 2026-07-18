"""Create source-addressable local text chunks for later retrieval."""

from typing import Any


def build_index_entries(
    *, document_id: str, text: str, chunk_size: int = 1200, overlap: int = 150
) -> list[dict[str, Any]]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")

    entries: list[dict[str, Any]] = []
    start = 0
    position = 1
    while start < len(text):
        end = min(len(text), start + chunk_size)
        entries.append(
            {
                "chunk_id": f"{document_id}-CHUNK-{position:04d}",
                "document_id": document_id,
                "start": start,
                "end": end,
                "text": text[start:end],
            }
        )
        if end == len(text):
            break
        start = end - overlap
        position += 1
    return entries
