from tibiapy.models.event import EventSchedule


class EventScheduleBuilder:

    def __init__(self, **kwargs):
        self._month = kwargs.get("month")
        self._year = kwargs.get("year")
        self._events = kwargs.get("events") or []

    def month(self, month):
        self._month = month
        return self

    def year(self, year):
        self._year = year
        return self

    def events(self, events):
        self._events = events
        return self

    def add_event(self, event):
        self._events.append(event)
        return self

    def build(self):
        return EventSchedule(
            month=self._month,
            year=self._year,
            events=self._events,
        )