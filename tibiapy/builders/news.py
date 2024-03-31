from __future__ import annotations

from typing import Collection, List, Optional, TYPE_CHECKING

from tibiapy.models import NewsEntry, NewsArchive, News

if TYPE_CHECKING:
    import datetime
    from typing_extensions import Self
    from tibiapy.enums import NewsType, NewsCategory


class NewsArchiveBuilder:
    def __init__(self):
        self._from_date = None
        self._to_date = None
        self._types = set()
        self._categories = set()
        self._entries = []

    def from_date(self, from_date: datetime.date) -> Self:
        self._from_date = from_date
        return self

    def to_date(self, to_date: datetime.date) -> Self:
        self._to_date = to_date
        return self

    def types(self, types: Collection[NewsType]) -> Self:
        self._types = set(types)
        return self

    def add_type(self, type: NewsType) -> Self:
        self._types.add(type)
        return self

    def categories(self, categories: Collection[NewsCategory]) -> Self:
        self._categories = set(categories)
        return self

    def add_category(self, category: NewsCategory) -> Self:
        self._categories.add(category)
        return self

    def entries(self, entries: List[NewsEntry]) -> Self:
        self._entries = entries
        return self

    def add_entry(self, entry: NewsEntry) -> Self:
        self._entries.append(entry)
        return self

    def build(self) -> NewsArchive:
        return NewsArchive(
            from_date=self._from_date,
            to_date=self._to_date,
            types=self._types,
            categories=self._categories,
            entries=self._entries,
        )


class NewsBuilder:
    def __init__(self):
        self._id = None
        self._category = None
        self._title = None
        self._published_on = None
        self._content = None
        self._thread_id = None

    def id(self, id: int) -> Self:
        self._id = id
        return self

    def category(self, category: NewsCategory) -> Self:
        self._category = category
        return self

    def title(self, title: str) -> Self:
        self._title = title
        return self

    def published_on(self, published_on: datetime.date) -> Self:
        self._published_on = published_on
        return self

    def content(self, content: str) -> Self:
        self._content = content
        return self

    def thread_id(self, thread_id: Optional[int]) -> Self:
        self._thread_id = thread_id
        return self

    def build(self) -> News:
        return News(
            id=self._id,
            category=self._category,
            title=self._title,
            published_on=self._published_on,
            content=self._content,
            thread_id=self._thread_id,
        )
