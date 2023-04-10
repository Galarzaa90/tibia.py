from abc import abstractmethod
from typing import TypeVar, Generic

T = TypeVar('T')

class BaseParser(Generic[T]):

    @classmethod
    @abstractmethod
    def from_content(cls, content: str) -> T:
        pass
