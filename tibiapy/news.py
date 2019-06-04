import datetime
import re
import urllib.parse
from typing import Optional

from tibiapy import abc, InvalidContent
from tibiapy.enums import NewsCategory, NewsType
from tibiapy.utils import parse_tibiacom_content, try_enum, parse_tibia_date

__all__ = (
    "News",
    "ListedNews",
)


ICON_PATTERN = re.compile(r"newsicon_([^_]+)_(?:small|big)")


class News(abc.BaseNews):
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
        self.id = news_id  # type: int
        self.title = title  # type: str
        self.content = content  # type: content
        self.date = date  # type: datetime.date
        self.category = category  # type: NewsCategory
        self.thread_id = kwargs.get("thread_id", None)  # type: Optional[int]
        self.category_icon = kwargs.get("category_icon")  # type: Optional[str]

    # id, title, category and date inherited from BaseNews.
    __slots__ = (
        "content",
        "thread_id",
    )

    @classmethod
    def from_content(cls, content, news_id=0):
        """
        Gets a news entry by its HTML content from Tibia.com

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
        if "(no news with id " in content:
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
            thread_div = content_table.find("div")
            if thread_div:
                news_link = thread_div.find('a')
                url = urllib.parse.urlparse(news_link["href"])
                query = urllib.parse.parse_qs(url.query)
                thread_id = int(query["threadid"][0])

            return cls(news_id, title, content, date, category, thread_id=thread_id, category_icon=img_url)
        except AttributeError:
            raise InvalidContent("content is not from the news archive section in Tibia.com")


class ListedNews(abc.BaseNews):
    """Represents a news entry.

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

    def __init__(self, news_id, title, news_type, category, date, **kwargs):
        self.id = news_id  # type: int
        self.title = title  # type: str
        self.type = news_type  # type: NewsType
        self.category = category  # type: NewsCategory
        self.date = date  # type: datetime.datetime
        self.category_icon = kwargs.get("category_icon", None)  # type: Optional[str]

    __slots__ = (
        "type",
    )

    def __repr__(self):
        return "<{0.__class__.__name__} id={0.id} title={0.title!r} type={0.type!r} category={0.category!r}" \
               " date={0.date!r}>".format(self)

    @classmethod
    def list_from_content(cls, content):
        """
        Gets a list of news from the HTML content of the news search page.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the page.

        Returns
        -------
        :class:`list` of :class:`ListedNews`
            List of news in the search results.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a news search's page.
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            tables = parsed_content.find_all("table", attrs={"width": "100%"})
            news = []
            news_table = tables[0]
            title_row = news_table.find("td", attrs={"class": "white", "colspan": "3"})
            if title_row.text != "Search Results":
                raise InvalidContent("content is not from the news archive section in Tibia.com")
            rows = news_table.find_all("tr", attrs={"class": ["Odd", "Even"]})
            for row in rows:
                cols_raw = row.find_all('td')
                if len(cols_raw) != 3:
                    continue
                entry = cls._parse_entry(cols_raw)
                news.append(entry)
            return news
        except (AttributeError, IndexError):
            raise InvalidContent("content is not from the news archive section in Tibia.com")

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
        return cls(news_id, title, news_type, category, date, category_icon=img_url)
