"""These are functions used thorough the module that may not be intended for public use."""
from __future__ import annotations

import datetime
import re
import urllib.parse
from collections import defaultdict
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Type, TypeVar, TypedDict, Union

import bs4
from pydantic import BaseModel

from tibiapy.errors import InvalidContentError

TIBIA_CASH_PATTERN = re.compile(r"(\d*\.?\d*)\s?k*$")

T = TypeVar("T")
D = TypeVar("D")


class FormData(BaseModel):
    """Represents data in a HTML form."""

    values: Dict[str, str] = {}
    """The values in the form.

    This contains text fields, select fields and radios.
    """
    values_multiple: Dict[str, List[str]] = defaultdict(list)
    """The selected values in the form of inputs that allow multiple selections.

    This contains the values of check boxes."""
    available_options: Dict[str, Dict[str, str]] = defaultdict(dict)
    """The available options in select fields, radios and check boxes."""
    action: Optional[str] = None
    """The form's action URL."""
    method: Optional[str] = None
    """The form's method."""


def clean_text(tag: Union[bs4.PageElement, str]) -> str:
    """Get the tag's text, removing non-breaking, leading and trailing spaces.

    Parameters
    ----------
    tag: :class:`bs4.Tag`, :class:`str`
        The tax to get the clean content of. Strings are also accepted.

    Returns
    -------
        The tag's cleaned text content.
    """
    text = tag.text if isinstance(tag, bs4.Tag) else tag
    return text.replace("\xa0", " ").strip()


def convert_line_breaks(element: bs4.Tag) -> None:
    """Convert the <br> tags in a HTML elements to actual line breaks.

    Parameters
    ----------
    element: :class:`bs4.Tag`
        A BeautifulSoup object.
    """
    for br in element.select("br"):
        br.replace_with("\n")


def get_rows(table_tag: bs4.Tag) -> bs4.ResultSet[bs4.Tag]:
    """Get all the row tags inside the container.

    A very simple shortcut function used for better code semantics.

    Parameters
    ----------
    table_tag: :class:`bs4.Tag`
        The tag where row tags will be search in. Not necessarily a table tag.

    Returns
    -------
        A result set with all the found rows.
    """
    return table_tag.select("tr")


def parse_form_data(form: bs4.Tag) -> FormData:
    """Parse the currently selected values in a form.

    This should correspond to all the data the form would send if submitted.

    Parameters
    ----------
    form: :class:`bs4.Tag`
        A form tag.

    Returns
    -------
        The values and data of the form.
    """
    form_data = FormData()
    if "action" in form.attrs:
        form_data.action = form.attrs["action"]

    if "method" in form.attrs:
        form_data.method = form.attrs["method"]

    for field in form.select("input[type=text], input[type=hidden]"):
        form_data.values[field.attrs.get("name")] = field.attrs.get("value")

    for select in form.select("select"):
        name = select.attrs.get("name")
        selected_option = select.select_one("option[selected]")
        options = select.select("option")
        form_data.available_options[name].update({clean_text(opt): opt.attrs.get("value") for opt in options})
        form_data.values[name] = selected_option.attrs.get("value") if selected_option else None

    for checkbox in form.select("input[type=checkbox]"):
        name = checkbox.attrs.get("name")
        label = checkbox.parent.text
        value = checkbox.attrs.get("value")
        form_data.available_options[name][label] = value
        if checkbox.has_attr("checked"):
            form_data.values_multiple[name].append(value)

    for radio in form.select("input[type=radio]"):
        name = radio.attrs.get("name")
        value = radio.attrs.get("value")
        label = radio.next_sibling.text.strip()
        form_data.available_options[name][label] = value
        if radio.has_attr("checked"):
            form_data.values[name] = value

    return form_data


def parse_integer(number: str, default: Optional[int] = 0) -> int:
    """Parse a string representing an integer, ignoring commas or periods.

    Parameters
    ----------
    number: :class:`str`
        A string representing a number.
    default: :class:`int`
        The default value to use if the string is not numeric.
        By default, 0 is used.

    Returns
    -------
    :class:`int`
        The represented integer, or the default value if invalid.
    """
    if number is None:
        return default

    try:
        number = re.sub(r"[,.]", "", number.strip())
        return int(number)
    except ValueError:
        return default


class LinkInfo(TypedDict):
    """Represent the dictionary containing link information."""

    text: str
    url: str
    query: Dict[str, Union[List[str], str]]


