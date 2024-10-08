# Async Python DDD utilities library

[![PyPI version](https://badge.fury.io/py/aioddd.svg)](https://badge.fury.io/py/aioddd)
[![PyPIDownloads](https://static.pepy.tech/badge/aioddd)](https://pepy.tech/project/aioddd)
[![CI](https://github.com/aiopy/python-aioddd/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/aiopy/python-aioddd/actions/workflows/ci.yml)

aioddd is an async Python DDD utilities library.

## Installation

Use the package manager [pip](https://pypi.org/project/aioddd/) to install aioddd.

```bash
pip install aioddd
```

## Documentation

- Visit [aioddd docs](https://aiopy.github.io/python-aioddd/).

## Usage

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

## Requirements

- Python >= 3.9

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://github.com/aiopy/python-aioddd/blob/master/LICENSE)
