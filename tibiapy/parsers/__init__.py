from abc import abstractmethod
from typing import TypeVar, Generic

from tibiapy.parsers.character import *
from tibiapy.parsers.news import NewsArchiveParser, NewsParser

T = TypeVar('T')


class BaseParser(Generic[T]):

    @classmethod
    @abstractmethod
    def from_content(cls, content: str) -> T:
        pass
