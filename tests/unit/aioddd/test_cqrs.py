from unittest.mock import Mock

import pytest

from aioddd import (
    Command,
    CommandNotRegisteredError,
    Query,
    QueryNotRegisteredError,
    SimpleCommandBus,
    SimpleQueryBus,
)
from aioddd.testing import AsyncMock


@pytest.mark.asyncio
async def test_simple_command_bus() -> None:
    command_handler_mock1 = Mock()
    command_handler_mock2 = Mock()
    command_handler_mock3 = Mock()

    class _CommandTest1(Command):
        pass

    class _CommandTest2(Command):
        pass

    class _CommandTest3(Command):
        pass

    command = _CommandTest1()

    command_handler_mock1.subscribed_to = lambda: _CommandTest1
    command_handler_mock1.handle = AsyncMock(return_value=None)
    command_handler_mock2.subscribed_to = lambda: _CommandTest2
    command_handler_mock2.handle = AsyncMock(return_value=None)
    command_handler_mock3.subscribed_to = lambda: _CommandTest3
    command_handler_mock3.handle = AsyncMock(return_value=None)

    bus = SimpleCommandBus(handlers=[command_handler_mock1])
    bus.add_handler(handler=command_handler_mock2)
    bus.add_handler(handler=[command_handler_mock3])

    await bus.dispatch(command=command)

    command_handler_mock1.handle.assert_called_once()
    command_handler_mock2.handle.assert_not_called()
    command_handler_mock3.handle.assert_not_called()


@pytest.mark.asyncio
async def test_simple_command_bus_fails_because_command_was_not_registered() -> None:
    class _CommandTest(Command):
        pass

    command = _CommandTest()
    bus = SimpleCommandBus(handlers=[])

    with pytest.raises(CommandNotRegisteredError):
        await bus.dispatch(command=command)


@pytest.mark.asyncio
async def test_simple_query_bus() -> None:
    query_handler_mock1 = Mock()
    query_handler_mock2 = Mock()
    query_handler_mock3 = Mock()

    class _QueryTest1(Query):
        pass

    class _QueryTest2(Query):
        pass

    class _QueryTest3(Query):
        pass

    query = _QueryTest1()

    query_handler_mock1.subscribed_to = lambda: _QueryTest1
    query_handler_mock1.handle = AsyncMock(return_value='test')
    query_handler_mock2.subscribed_to = lambda: _QueryTest2
    query_handler_mock2.handle = AsyncMock(return_value=None)
    query_handler_mock3.subscribed_to = lambda: _QueryTest3
    query_handler_mock3.handle = AsyncMock(return_value=None)

    bus = SimpleQueryBus(handlers=[query_handler_mock1])
    bus.add_handler(handler=query_handler_mock2)
    bus.add_handler(handler=[query_handler_mock3])

    res = await bus.ask(query=query)

    query_handler_mock1.handle.assert_called_once()
    query_handler_mock2.handle.assert_not_called()
    query_handler_mock3.handle.assert_not_called()
    assert res == 'test'


@pytest.mark.asyncio
async def test_simple_query_bus_fails_because_query_was_not_registered() -> None:
    class _QueryTest(Query):
        pass

    query = _QueryTest()
    bus = SimpleQueryBus(handlers=[])

    with pytest.raises(QueryNotRegisteredError):
        await bus.ask(query=query)
