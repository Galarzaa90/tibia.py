"""Models related to the news section in Tibia.com."""
import datetime
from typing import Optional, Set, List

from tibiapy.enums import NewsCategory, NewsType
from tibiapy.models import BaseModel
from tibiapy.urls import get_news_archive_url, get_news_url

__all__ = (
    "BaseNews",
    "News",
    "NewsArchive",
    "NewsEntry",
)


class BaseNews(BaseModel):
    """Base class for all news classes.

    Implements the :py:attr:`id` attribute and common properties.

    The following implement this class:

    - :class:`.News`
    - :class:`.NewsEntry`
    """

    id: int
    """The internal ID of the news entry."""
    category: NewsCategory
    """The category this belongs to."""

    def __eq__(self, o: object) -> bool:
        """Two news articles are considered equal if their names or ids are equal."""
        return self.id == o.id if isinstance(o, self.__class__) else False

    @property
    def url(self) -> str:
        """The URL to the Tibia.com page of the news entry."""
        return get_news_url(self.id)


class News(BaseNews):
    """Represents a news article."""

    title: str
    """The title of the news entry."""
    published_on: datetime.date
    """The date when the news were published."""
    content: str
    """The raw html content of the entry."""
    thread_id: Optional[int] = None
    """The thread id of the designated discussion thread for this entry."""

    @property
    def thread_url(self) -> str:
        """The URL to the thread discussing this news entry, if any."""
        return get_news_url(self.thread_id) if self.thread_id else None


class NewsEntry(BaseNews):
    """Represents a news article listed in the News Archive."""

    title: str
    """The title of the news entry.

    News tickers have a fragment of their content as a title.
    """
    published_on: datetime.date
    """The date when the news were published."""
    type: NewsType
    """The type of news of this list entry."""


class NewsArchive(BaseModel):
    """A news entry from the news archive."""

    from_date: datetime.date
    """The start date to show news for."""
    to_date: datetime.date
    """The end date to show news for."""
    types: Set[NewsType]
    """The type of news to show."""
    categories: Set[NewsCategory]
    """The categories to show."""

    entries: List[NewsEntry]
    """The news matching the provided parameters."""

    @property
    def url(self) -> str:
        """Get the URL to the News Archive in Tibia.com."""
        return get_news_archive_url()
