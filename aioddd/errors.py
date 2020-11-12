from json import dumps
from typing import Any, Dict, Optional
from uuid import uuid4


def raise_(err: BaseException) -> BaseException:
    raise err  # pragma: no cover


class BaseError(Exception):
    _id: str
    _code: str = 'code'
    _title: str = 'title'
    _detail: str
    _meta: Dict[str, Any]

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args)
        self._id = kwargs.get('id', str(uuid4()))
        self._code = kwargs.get('code', self._code)
        self._title = kwargs.get('title', self._title)
        self._detail = dumps(kwargs.get('detail', {}))
        self._meta = kwargs.get('meta', {})
        self.ensure_there_is_not_a_system_exit()

    @classmethod
    def create(
        cls,
        detail: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Any]] = None,
        **kwargs: Dict[str, Any],
    ) -> 'BaseError':
        return cls(detail=detail or {}, meta=meta or {}, **kwargs)

    def with_exception(self, err: BaseException) -> 'BaseError':
        self._meta.update({'exception': str(err), 'exception_type': str(type(err))})
        self.ensure_there_is_not_a_system_exit()
        return self

    def ensure_there_is_not_a_system_exit(self) -> None:
        if self._meta.get('exception_type', None) == '<class \'SystemExit\'>':
            raise SystemExit(self._meta.get('exception'))

    def id(self) -> str:
        return self._id

    def code(self) -> str:
        return self._code

    def title(self) -> str:
        return self._title

    def detail(self) -> str:
        return self._detail

    def meta(self) -> Dict[str, Any]:
        return self._meta

    def __str__(self) -> str:
        return dumps(
            {
                'id': self._id,
                'code': self._code,
                'title': self._title,
                'detail': self._detail,
                'meta': self._meta,
            },
            indent=2,
        )


class NotFoundError(BaseError):
    _code = 'not_found'
    _title = 'Not found'


class ConflictError(BaseError):
    _code = 'conflict'
    _title = 'Conflict'


class BadRequestError(BaseError):
    _code = 'bad_request'
    _title = 'Bad Request'


class UnauthorizedError(BaseError):
    _code = 'unauthorized'
    _title = 'Unauthorized'


class ForbiddenError(BaseError):
    _code = 'forbidden'
    _title = 'Forbidden'


class UnknownError(BaseError):
    _code = 'unknown'
    _title = 'Unknown error'


class IdInvalidError(ConflictError):
    _code = 'id_invalid'
    _title = 'Invalid id'


class TimestampInvalidError(ConflictError):
    _code = 'timestamp_invalid'
    _title = 'Invalid timestamp'


class DateTimeInvalidError(ConflictError):
    _code = 'datetime_invalid'
    _title = 'Invalid datetime'


class EventMapperNotFoundError(NotFoundError):
    _code = 'event_mapper_not_found'
    _title = 'Event Mapper not found'


class EventNotPublishedError(ConflictError):
    _code = 'event_not_published'
    _title = 'Event not published'


class CommandNotRegisteredError(NotFoundError):
    _code = 'command_not_registered_error'
    _title = 'Command not registered'


class QueryNotRegisteredError(NotFoundError):
    _code = 'query_not_registered_error'
    _title = 'Query not registered'