def parse_link_info(link_tag: bs4.Tag) -> LinkInfo:
    """Parse the information of a link tag.

    It will parse the link's content, target URL as well as the query parameters where applicable.

    Parameters
    ----------
    link_tag: :class:`bs4.Tag`
        The link tag object.

    Returns
    -------
    :class:`dict`:
        A dictionary containing the link's data.

    Examples
    --------
    >>> # <a href="https://www.tibia.com/community/?subtopic=houses&page=view&houseid=55302&world=Gladera">House</>
    >>> parse_link_info(link_tag)
    {
        "text": "House",
        "url": "https://www.tibia.com/community/?subtopic=houses&page=view&houseid=55302&world=Gladera"
        "query": {
            "subtopic": "houses",
            "page": "view",
            "houseid": "55302",
            "world": "Gladera"
        }
    }

    When parsing links that have multiple query parameters, they are displayed as a list.
    Empty parameters are omitted.

    >>> # <a href="https://example.com/?world=&beprotection=-1&worldtypes[]=0&worldtypes[]=3">Link</a>
    >>> parse_link_info(link_tag)
    {
        "text": "Link",
        "url": "https://example.com/?world=&beprotection=-1&worldtypes[]=0&worldtypes[]=3"
        "query": {
            "beprotection": "-1",
            "worldtypes": ["0", "3"]
        }
    }
    """
    url = link_tag["href"]
    info = {"text": link_tag.text.strip(), "url": url, "query": {}}
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.query:
        query_params = urllib.parse.parse_qs(parsed_url.query)
        for param, value in query_params.items():
            if len(value) == 1:
                info["query"][param] = value[0]
            else:
                info["query"][param] = value

    return info


def parse_tibia_datetime(datetime_str: str) -> Optional[datetime.datetime]:
    """Parse date and time from the format used in Tibia.com.

    Accepted format:

    - ``MMM DD YYYY, HH:mm:ss ZZZ``, e.g. ``Dec 10 2018, 21:53:37 CET``.
    - ``MMM DD YYYY, HH:mm ZZZ``, e.g. ``Dec 10 2018, 21:53 CET``.

    Parameters
    ----------
    datetime_str: :class:`str`
        The date and time as represented in Tibia.com

    Returns
    -------
    :class:`datetime.datetime`, optional
        The represented datetime, in UTC (timezone aware).
    """
    try:
        datetime_str = clean_text(datetime_str).replace(",", "")
        # Extracting timezone
        tz = datetime_str[-4:].strip()

        # Convert time string to time object
        # Removing timezone cause CEST and CET are not supported
        try:
            t = datetime.datetime.strptime(datetime_str[:-4].strip(), "%b %d %Y %H:%M:%S")
        except ValueError:
            t = datetime.datetime.strptime(datetime_str[:-4].strip(), "%b %d %Y %H:%M")

        # Getting the offset
        if tz == "CET":
            utc_offset = 1
        elif tz == "CEST":
            utc_offset = 2
        else:
            return None
        # Add/subtract hours to get the real time
        t = t - datetime.timedelta(hours=utc_offset)
        return t.replace(tzinfo=datetime.timezone.utc)
    except (ValueError, AttributeError):
        return None


def parse_tibia_date(date_str: str) -> Optional[datetime.date]:
    """Parse a date from the format used in Tibia.com.

    Accepted format:

    - ``MMM DD YYYY``, e.g. ``Jul 23 2015``

    Parameters
    ----------
    date_str: :class:`str`
        The date as represented in Tibia.com

    Returns
    -------
    :class:`datetime.date`, optional
        The represented date, in UTC (timezone aware).
    """
    try:
        t = datetime.datetime.strptime(date_str.strip(), "%b %d %Y")
        return t.date()
    except (ValueError, AttributeError):
        return None


def parse_tibia_forum_datetime(datetime_str: str, utc_offset: int = 1) -> datetime.datetime:
    """Parse a date in the format used in the Tibia.com forums.

    Accepted format:

    - ``DD.MM.YY HH:mm:ss``, e.g. ``23.07.2015 21:30:30``

    Parameters
    ----------
    datetime_str: :class:`str`
        The string containing the date and time.
    utc_offset: :class:`int`
        The UTC offset to apply to the parsed datetime.

        Since the timestamps contain no timezone information, it can be passed as an additional parameter.

        By default CET (+1) is considered.

    Returns
    -------
    :class:`datetime.datetime`
        The represented datetime, in UTC (timezone aware).
    """
    t = datetime.datetime.strptime(datetime_str.strip(), "%d.%m.%Y %H:%M:%S")
    # Add/subtract hours to get the real time
    t = t - datetime.timedelta(hours=utc_offset)
    return t.replace(tzinfo=datetime.timezone.utc)


