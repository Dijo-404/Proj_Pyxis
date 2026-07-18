"""Authentication, authorization, and sensitive-data masking boundary."""


def mask_identifier(value: str, visible_suffix: int = 4) -> str:
    """Mask an identifier while retaining a short reviewer-visible suffix."""
    if visible_suffix < 0:
        raise ValueError("visible_suffix cannot be negative")
    if visible_suffix == 0:
        return "*" * len(value)
    if len(value) <= visible_suffix:
        return "*" * len(value)
    return "*" * (len(value) - visible_suffix) + value[-visible_suffix:]
