"""Models related to the news section in Tibia.com."""
import datetime
import re
import urllib.parse
from typing import List, Optional

from tibiapy import abc
from tibiapy.enums import NewsCategory, NewsType
from tibiapy.errors import InvalidContent
from tibiapy.utils import get_tibia_url, parse_form_data, parse_tibia_date, parse_tibiacom_content, \
    parse_tibiacom_tables, try_enum

__all__ = (
    "News",
    "NewsArchive",
    "NewsEntry",
)

ICON_PATTERN = re.compile(r"newsicon_([^_]+)_(?:small|big)")


class NewsArchive(abc.Serializable):
    """Represents the news archive.

    .. versionadded:: 5.0.0

    Attributes
    ----------
    start_date: :class:`datetime.date`
        The start date to show news for.
    end_date: :class:`datetime.date`
        The end date to show news for.
    types: :class:`list` of :class:`NewsType`
        The type of news to show.
    categories: :class:`list` of :class:`NewsCategory`.
        The categories to show.
    entries: :class:`list` of :class:`NewsEntry`
        The news matching the provided parameters.
    """

    __slots__ = (
        "start_date",
        "end_date",
        "types",
        "categories",
        "entries",
    )

    def __init__(self, **kwargs):
        self.start_date: datetime.date = kwargs.get("start_date")
        self.end_date: datetime.date = kwargs.get("end_date")
        self.types: List[NewsType] = kwargs.get("types", [])
        self.categories: List[NewsCategory] = kwargs.get("categories", [])
        self.entries: List[NewsEntry] = kwargs.get("entries", [])

    def __repr__(self):
        return f"<{self.__class__.__name__} start_date={self.start_date!r} end_date={self.end_date!r}>"

    @property
    def url(self):
        return self.get_url()

    @property
    def form_data(self):
        return self.get_form_data(self.start_date, self.end_date, self.categories, self.types)

    @classmethod
    def get_form_data(cls, start_date, end_date, categories=None, types=None):
        """Get the form data attributes to search news with specific parameters.

        Parameters
        ----------
        start_date: :class:`datetime.date`
            The beginning date to search dates in.
        end_date: :class:`datetime.date`
            The end date to search dates in.
        categories: `list` of :class:`NewsCategory`
            The allowed categories to show. If left blank, all categories will be searched.
        types: `list` of :class:`NewsType`
            The allowed news types to show. if unused, all types will be searched.

        Returns
        -------
        :class:`dict`
            A dictionary with the required form data to search news in the archive.
        """
        if not categories:
            categories = list(NewsCategory)
        if not types:
            types = list(NewsType)
        data = {
            "filter_begin_day": start_date.day,
            "filter_begin_month": start_date.month,
            "filter_begin_year": start_date.year,
            "filter_end_day": end_date.day,
            "filter_end_month": end_date.month,
            "filter_end_year": end_date.year,
        }
        for category in categories:
            key = f"filter_{category.value}"
            data[key] = category.value
        if NewsType.FEATURED_ARTICLE in types:
            data["filter_article"] = "article"
        if NewsType.NEWS in types:
            data["filter_news"] = "news"
        if NewsType.NEWS_TICKER in types:
            data["filter_ticker"] = "ticker"
        return data

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

    @classmethod
    def from_content(cls, content):
        """Get a list of news from the HTML content of the news search page.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the page.

        Returns
        -------
        :class:`NewsArchive`
            The news archive with the news found.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a news search's page.
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            tables = parse_tibiacom_tables(parsed_content)
            if "News Archive Search" not in tables:
                raise InvalidContent("content is not from the news archive section in Tibia.com")
            form = parsed_content.find("form")
            news_archive = cls._parse_filtering(form)
            if "Search Results" in tables:
                rows = tables["Search Results"].find_all("tr", attrs={"class": ["Odd", "Even"]})
                for row in rows:
                    cols_raw = row.find_all('td')
                    if len(cols_raw) != 3:
                        continue
                    entry = cls._parse_entry(cols_raw)
                    news_archive.entries.append(entry)
            return news_archive
        except (AttributeError, IndexError, ValueError, KeyError) as e:
            raise InvalidContent("content is not from the news archive section in Tibia.com", e)

    @classmethod
    def _parse_filtering(cls, form):
        form_data = parse_form_data(form)
        start_date = datetime.date(
            int(form_data.pop("filter_begin_year")),
            int(form_data.pop("filter_begin_month")),
            int(form_data.pop("filter_begin_day")),
        )
        end_date = datetime.date(
            int(form_data.pop("filter_end_year")),
            int(form_data.pop("filter_end_month")),
            int(form_data.pop("filter_end_day")),
        )
        news_types = []
        for news_type in NewsType:
            value = form_data.pop(news_type.filter_name, None)
            if value:
                news_types.append(news_type)
        categories = []
        for category in NewsCategory:
            value = form_data.pop(category.filter_name, None)
            if value:
                categories.append(category)
        return cls(start_date=start_date, end_date=end_date, categories=categories, types=news_types)

    @classmethod
    def _parse_entry(cls, cols_raw):
        img = cols_raw[0].find('img')
        img_url = img["src"]
        category_name = ICON_PATTERN.search(img_url)
        category = try_enum(NewsCategory, category_name.group(1))
        for br in cols_raw[1].find_all("br"):
            br.replace_with("\n")
        date_str, news_type_str = cols_raw[1].text.splitlines()
        date = parse_tibia_date(date_str)
        news_type_str = news_type_str.replace('\xa0', ' ')
        news_type = try_enum(NewsType, news_type_str)
        title = cols_raw[2].text
        news_link = cols_raw[2].find('a')
        url = urllib.parse.urlparse(news_link["href"])
        query = urllib.parse.parse_qs(url.query)
        news_id = int(query["id"][0])
        return NewsEntry(news_id, title, news_type, category, date, category_icon=img_url)


class News(abc.BaseNews, abc.Serializable):
    """Represents a news entry.

    Attributes
    ----------
    id: :class:`int`
        The internal ID of the news entry.
    title: :class:`str`
        The title of the news entry.
    category: :class:`NewsCategory`
        The category this belongs to.
    category_icon: :class:`str`
        The URL of the icon corresponding to the category.
    date: :class:`datetime.date`
        The date when the news were published.
    content: :class:`str`, optional
        The raw html content of the entry.
    thread_id: :class:`int`, optional
        The thread id of the designated discussion thread for this entry.
    """

    def __init__(self, news_id, title, content, date, category, **kwargs):
        self.id: int = news_id
        self.title: str = title
        self.content: str = content
        self.date: datetime.date = date
        self.category: NewsCategory = category
        self.thread_id: Optional[int] = kwargs.get("thread_id", None)
        self.category_icon: Optional[str] = kwargs.get("category_icon")

    # id, title, category and date inherited from BaseNews.
    __slots__ = (
        "id",
        "title",
        "category",
        "category_icon",
        "date",
        "content",
        "thread_id",
    )

    @property
    def thread_url(self):
        """:class:`str`: The URL to the thread discussing this news entry, if any."""
        return abc.BaseThread.get_url(self.thread_id) if self.thread_id else None

    @classmethod
    def from_content(cls, content, news_id=0):
        """Get a news entry by its HTML content from Tibia.com.

        Notes
        -----
        Since there's no way to obtain the entry's Id from the page contents, it will always be 0.
        A news_id can be passed to set the news_id of the resulting object.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the page.
        news_id: :class:`int`, optional
            The news_id belonging to the content being parsed.

        Returns
        -------
        :class:`News`
            The news article found in the page.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a news' page.
        """
        if "News not found" in content:
            return None
        try:
            parsed_content = parse_tibiacom_content(content)
            # Read Information from the headline
            headline = parsed_content.find("div", attrs={"class": "NewsHeadline"})
            img = headline.find('img')
            img_url = img["src"]
            category_name = ICON_PATTERN.search(img_url)
            category = try_enum(NewsCategory, category_name.group(1))
            title_div = headline.find("div", attrs={"class": "NewsHeadlineText"})
            title = title_div.text.replace('\xa0', ' ')
            date_div = headline.find("div", attrs={"class": "NewsHeadlineDate"})
            date_str = date_div.text.replace('\xa0', ' ').replace('-', '').strip()
            date = parse_tibia_date(date_str)

            # Read the page's content.
            content_table = parsed_content.find("table")
            content_row = content_table.find("td")
            content = content_row.encode_contents().decode()
            thread_id = None
            thread_link = content_table.select_one("div.NewsForumLink a")
            if thread_link:
                url = urllib.parse.urlparse(thread_link["href"])
                query = urllib.parse.parse_qs(url.query)
                thread_id = int(query["threadid"][0])

            return cls(news_id, title, content, date, category, thread_id=thread_id, category_icon=img_url)
        except AttributeError:
            raise InvalidContent("content is not from the news archive section in Tibia.com")


class NewsEntry(abc.BaseNews, abc.Serializable):
    """A news entry from the news archive.

    Attributes
    ----------
    id: :class:`int`
        The internal ID of the news entry.
    title: :class:`str`
        The title of the news entry.
        News tickers have a fragment of their content as a title.
    category: :class:`NewsCategory`
        The category this belongs to.
    category_icon: :class:`str`
        The URL of the icon corresponding to the category.
    date: :class:`datetime.date`
        The date when the news were published.
    type: :class:`NewsType`
        The type of news of this list entry.
    """

    __slots__ = (
        "id",
        "title",
        "category",
        "category_icon",
        "date",
        "type",
    )

    def __init__(self, news_id, title, news_type, category, date, **kwargs):
        self.id: int = news_id
        self.title: str = title
        self.type: NewsType = news_type
        self.category: NewsCategory = category
        self.date: datetime.datetime = date
        self.category_icon: Optional[str] = kwargs.get("category_icon", None)

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id} title={self.title!r} type={self.type!r} " \
               f"category={self.category!r} date={self.date!r}>"
