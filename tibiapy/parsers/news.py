import datetime
import re
import urllib.parse

import bs4

from tibiapy.builders.news import NewsArchiveBuilder, NewsBuilder
from tibiapy.enums import NewsCategory, NewsType
from tibiapy.errors import InvalidContent
from tibiapy.models.news import NewsArchive, News, NewsEntry
from tibiapy.utils import (parse_tibia_date,
                           parse_tibiacom_content, parse_tibiacom_tables,
                           try_enum, parse_link_info, parse_form_data_new, clean_text)

__all__ = (
    "NewsParser",
    "NewsArchiveParser",
)

ICON_PATTERN = re.compile(r"newsicon_([^_]+)_(?:small|big)")


class NewsArchiveParser:
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
            form = parsed_content.select_one("form")
            builder = NewsArchiveBuilder()
            cls._parse_filter_table(builder, form)
            if "Search Results" in tables:
                rows = tables["Search Results"].select("tr.Odd, tr.Even")
                for row in rows:
                    cols_raw = row.select('td')
                    if len(cols_raw) != 3:
                        continue
                    builder.add_entry(cls._parse_entry(cols_raw))
            return builder.build()
        except (AttributeError, IndexError, ValueError, KeyError) as e:
            raise InvalidContent("content is not from the news archive section in Tibia.com", e) from e

    @classmethod
    def _parse_filter_table(cls, builder: NewsArchiveBuilder, form: bs4.Tag):
        form_data = parse_form_data_new(form)
        builder.from_date(datetime.date(
            int(form_data.values["filter_begin_year"]),
            int(form_data.values["filter_begin_month"]),
            int(form_data.values["filter_begin_day"]),
        )).to_date(
            datetime.date(
                int(form_data.values["filter_end_year"]),
                int(form_data.values["filter_end_month"]),
                int(form_data.values["filter_end_day"]),
            )
        )
        for news_type in NewsType:
            if news_type.filter_name in form_data.values_multiple:
                builder.add_type(news_type)
        for category in NewsCategory:
            if category.filter_name in form_data.values_multiple:
                builder.add_category(category)

    @classmethod
    def _parse_entry(cls, cols_raw):
        img = cols_raw[0].select_one('img')
        img_url = img["src"]
        category_name = ICON_PATTERN.search(img_url)
        category = try_enum(NewsCategory, category_name.group(1))
        for br in cols_raw[1].select("br"):
            br.replace_with("\n")
        date_str, news_type_str = cols_raw[1].text.splitlines()
        date = parse_tibia_date(date_str)
        news_type_str = news_type_str.replace('\xa0', ' ')
        news_type = try_enum(NewsType, news_type_str)
        title = cols_raw[2].text
        news_link = parse_link_info(cols_raw[2].select_one('a'))
        news_id = int(news_link["query"]["id"])
        return NewsEntry(id=news_id, title=title, type=news_type, category=category, published_on=date)


class NewsParser:
    """Represents a news entry."""

    @classmethod
    def from_content(cls, content, news_id=0):
        """Get a news entry by its HTML content from Tibia.com.

        Notes
        -----
        Since there's no way to obtain the entry's ID from the page contents, it will always be 0.
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
            builder = NewsBuilder().id(news_id)
            # Read Information from the headline
            headline = parsed_content.select_one("div.NewsHeadline")
            img = headline.select_one('img')
            img_url = img["src"]
            category_name = ICON_PATTERN.search(img_url)
            builder.category(try_enum(NewsCategory, category_name.group(1)))
            title_div = headline.select_one("div.NewsHeadlineText")
            builder.title(clean_text(title_div))
            date_div = headline.select_one("div.NewsHeadlineDate")
            date_str = clean_text(date_div).replace('-', '').strip()
            builder.published_on(parse_tibia_date(date_str))

            # Read the page's content.
            content_table = parsed_content.select_one("table")
            content_row = content_table.select_one("td")
            builder.content(content_row.encode_contents().decode())
            if thread_link := content_table.select_one("div.NewsForumLink a"):
                url = urllib.parse.urlparse(thread_link["href"])
                query = urllib.parse.parse_qs(url.query)
                builder.thread_id(int(query["threadid"][0]))

            return builder.build()
        except AttributeError as e:
            raise InvalidContent("content is not from the news archive section in Tibia.com") from e
