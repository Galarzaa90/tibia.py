import datetime

import tibiapy.utils
from tests.tests_tibiapy import TestTibiaPy

PATH_CHARACTER_RESOURCE = "character_regular.txt"


class TestUtils(TestTibiaPy):
    def testTibiaDateTimeCEST(self):
        time = tibiapy.utils.parse_tibia_datetime("Jul 10 2018, 07:13:32 CEST")
        self.assertIsInstance(time, datetime.datetime)
        self.assertEqual(time.month, 7)
        self.assertEqual(time.day, 10)
        self.assertEqual(time.year, 2018)
        self.assertEqual(time.hour, 5)
        self.assertEqual(time.minute, 13)
        self.assertEqual(time.second, 32)

    def testTibiaDateTimeEST(self):
        time = tibiapy.utils.parse_tibia_datetime("Jan 10 2018, 07:13:32 CET")
        self.assertIsInstance(time, datetime.datetime)
        self.assertEqual(time.month, 1)
        self.assertEqual(time.day, 10)
        self.assertEqual(time.year, 2018)
        self.assertEqual(time.hour, 6)
        self.assertEqual(time.minute, 13)
        self.assertEqual(time.second, 32)

    def testTibiaDateInvalidTimezone(self):
        time = tibiapy.utils.parse_tibia_datetime("Aug 10 2015, 23:13:32 PST")
        self.assertIsNone(time)

    def testTibiaDateTimeInvalid(self):
        time = tibiapy.utils.parse_tibia_datetime("13:37:00 10 Feb 2003")
        self.assertIsNone(time)

    def testTibiaDate(self):
        date = tibiapy.utils.parse_tibia_date("Jun 20 2018")
        self.assertIsInstance(date, datetime.date)
        self.assertEqual(date.month, 6)
        self.assertEqual(date.day, 20)
        self.assertEqual(date.year, 2018)

    def testTibiaDateInvalid(self):
        date = tibiapy.utils.parse_tibia_date("8 Nov 2018")
        self.assertIsNone(date)
