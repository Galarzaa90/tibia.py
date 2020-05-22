import datetime
import functools
import json
import re
import urllib.parse
import warnings
from collections import OrderedDict
from typing import Optional, Type, TypeVar, Union

import bs4

from tibiapy.errors import InvalidContent

TIBIA_CASH_PATTERN = re.compile(r'(\d*\.?\d*)k*$')


def get_tibia_url(section, subtopic, **kwargs):
    """

    Parameters
    ----------
    section: :class:`str`
        The desired section (e.g. community, abouttibia, manual, library)
    subtopic: :class:`str`
        The desired subtopic (e.g. characters, guilds, houses, etc)
    kwargs:
        Additional parameters to pass to the url (e.g name, world, houseid, etc)

    Returns
    -------
    :class:`str`
        The generated Tibia.com URL.

    Examples
    --------
    >>> get_tibia_url("community", "houses", page="view", houseid=55302, world="Gladera")
    https://www.tibia.com/community/?subtopic=houses&page=view&houseid=55302&world=Gladera

    You can also build a dictionary and pass it like:

    >>> params = {'world': "Gladera", }
    >>> get_tibia_url("community", "worlds", **params)
    https://www.tibia.com/community/?subtopic=worlds&world=Gladera
    """
    url = "https://www.tibia.com/%s/?" % section
    params = OrderedDict(subtopic=subtopic)
    if kwargs:
        for key, value in kwargs.items():
            if isinstance(value, str):
                value = value.encode('iso-8859-1')
            params[key] = value
    return url + urllib.parse.urlencode(params)


def parse_integer(number: str, default=0):
    """Parses a string representing an integer, ignoring commas or periods.

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
    try:
        number = re.sub(r'[,.]', '', number.strip())
        return int(number)
    except ValueError:
        return default


def parse_tibia_datetime(datetime_str) -> Optional[datetime.datetime]:
    """Parses date and time from the format used in Tibia.com

    Accepted format:

    - ``MMM DD YYYY, HH:mm:ss ZZZ``, e.g. ``Dec 10 2018, 21:53:37 CET``.

    Parameters
    -------------
    datetime_str: :class:`str`
        The date and time as represented in Tibia.com

    Returns
    -----------
    :class:`datetime.datetime`, optional
        The represented datetime, in UTC.
    """
    try:
        datetime_str = datetime_str.replace(",", "").replace("&#160;", " ")
        # Extracting timezone
        tz = datetime_str[-4:].strip()

        # Convert time string to time object
        # Removing timezone cause CEST and CET are not supported
        t = datetime.datetime.strptime(datetime_str[:-4].strip(), "%b %d %Y %H:%M:%S")

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
    """Parses a date from the format used in Tibia.com

    Accepted format:

    - ``MMM DD YYYY``, e.g. ``Jul 23 2015``

    Parameters
    -----------
    date_str: :class:`str`
        The date as represented in Tibia.com

    Returns
    -----------
    :class:`datetime.date`, optional
        The represented date."""
    try:
        t = datetime.datetime.strptime(date_str.strip(), "%b %d %Y")
        return t.date()
    except (ValueError, AttributeError):
        return None


def parse_tibia_full_date(date_str) -> Optional[datetime.date]:
    """Parses a date in the fuller format used in Tibia.com

    Accepted format:

    - ``MMMM DD, YYYY``, e.g. ``July 23, 2015``

    Parameters
    -----------
    date_str: :class:`str`
        The date as represented in Tibia.com

    Returns
    -----------
    :class:`datetime.date`, optional
        The represended date.
    """
    try:
        t = datetime.datetime.strptime(date_str.strip(), "%B %d, %Y")
        return t.date()
    except (ValueError, AttributeError):
        return None


def parse_tibiadata_datetime(date_dict) -> Optional[datetime.datetime]:
    """Parses time objects from the TibiaData API.

    Time objects are made of a dictionary with three keys:
        date: contains a string representation of the time
        timezone: a string representation of the timezone the date time is based on
        timezone_type: the type of representation used in the timezone key


    Parameters
    ----------
    date_dict: :class:`dict`
        Dictionary representing the time object.

    Returns
    -------
    :class:`datetime.date`, optional
        The represented datetime, in UTC.
    """
    try:
        t = datetime.datetime.strptime(date_dict["date"], "%Y-%m-%d %H:%M:%S.%f")
    except (KeyError, ValueError, TypeError):
        return None

    if date_dict["timezone"] == "CET":
        timezone_offset = 1
    elif date_dict["timezone"] == "CEST":
        timezone_offset = 2
    else:
        return None
    # We subtract the offset to convert the time to UTC
    t = t - datetime.timedelta(hours=timezone_offset)
    return t.replace(tzinfo=datetime.timezone.utc)


def parse_tibiadata_date(date_str) -> Optional[datetime.date]:
    """Parses a date from the format used in TibiaData.

    Parameters
    ----------
    date_str: :class:`str`
        The date as represented in Tibia.com

    Returns
    -------
    :class:`datetime.date`, optional
        The represended date."""
    try:
        t = datetime.datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return t.date()
    except (ValueError, AttributeError):
        return None


def parse_number_words(text_num):
    """Parses the word representation of a number to a integer.

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
    """Attempts to convert an object into a datetime.

    If the date format is known, it's recommended to use the corresponding function
    This is meant to be used in constructors.

    Parameters
    ----------
    obj: :class:`str`, :class:`dict`, :class:`datetime.datetime`
        The object to convert.

    Returns
    -------
    :class:`datetime.datetime`, optional
        The represented datetime, or ``None`` if conversion wasn't possible.
    """
    if obj is None:
        return None
    if isinstance(obj, datetime.datetime):
        return obj
    res = parse_tibia_datetime(obj)
    if res is not None:
        return res
    res = parse_tibiadata_datetime(obj)
    return res


