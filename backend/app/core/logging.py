"""Application logging configuration with safe, structured defaults."""

import logging


def configure_logging(level: str = "INFO") -> None:
    """Configure process logging without including customer data."""
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
