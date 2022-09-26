# Librería de utilidades Async Python de DDD

¿Qué ofrece?:

* **Aggregates**: Aggregate & AggregateRoot
* **ValueObjects**: Id, Timestamp & StrDateTime
* **CQRS**: Command, CommandBus, SimpleCommandBus, Query, Response, QueryHandler, QueryBus & SimpleQueryBus
* **EventSourcing**: Event, EventMapper, EventPublisher, EventHandler, EventBus, SimpleEventBus & InternalEventPublisher
* **Errors**: raise_, BaseError, NotFoundError, ConflictError, BadRequestError, UnauthorizedError, ForbiddenError, UnknownError, IdInvalidError, TimestampInvalidError, DateTimeInvalidError, EventMapperNotFoundError, EventNotPublishedError, CommandNotRegisteredError & QueryNotRegisteredError
* **Tests**: AsyncMock & mock
* **Utils**: get_env & get_simple_logger

## Requisitos

- Python 3.7+

## Instalación

```shell
python3 -m pip install aioddd
```

## Ejemplo

```python
from asyncio import get_event_loop
from dataclasses import dataclass
from typing import Type
from aioddd import NotFoundError, \
    Command, CommandHandler, SimpleCommandBus, \
    Query, QueryHandler, OptionalResponse, SimpleQueryBus, Event

_products = []

class ProductStored(Event):
    @dataclass
    class Attributes:
        ref: str

    attributes: Attributes

class StoreProductCommand(Command):
    def __init__(self, ref: str):
        self.ref = ref

class StoreProductCommandHandler(CommandHandler):
    def subscribed_to(self) -> Type[Command]:
        return StoreProductCommand

    async def handle(self, command: StoreProductCommand) -> None:
        _products.append(command.ref)

class ProductNotFoundError(NotFoundError):
    _code = 'product_not_found'
    _title = 'Product not found'

class FindProductQuery(Query):
    def __init__(self, ref: str):
        self.ref = ref

class FindProductQueryHandler(QueryHandler):
    def subscribed_to(self) -> Type[Query]:
        return FindProductQuery

    async def handle(self, query: FindProductQuery) -> OptionalResponse:
        if query.ref != '123':
            raise ProductNotFoundError.create(detail={'ref': query.ref})
        return {'ref': query.ref}

async def main() -> None:
    commands_bus = SimpleCommandBus([StoreProductCommandHandler()])
    await commands_bus.dispatch(StoreProductCommand('123'))
    query_bus = SimpleQueryBus([FindProductQueryHandler()])
    response = await query_bus.ask(FindProductQuery('123'))
    print(response)


if __name__ == '__main__':
    get_event_loop().run_until_complete(main())
```

## Licencia

[MIT](https://github.com/aiopy/python-aioddd/blob/master/LICENSE)


### WIP
