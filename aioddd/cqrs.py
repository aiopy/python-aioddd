from abc import ABC, abstractmethod
from typing import Any, List, Optional, Type, Union

from .errors import CommandNotRegisteredError, QueryNotRegisteredError


class Command(ABC):
    pass


class CommandHandler(ABC):
    @abstractmethod
    def subscribed_to(self) -> Type[Command]:
        pass  # pragma: no cover

    @abstractmethod
    async def handle(self, command: Command) -> None:
        pass  # pragma: no cover


class CommandBus(ABC):
    @abstractmethod
    async def dispatch(self, command: Command) -> None:
        pass  # pragma: no cover


class SimpleCommandBus(CommandBus):
    _handlers: List[CommandHandler]

    def __init__(self, handlers: List[CommandHandler]) -> None:
        self._handlers = handlers

    def add_handler(self, handler: Union[CommandHandler, List[CommandHandler]]) -> None:
        if not isinstance(handler, list):
            handler = [handler]
        for handler_ in handler:
            self._handlers.append(handler_)

    async def dispatch(self, command: Command) -> None:
        handlers = [handler for handler in self._handlers if isinstance(command, handler.subscribed_to())]
        if len(handlers) != 1:
            raise CommandNotRegisteredError.create(detail={'command': command.__class__.__name__})
        await handlers[0].handle(command)


class Query(ABC):
    pass


class Response(dict):
    pass


OptionalResponse = Optional[Union[Any, Response, List[Response]]]


class QueryHandler(ABC):
    @abstractmethod
    def subscribed_to(self) -> Type[Query]:
        pass  # pragma: no cover

    @abstractmethod
    async def handle(self, query: Query) -> OptionalResponse:
        pass  # pragma: no cover


class QueryBus(ABC):
    @abstractmethod
    async def ask(self, query: Query) -> OptionalResponse:
        pass  # pragma: no cover


class SimpleQueryBus(QueryBus):
    _handlers: List[QueryHandler]

    def __init__(self, handlers: List[QueryHandler]) -> None:
        self._handlers = handlers

    def add_handler(self, handler: Union[QueryHandler, List[QueryHandler]]) -> None:
        if not isinstance(handler, list):
            handler = [handler]
        for handler_ in handler:
            self._handlers.append(handler_)

    async def ask(self, query: Query) -> OptionalResponse:
        handlers = [handler for handler in self._handlers if isinstance(query, handler.subscribed_to())]
        if len(handlers) != 1:
            raise QueryNotRegisteredError.create(detail={'query': query.__class__.__name__})
        return await handlers[0].handle(query)