def parse_tibia_full_date(date_str: str) -> Optional[datetime.date]:
    """Parse a date in the fuller format used in Tibia.com.

    Accepted format:

    - ``MMMM DD, YYYY``, e.g. ``July 23, 2015``

    Parameters
    ----------
    date_str: :class:`str`
        The date as represented in Tibia.com

    Returns
    -------
    :class:`datetime.date`, optional
        The represented date, in UTC (timezone aware).
    """
    try:
        t = datetime.datetime.strptime(date_str.strip(), "%B %d, %Y")
        return t.date()
    except (ValueError, AttributeError):
        return None


def parse_number_words(text_num: str) -> int:
    """Parse the word representation of a number to a integer.

    Parameters
    ----------
    text_num: :class:`str`
        The text representation of a number.

    Returns
    -------
    :class:`int`
        The number represented by the string.
    """
    units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
    ]

    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

    scales = ["hundred", "thousand", "million", "billion", "trillion"]

    numwords = {"and": (1, 0)}
    for idx, word in enumerate(units):
        numwords[word] = (1, idx)

    for idx, word in enumerate(tens):
        numwords[word] = (1, idx * 10)

    for idx, word in enumerate(scales):
        numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    text_num = text_num.replace("-", " ")
    for word in text_num.split():
        if word not in numwords:
            return 0

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current


def try_datetime(obj: Union[str, datetime.datetime]) -> Optional[datetime.datetime]:
    """Attempt to convert an object into a datetime.

    If the date format is known, it's recommended to use the corresponding function
    This is meant to be used in constructors.

    Parameters
    ----------
    obj: :class:`str`, :class:`dict`, :class:`datetime.datetime`
        The object to convert.

    Returns
    -------
    :class:`datetime.datetime`, optional
        The represented datetime, in UTC (timezone aware), or :obj:`None` if conversion wasn't possible.
    """
    if obj is None:
        return None

    return obj if isinstance(obj, datetime.datetime) else parse_tibia_datetime(obj)


def try_date(obj: Union[str, datetime.datetime, datetime.date]) -> Optional[datetime.date]:
    """Attempt to convert an object into a date.

    If the date format is known, it's recommended to use the corresponding function
    This is meant to be used in constructors.

    Parameters
    ----------
    obj: :class:`str`, :class:`datetime.datetime`, :class:`datetime.date`
        The object to convert.

    Returns
    -------
    :class:`datetime.date`, optional
        The represented date, in UTC (timezone aware).
    """
    if obj is None:
        return None

    if isinstance(obj, datetime.datetime):
        return obj.date()

    if isinstance(obj, datetime.date):
        return obj

    res = parse_tibia_date(obj)
    return res if res is not None else parse_tibia_full_date(obj)


def parse_tables_map(
        parsed_content: bs4.BeautifulSoup,
        selector: str = "div.TableContentContainer",
) -> Dict[str, bs4.Tag]:
    """Parse Tibia.com style tables, building a map with their title as key."""
    tables = parsed_content.select("div.TableContainer")
    output = {}
    for table in tables:
        caption = table.select_one("div.Text")
        if not caption:
            raise InvalidContentError("table has no caption")

        if content_table := table.select_one(selector):
            output[clean_text(caption)] = content_table

    return output


def parse_tibiacom_content(
        content: str,
        *,
        html_class: str = "BoxContent",
        tag: str = "div",
        builder: str = "lxml",
) -> bs4.BeautifulSoup:
    """Parse HTML content from Tibia.com into a BeautifulSoup object.

    Parameters
    ----------
    content: :class:`str`
        The raw HTML content from Tibia.com
    html_class: :class:`str`
        The HTML class of the parsed element. The default value is ``BoxContent``.
    tag: :class:`str`
        The HTML tag select. The default value is ``div``.
    builder: :class:`str`
        The builder to use. The default value is ``lxml``.

    Returns
    -------
    :class:`bs4.BeautifulSoup`, optional
        The parsed content.
    """
    strainer = bs4.SoupStrainer(tag, class_=html_class) if builder != "html5lib" else None
    return bs4.BeautifulSoup(content.replace("ISO-8859-1", "utf-8", 1), builder, parse_only=strainer)


def parse_tibiacom_tables(parsed_content: bs4.BeautifulSoup) -> Dict[str, bs4.Tag]:
    """Parse tables from Tibia.com into a mapping by the tables title.

    This is used for the table style used in Tibia.com, where a table is wrapped in a container with a title.

    Parameters
    ----------
    parsed_content: :class:`bs4.BeautifulSoup`
        The content to find the tables in.

    Returns
    -------
    :class:`dict`
        A dictionary mapping the container titles and the contained table.
    """
    table_containers = parsed_content.select("div.TableContainer")
    tables = {}
    for table_container in table_containers:
        text_tag = table_container.select_one("div.Text")
        if table := table_container.select_one("table.TableContent"):
            tables[text_tag.text.strip()] = table

    return tables


