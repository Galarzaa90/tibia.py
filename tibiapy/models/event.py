"""Models related to the event schedule calendar."""
import datetime
from typing import Any

from tibiapy.models import BaseModel
from tibiapy.urls import get_event_schedule_url


class EventEntry(BaseModel):
    """Represents an event's entry in the calendar."""

    title: str
    """The title of the event."""
    description: str
    """The description of the event."""
    start_date: datetime.date | None = None
    """The day the event starts.

    If the event is continuing from the previous month, this will be `None`."""
    end_date: datetime.date | None = None
    """The day the event ends.

    If the event is continuing on the next month, this will be `None`."""

    color: str | None = None
    """The displayed color of the event."""

    def __eq__(self, other: Any):
        return self.title == other.title

    @property
    def duration(self) -> int | None:
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
    events: list[EventEntry] = []
    """A list of events that happen during this month.

    It might include some events from the previous and next months as well."""

    @property
    def url(self) -> str:
        """Get the URL to the event calendar with the current parameters."""
        return get_event_schedule_url(self.month, self.year)

    def get_events_on(self, date: datetime.date) -> list[EventEntry]:
        """Get a list of events that are active during the specified desired_date.

        Parameters
        ----------
        date:
            The date to check.

        Returns
        -------
        :
            The events that are active during the desired_date, if any.

        Notes
        -----
        Dates outside the calendar's month and year may yield unexpected results.

        """

        def is_between(start: datetime.date | None, end: datetime.date | None, desired_date: datetime.date):
            start = start or datetime.date.min
            end = end or datetime.date.max
            return start <= desired_date <= end

        return [e for e in self.events if is_between(e.start_date, e.end_date, date)]
