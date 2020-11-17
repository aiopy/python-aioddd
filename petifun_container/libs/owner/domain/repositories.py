from abc import ABC, abstractmethod


class OwnerRepository(ABC):
    @abstractmethod
    def search(self, user_id: str) -> any:
        pass
