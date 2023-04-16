import unittest
import datetime

from tests.tests_tibiapy import TestCommons
from tibiapy.models.event import EventSchedule
from tibiapy.parsers.event import EventScheduleParser

FILE_EVENT_CALENDAR = "events/event_schedule.txt"


class TestEvents(TestCommons, unittest.TestCase):
    def test_event_schedule_parser_from_content(self):
        """Testing parsing the event schedule"""
        content = self.load_resource(FILE_EVENT_CALENDAR)
        calendar = EventScheduleParser.from_content(content)

        self.assertIsInstance(calendar, EventSchedule)
        self.assertEqual(9, calendar.month)
        self.assertEqual(2020, calendar.year)
        self.assertEqual(6, len(calendar.events))
        self.assertEqual(calendar.url, EventSchedule.get_url(calendar.month, calendar.year))
        events_on_day = calendar.get_events_on(datetime.date(2020, 9, 15))
        self.assertEqual(2, len(events_on_day))
        self.assertEqual(4, events_on_day[0].duration)
