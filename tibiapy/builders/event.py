from __future__ import annotations

from typing import List, TYPE_CHECKING

from tibiapy.models.event import EventSchedule

if TYPE_CHECKING:
    from tibiapy.models.event import EventEntry


class EventScheduleBuilder:

    def __init__(self):
        self._month = None
        self._year = None
        self._events = []

    def month(self, month: int):
        self._month = month
        return self

    def year(self, year: int):
        self._year = year
        return self

    def events(self, events: List[EventEntry]):
        self._events = events
        return self

    def add_event(self, event: EventEntry):
        self._events.append(event)
        return self

    def build(self):
        return EventSchedule(
            month=self._month,
            year=self._year,
            events=self._events,
        )
