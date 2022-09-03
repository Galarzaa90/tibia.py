"""These are functions used thorough the module that may not be intended for public use."""
import datetime
import functools
import itertools
import re
import urllib.parse
import warnings
from collections import OrderedDict
from typing import Dict, Optional, Tuple, Type, TypeVar, Union

import bs4

TIBIA_CASH_PATTERN = re.compile(r'(\d*\.?\d*)\s?k*$')


def convert_line_breaks(element):
    """Convert the <br> tags in a HTML elements to actual line breaks.

    Parameters
    ----------
    element: :class:`bs4.Tag`
        A BeautifulSoup object.
    """
    for br in element.find_all("br"):
        br.replace_with("\n")


def get_tibia_url(section, subtopic=None, *args, anchor=None, test=False, **kwargs):
    """Build a URL to Tibia.com with the given parameters.

    Parameters
    ----------
    section: :class:`str`
        The desired section (e.g. community, abouttibia, manual, library)
    subtopic: :class:`str`, optional
        The desired subtopic (e.g. characters, guilds, houses, etc)
    anchor: :class:`str`
        A link anchor to add to the link.
    args:
        A list of key-value pairs to add as query parameters.
        This allows passing multiple parameters with the same name.
    kwargs:
        Additional parameters to pass to the url as query parameters (e.g name, world, houseid, etc)
    test: :class:`bool`
        Whether to use the test website or not.

    Returns
    -------
    :class:`str`
        The generated Tibia.com URL.

    Examples
    --------
    >>> get_tibia_url("community", "houses", page="view", houseid=55302, world="Gladera")
    https://www.tibia.com/community/?subtopic=houses&page=view&houseid=55302&world=Gladera

    You can also build a dictionary and pass it like:

    >>> params = {'world': "Gladera"}
    >>> get_tibia_url("community", "worlds", **params)
    https://www.tibia.com/community/?subtopic=worlds&world=Gladera
    """
    base_url = "www.tibia.com" if not test else "www.test.tibia.com"
    url = f"https://{base_url}/{section}/?"
    params = OrderedDict(subtopic=subtopic) if subtopic else OrderedDict()
    if kwargs:
        for key, value in kwargs.items():
            if isinstance(value, str):
                value = value.encode('iso-8859-1')
            if value is None:
                continue
            params[key] = value
    url += urllib.parse.urlencode(params)
    if args:
        url += "&"
        url += urllib.parse.urlencode(args)
    if anchor:
        url += f"#{anchor}"
    return url


def parse_form_data(form: bs4.Tag, include_options=True):
    """Parse the currently selected values in a form.

    This should correspond to all the data the form would send if submitted.

    Parameters
    ----------
    form: :class:`bs4.Tag`
        A form tag.
    include_options: :class:`bool`
        Whether to also include listings of all the possible options.
        These will be nested inside the __options__ parameter of the resulting dictionary.

    Returns
    -------
    :class:`dict`
        A dictionary containing all the data.
    """
    data = {}
    if "action" in form.attrs:
        data["__action__"] = form.attrs["action"]
    if "method" in form.attrs:
        data["__method__"] = form.attrs["method"]
    text_inputs = form.find_all("input", {"type": "text"})
    data.update({field.attrs.get("name"): field.attrs.get("value") for field in text_inputs})
    selects = form.find_all("select")
    if include_options:
        data["__options__"] = {}
    for select in selects:
        name = select.attrs.get("name")
        selected_option = select.find("option", {"selected": True})
        if include_options:
            options = select.find_all("option")
            data["__options__"][name] = {opt.text: opt.attrs.get("value") for opt in options}
        data[name] = selected_option.attrs.get("value") if selected_option else None
    checkboxes = form.find_all("input", {"type": "checkbox", "checked": True})
    data.update({field.attrs.get("name"): field.attrs.get("value") for field in checkboxes})
    # Parse Radios
    all_radios = form.find_all("input", {"type": "radio"})
    for name, _radios in itertools.groupby(all_radios, key=lambda t: t.attrs["name"]):
        radios = list(_radios)
        selected_radio = next((r for r in radios if r.attrs.get("checked") is not None), None)
        if include_options:
            data["__options__"][name] = {str(r.next_sibling).strip(): r.attrs["value"] for r in radios}
        data[name] = selected_radio.attrs["value"] if selected_radio else None
    return data


def parse_integer(number: str, default: Optional[int] = 0):
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
        number = re.sub(r'[,.]', '', number.strip())
        return int(number)
    except ValueError:
        return default


def parse_link_info(link_tag):
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


def parse_tibia_datetime(datetime_str) -> Optional[datetime.datetime]:
    """Parse date and time from the format used in Tibia.com.

    Accepted format:

    - ``MMM DD YYYY, HH:mm:ss ZZZ``, e.g. ``Dec 10 2018, 21:53:37 CET``.
    - ``MMM DD YYYY, HH:mm ZZZ``, e.g. ``Dec 10 2018, 21:53 CET``.

    Parameters
    -------------
    datetime_str: :class:`str`
        The date and time as represented in Tibia.com

    Returns
    -----------
    :class:`datetime.datetime`, optional
        The represented datetime, in UTC (timezone aware).
    """
    try:
        datetime_str = datetime_str.replace(",", "").replace("&#160;", " ").strip()
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


