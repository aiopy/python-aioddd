from petifun_container.libs.owner.domain.repositories import OwnerRepository
from petifun_container.libs.shared.infrastructure.mongodb_connection import MongoDBConnection


class MongoDBOwnerRepository(OwnerRepository):
    def __init__(self, connection: MongoDBConnection):
        self.connection = connection

    def search(self, user_id: str) -> any:
        return {}
