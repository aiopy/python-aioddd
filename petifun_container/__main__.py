from inspect import signature
from pprint import pprint
from typing import Any, Dict, List, Type

from aioddd import Container
from petifun_container.libs.owner.application.services import OwnerCreatorService
from petifun_container.libs.owner.domain.repositories import OwnerRepository
from petifun_container.libs.owner.infrastructure.mongodb_repositories import MongoDBOwnerRepository
from petifun_container.libs.shared.application.services import Service
from petifun_container.libs.shared.infrastructure.mongodb_connection import MongoDBConnection
from petifun_container.libs.user.application.services import UserCreatorService
from petifun_container.libs.user.domain.repositories import UserRepository
from petifun_container.libs.user.infrastructure.mongodb_repositories import MongoDBUserRepository

if __name__ == '__main__':
    container = Container()
    container.resolve([
        ('environment', 'development'),
        ('total', 3),
        MongoDBConnection,
        UserCreatorService,
        (UserRepository, MongoDBUserRepository),
        (OwnerRepository, MongoDBOwnerRepository),
        (
            OwnerCreatorService,
            OwnerCreatorService,
            {'count': container.resolve_parameter(lambda di: di.get('total', typ=int))}
        ),
        ('tz', 'utc'),
    ])

    assert container.__contains__(MongoDBConnection)
    assert container.__contains__(UserRepository)
    assert container.__contains__(OwnerRepository)
    assert container.__contains__(UserCreatorService)
    assert container.__contains__(OwnerCreatorService)

    assert container.get(UserCreatorService).repository is container.get(UserRepository)
    assert container.get(OwnerCreatorService).repository is container.get(OwnerRepository)
    assert container.get(OwnerCreatorService).count == 3
    assert container.get('total', typ=int) == 3



