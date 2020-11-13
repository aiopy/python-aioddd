from dataclasses import asdict, dataclass
from unittest.mock import Mock

import pytest

from aioddd import (
    ConfigEventMappers,
    Event,
    EventBus,
    EventMapper,
    EventMapperNotFoundError,
    EventPublisher,
    EventPublishers,
    Id,
    InternalEventPublisher,
    SimpleEventBus,
    find_event_mapper_by_name,
    find_event_mapper_by_type,
)
from aioddd.testing import AsyncMock, mock


def test_event_and_event_mapper() -> None:
    class _EventTest(Event):
        @dataclass
        class Attributes:
            __slots__ = ('foo',)
            foo: str

        attributes: Attributes

    event = _EventTest(attributes=_EventTest.Attributes(foo='test'))

    assert Id.validate(event.meta.id)
    assert event.meta.type == 'event'
    assert event.attributes.foo == 'test'

    class _EventTestEventMapper(EventMapper):
        event_type = _EventTest
        service_name = 'test_service_name'
        event_name = 'test_name'

    event_mapper = _EventTestEventMapper()

    assert event_mapper.belongs_to(event)
    assert event_mapper.service_name == 'test_service_name'
    assert event_mapper.event_name == 'test_name'

    event_encoded = event_mapper.encode(event)

    assert event_encoded['attributes'] == asdict(event.attributes)
    event_decoded = event_mapper.decode(event_encoded)

    assert event_decoded.meta == event.meta
    assert event_decoded.attributes == event.attributes


def test_find_event_mapper_by_name() -> None:
    class _TestEventMapper(EventMapper):
        service_name = 'svc'
        event_name = 'name'

    mappers = [_TestEventMapper()]
    event_mapper = find_event_mapper_by_name(name='svc.name', mappers=mappers)
    assert event_mapper is mappers[0]


def test_not_find_event_mapper_by_name() -> None:
    pytest.raises(EventMapperNotFoundError, lambda: find_event_mapper_by_name(name='svc.name', mappers=[]))


def test_find_event_mapper_by_type() -> None:
    class _EventTest(Event):
        pass

    class _TestEventMapper(EventMapper):
        event_type = _EventTest

    mappers = [_TestEventMapper()]
    event_mapper = find_event_mapper_by_type(msg=_EventTest({}), mappers=mappers)
    assert event_mapper is mappers[0]


def test_not_find_event_mapper_by_type() -> None:
    class _EventTest(Event):
        pass

    pytest.raises(EventMapperNotFoundError, lambda: find_event_mapper_by_type(msg=_EventTest({}), mappers=[]))


def test_config_event_mappers() -> None:
    class _TestEventMapper1(EventMapper):
        pass

    class _TestEventMapper2(EventMapper):
        pass

    class _TestEventMapper3(EventMapper):
        pass

    sut = ConfigEventMappers(mappers=[_TestEventMapper1()])

    assert isinstance(sut.all()[0], _TestEventMapper1)

    sut.add(mappers=_TestEventMapper2())

    assert isinstance(sut.all()[1], _TestEventMapper2)

    sut.add(mappers=[_TestEventMapper3()])

    assert isinstance(sut.all()[2], _TestEventMapper3)


@pytest.mark.asyncio
async def test_event_publishers() -> None:
    event_publisher_mock1 = mock(EventPublisher, ['publish'])
    event_publisher_mock2 = mock(EventPublisher, ['publish'])
    event_publisher_mock3 = mock(EventPublisher, ['publish'])

    event_publisher_mock1.publish.return_value = None
    event_publisher_mock2.publish.return_value = None
    event_publisher_mock3.publish.return_value = None

    publisher = EventPublishers(publishers=[event_publisher_mock1])
    publisher.add(publishers=event_publisher_mock2)
    publisher.add(publishers=[event_publisher_mock3])

    await publisher.publish(events=[mock(Event)])

    event_publisher_mock1.publish.assert_called_once()
    event_publisher_mock2.publish.assert_called_once()
    event_publisher_mock3.publish.assert_called_once()


@pytest.mark.asyncio
async def test_simple_event_bus() -> None:
    event_handler_mock1 = Mock()
    event_handler_mock2 = Mock()
    event_handler_mock3 = Mock()

    class _EventTest(Event):
        pass

    event = _EventTest()

    event_handler_mock1.subscribed_to = lambda: [_EventTest]
    event_handler_mock1.handle = AsyncMock(return_value=None)
    event_handler_mock2.subscribed_to = lambda: [_EventTest]
    event_handler_mock2.handle = AsyncMock(return_value=None)
    event_handler_mock3.subscribed_to = lambda: [_EventTest]
    event_handler_mock3.handle = AsyncMock(return_value=None)

    bus = SimpleEventBus(handlers=[event_handler_mock1])
    bus.add_handler(handler=event_handler_mock2)
    bus.add_handler(handler=[event_handler_mock3])

    await bus.notify(events=[event])

    event_handler_mock1.handle.assert_called_once()
    event_handler_mock2.handle.assert_called_once()
    event_handler_mock3.handle.assert_called_once()


@pytest.mark.asyncio
async def test_internal_event_publisher() -> None:
    event_bus_mock = mock(EventBus, ['notify'])

    class _EventTest(Event):
        pass

    event = _EventTest()

    event_bus_mock.notify.return_value = None

    publisher = InternalEventPublisher(event_bus=event_bus_mock)

    await publisher.publish(events=[event])

    event_bus_mock.notify.assert_called_once()
