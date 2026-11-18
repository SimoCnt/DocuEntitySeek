import logging
import sys

from app.core.config import get_settings


LOGGER_NAME = "docuentityseek"


def configure_logging() -> None:
    settings = get_settings()
    level = getattr(logging, settings.app_log_level.upper(), logging.INFO)
    logger = logging.getLogger(LOGGER_NAME)

    logger.setLevel(level)
    logger.propagate = False

    if logger.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-5s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"{LOGGER_NAME}.{name}")