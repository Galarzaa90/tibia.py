import datetime


def parse_tibia_datetime(datetime_str):
    """Parses date and time from the format used in Tibia.com

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

    Parameters
    -----------
    date_str: str
        The date as represented in Tibia.com

    Returns
    -----------
    :class:`datetime.date`
        The represended date."""
    try:
        t = datetime.datetime.strptime(date_str.strip(), "%b %d %Y")
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
    # We substract the offset to convert the time to UTC
    t = t - datetime.timedelta(hours=timezone_offset)
    return t.replace(tzinfo=datetime.timezone.utc)


def parse_tibiadata_date(date_str):
    """Parses a date from the format used in TibiaData

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