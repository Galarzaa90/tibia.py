from tests.tests_tibiapy import TestCommons
from tibiapy.urls import get_highscores_url


class TestUrls(TestCommons):

    def test_get_highscores_url_empty_params(self):
        url = get_highscores_url()

        self.assertEqual("https://www.tibia.com/community/?subtopic=highscores&currentpage=1", url)
