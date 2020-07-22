from datetime import datetime, timedelta, tzinfo
from time import time
from typing import Optional
from uuid import uuid4, UUID

from .errors import IdInvalidError, TimestampInvalidError


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
        except IdInvalidError as _:
            return False

    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value


class Timestamp:
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
        else:
            return datetime.fromtimestamp(other.value(), tz) - datetime.fromtimestamp(self._value, tz)

    def value(self) -> int:
        return self._value
