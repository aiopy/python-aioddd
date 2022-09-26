from logging import NOTSET, Formatter, Logger, StreamHandler, getLogger
from os import getenv
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, cast


def get_env(key: str, default: Optional[str] = None, cast_default_to_str: bool = True) -> Optional[str]:
    """Get an environment variable, return default if it is empty or doesn't exist."""
    value = getenv(key, default)
    if value is None or len(value) == 0:
        value = str(default) if cast_default_to_str else default
    return value


def get_str_env(key: str, default: str = '') -> str:
    return cast(str, get_env(key=key, default=default, cast_default_to_str=True))


_boolean_positive_values: List[str] = ['True', 'true', 'yes', 'Y', 'y', '1']


def get_bool_env(key: str, default: Union[bool, int] = False) -> bool:
    return get_env(key=key, default=str(int(default)), cast_default_to_str=False) in _boolean_positive_values


def get_int_env(key: str, default: Union[bool, int] = 0) -> int:
    val = cast(str, get_env(key=key, default=str(int(default)), cast_default_to_str=False))
    return int(val) if val.isdigit() else default


def get_float_env(key: str, default: Union[bool, int, float] = 0) -> float:
    val = cast(str, get_env(key=key, default=str(float(default)), cast_default_to_str=False))
    return float(val) if val.isdigit() or val.replace('.', '').isdigit() else default


def get_list_str_env(
    key: str,
    default: Optional[List[str]] = None,
    *,
    delimiter: str = ',',
    allow_empty: bool = True,
) -> List[str]:
    val = cast(str, get_env(key=key, default='' if allow_empty else delimiter.join(default or [])))
    return [] if allow_empty and (val is None or len(val) == 0) else val.split(delimiter)


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
    return val  # type: ignore


env.resolver = lambda: None  # type: ignore
