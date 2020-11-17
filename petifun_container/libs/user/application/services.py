from petifun_container.libs.shared.application.services import Service
from petifun_container.libs.user.domain.repositories import UserRepository


class UserCreatorService(Service):
    def __init__(self, repository: UserRepository):
        self.repository = repository
