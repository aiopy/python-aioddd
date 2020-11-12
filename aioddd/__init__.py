# type: ignore
# pylint: skip-file
from abc import ABC
from typing import List

from .container import Container
from .cqrs import (
    Command,
    CommandBus,
    CommandHandler,
    OptionalResponse,
    Query,
    QueryBus,
    QueryHandler,
    Response,
    SimpleCommandBus,
    SimpleQueryBus,
)
from .errors import (
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
from .events import (
    ConfigEventMappers,
    Event,
    EventBus,
    EventHandler,
    EventMapper,
    EventMapperNotFoundError,
    EventPublisher,
    EventPublishers,
    InternalEventPublisher,
    SimpleEventBus,
    find_event_mapper_by_name,
    find_event_mapper_by_type,
)
from .utils import get_env, get_simple_logger
from .value_objects import Id, Timestamp

__all__ = (
    'Container',
    'Aggregate',
    'AggregateRoot',
    # cqrs
    'Command',
    'CommandHandler',
    'CommandBus',
    'SimpleCommandBus',
    'Query',
    'Response',
    'OptionalResponse',
    'QueryHandler',
    'QueryBus',
    'SimpleQueryBus',
    # errors
    'BaseError',
    'NotFoundError',
    'ConflictError',
    'BadRequestError',
    'UnauthorizedError',
    'ForbiddenError',
    'UnknownError',
    'IdInvalidError',
    'TimestampInvalidError',
    'DateTimeInvalidError',
    'EventNotPublishedError',
    'CommandNotRegisteredError',
    'QueryNotRegisteredError',
    # events
    'Event',
    'EventMapper',
    'EventPublisher',
    'EventHandler',
    'EventBus',
    'SimpleEventBus',
    'find_event_mapper_by_name',
    'find_event_mapper_by_type',
    'EventPublishers',
    'ConfigEventMappers',
    'EventMapperNotFoundError',
    'InternalEventPublisher',
    # utils
    'get_env',
    'get_simple_logger',
    # value_objects
    'Id',
    'Timestamp',
)


class Aggregate(ABC):
    pass


class AggregateRoot(Aggregate):
    _events: List[Event]

    def __init__(self) -> None:
        self._events = []

    def pull_aggregate_events(self) -> List[Event]:
        _events = self._events
        self._events = []
        return _events

    def record_aggregate_event(self, event: Event) -> None:
        self._events.append(event)
