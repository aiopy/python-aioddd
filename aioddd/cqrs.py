from abc import ABC, abstractmethod
from typing import Optional, List, Type, TypedDict, Union, Any

from .errors import CommandNotRegisteredError, QueryNotRegisteredError


class Command(ABC):
    pass


class CommandHandler(ABC):
    @abstractmethod
    def subscribed_to(self) -> Type[Command]:
        pass

    @abstractmethod
    async def handle(self, command: Command) -> None:
        pass


class CommandBus(ABC):
    @abstractmethod
    async def dispatch(self, command: Command) -> None:
        pass


class SimpleCommandBus(CommandBus):
    _handlers: List[CommandHandler]

    def __init__(self, handlers: List[CommandHandler]) -> None:
        self._handlers = handlers

    def add_handler(self, handler: Union[CommandHandler, List[CommandHandler]]) -> None:
        if isinstance(handler, CommandHandler):
            self._handlers.append(handler)
        elif isinstance(handler, list):
            self.add_handler(handler=handler)

    async def dispatch(self, command: Command) -> None:
        handlers = [handler for handler in self._handlers if isinstance(command, handler.subscribed_to())]
        if len(handlers) != 1:
            raise CommandNotRegisteredError.create(detail={'command': command.__class__.__name__})
        await handlers[0].handle(command)


class Query(ABC):
    pass


class Response(TypedDict):
    pass


OptionalResponse = Optional[Union[Any, Response, List[Response]]]


class QueryHandler(ABC):
    @abstractmethod
    def subscribed_to(self) -> Type[Query]:
        pass

    @abstractmethod
    async def handle(self, query: Query) -> OptionalResponse:
        pass


class QueryBus(ABC):
    @abstractmethod
    async def ask(self, query: Query) -> OptionalResponse:
        pass


class SimpleQueryBus(QueryBus):
    _handlers: List[QueryHandler]

    def __init__(self, handlers: List[QueryHandler]):
        self._handlers = handlers

    def add_handler(self, handler: Union[QueryHandler, List[QueryHandler]]) -> None:
        if isinstance(handler, QueryHandler):
            self._handlers.append(handler)
        elif isinstance(handler, list):
            self.add_handler(handler=handler)

    async def ask(self, query: Query) -> OptionalResponse:
        handlers = [handler for handler in self._handlers if isinstance(query, handler.subscribed_to())]
        if len(handlers) != 1:
            raise QueryNotRegisteredError.create(detail={'query': query.__class__.__name__})
        return await handlers[0].handle(query)
