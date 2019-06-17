import bs4

from tibiapy.utils import parse_tibiacom_content

__all__ = (
    "BoostedCreature",
)

BOOSTED_ALT = "Today's boosted creature: "


class BoostedCreature:
    def __init__(self, name, image_url):
        self.name = name
        self.image_url = image_url

    @classmethod
    def from_content(cls, content):
        parsed_content = bs4.BeautifulSoup(content.replace('ISO-8859-1', 'utf-8'), "lxml", parse_only=bs4.SoupStrainer("div", attrs={"id": "RightArtwork"}))
        img = parsed_content.find("img", attrs={"id": "Monster"})
        name = img["title"].replace(BOOSTED_ALT, "").strip()
        image_url = img["src"]
        return cls(name, image_url)
