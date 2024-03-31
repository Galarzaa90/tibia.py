from tests.tests_tibiapy import TestCommons
from tibiapy.models.fansite import FansitesSection
from tibiapy.parsers.fansite import FansitesSectionParser

FILE_FANSITES_SECTION = "fansites/fansites.txt"


class TestFansitesSection(TestCommons):
    def test_fansites_parser_from_content(self):
        """Testing parsing the fansites section."""
        content = self.load_resource(FILE_FANSITES_SECTION)
        fansites_section = FansitesSectionParser.from_content(content)

        self.assertIsInstance(fansites_section, FansitesSection)
        self.assertIsNotEmpty(fansites_section.promoted_fansites)
        self.assertIsNotEmpty(fansites_section.supported_fansites)
