import datetime
from typing import Optional, Set, List

from pydantic import BaseModel

from tibiapy import NewsCategory, NewsType


class News(BaseModel):
    id: int
    title: str
    category: NewsCategory
    category_icon: str
    date: datetime.date
    content: str
    thread_id: Optional[int] = None


class NewsEntry(BaseModel):
    id: int
    title: str
    category: NewsCategory
    category_icon: str
    date: datetime.date
    content: str
    type: NewsType


class NewsArchive(BaseModel):
    start_date: datetime.date
    end_date: datetime.date
    types: Set[NewsType]
    categories: Set[NewsCategory]
    entries: List[NewsEntry]
