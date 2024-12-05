from abc import abstractmethod
from typing import Protocol


class AccessTokenRequestHandlerInterface(Protocol):
    @abstractmethod
    def get_access_token_from_request(self) -> str:
        """
        :raises AdapterError:
        """

    @abstractmethod
    def add_access_token_to_request(self, new_access_token: str) -> None: ...

    @abstractmethod
    def delete_access_token_from_request(self) -> None: ...
