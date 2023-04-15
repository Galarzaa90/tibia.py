import datetime
from typing import Collection, List, Optional

from tibiapy import NewsType, NewsCategory
from tibiapy.models import NewsEntry, NewsArchive, News


class NewsArchiveBuilder:
    def __init__(self):
        self._start_date = None
        self._end_date = None
        self._types = set()
        self._categories = set()
        self._entries = []

    def start_date(self, start_date: datetime.date):
        self._start_date = start_date
        return self

    def end_date(self, end_date: datetime.date):
        self._end_date = end_date
        return self

    def types(self, types: Collection[NewsType]):
        self._types = set(types)
        return self

    def add_type(self, type: NewsType):
        self._types.add(type)
        return self

    def categories(self, categories: Collection[NewsCategory]):
        self._categories = set(categories)
        return self

    def add_category(self, category: NewsCategory):
        self._categories.add(category)
        return self

    def entries(self, entries: List[NewsEntry]):
        self._entries = entries
        return self

    def add_entry(self, entry: NewsEntry):
        self._entries.append(entry)
        return self

    def build(self):
        return NewsArchive(
            start_date=self._start_date,
            end_date=self._end_date,
            types=self._types,
            categories=self._categories,
            entries=self._entries,
        )


class NewsBuilder:
    def __init__(self):
        self._id = None
        self._category = None
        self._title = None
        self._date = None
        self._content = None
        self._thread_id = None

    def id(self, id: int):
        self._id = id
        return self

    def category(self, category: NewsCategory):
        self._category = category
        return self

    def title(self, title: str):
        self._title = title
        return self

    def date(self, date: datetime.date):
        self._date = date
        return self

    def content(self, content: str):
        self._content = content
        return self

    def thread_id(self, thread_id: Optional[int]):
        self._thread_id = thread_id
        return self

    def build(self):
        return News(
            id=self._id,
            category=self._category,
            title=self._title,
            date=self._date,
            content=self._content,
            thread_id=self._thread_id,
        )
