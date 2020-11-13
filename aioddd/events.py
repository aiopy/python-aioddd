from abc import ABC, abstractmethod
from calendar import timegm
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Type, Union
from uuid import uuid4

from .errors import EventMapperNotFoundError


@dataclass
class Event:
    """Class for keeping track of an Event."""

    @dataclass
    class Attributes:
        """Class for keeping track of an Attributes of Event."""

    @dataclass
    class Meta:
        """Class for keeping track of a Metas of Event."""

        __slots__ = ('id', 'type', 'occurred_on')
        id: str
        type: str
        occurred_on: int

    attributes: Attributes = field(default_factory=lambda: Event.Attributes())
    meta: Meta = field(
        default_factory=lambda: Event.Meta(
            id=str(uuid4()),
            type='event',
            occurred_on=timegm(datetime.utcnow().utctimetuple()),
        )
    )


class EventMapper:
    __slots__ = ('event_type', 'service_name', 'event_name')

    event_type: Type[Event]
    service_name: str
    event_name: str

    def belongs_to(self, msg: Event) -> bool:
        return isinstance(msg, self.event_type)

    def encode(self, msg: Event) -> Dict[str, Any]:
        return {
            **asdict(msg.meta),
            'attributes': self.map_attributes(msg.attributes),
            'meta': {'message': f'{self.service_name}.{self.event_name}'},
        }

    def decode(self, data: Dict[str, Any]) -> Event:
        attributes = self.event_type.Attributes(**data['attributes'])  # type: ignore
        return self.event_type(
            attributes=attributes,
            meta=self.event_type.Meta(
                id=data['id'],
                type=data['type'],
                occurred_on=data['occurred_on'],
            ),
        )

    @staticmethod
    def map_attributes(attributes: Event.Attributes) -> Dict[str, Any]:
        return asdict(attributes)


def find_event_mapper_by_name(name: str, mappers: List[EventMapper]) -> EventMapper:
    for mapper in mappers:
        if f'{mapper.service_name}.{mapper.event_name}' == name:
            return mapper
    raise EventMapperNotFoundError.create(detail={'name': name})


def find_event_mapper_by_type(msg: Event, mappers: List[EventMapper]) -> EventMapper:
    for mapper in mappers:
        if mapper.belongs_to(msg):
            return mapper
    raise EventMapperNotFoundError.create(detail={'type': str(type(msg))})


class ConfigEventMappers:
    _mappers: List[EventMapper]

    def __init__(self, mappers: List[EventMapper]) -> None:
        self._mappers = mappers

    def add(self, mappers: Union[EventMapper, List[EventMapper]]) -> None:
        if isinstance(mappers, EventMapper):
            self._mappers.append(mappers)
        elif isinstance(mappers, list):
            for mapper in mappers:
                self._mappers.append(mapper)

    def all(self) -> List[EventMapper]:
        return self._mappers


class EventPublisher(ABC):
    @abstractmethod
    async def publish(self, events: List[Event]) -> None:
        pass  # pragma: no cover


class EventPublishers(EventPublisher):
    _publishers: List[EventPublisher]

    def __init__(self, publishers: List[EventPublisher]) -> None:
        self._publishers = publishers

    def add(self, publishers: Union[EventPublisher, List[EventPublisher]]) -> None:
        if not isinstance(publishers, list):
            publishers = [publishers]
        for publisher in publishers:
            self._publishers.append(publisher)

    async def publish(self, events: List[Event]) -> None:
        for publisher in self._publishers:
            await publisher.publish(events)


class EventHandler(ABC):
    @abstractmethod
    def subscribed_to(self) -> List[Type[Event]]:
        pass  # pragma: no cover

    @abstractmethod
    async def handle(self, events: List[Event]) -> None:
        pass  # pragma: no cover


class EventBus(ABC):
    @abstractmethod
    async def notify(self, events: List[Event]) -> None:
        pass  # pragma: no cover


class SimpleEventBus(EventBus):
    _handlers: List[EventHandler]

    def __init__(self, handlers: List[EventHandler]):
        self._handlers = handlers

    def add_handler(self, handler: Union[EventHandler, List[EventHandler]]) -> None:
        if not isinstance(handler, list):
            handler = [handler]
        for handler_ in handler:
            self._handlers.append(handler_)

    async def notify(self, events: List[Event]) -> None:
        for event in events:
            for handler in self._handlers:
                for event_type in handler.subscribed_to():
                    if isinstance(event, event_type):
                        await handler.handle([event])


class InternalEventPublisher(EventPublisher):
    __slots__ = '_event_bus'

    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus

    async def publish(self, events: List[Event]) -> None:
        await self._event_bus.notify(events=events)
