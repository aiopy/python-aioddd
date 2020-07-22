from abc import ABC
from typing import List

from .cqrs import \
    Command, CommandHandler, CommandBus, SimpleCommandBus, \
    Query, Response, OptionalResponse, QueryHandler, QueryBus, SimpleQueryBus
from .errors import \
    BaseError, \
    NotFoundError, ConflictError, BadRequestError, UnknownError, \
    IdInvalidError, \
    TimestampInvalidError, DateTimeInvalidError, \
    EventMapperNotFoundError, EventNotPublishedError, \
    CommandNotRegisteredError, QueryNotRegisteredError
from .events import Event, EventMapper, EventPublisher, EventHandler, EventBus, SimpleEventBus, \
    find_event_mapper_by_name, find_event_mapper_by_type
from .value_objects import Timestamp, Id

__all__ = (
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
    'UnknownError',
    'IdInvalidError',
    'TimestampInvalidError',
    'DateTimeInvalidError',
    'EventMapperNotFoundError',
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
    # value_objects
    'Id',
    'Timestamp'
)


class Aggregate(ABC):
    pass


class AggregateRoot(Aggregate):
    _events: List[Event]

    def __init__(self) -> None:
        self._events = []

    def pull_aggregate_events(self) -> List[Event]:
        evts = self._events
        self._events = []
        return evts

    def record_aggregate_event(self, event: Event) -> None:
        self._events.append(event)
