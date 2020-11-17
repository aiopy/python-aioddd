from abc import ABC, abstractmethod


class UserRepository(ABC):
    @abstractmethod
    def search(self, user_id: str) -> any:
        pass
