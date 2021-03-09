import re

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

HP_PATTERN = re.compile(r"have (\d+) hitpoints")
EXP_PATTERN = re.compile(r"yield (\d+) experience")
IMMUNE_PATTERN = re.compile(r"immune to ([^.]+)")
WEAK_PATTERN = re.compile(r"weak against ([^.]+)")
STRONG_PATTERN = re.compile(r"strong against ([^.]+)")
LOOT_PATTERN = re.compile(r"They carry (.*) with them.")
MANA_COST = re.compile(r"takes (\d+) mana")


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
    def get_url(cls):
        return get_tibia_url("library", "creature")

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
    _valid_elements = ["ice", "fire", "earth", "poison", "death", "holy", "physical", "energy"]
    __slots__ = (
        "name",
        "race",
        "description",
        "hitpoints",
        "experience",
        "immune_to",
        "weak_against",
        "strong_against",
        "loot",
        "mana_cost",
        "summonable",
        "convinceable",
    )

    def __init__(self, name, race, immnute_to=None, weak_against=None, strong_against=None, loot=None, mana_cost=None,
                 summonable=False, convinceable=False):
        self.name = name
        self.race = race
        self.immune_to = immnute_to or []
        self.weak_against = weak_against or []
        self.strong_against = strong_against or []
        self.loot = loot
        self.mana_cost = mana_cost
        self.summonable = summonable
        self.convinceable = convinceable

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
        m = HP_PATTERN.search(hp_text)
        if m:
            creature.hitpoints = int(m.group(1))
        m = EXP_PATTERN.search(exp_text)
        if m:
            creature.experience = int(m.group(1))
        m = IMMUNE_PATTERN.search(hp_text)
        if m:
            for element in cls._valid_elements:
                if element in m.group(1):
                    creature.immune_to.append(element)
        if "cannot be paralysed" in hp_text:
            creature.immune_to.append("paralyze")
        m = WEAK_PATTERN.search(hp_text)
        if m:
            for element in cls._valid_elements:
                if element in m.group(1):
                    creature.weak_against.append(element)
        m = STRONG_PATTERN.search(hp_text)
        if m:
            for element in cls._valid_elements:
                if element in m.group(1):
                    creature.strong_against.append(element)
        if "sense invisible" in hp_text:
            creature.immune_to.append("invisible")
        m = LOOT_PATTERN.search(exp_text)
        if m:
            creature.loot = m.group(1)
        m = MANA_COST.search(hp_text)
        if m:
            creature.mana_cost = int(m.group(1))
            if "summon or convince" in hp_text:
                creature.convinceable = True
                creature.summonable = True
            if "cannot be summoned" in hp_text:
                creature.convinceable = True
            if "cannot be convinced" in hp_text:
                creature.summonable = True
        return creature