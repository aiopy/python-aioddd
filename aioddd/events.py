from abc import ABC, abstractmethod
from calendar import timegm
from datetime import datetime
from typing import List, Dict, Union, Type, Any, final
from uuid import uuid4

from .errors import EventMapperNotFoundError


class Event(ABC):
    __slots__ = ('_id', '_type', '_occurred_on', '_attributes')

    def __init__(self, attributes: Dict[str, Any], **kwargs):
        self._id = kwargs.get('id', str(uuid4()))
        self._type = kwargs.get('type', 'event')
        self._occurred_on = kwargs.get('occurred_on', timegm(datetime.utcnow().utctimetuple()))
        self._attributes = attributes

    def get_meta(self) -> Dict[str, Union[str, int]]:
        return {
            'id': self._id,
            'type': self._type,
            'occurredOn': self._occurred_on,
        }

    def get_attributes(self) -> Dict[str, Any]:
        return self._attributes


class EventMapper(ABC):
    @abstractmethod
    def belongs_to(self, msg: Event) -> bool:
        pass

    @abstractmethod
    def service_name(self) -> str:
        pass

    @abstractmethod
    def name(self) -> str:
        pass

    def encode(self, msg: Event) -> Dict[str, Any]:
        attrs = self.map_attributes(msg)
        meta = msg.get_meta()
        return {
            'id': meta['id'],
            'type': meta['type'],
            'occurredOn': meta['occurredOn'],
            'attributes': attrs,
            'meta': {
                'message': f'{self.service_name()}.{self.name()}'
            },
        }

    @abstractmethod
    def decode(self, data: Dict[str, Any]) -> Event:
        pass

    @staticmethod
    def map_attributes(msg: Event) -> Dict[str, Any]:
        return msg.get_attributes()


def find_event_mapper_by_name(name: str, mappers: List[EventMapper]) -> EventMapper:
    for mapper in mappers:
        if f'{mapper.service_name()}.{mapper.name()}' == name:
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
        pass


@final
class EventPublishers(EventPublisher):
    _publishers: List[EventPublisher]

    def __init__(self, publishers: List[EventPublisher]) -> None:
        self._publishers = publishers

    def add(self, publishers: Union[EventPublisher, List[EventPublisher]]) -> None:
        if isinstance(publishers, EventPublisher):
            self._publishers.append(publishers)
        elif isinstance(publishers, list):
            for publisher in publishers:
                self._publishers.append(publisher)

    async def publish(self, events: List[Event]) -> None:
        for publisher in self._publishers:
            await publisher.publish(events)


class EventHandler(ABC):
    @abstractmethod
    def subscribed_to(self) -> List[Type[Event]]:
        pass

    @abstractmethod
    async def handle(self, events: List[Event]) -> None:
        pass


class EventBus(ABC):
    @abstractmethod
    async def notify(self, events: List[Event]) -> None:
        pass


class SimpleEventBus(EventBus):
    _handlers: List[EventHandler]

    def __init__(self, handlers: List[EventHandler]):
        self._handlers = handlers

    def add_handler(self, handler: EventHandler) -> None:
        self._handlers.append(handler)

    async def notify(self, events: List[Event]) -> None:
        for event in events:
            for handler in self._handlers:
                for event_type in handler.subscribed_to():
                    if isinstance(event, event_type):
                        await handler.handle([event])
