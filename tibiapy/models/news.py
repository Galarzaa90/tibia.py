"""Models related to the news section in Tibia.com."""
import datetime
from typing import Optional, Set, List

from pydantic import BaseModel

from tibiapy import NewsCategory, NewsType
from tibiapy.utils import get_tibia_url

__all__ = (
    "News",
    "NewsArchive",
    "NewsEntry"
)

class BaseNews(BaseModel):
    id: int
    """The internal ID of the news entry."""

    @property
    def url(self):
        """:class:`str`: The URL to the Tibia.com page of the news entry."""
        return self.get_url(self.id)

    @classmethod
    def get_url(cls, news_id):
        """Get the Tibia.com URL for a news entry by its id.

        Parameters
        ------------
        news_id: :class:`int`
            The id of the news entry.

        Returns
        --------
        :class:`str`
            The URL to the news' page
        """
        return get_tibia_url("news", "newsarchive", id=news_id)


class News(BaseNews):
    title: str
    """The title of the news entry."""
    category: NewsCategory
    """The category this belongs to."""
    category_icon: str
    """The URL of the icon corresponding to the category."""
    date: datetime.date
    """The date when the news were published."""
    content: str
    """The raw html content of the entry."""
    thread_id: Optional[int] = None
    """The thread id of the designated discussion thread for this entry."""

    @property
    def thread_url(self):
        """:class:`str`: The URL to the thread discussing this news entry, if any."""
        return self.get_url(self.thread_id) if self.thread_id else None


class NewsEntry(BaseNews):
    title: str
    """The title of the news entry.
    
    News tickers have a fragment of their content as a title.
    """
    category: NewsCategory
    """The category this belongs to."""
    category_icon: str
    """The URL of the icon corresponding to the category."""
    date: datetime.date
    """The date when the news were published."""
    type: NewsType
    """The type of news of this list entry."""


class NewsArchive(BaseModel):
    start_date: datetime.date
    """The start date to show news for."""
    end_date: datetime.date
    """The end date to show news for."""
    types: Set[NewsType]
    """The type of news to show."""
    categories: Set[NewsCategory]
    """The categories to show."""
    entries: List[NewsEntry]
    """The news matching the provided parameters."""


    @property
    def url(self):
        return self.get_url()


    @classmethod
    def get_url(cls):
        """Get the URL to Tibia.com's news archive page.

        Notes
        -----
        It is not possible to perform a search using query parameters.
        News searches can only be performed using POST requests sending the parameters as form-data.

        Returns
        -------
        :class:`str`
            The URL to the news archive page on Tibia.com.
        """
        return get_tibia_url("news", "newsarchive")
    