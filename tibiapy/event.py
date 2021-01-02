import re
import time
import datetime

from typing import List

from tibiapy import abc
from tibiapy.utils import get_tibia_url, parse_popup, parse_tibiacom_content

__all__ = (
    'EventSchedule',
    'EventEntry',
)

month_year_regex = re.compile(r'([A-z]+)\s(\d+)')


class EventSchedule(abc.Serializable):
    """Represents the event's calendar in Tibia.com

    Attributes
    ----------
    month: :class:`int`
        The month being displayed.

        Note that some days from the previous and next month may be included too.
    year: :class:`int`
        The year being displayed.
    events: :class:`list` of :class:`EventEntry`
        A list of events that happen during this month.

        It might include some events from the previous and next months as well.
    """

    __slots__ = (
        'month',
        'year',
        'events',
    )

    def __init__(self, month, year, **kwargs):
        self.month: int = month
        self.year: int = year
        self.events: List[EventEntry] = kwargs.get("events", [])

    def __repr__(self):
        return f"<{self.__class__.__name__} month={self.month} year={self.year}>"

    @property
    def url(self):
        """:class:`str`: Gets the URL to the event calendar with the current parameters."""
        return self.get_url(self.month, self.year)

    def get_events_on(self, date):
        """Gets a list of events that are active during the specified desired_date.

        Parameters
        ----------
        date: :class:`datetime.date`
            The date to check.

        Returns
        -------
        :class:`list` of :class:`EventEntry`
            The events that are active during the desired_date, if any.

        Notes
        -----
        Dates outside the calendar's month and year may yield unexpected results.
        """
        def is_between(start, end, desired_date):
            start = start or datetime.date.min
            end = end or datetime.date.max
            return start <= desired_date <= end
        return [e for e in self.events if is_between(e.start_date, e.end_date, date)]

    @classmethod
    def get_url(cls, month=None, year=None):
        """Gets the URL to the Event Schedule or Event Calendar on Tibia.com

        Notes
        -----
        If no parameters are passed, it will show the calendar for the current month and year.

        Tibia.com limits the dates that the calendar displays, passing a month and year far from the current ones may
        result in the response being for the current month and year instead.

        Parameters
        ----------
        month: :class:`int`, optional
            The desired month.
        year: :class:`int`, optional
            The desired year.

        Returns
        -------
        :class:`str`
            The URL to the calendar with the given parameters.
        """
        return get_tibia_url("news", "eventcalendar", calendarmonth=month, calendaryear=year)

    @classmethod
    def from_content(cls, content):
        """Creates an instance of the class from the html content of the event's calendar.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the page.

        Returns
        -------
        :class:`EventSchedule`
            The event calendar contained in the page

        Raises
        ------
        InvalidContent
            If content is not the HTML of the event's schedule page.
        """
        parsed_content = parse_tibiacom_content(content)

        month_year_div = parsed_content.find("div", {"class": "eventscheduleheaderdateblock"})
        month, year = month_year_regex.search(month_year_div.text).groups()
        month = time.strptime(month, "%B").tm_mon
        year = int(year)

        schedule = cls(month, year)

        events_table = parsed_content.find("table", {"id": "eventscheduletable"})
        day_cells = events_table.find_all("td")
        # Keep track of events that are ongoing
        ongoing_events = []
        # Keep track of all events present in that day
        ongoing_day = 1
        first_day = True
        for day_cell in day_cells:
            day_div = day_cell.find("div")
            day = int(day_div.text)
            # The first cells may belong to the previous month
            if ongoing_day < day:
                month -= 1
            # The last cells may belong to the last month
            if day < ongoing_day:
                month += 1
            if month > 12:
                month = 1
                year += 1
            if month < 1:
                month = 12
                year -= 1
            ongoing_day = day + 1
            today_events = []
            popup_spans = day_cell.find_all('span', attrs={"class": "HelperDivIndicator"})
            for popup in popup_spans:
                title, popup_content = parse_popup(popup["onmouseover"])
                divs = popup_content.find_all("div")
                # Multiple events can be described in the same popup, they come in pairs, title and content.
                for title, content in zip(*[iter(d.text for d in divs)]*2):
                    title = title.replace(":", "")
                    content = content.replace("• ", "")
                    event = EventEntry(title, content)
                    today_events.append(event)
                    # If this is not an event that was already ongoing from previous days, add to list
                    if event not in ongoing_events:
                        # Only add a start date if this is not the first day of the calendar
                        # We do not know the actual start date of the event.
                        if not first_day:
                            event.start_date = datetime.date(day=day, month=month, year=year)
                        ongoing_events.append(event)
            # Check which of the ongoing events did not show up today, meaning it has ended now
            for pending_event in ongoing_events[:]:
                if pending_event not in today_events:
                    # If it didn't show up today, it means it ended yesterday.
                    end_date = datetime.date(day=day, month=month, year=year) - datetime.timedelta(days=1)
                    pending_event.end_date = end_date
                    schedule.events.append(pending_event)
                    # Remove from ongoing
                    ongoing_events.remove(pending_event)
            first_day = False
        # Add any leftover ongoing events without a end date, as we don't know when they end.
        schedule.events.extend(ongoing_events)
        return schedule


class EventEntry(abc.Serializable):
    """Represents an event's entry in the calendar.

    Attributes
    ----------
    title: :class:`str`
        The title of the event.
    description: :class:`str`
        The description of the event.
    start_date: :class:`datetime.date`
        The day the event starts.

        If the event is continuing from the previous month, this will be :obj:`None`.
    end_date: :class:`datetime.date`
        The day the event ends.

        If the event is continuing on the next month, this will be :obj:`None`.
    """

    __slots__ = (
        "title",
        "description",
        "start_date",
        "end_date",
    )

    _serializable_properties = (
        "duration",
    )

    def __init__(self, title, description, **kwargs):
        self.title = title
        self.description = description
        self.start_date = kwargs.get("start_date")
        self.end_date = kwargs.get("end_date")

    def __eq__(self, other):
        return self.title == other.title

    def __repr__(self):
        return f"<{self.__class__.__name__} title={self.title!r} description={self.description!r}>"

    @property
    def duration(self):
        return (self.end_date-self.start_date+datetime.timedelta(days=1)).days if (self.end_date and self.start_date) else None
