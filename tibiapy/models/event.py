"""Models related to the event schedule calendar."""
import datetime
from typing import Any, List, Optional

from tibiapy.models import BaseModel
from tibiapy.urls import get_event_schedule_url


class EventEntry(BaseModel):
    """Represents an event's entry in the calendar."""

    title: str
    """The title of the event."""
    description: str
    """The description of the event."""
    start_date: Optional[datetime.date] = None
    """The day the event starts.

    If the event is continuing from the previous month, this will be :obj:`None`."""
    end_date: Optional[datetime.date] = None
    """The day the event ends.

    If the event is continuing on the next month, this will be :obj:`None`."""

    color: Optional[str] = None
    """The displayed color of the event."""

    def __eq__(self, other: Any):
        return self.title == other.title

    @property
    def duration(self) -> int:
        """The number of days this event will be active for."""
        return (self.end_date - self.start_date + datetime.timedelta(days=1)).days if (
                self.end_date and self.start_date
        ) else None


class EventSchedule(BaseModel):
    """Represents the event's calendar in Tibia.com."""

    month: int
    """The month being displayed.

    Note that some days from the previous and next month may be included too."""
    year: int
    """The year being displayed."""
    events: List[EventEntry] = []
    """A list of events that happen during this month.

    It might include some events from the previous and next months as well."""

    @property
    def url(self) -> str:
        """Get the URL to the event calendar with the current parameters."""
        return get_event_schedule_url(self.month, self.year)

    def get_events_on(self, date: datetime.date) -> List[EventEntry]:
        """Get a list of events that are active during the specified desired_date.

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

        def is_between(start: Optional[datetime.date], end: Optional[datetime.date], desired_date: datetime.date):
            start = start or datetime.date.min
            end = end or datetime.date.max
            return start <= desired_date <= end

        return [e for e in self.events if is_between(e.start_date, e.end_date, date)]
