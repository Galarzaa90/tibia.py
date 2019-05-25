import re
import urllib.parse

from tibiapy import abc
from tibiapy.enums import NewsCategory, NewsType
from tibiapy.utils import parse_tibiacom_content, try_enum, parse_tibia_date

__all__ = ("NewsEntry",)


ICON_PATTERN = re.compile(r"newsicon_([^_]+)_small")


class NewsEntry(abc.Serializable):
    def __init__(self, news_id, title, news_type, category, date):
        self.id = news_id
        self.title = title
        self.type = news_type
        self.category = category
        self.date = date

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
