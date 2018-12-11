import datetime


def parse_tibia_datetime(datetime_str):
    """Parses date and time from the format used in Tibia.com

    Accepted format:

    - ``MMM DD YYYY, HH:mm:ss ZZZ``, e.g. ``Dec 10 2018, 21:53:37 CET``.

    Parameters
    -------------
    datetime_str: str
        The date and time as represented in Tibia.com

    Returns
    -----------
    :class:`datetime.datetime`
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
    except ValueError:
        return None


def parse_tibia_date(date_str):
    """Parses a date from the format used in Tibia.com

    Accepted format:

    - ``MMM DD YYYY``, e.g. ``Jul 23 2015``

    Parameters
    -----------
    date_str: str
        The date as represented in Tibia.com

    Returns
    -----------
    :class:`datetime.date`
        The represented date."""
    try:
        t = datetime.datetime.strptime(date_str.strip(), "%b %d %Y")
        return t.date()
    except ValueError:
        return None

def parse_tibia_full_date(date_str):
    """Parses a date in the fuller format used in Tibia.com

    Accepted format:

    - ``MMMM DD, YYYY``, e.g. ``July, 23 2015``

    Parameters
    -----------
    date_str: str
        The date as represented in Tibia.com

    Returns
    -----------
    :class:`datetime.date`
        The represended date."""
    try:
        t = datetime.datetime.strptime(date_str.strip(), "%B %d, %Y")
        return t.date()
    except ValueError:
        return None

def parse_tibiadata_datetime(date_dict):
    """Parses time objects from the TibiaData API.

    Time objects are made of a dictionary with three keys:
        date: contains a string representation of the time
        timezone: a string representation of the timezone the date time is based on
        timezone_type: the type of representation used in the timezone key


    Parameters
    ----------
    date_dict:
        Dictionary representing the time object.

    Returns
    -------
    :class:`datetime.date`:
        The represented datetime, in UTC.
    """
    try:
        t = datetime.datetime.strptime(date_dict["date"], "%Y-%m-%d %H:%M:%S.%f")
    except (KeyError, ValueError):
        return None

    if date_dict["timezone_type"] == 2:
        if date_dict["timezone"] == "CET":
            timezone_offset = 1
        elif date_dict["timezone"] == "CEST":
            timezone_offset = 2
        else:
            return None
    else:
        timezone_offset = 1
    # We subtract the offset to convert the time to UTC
    t = t - datetime.timedelta(hours=timezone_offset)
    return t.replace(tzinfo=datetime.timezone.utc)


def parse_tibiadata_date(date_str):
    """Parses a date from the format used in TibiaData.

    Parameters
    -----------
    date_str: str
        The date as represented in Tibia.com

    Returns
    -----------
    :class:`datetime.date`
        The represended date."""
    try:
        t = datetime.datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return t.date()
    except ValueError:
        return None

def parse_number_words(textnum):
    numwords = {}
    units = [
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen",
    ]

    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

    scales = ["hundred", "thousand", "million", "billion", "trillion"]

    numwords["and"] = (1, 0)
    for idx, word in enumerate(units):    numwords[word] = (1, idx)
    for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
    for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    textnum = textnum.replace("-", " ")
    for word in textnum.split():
        if word not in numwords:
          raise Exception("Illegal word: " + word)

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current