def try_date(obj) -> Optional[datetime.date]:
    """Attempts to convert an object into a date.

    If the date format is known, it's recommended to use the corresponding function
    This is meant to be used in constructors.

    Parameters
    ----------
    obj: :class:`str`, :class:`datetime.datetime`, :class:`datetime.date`
        The object to convert.

    Returns
    -------
    :class:`datetime.date`, optional
        The represented date.
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
    res = parse_tibia_full_date(obj)
    if res is not None:
        return res
    res = parse_tibiadata_date(obj)
    return res


def parse_tibiacom_content(content, *, html_class="BoxContent", tag="div", builder="lxml"):
    """Parses HTML content from Tibia.com into a BeautifulSoup object.

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
    return bs4.BeautifulSoup(content.replace('ISO-8859-1', 'utf-8'), builder, parse_only=strainer)


T = TypeVar('T')
D = TypeVar('D')


def try_enum(cls: Type[T], val, default: D = None) -> Union[T, D]:
    """Attempts to convert a value into their enum value

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
        return default


def parse_json(content):
    """Tries to parse a string into a json object.

    This also performs a trim of all values, recursively removing leading and trailing whitespace.

    Parameters
    ----------
    content: :class:`str`
        A JSON format string.

    Returns
    -------
    obj
        The object represented by the json string.

    Raises
    ------
    InvalidContent
        If the content is not a valid json string.
    """
    try:
        json_content = json.loads(content)
        return _recursive_strip(json_content)
    except json.JSONDecodeError:
        raise InvalidContent("content is not a json string.")


def parse_tibia_money(argument):
    """Parses a string that may contain 'k' as thousand suffix.

    Parameters
    ----------
    argument: :class:`str`
        A numeric string.

    Returns
    -------
    int:
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
    """
    Splits a string listing elements into an actual list.

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


def _recursive_strip(value):
    if isinstance(value, dict):
        return {k: _recursive_strip(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_recursive_strip(i) for i in value]
    if isinstance(value, str):
        return value.strip()
    return value


def deprecated(instead=None):
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
