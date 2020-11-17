from petifun_container.libs.shared.infrastructure.mongodb_connection import MongoDBConnection
from petifun_container.libs.user.domain.repositories import UserRepository


class MongoDBUserRepository(UserRepository):
    def __init__(self, connection: MongoDBConnection):
        self.connection = connection

    def search(self, user_id: str) -> any:
        return {}
