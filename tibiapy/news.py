import re
import urllib.parse

from tibiapy import abc
from tibiapy.enums import NewsCategory, NewsType
from tibiapy.utils import parse_tibiacom_content, try_enum, parse_tibia_date

__all__ = ("NewsEntry", "ListedNews",)


ICON_PATTERN = re.compile(r"newsicon_([^_]+)_(?:small|big)")


class NewsEntry(abc.BaseNews):
    def __init__(self, news_id, title, content, date, category, thread_id=None):
        self.id = news_id
        self.title = title
        self.content = content
        self.date = date
        self.category = category
        self.thread_id = thread_id

    __slots__ = ("content", "thread_id", )

    @classmethod
    def from_content(cls, content, news_id=0):
        parsed_content = parse_tibiacom_content(content)
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

        content_table = parsed_content.find("table")
        content_row = content_table.find("td")
        content = content_row.encode_contents()
        thread_id = None
        thread_div = content_table.find("div")
        if thread_div:
            news_link = thread_div.find('a')
            url = urllib.parse.urlparse(news_link["href"])
            query = urllib.parse.parse_qs(url.query)
            thread_id = int(query["threadid"][0])

        return cls(news_id, title, content, date, category, thread_id)


class ListedNews(abc.BaseNews):
    def __init__(self, news_id, title, news_type, category, date):
        self.id = news_id
        self.title = title
        self.type = news_type
        self.category = category
        self.date = date

    __slots__ = ("type", )

    def __repr__(self):
        return "<{0.__class__.__name__} id={0.id} title={0.title!r} type={0.type!r} category={0.category!r}" \
               " date={0.date!r}>".format(self)

    @classmethod
    def from_content(cls, content):
        parsed_content = parse_tibiacom_content(content)
        tables = parsed_content.find_all("table", attrs={"width": "100%"})
        news = []
        if len(tables) < 2:
            return news
        news_table = tables[0]
        rows = news_table.find_all("tr", attrs={"class": ["Odd", "Even"]})
        for row in rows:
            cols_raw = row.find_all('td')
            entry = cls._parse_entry(cols_raw)
            news.append(entry)
        return news

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
        return cls(news_id, title, news_type, category, date)
