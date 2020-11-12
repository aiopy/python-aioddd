import pytest

from aioddd import (
    BadRequestError,
    BaseError,
    CommandNotRegisteredError,
    ConflictError,
    DateTimeInvalidError,
    EventMapperNotFoundError,
    EventNotPublishedError,
    ForbiddenError,
    IdInvalidError,
    NotFoundError,
    QueryNotRegisteredError,
    TimestampInvalidError,
    UnauthorizedError,
    UnknownError,
)


def test_base_error_raise_a_system_exit_exception_when_it_is() -> None:
    pytest.raises(SystemExit, lambda: BaseError().with_exception(SystemExit()))


def test_base_error() -> None:
    err = BaseError(id='test_id').with_exception(Exception('test'))
    assert err.id() == 'test_id'
    assert err.code() == 'code'
    assert err.title() == 'title'
    assert err.detail() == '{}'
    assert err.meta() == {'exception': 'test', 'exception_type': "<class 'Exception'>"}
    assert (
        err.__str__()
        == '''{
  "id": "test_id",
  "code": "code",
  "title": "title",
  "detail": "{}",
  "meta": {
    "exception": "test",
    "exception_type": "<class 'Exception'>"
  }
}'''
    )


def test_base_error_create_method() -> None:
    err = BaseError().create(detail={'foo': 'test'}, meta={'test': 'foo'}, id='test_id')
    assert err.id() == 'test_id'
    assert err.code() == 'code'
    assert err.title() == 'title'
    assert err.detail() == '{"foo": "test"}'
    assert err.meta() == {"test": "foo"}


def test_not_found_error() -> None:
    err = NotFoundError()
    assert err.code() == 'not_found'
    assert err.title() == 'Not found'


def test_conflict_error() -> None:
    err = ConflictError()
    assert err.code() == 'conflict'
    assert err.title() == 'Conflict'


def test_bad_request_error() -> None:
    err = BadRequestError()
    assert err.code() == 'bad_request'
    assert err.title() == 'Bad Request'


def test_unauthorized_error() -> None:
    err = UnauthorizedError()
    assert err.code() == 'unauthorized'
    assert err.title() == 'Unauthorized'


def test_forbidden_error() -> None:
    err = ForbiddenError()
    assert err.code() == 'forbidden'
    assert err.title() == 'Forbidden'


def test_unknown_error() -> None:
    err = UnknownError()
    assert err.code() == 'unknown'
    assert err.title() == 'Unknown error'


def test_id_invalid_error() -> None:
    err = IdInvalidError()
    assert err.code() == 'id_invalid'
    assert err.title() == 'Invalid id'


def test_timestamp_invalid_error() -> None:
    err = TimestampInvalidError()
    assert err.code() == 'timestamp_invalid'
    assert err.title() == 'Invalid timestamp'


def test_datetime_invalid_error() -> None:
    err = DateTimeInvalidError()
    assert err.code() == 'datetime_invalid'
    assert err.title() == 'Invalid datetime'


def test_event_mapper_not_found_error() -> None:
    err = EventMapperNotFoundError()
    assert err.code() == 'event_mapper_not_found'
    assert err.title() == 'Event Mapper not found'


def test_event_not_published_error() -> None:
    err = EventNotPublishedError()
    assert err.code() == 'event_not_published'
    assert err.title() == 'Event not published'


def test_command_not_registered_error() -> None:
    err = CommandNotRegisteredError()
    assert err.code() == 'command_not_registered_error'
    assert err.title() == 'Command not registered'


def test_query_not_registered_error() -> None:
    err = QueryNotRegisteredError()
    assert err.code() == 'query_not_registered_error'
    assert err.title() == 'Query not registered'
