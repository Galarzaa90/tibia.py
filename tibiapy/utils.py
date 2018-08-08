import datetime as dt


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
    datetime_str = datetime_str.replace(",", "").replace("&#160;", " ")
    # Extracting timezone
    tz = datetime_str[-4:].strip()

    # Convert time string to time object
    # Removing timezone cause CEST and CET are not supported
    t = dt.datetime.strptime(datetime_str[:-4].strip(), "%b %d %Y %H:%M:%S")

    # Getting the offset
    if tz == "CET":
        utc_offset = 1
    elif tz == "CEST":
        utc_offset = 2
    else:
        utc_offset = 1
    # Add/subtract hours to get the real time
    t = t - dt.timedelta(hours=utc_offset)
    return t.replace(tzinfo=dt.timezone.utc)


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
    t = dt.datetime.strptime(date_str.strip(), "%b %d %Y")
    return t.date()