def try_enum(cls: Type[T], val: Any, default: D = None) -> Union[T, D]:
    """Attempt to convert a value into their enum value.

    Parameters
    ----------
    cls: :class:`Enum`
        The enum to convert to.
    val:
        The value to try to convert to Enum
    default: optional
        The value to return if no enum value is found.

    Returns
    -------
    obj:
        The enum value if found, otherwise None.
    """
    if isinstance(val, cls):
        return val

    try:
        return cls(val)
    except ValueError:
        try:
            if isinstance(val, str):
                val = val.upper()

            return cls._member_map_[val]
        except KeyError:
            return default


def parse_tibia_money(argument: str) -> int:
    """Parse a string that may contain 'k' as thousands suffix.

    Parameters
    ----------
    argument: :class:`str`
        A numeric string using k as a prefix for thousands.

    Returns
    -------
    :class:`int`:
        The value represented by the string.
    """
    try:
        return int(argument)
    except ValueError as e:
        argument = argument.replace(",", "").strip().lower()
        m = TIBIA_CASH_PATTERN.match(argument)
        if not m or not m.group(1):
            raise ValueError("not a numeric value") from e

        num = float(m.group(1))
        k_count = argument.count("k")
        num *= pow(1000, k_count)
        return int(num)


def split_list(items: str, separator: str = ",", last_separator: str = " and ") -> List[str]:
    """Split a string listing elements into an actual list.

    Parameters
    ----------
    items: :class:`str`
        A string listing elements.
    separator: :class:`str`
        The separator between each item. A comma by default.
    last_separator: :class:`str`
        The separator used for the last item. ' and ' by default.

    Returns
    -------
    :class:`list` of :class:`str`
        A list containing each one of the items.
    """
    if items is None:
        return None

    items = items.split(separator)
    last_item = items[-1]
    last_split = last_item.split(last_separator)
    if len(last_split) > 1:
        items[-1] = last_separator.join(last_split[:-1])
        items.append(last_split[-1])

    return [e.strip() for e in items]


def parse_popup(popup_content: str) -> Tuple[str, bs4.BeautifulSoup]:
    """Parse the information popups used through Tibia.com.

    Parameters
    ----------
    popup_content: :class:`str`
        The raw content of the javascript function that creates the popup.

    Returns
    -------
    :class:`str`
        The popup's title.
    :class:`bs4.BeautifulSoup`
        The parsed HTML content of the popup.
    """
    parts = popup_content.split(",", 2)
    title = parts[1].replace("'", "").strip()
    html = (
        parts[-1]
        .replace(r"\'", '"')
        .replace("'", "")
        .replace(",);", "")
        .replace(", );", "")
        .strip()
    )
    parsed_html = bs4.BeautifulSoup(html, "lxml")
    return title, parsed_html


results_pattern = re.compile(r"Results: ([\d,]+)")
page_pattern = re.compile(r"page=(\d+)")


def parse_pagination(pagination_block: bs4.Tag) -> Tuple[int, int, int]:
    """Parse a pagination section in Tibia.com and extracts its information.

    Parameters
    ----------
    pagination_block: :class:`bs4.Tag`
        The HTML containing the pagination information.

    Returns
    -------
    page : :class:`int`
        The current page.
    total_pages : :class:`int`
        The total number of pages.
    results_count : :class:`int`
        The total number of results.
    """
    pages_div, results_div = pagination_block.select("small > div")
    current_page_link = pages_div.select_one("span.CurrentPageLink")
    page_links = pages_div.select("span.PageLink")
    # pages_with_links = pages_div.select(#)
    first_or_last_pages = pages_div.select("span.FirstOrLastElement")
    page = -1
    total_pages = -1
    if first_or_last_pages:
        if last_page_link := first_or_last_pages[-1].select_one("a"):
            if m := page_pattern.search(last_page_link["href"]):
                total_pages = int(m.group(1))
        else:
            last_page_link = page_links[-2].select_one("a")
            total_pages = int(last_page_link.text) + 1
    else:
        last_page_link = page_links[-1]
        total_pages = int(last_page_link.text)

    try:
        page = int(current_page_link.text)
    except ValueError:
        page = 1 if "First" in current_page_link.text else total_pages

    results_count = parse_integer(results_pattern.search(results_div.text).group(1))
    return page, total_pages, results_count


def take_while(iterable: Iterable[T], predicate: Callable[[T], bool]) -> Iterable[T]:
    """Go through items in an iterable until the predicate function is not True."""
    for item in iterable:
        if predicate(item):
            yield item
        else:
            break