def parse_tibia_date(date_str) -> Optional[datetime.date]:
    """Parse a date from the format used in Tibia.com.

    Accepted format:

    - ``MMM DD YYYY``, e.g. ``Jul 23 2015``

    Parameters
    -----------
    date_str: :class:`str`
        The date as represented in Tibia.com

    Returns
    -----------
    :class:`datetime.date`, optional
        The represented date, in UTC (timezone aware).
    """
    try:
        t = datetime.datetime.strptime(date_str.strip(), "%b %d %Y")
        return t.date()
    except (ValueError, AttributeError):
        return None


def parse_tibia_forum_datetime(datetime_str, utc_offset=1):
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
    :class:`datetime`
        The represented datetime, in UTC (timezone aware).
    """
    t = datetime.datetime.strptime(datetime_str.strip(), "%d.%m.%Y %H:%M:%S")
    # Add/subtract hours to get the real time
    t = t - datetime.timedelta(hours=utc_offset)
    return t.replace(tzinfo=datetime.timezone.utc)


def parse_tibia_full_date(date_str) -> Optional[datetime.date]:
    """Parse a date in the fuller format used in Tibia.com.

    Accepted format:

    - ``MMMM DD, YYYY``, e.g. ``July 23, 2015``

    Parameters
    -----------
    date_str: :class:`str`
        The date as represented in Tibia.com

    Returns
    -----------
    :class:`datetime.date`, optional
        The represented date, in UTC (timezone aware).
    """
    try:
        t = datetime.datetime.strptime(date_str.strip(), "%B %d, %Y")
        return t.date()
    except (ValueError, AttributeError):
        return None


def parse_number_words(text_num):
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
    numwords = {}
    units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
    ]

    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

    scales = ["hundred", "thousand", "million", "billion", "trillion"]

    numwords["and"] = (1, 0)
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


def try_datetime(obj) -> Optional[datetime.datetime]:
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
    if isinstance(obj, datetime.datetime):
        return obj
    return parse_tibia_datetime(obj)


def try_date(obj) -> Optional[datetime.date]:
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
    if res is not None:
        return res
    return parse_tibia_full_date(obj)


def parse_tibiacom_content(content, *, html_class="BoxContent", tag="div", builder="lxml"):
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
    return bs4.BeautifulSoup(content.replace('ISO-8859-1', 'utf-8', 1), builder, parse_only=strainer)


def parse_tibiacom_tables(parsed_content) -> Dict[str, bs4.Tag]:
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
    table_containers = parsed_content.find_all("div", attrs={"class": "TableContainer"})
    tables = {}
    for table_container in table_containers:
        text_tag = table_container.find("div", attrs={"class": "Text"})
        table = table_container.find("table", attrs={"class": "TableContent"})
        if not table:
            continue
        tables[text_tag.text.strip()] = table
    return tables


T = TypeVar('T')
D = TypeVar('D')


def try_enum(cls: Type[T], val, default: D = None) -> Union[T, D]:
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


def parse_tibia_money(argument):
    """Parse a string that may contain 'k' as thousand suffix.

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
    except ValueError:
        argument = argument.replace(",", "").strip().lower()
        m = TIBIA_CASH_PATTERN.match(argument)
        if not m or not m.group(1):
            raise ValueError("not a numeric value")
        num = float(m.group(1))
        k_count = argument.count("k")
        num *= pow(1000, k_count)
        return int(num)


def split_list(items, separator=",", last_separator=" and "):
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


def _recursive_strip(value):  # pragma: no cover
    if isinstance(value, dict):
        return {k: _recursive_strip(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_recursive_strip(i) for i in value]
    if isinstance(value, str):
        return value.strip()
    return value


def deprecated(instead=None):  # pragma: no cover
    def actual_decorator(func):
        @functools.wraps(func)
        def decorated(*args, **kwargs):
            warnings.simplefilter('always', DeprecationWarning)
            if instead:
                fmt = "{0.__name__} is deprecated, use {1} instead."
            else:
                fmt = '{0.__name__} is deprecated.'

            warnings.warn(fmt.format(func, instead), stacklevel=3, category=DeprecationWarning)
            warnings.simplefilter('default', DeprecationWarning)
            return func(*args, **kwargs)
        return decorated
    return actual_decorator


def parse_popup(popup_content) -> Tuple[str, bs4.BeautifulSoup]:
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
    title = parts[1].replace(r"'", "").strip()
    html = parts[-1].replace(r"\'", '"').replace(r"'", "").replace(",);", "").replace(", );", "").strip()
    parsed_html = bs4.BeautifulSoup(html, 'lxml')
    return title, parsed_html


results_pattern = re.compile(r'Results: ([\d,]+)')
page_pattern = re.compile(r'page=(\d+)')


def parse_pagination(pagination_block) -> Tuple[int, int, int]:
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
    pages_div, results_div = pagination_block.find_all("div")
    current_page_link = pages_div.find("span", {"class": "CurrentPageLink"})
    page_links = pages_div.find_all("span", {"class": "PageLink"})
    # pages_with_links = pages_div.select(#)
    first_or_last_pages = pages_div.find_all("span", {"class": "FirstOrLastElement"})
    page = -1
    total_pages = -1
    if first_or_last_pages:
        last_page_link = first_or_last_pages[-1].find("a")
        if last_page_link:
            m = page_pattern.search(last_page_link["href"])
            if m:
                total_pages = int(m.group(1))
        else:
            last_page_link = page_links[-2].find("a")
            total_pages = int(last_page_link.text) + 1
    else:
        last_page_link = page_links[-1]
        total_pages = int(last_page_link.text)
    try:
        page = int(current_page_link.text)
    except ValueError:
        if "First" in current_page_link.text:
            page = 1
        else:
            page = total_pages
    results_count = parse_integer(results_pattern.search(results_div.text).group(1))
    return page, total_pages, results_count
