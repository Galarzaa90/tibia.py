import datetime
import unittest

import tibiapy
from tests.tests_tibiapy import TestCommons
from tibiapy import enums, utils
from tibiapy.utils import get_tibia_url, parse_integer, parse_tibia_money

TIBIA_DATETIME_CEST = "Jul 10 2018, 07:13:32 CEST"
TIBIA_DATETIME_CET = "Jan 10 2018, 07:13:32 CET"
TIBIA_DATETIME_PST = "Aug 10 2015, 23:13:32 PST"
TIBIA_DATETIME_INVALID = "13:37:00 10 Feb 2003"

TIBIA_DATE = "Jun 20 2018"
TIBIA_FULL_DATE = "July 23, 2015"
TIBIA_DATE_INVALID = "8 Nov 2018"


class TestUtils(TestCommons, unittest.TestCase):
    def test_serializable_get_item(self):
        """Testing the muliple ways to use __get__ for Serializable"""
        # Class inherits from Serializable
        world = tibiapy.World("Calmera")

        # Serializable allows accessing attributes like a dictionary
        self.assertEqual(world.name, world["name"])
        # And setting values too
        world["location"] = tibiapy.enums.WorldLocation.NORTH_AMERICA
        self.assertEqual(world.location, tibiapy.enums.WorldLocation.NORTH_AMERICA)

        # Accessing via __get__ returns KeyError instead of AttributeError to follow dictionary behaviour
        with self.assertRaises(KeyError):
            _level = world["level"]  # NOSONAR

        # Accessing an undefined attribute that is defined in __slots__ returns `None` instead of raising an exception.
        del world.location
        self.assertIsNone(world["location"])

        # New attributes can't be created by assignation
        with self.assertRaises(KeyError):
            world["custom"] = "custom value"

    def test_parse_tibia_datetime(self):
        time = utils.parse_tibia_datetime(TIBIA_DATETIME_CEST)
        self.assertIsInstance(time, datetime.datetime)
        self.assertEqual(time.month, 7)
        self.assertEqual(time.day, 10)
        self.assertEqual(time.year, 2018)
        self.assertEqual(time.hour, 5)
        self.assertEqual(time.minute, 13)
        self.assertEqual(time.second, 32)

        time = utils.parse_tibia_datetime(TIBIA_DATETIME_CET)
        self.assertIsInstance(time, datetime.datetime)
        self.assertEqual(time.month, 1)
        self.assertEqual(time.day, 10)
        self.assertEqual(time.year, 2018)
        self.assertEqual(time.hour, 6)
        self.assertEqual(time.minute, 13)
        self.assertEqual(time.second, 32)

    def test_parse_tibia_datetime_invalid_timezone(self):
        time = utils.parse_tibia_datetime(TIBIA_DATETIME_PST)
        self.assertIsNone(time)

    def test_parse_tibia_datetime_invalid_datetime(self):
        time = utils.parse_tibia_datetime(TIBIA_DATETIME_INVALID)
        self.assertIsNone(time)

    def test_parse_tibia_date(self):
        date = utils.parse_tibia_date(TIBIA_DATE)
        self.assertIsInstance(date, datetime.date)
        self.assertEqual(date.month, 6)
        self.assertEqual(date.day, 20)
        self.assertEqual(date.year, 2018)

    def test_parse_tibia_date_full(self):
        date = utils.parse_tibia_full_date(TIBIA_FULL_DATE)
        self.assertIsInstance(date, datetime.date)
        self.assertEqual(date.month, 7)
        self.assertEqual(date.day, 23)
        self.assertEqual(date.year, 2015)

    def test_parse_tibia_date_invalid(self):
        date = utils.parse_tibia_date(TIBIA_DATETIME_INVALID)
        self.assertIsNone(date)

    def test_try_date(self):
        date = utils.try_date(datetime.datetime.now())
        self.assertIsInstance(date, datetime.date)

        date = utils.try_date(datetime.date.today())
        self.assertIsInstance(date, datetime.date)
        self.assertEqual(date, datetime.date.today())

        date = utils.try_date(TIBIA_DATE)
        self.assertIsInstance(date, datetime.date)

        date = utils.try_date(TIBIA_FULL_DATE)
        self.assertIsInstance(date, datetime.date)

    def test_try_date_time(self):
        date_time = utils.try_datetime(datetime.datetime.now())
        self.assertIsInstance(date_time, datetime.datetime)

        date_time = utils.try_datetime(TIBIA_DATETIME_CEST)
        self.assertIsInstance(date_time, datetime.datetime)

    def test_parse_number_words(self):
        self.assertEqual(utils.parse_number_words("one"), 1)
        self.assertEqual(utils.parse_number_words("no"), 0)
        self.assertEqual(utils.parse_number_words("..."), 0)
        self.assertEqual(utils.parse_number_words("twenty-one"), 21)
        self.assertEqual(utils.parse_number_words("one hundred two"), 102)
        self.assertEqual(utils.parse_number_words("two thousand forty five"), 2045)

    def test_try_enum(self):
        self.assertEqual(utils.try_enum(enums.Sex, "male"), enums.Sex.MALE)
        self.assertEqual(utils.try_enum(enums.TransferType, "", enums.TransferType.REGULAR), enums.TransferType.REGULAR)
        self.assertEqual(utils.try_enum(enums.WorldLocation, enums.WorldLocation.EUROPE), enums.WorldLocation.EUROPE)
        self.assertEqual(utils.try_enum(enums.VocationFilter, 4), enums.VocationFilter.SORCERERS)
        self.assertEqual(utils.try_enum(enums.Category, "FISHING"), enums.Category.FISHING)

    def test_enum_str(self):
        self.assertEqual(str(enums.Sex.MALE), enums.Sex.MALE.value)
        self.assertEqual(enums.VocationFilter.from_name("royal paladin"), enums.VocationFilter.PALADINS)
        self.assertEqual(enums.VocationFilter.from_name("unknown"), enums.VocationFilter.ALL)
        self.assertIsNone(enums.VocationFilter.from_name("unknown", False))

    def test_parse_tibia_money(self):
        self.assertEqual(1000, parse_tibia_money("1k"))
        self.assertEqual(5000000, parse_tibia_money("5kk"))
        self.assertEqual(2500, parse_tibia_money("2.5k"))
        self.assertEqual(50, parse_tibia_money("50"))
        with self.assertRaises(ValueError):
            parse_tibia_money("abc")

    def test_parse_integer(self):
        self.assertEqual(1450, parse_integer("1.450"))
        self.assertEqual(1110, parse_integer("1,110"))
        self.assertEqual(15, parse_integer("15"))
        self.assertEqual(0, parse_integer("abc"))
        self.assertEqual(-1, parse_integer("abc", -1))

    def test_get_tibia_url(self):
        self.assertEqual("https://www.tibia.com/community/?subtopic=character&name=Galarzaa+Fidera",
                         get_tibia_url("community", "character", name="Galarzaa Fidera"))
        self.assertEqual("https://www.tibia.com/community/?subtopic=character&name=Fn%F6",
                         get_tibia_url("community", "character", name="Fnö"))

    def test_parse_pagination_collapsed_first_page(self):
        """Parsing with current page 1 out of 915"""
        content = """<td class="PageNavigation"><small><div style="float: left;"><b>» <span class="PageLink 
        FirstOrLastElement"><span class="CurrentPageLink">First Page</span></span> <span class="PageLink "><a 
        href="https://www.tibia.com/charactertrade/?subtopic=pastcharactertrades&amp;currentpage=2">2</a></span> 
        <span class="PageLink "><a href="https://www.tibia.com/charactertrade/?subtopic=pastcharactertrades&amp
        ;currentpage=3">3</a></span> <span class="PageLink "><a 
        href="https://www.tibia.com/charactertrade/?subtopic=pastcharactertrades&amp;currentpage=4">4</a></span> 
        <span class="PageLink "><a href="https://www.tibia.com/charactertrade/?subtopic=pastcharactertrades&amp
        ;currentpage=5">5</a></span> <span class="PageLink "><a 
        href="https://www.tibia.com/charactertrade/?subtopic=pastcharactertrades&amp;currentpage=6">6</a></span> 
        <span class="PageLink "><a href="https://www.tibia.com/charactertrade/?subtopic=pastcharactertrades&amp
        ;currentpage=7">7</a></span> ... <span class="PageLink FirstOrLastElement"><a 
        href="https://www.tibia.com/charactertrade/?subtopic=pastcharactertrades&amp;currentpage=915">Last 
        Page</a></span></b></div><div style="float: right;"><b>» Results: 22874</b></div></small></td>"""
        parsed_content = utils.parse_tibiacom_content(content, builder="html5lib")
        page, total_pages, results_count = utils.parse_pagination(parsed_content)
        self.assertEqual(1, page)
        self.assertEqual(915, total_pages)
        self.assertEqual(22874, results_count)

    def test_parse_pagination_collapse_second_page(self):
        """Parsing with current page 2 out of 928"""
        content = """<td class="PageNavigation"><small><div style="float: left;"><b>» <span class="PageLink 
        FirstOrLastElement"><a href="https://www.tibia.com/charactertrade/?subtopic=pastcharactertrades&amp
        ;currentpage=1">First Page</a></span> <span class="PageLink "><span class="CurrentPageLink">2</span></span> 
        <span class="PageLink "><a href="https://www.tibia.com/charactertrade/?subtopic=pastcharactertrades&amp
        ;currentpage=3">3</a></span> <span class="PageLink "><a 
        href="https://www.tibia.com/charactertrade/?subtopic=pastcharactertrades&amp;currentpage=4">4</a></span> 
        <span class="PageLink "><a href="https://www.tibia.com/charactertrade/?subtopic=pastcharactertrades&amp
        ;currentpage=5">5</a></span> <span class="PageLink "><a 
        href="https://www.tibia.com/charactertrade/?subtopic=pastcharactertrades&amp;currentpage=6">6</a></span> 
        <span class="PageLink "><a href="https://www.tibia.com/charactertrade/?subtopic=pastcharactertrades&amp
        ;currentpage=7">7</a></span> <span class="PageLink "><a 
        href="https://www.tibia.com/charactertrade/?subtopic=pastcharactertrades&amp;currentpage=8">8</a></span> ... 
        <span class="PageLink FirstOrLastElement"><a 
        href="https://www.tibia.com/charactertrade/?subtopic=pastcharactertrades&amp;currentpage=928">Last 
        Page</a></span></b></div><div style="float: right;"><b>» Results: 23197</b></div></small></td> """
        parsed_content = utils.parse_tibiacom_content(content, builder="html5lib")
        page, total_pages, results_count = utils.parse_pagination(parsed_content)
        self.assertEqual(2, page)
        self.assertEqual(928, total_pages)
        self.assertEqual(23197, results_count)

    def test_parse_pagination_collapse_last_page(self):
        """Parsing the last page out of 928"""
        content = """<td class="PageNavigation"><small><div style="float: left;"><b>» <span class="PageLink 
        FirstOrLastElement"><a href="https://www.tibia.com/charactertrade/?subtopic=pastcharactertrades&amp
        ;currentpage=1">First Page</a></span> ... <span class="PageLink "><a 
        href="https://www.tibia.com/charactertrade/?subtopic=pastcharactertrades&amp;currentpage=925">925</a></span> 
        <span class="PageLink "><a href="https://www.tibia.com/charactertrade/?subtopic=pastcharactertrades&amp
        ;currentpage=926">926</a></span> <span class="PageLink "><a 
        href="https://www.tibia.com/charactertrade/?subtopic=pastcharactertrades&amp;currentpage=927">927</a></span> 
        <span class="PageLink FirstOrLastElement"><span class="CurrentPageLink">Last Page</span></span></b></div><div 
        style="float: right;"><b>» Results: 23197</b></div></small></td> """
        parsed_content = utils.parse_tibiacom_content(content, builder="html5lib")
        page, total_pages, results_count = utils.parse_pagination(parsed_content)
        self.assertEqual(928, page)
        self.assertEqual(928, total_pages)
        self.assertEqual(23197, results_count)

    def test_parse_pagination_collapsed_middle(self):
        """Parsing page 300 out of 503"""
        content = """<td class="PageNavigation"><small><div style="float: left;"><b>» <span class="PageLink 
        FirstOrLastElement"><a href="https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades&amp
        ;currentpage=1">First Page</a></span> ... <span class="PageLink "><a 
        href="https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades&currentpage=297">297</a></span> 
        <span class="PageLink "><a href="https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades
        &currentpage=298">298</a></span> <span class="PageLink "><a 
        href="https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades&currentpage=299">299</a></span> 
        <span class="PageLink "><span class="CurrentPageLink">300</span></span> <span class="PageLink "><a 
        href="https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades&currentpage=301">301</a></span> 
        <span class="PageLink "><a href="https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades
        &currentpage=302">302</a></span> <span class="PageLink "><a 
        href="https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades&currentpage=303">303</a></span> 
        ... <span class="PageLink FirstOrLastElement"><a 
        href="https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades&currentpage=503">Last 
        Page</a></span></b></div><div style="float: right;"><b>» Results: 12568</b></div></small></td> """
        parsed_content = utils.parse_tibiacom_content(content, builder="html5lib")
        page, total_pages, results_count = utils.parse_pagination(parsed_content)
        self.assertEqual(300, page)
        self.assertEqual(503, total_pages)
        self.assertEqual(12568, results_count)

    def parse_parse_pagination_not_collapsed_first_page(self):
        """Parsing first page with page numbers not collapsed"""
        content = """<small><div style="float: left;"><b>» Pages: <span 
        class="PageLink "><span class="CurrentPageLink">1</span></span> <span class="PageLink "><a 
        class="CipAjaxLink" ajaxcip="true" ajaxcip_datatype="Container" 
        href="https://www.tibia.com/charactertrade/ajax_getcharacterdata.php?auctionid=29122&amp;type=0&amp
        ;currentpage=2">2</a></span> <span class="PageLink "><a class="CipAjaxLink" ajaxcip="true" 
        ajaxcip_datatype="Container" href="https://www.tibia.com/charactertrade/ajax_getcharacterdata.php?auctionid
        =29122&amp;type=0&amp;currentpage=3">3</a></span> <span class="PageLink "><a class="CipAjaxLink" 
        ajaxcip="true" ajaxcip_datatype="Container" 
        href="https://www.tibia.com/charactertrade/ajax_getcharacterdata.php?auctionid=29122&amp;type=0&amp
        ;currentpage=4">4</a></span> <span class="PageLink "><a class="CipAjaxLink" ajaxcip="true" 
        ajaxcip_datatype="Container" href="https://www.tibia.com/charactertrade/ajax_getcharacterdata.php?auctionid
        =29122&amp;type=0&amp;currentpage=5">5</a></span> <span class="PageLink "><a class="CipAjaxLink" 
        ajaxcip="true" ajaxcip_datatype="Container" 
        href="https://www.tibia.com/charactertrade/ajax_getcharacterdata.php?auctionid=29122&amp;type=0&amp
        ;currentpage=6">6</a></span> <span class="PageLink "><a class="CipAjaxLink" ajaxcip="true" 
        ajaxcip_datatype="Container" href="https://www.tibia.com/charactertrade/ajax_getcharacterdata.php?auctionid
        =29122&amp;type=0&amp;currentpage=7">7</a></span> <span class="PageLink "><a class="CipAjaxLink" 
        ajaxcip="true" ajaxcip_datatype="Container" 
        href="https://www.tibia.com/charactertrade/ajax_getcharacterdata.php?auctionid=29122&amp;type=0&amp
        ;currentpage=8">8</a></span></b></div><div style="float: right;"><b>» Results: 567</b></div></small>"""
        parsed_content = utils.parse_tibiacom_content(content, builder="html5lib")
        page, total_pages, results_count = utils.parse_pagination(parsed_content)
        self.assertEqual(1, page)
        self.assertEqual(8, total_pages)
        self.assertEqual(567, results_count)

