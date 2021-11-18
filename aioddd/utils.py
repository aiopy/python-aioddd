from logging import NOTSET, Formatter, Logger, StreamHandler, getLogger
from os import getenv
from typing import Any, Dict, Optional, Type, TypeVar, Union


def get_env(key: str, default: Optional[str] = None, cast_default_to_str: bool = True) -> Optional[str]:
    """Get an environment variable, return default if it is empty or doesn't exist."""
    value = getenv(key, default)
    return str(default) if cast_default_to_str else default if not value or len(value) == 0 else value


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


def env(key: Optional[str] = None, typ: Optional[Type[_T]] = None) -> _T:
    """Get full environment variables resolved if no argument given or env var matching key and optional type given."""
    global _ENV
    if _ENV is None:
        _ENV = env.resolver()  # type: ignore
    if key is None:
        return _ENV  # type: ignore
    if not isinstance(_ENV, dict):
        raise ValueError('"_ENV" variable must be a dict. Check env.resolver method.')
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


env.resolver = lambda: None  # type: ignore
