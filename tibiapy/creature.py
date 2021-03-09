import bs4
import urllib.parse

from tibiapy import abc
from tibiapy.errors import InvalidContent

__all__ = (
    "BoostedCreature",
    "Creature",
    "CreaturesSection",
    "CreatureDetail",
)

from tibiapy.utils import parse_tibiacom_content, get_tibia_url

BOOSTED_ALT = "Today's boosted creature: "


class BoostedCreature(abc.Serializable):
    """Represents a boosted creature entry.

    This creature changes every server save and applies to all Game Worlds.
    Boosted creatures yield twice the amount of experience points, carry more loot and respawn at a faster rate.

    Attributes
    ----------
    name: :class:`str`
        The name of the boosted creature.
    image_url: :class:`str`
        An URL containing the boosted creature's image.
    """
    __slots__ = (
        "name",
        "image_url",
    )

    def __init__(self, name, image_url):
        self.name: str = name
        self.image_url: str = image_url

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} image_url={self.image_url!r}>"

    @classmethod
    def from_content(cls, content):
        """
        Gets the boosted creature from any Tibia.com page.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of a Tibia.com page.

        Returns
        -------
        :class:`BoostedCreature`
            The boosted creature of the day.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a Tibia.com's page.
        """
        try:
            parsed_content = bs4.BeautifulSoup(content.replace('ISO-8859-1', 'utf-8'), "lxml",
                                               parse_only=bs4.SoupStrainer("div", attrs={"id": "RightArtwork"}))
            img = parsed_content.find("img", attrs={"id": "Monster"})
            name = img["title"].replace(BOOSTED_ALT, "").strip()
            image_url = img["src"]
            return cls(name, image_url)
        except TypeError:
            raise InvalidContent("content is not from Tibia.com")


class Creature(abc.Serializable):
    """Represents a creature in the Library section.

    Attributes
    ----------
    name: :class:`str`
        The name of the creature, in plural.
    race: :class:`str`
        The internal name of the creature's race. Used for links and images."""

    __slots__ = (
        "name",
        "race",
    )

    def __init__(self, name, race=None):
        self.name = name
        self.race = race

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} race={self.race!r}>"

    @property
    def url(self):
        return self.get_url(self.race)

    @property
    def image_url(self):
        return f"https://static.tibia.com/images/library/{self.race}.gif"

    @classmethod
    def get_url(cls, race):
        return get_tibia_url("library", "creatures", race=race)


class CreaturesSection(abc.Serializable):
    """a

    Attributes
    ----------
    boosted_creature: :class:`Creature`
        The current boosted creature.
    creatures: list of :class:`Creature`
        The list of creatures in the library.
    """

    __slots__ = (
        "boosted_creature",
        "creatures",
    )

    def __init__(self, boosted_creature, creatures):
        self.boosted_creature = boosted_creature
        self.creatures = creatures or []

    @classmethod
    def from_content(cls, content):
        parsed_content = parse_tibiacom_content(content)
        boosted_creature_table = parsed_content.find("div", {"class": "TableContainer"})
        boosted_creature_text = boosted_creature_table.find("div", {"class": "Text"})
        if not boosted_creature_text or "Boosted" not in boosted_creature_text.text:
            return None
        boosted_creature_link = boosted_creature_table.find("a")
        url = urllib.parse.urlparse(boosted_creature_link["href"])
        query = urllib.parse.parse_qs(url.query)
        boosted_creature = Creature(boosted_creature_link.text, query["race"][0])

        list_table = parsed_content.find("div", style=lambda v: v and 'display: table' in v)
        entries_container = list_table.find_all("div", style=lambda v: v and 'float: left' in v)
        entries = []
        for entry_container in entries_container:
            name = entry_container.text.strip()
            link = entry_container.find("a")
            url = urllib.parse.urlparse(link["href"])
            query = urllib.parse.parse_qs(url.query)
            entries.append(Creature(name, query["race"][0]))
        return cls(boosted_creature, entries)


class CreatureDetail(abc.Serializable):
    __slots__ = (
        "name",
        "race",
        "description",
        "hitpoints",
        "experience"
    )

    def __init__(self, name, race):
        self.name = name
        self.race = race

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} race={self.race!r}>"

    @classmethod
    def get_url(cls, race):
        return get_tibia_url("library", "creatures", race=race)

    @classmethod
    def from_content(cls, content):
        parsed_content = parse_tibiacom_content(content)
        pagination_container, content_container = \
            parsed_content.find_all("div", style=lambda v: v and 'position: relative' in v)
        title_container, description_container = content_container.find_all("div")
        title = title_container.find("h2")
        name = title.text.strip()

        img = title_container.find("img")
        img_url = img["src"]
        race = img_url.split("/")[-1].replace(".gif", "")
        creature = cls(name, race)

        paragraph_tags = description_container.find_all("p")
        paragraphs = [p.text for p in paragraph_tags]
        creature.description = "\n".join(paragraphs[:-2])
        hp_text = paragraphs[-2]
        exp_text = paragraphs[-1]
        return creature