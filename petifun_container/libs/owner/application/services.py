from petifun_container.libs.owner.domain.repositories import OwnerRepository
from petifun_container.libs.shared.application.services import Service


class OwnerCreatorService(Service):
    def __init__(self, repository: OwnerRepository, count: int):
        self.repository = repository
        self.count = count
