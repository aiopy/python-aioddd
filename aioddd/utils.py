from logging import getLogger, StreamHandler, Formatter, Logger, NOTSET
from os import getenv
from typing import Optional, Union


def get_env(key: str, default: Optional[str] = None) -> str:
    """Get an environment variable, return default if it is empty or doesn't exist."""
    value = getenv(key, default)
    return str(default) if not value or len(value) == 0 else value


def get_simple_logger(
        name: Optional[str] = None,
        level: Union[str, int] = NOTSET,
        fmt: str = '[%(asctime)s] - %(name)s - %(levelname)s - %(message)s'
) -> Logger:
    logger = getLogger(name)
    logger.setLevel(level)
    handler = StreamHandler()
    handler.setLevel(level)
    formatter = Formatter(fmt)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
