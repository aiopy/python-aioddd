from logging import NOTSET, Formatter, Logger, StreamHandler, getLogger
from os import getenv
from typing import Any, Dict, Optional, Type, TypeVar, Union


def get_env(key: str, default: Optional[str] = None) -> str:  # pragma: no cover
    """Get an environment variable, return default if it is empty or doesn't exist."""
    value = getenv(key, default)
    return str(default) if not value or len(value) == 0 else value


def get_simple_logger(
    name: Optional[str] = None,
    level: Union[str, int] = NOTSET,
    fmt: str = '[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',
) -> Logger:  # pragma: no cover
    logger = getLogger(name)
    logger.setLevel(level)
    handler = StreamHandler()
    handler.setLevel(level)
    formatter = Formatter(fmt)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


_T = TypeVar('_T')
_ENV: Optional[Dict[str, Any]] = None


def env_resolver() -> Optional[Dict[str, Any]]:
    """Override this method to use below env method to automatically cache and get type validations magically."""
    return {}


def env(key: Optional[str] = None, typ: Optional[Type[_T]] = None) -> _T:
    global _ENV
    if not _ENV:
        _ENV = env_resolver() or {}
    if not key:
        return _ENV  # type: ignore
    if key not in _ENV:
        raise KeyError(
            '<{0}{1}> does not exist as environment variable'.format(key, ': {0}'.format(typ.__name__) if typ else '')
        )
    val = _ENV[key]
    if typ and not isinstance(val, (typ,)):
        raise TypeError(
            '<{0}{1}> does not exist as environment variable'.format(key, ': {0}'.format(typ.__name__) if typ else '')
        )
    return val
