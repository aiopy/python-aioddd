from datetime import datetime, timedelta, tzinfo
from time import time
from typing import Optional
from uuid import UUID, uuid4

from .errors import IdInvalidError, TimestampInvalidError
from .helpers import datetime_fromisoformat


class Id:
    __slots__ = '_value'

    def __init__(self, value: str) -> None:
        try:
            self._value = str(UUID(value))
        except Exception as err:
            raise IdInvalidError.create(detail={'id': value}).with_exception(err)

    @classmethod
    def generate(cls) -> 'Id':
        return cls(str(uuid4()))

    @staticmethod
    def validate(value: str) -> bool:
        try:
            Id(value)
            return True
        except IdInvalidError:
            return False

    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value


class Timestamp:  # pragma: no cover
    __slots__ = '_value'

    def __init__(self, value: float, utc: bool = True, tz: Optional[tzinfo] = None) -> None:
        try:
            if utc:
                datetime.utcfromtimestamp(value)
            else:
                datetime.fromtimestamp(value, tz)
            self._value = int(value)
        except Exception as err:
            raise TimestampInvalidError.create(detail={'timestamp': int(value)}).with_exception(err)

    @classmethod
    def now(cls) -> 'Timestamp':
        return cls(time())

    def diff(self, other: 'Timestamp', utc: bool = True, tz: Optional[tzinfo] = None) -> timedelta:
        if utc:
            return datetime.utcfromtimestamp(other.value()) - datetime.utcfromtimestamp(self._value)
        return datetime.fromtimestamp(other.value(), tz) - datetime.fromtimestamp(self._value, tz)

    def value(self) -> int:
        return self._value


class StrDateTime:  # pragma: no cover
    __slots__ = ('_value', '_format')

    def __init__(self, value: str, fmt: str = '%Y-%m-%d %H:%M') -> None:
        self._value = datetime_fromisoformat(value).__format__(fmt)
        self._format = fmt

    @classmethod
    def now(cls, utc: bool = True, tz: Optional[tzinfo] = None, fmt: str = '%Y-%m-%d %H:%M') -> 'StrDateTime':
        if utc:
            return cls(value=datetime.utcnow().__str__(), fmt=fmt)
        return cls(value=datetime.now(tz=tz).__str__(), fmt=fmt)

    def format(self) -> str:
        return self._format

    def value(self) -> str:
        return self._value
