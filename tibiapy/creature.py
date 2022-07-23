"""Models related to the creatures section in the library."""
import os
import re
import urllib.parse
from typing import List, Optional

import bs4

from tibiapy import abc
from tibiapy.errors import InvalidContent

__all__ = (
    "BoostedCreatures",
    "BoostableBosses",
    "BossEntry",
    "CreatureEntry",
    "CreaturesSection",
    "Creature",
)

from tibiapy.utils import parse_tibiacom_content, get_tibia_url

BOOSTED_ALT = re.compile("Today's boosted \w+: ")


HP_PATTERN = re.compile(r"have (\d+) hitpoints")
EXP_PATTERN = re.compile(r"yield (\d+) experience")
IMMUNE_PATTERN = re.compile(r"immune to ([^.]+)")
WEAK_PATTERN = re.compile(r"weak against ([^.]+)")
STRONG_PATTERN = re.compile(r"strong against ([^.]+)")
LOOT_PATTERN = re.compile(r"They carry (.*) with them.")
MANA_COST = re.compile(r"takes (\d+) mana")


class BoostedCreatures(abc.Serializable):
    """Contains both boosted creature and boosted boss.

    Attributes
    ----------
    creature: :class:`CreatureEntry`
        The boosted creature of the day.
    boss: :class:`BossEntry`
        The boosted boss of the day.
    """

    __slots__ = (
        "creature",
        "boss",
    )

    def __init__(self, creature, boss):
        self.creature: CreatureEntry = creature
        self.boss: BossEntry = boss

    @classmethod
    def _parse_boosted_platform(cls, parsed_content: bs4.BeautifulSoup, tag_id: str):
        img = parsed_content.find("img", attrs={"id": tag_id})
        name = BOOSTED_ALT.sub("", img["title"]).strip()
        image_url = img["src"]
        identifier = image_url.split("/")[-1].replace(".gif", "")
        return name, identifier

    @classmethod
    def from_header(cls, content: str):
        """Parses both boosted creature and boss from the content of any section in Tibia.com

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the page.

        Returns
        -------
        :class:`BoostedCreatures`
            The boosted creature an boss.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a Tibia.com page.
        """
        try:
            parsed_content = bs4.BeautifulSoup(content.replace('ISO-8859-1', 'utf-8'), "lxml",
                                               parse_only=bs4.SoupStrainer("div", attrs={"id": "RightArtwork"}))
            creature_name, creature_identifier = cls._parse_boosted_platform(parsed_content, "Monster")
            boss_name, boss_identifier = cls._parse_boosted_platform(parsed_content, "Boss")
            return cls(CreatureEntry(creature_name, creature_identifier), BossEntry(boss_name, boss_identifier))
        except (TypeError, NameError, KeyError) as e:
            raise InvalidContent("content is not from Tibia.com", e)


class BoostableBosses(abc.Serializable):
    """Represents the boostable bosses section in the Tibia.com library

    Attributes
    ----------
    boosted_boss: :class:`BossEntry`
        The current boosted boss.
    bosses: list of :class:`BossEntry`
        The list of boostable bosses.
    """

    __slots__ = (
        "boosted_boss",
        "bosses",
    )

    def __init__(self, boosted_boss, bosses):
        self.boosted_boss: BossEntry = boosted_boss
        self.bosses: List[BossEntry] = bosses

    @classmethod
    def get_url(cls):
        """Get the URL to the Tibia.com boostable bosses.

        Returns
        -------
        :class:`str`:
            The URL to the Tibia.com library section.
        """
        return get_tibia_url("library", "boostablebosses")

    @classmethod
    def from_content(cls, content):
        """Create an instance of the class from the html content of the boostable bosses library's page.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the page.

        Returns
        -------
        :class:`BoostableBosses`
            The Boostable Bosses section.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a creature library's page.
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            boosted_creature_table = parsed_content.find("div", {"class": "TableContainer"})
            boosted_creature_text = boosted_creature_table.find("div", {"class": "Text"})
            if not boosted_creature_text or "Boosted" not in boosted_creature_text.text:
                raise InvalidContent("content is not from the boostable bosses section.")
            boosted_boss_tag = boosted_creature_table.find("b")
            boosted_boss_image = boosted_creature_table.find("img")
            image_url = urllib.parse.urlparse(boosted_boss_image["src"])
            boosted_boss = BossEntry(boosted_boss_tag.text, os.path.basename(image_url.path).replace(".gif", ""))

            list_table = parsed_content.find("div", style=lambda v: v and 'display: table' in v)
            entries_container = list_table.find_all("div", style=lambda v: v and 'float: left' in v)
            entries = []
            for entry_container in entries_container:
                name = entry_container.text.strip()
                image = entry_container.find("img")
                image_url = urllib.parse.urlparse(image["src"])
                identifier = os.path.basename(image_url.path).replace(".gif", "")
                entries.append(BossEntry(name, identifier))
            return cls(boosted_boss, entries)
        except (AttributeError, ValueError) as e:
            raise InvalidContent("content is not the boosted boss's library", e)


    @classmethod
    def boosted_boss_from_header(cls, content):
        """Get the boosted boss from any Tibia.com page.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of a Tibia.com page.

        Returns
        -------
        :class:`BossEntry`
            The boosted boss of the day.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a Tibia.com's page.
        """
        return BoostedCreatures.from_header(content).boss


class BossEntry(abc.Serializable):
    """Represents a boss in the boostable bosses section in the Tibia.com library.

    Attributes
    ----------
    name: :class:`str`
        The name of the boss..
    identifier: :class:`str`
        The internal name of the boss. Used for images.
    """

    __slots__ = (
        "name",
        "identifier",
    )

    _serializable_properties = (
        "image_url",
    )

    def __init__(self, name, identifier=None):
        self.name: str = name
        self.identifier: str = identifier

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} identifier={self.identifier!r}>"

    @property
    def image_url(self):
        """:class:`str`: The URL to this boss's image."""
        return f"https://static.tibia.com/images/library/{self.identifier}.gif"


class CreaturesSection(abc.Serializable):
    """Represents the creature's section in the Tibia.com library.

    Attributes
    ----------
    boosted_creature: :class:`CreatureEntry`
        The current boosted creature.
    creatures: list of :class:`CreatureEntry`
        The list of creatures in the library.
    """

    __slots__ = (
        "boosted_creature",
        "creatures",
    )

    def __init__(self, boosted_creature, creatures):
        self.boosted_creature: CreatureEntry = boosted_creature
        self.creatures: List[CreatureEntry] = creatures or []

    @classmethod
    def get_url(cls):
        """Get the URL to the Tibia.com library section.

        Returns
        -------
        :class:`str`:
            The URL to the Tibia.com library section.
        """
        return get_tibia_url("library", "creature")

    @classmethod
    def boosted_creature_from_header(cls, content):
        """Get the boosted creature from any Tibia.com page.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of a Tibia.com page.

        Returns
        -------
        :class:`CreatureEntry`
            The boosted creature of the day.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a Tibia.com's page.
        """
        return BoostedCreatures.from_header(content).creature

    @classmethod
    def from_content(cls, content):
        """Create an instance of the class from the html content of the creature library's page.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the page.

        Returns
        -------
        :class:`CreaturesSection`
            The creatures section from Tibia.com.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a creature library's page.
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            boosted_creature_table = parsed_content.find("div", {"class": "TableContainer"})
            boosted_creature_text = boosted_creature_table.find("div", {"class": "Text"})
            if not boosted_creature_text or "Boosted" not in boosted_creature_text.text:
                raise InvalidContent("content is not from the creatures section.")
            boosted_creature_link = boosted_creature_table.find("a")
            url = urllib.parse.urlparse(boosted_creature_link["href"])
            query = urllib.parse.parse_qs(url.query)
            boosted_creature = CreatureEntry(boosted_creature_link.text, query["race"][0])

            list_table = parsed_content.find("div", style=lambda v: v and 'display: table' in v)
            entries_container = list_table.find_all("div", style=lambda v: v and 'float: left' in v)
            entries = []
            for entry_container in entries_container:
                name = entry_container.text.strip()
                link = entry_container.find("a")
                url = urllib.parse.urlparse(link["href"])
                query = urllib.parse.parse_qs(url.query)
                entries.append(CreatureEntry(name, query["race"][0]))
            return cls(boosted_creature, entries)
        except (AttributeError, ValueError) as e:
            raise InvalidContent("content is not the creature's library", e)


class CreatureEntry(abc.Serializable):
    """Represents a creature in the Library section.

    Attributes
    ----------
    name: :class:`str`
        The name of the creature, usually in plural, except for the boosted creature.
    identifier: :class:`str`
        The internal name of the creature's race. Used for links and images.
    """

    __slots__ = (
        "name",
        "identifier",
    )

    _serializable_properties = (
        "image_url",
    )

    def __init__(self, name, identifier=None):
        self.name: str = name
        self.identifier: str = identifier

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} identifier={self.identifier!r}>"

    @property
    def url(self):
        """:class:`str`: The URL to this creature's details."""
        return self.get_url(self.identifier)

    @property
    def image_url(self):
        """:class:`str`: The URL to this creature's image."""
        return f"https://static.tibia.com/images/library/{self.identifier}.gif"

    @classmethod
    def get_url(cls, identifier):
        """Get the URL to the creature's detail page on Tibia.com.

        Parameters
        ----------
        identifier: :class:`str`
            The race's internal name.

        Returns
        -------
        :class:`str`
            The URL to the detail page.
        """
        return get_tibia_url("library", "creatures", race=identifier)


class Creature(CreatureEntry):
    """Represents a creature's details on the Tibia.com library.

    Attributes
    ----------
    name: :class:`str`
        The name of the creature, in plural form.
    identifier: :class:`str`
        The race's internal name. Used for links and images.
    description: :class:`str`
        A description of the creature.
    hitpoints: :class:`int`
        The number of hitpoints the creature has.
    experience: :class:`int`
        The number of experience points given for killing this creature.
    immune_to: list of :class:`str`
        The elements this creature is immune to.
    weak_against: list of :class:`str`
        The elements this creature is weak against.
    strong_against: list of :class:`str`
        The elements this creature is strong against.
    loot: :class:`str`
        Some of the items this creature drops.
    mana_cost: :class:`int`, optional
        The mana neccessary to summon or convince this creature.
    summonable: :class:`bool`
        Whether this creature can be summoned or not.
    convinceable: :class:`bool`
        Whether this creature can be convinced or not.
    """

    _valid_elements = ["ice", "fire", "earth", "poison", "death", "holy", "physical", "energy"]

    __slots__ = (
        "name",
        "identifier",
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

    def __init__(self, name, identifier, **kwargs):
        super().__init__(name, identifier)
        self.immune_to: List[str] = kwargs.get("immune_to", [])
        self.weak_against: List[str] = kwargs.get("weak_against", [])
        self.strong_against: List[str] = kwargs.get("strong_against", [])
        self.loot: str = kwargs.get("loot")
        self.mana_cost: Optional[int] = kwargs.get("mana_cost")
        self.summonable: bool = kwargs.get("summonable", False)
        self.convinceable: bool = kwargs.get("convinceable", False)

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} identifier={self.identifier!r}>"

    @classmethod
    def from_content(cls, content):
        """Create an instance of the class from the html content of the creature library's page.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the page.

        Returns
        -------
        :class:`Creature`
            The character contained in the page.
        """
        try:
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
            creature._parse_hp_text(hp_text)

            exp_text = paragraphs[-1]
            creature._parse_exp_text(exp_text)
            return creature
        except ValueError:
            return None

    def _parse_exp_text(self, exp_text):
        """Parse the experience text, containing dropped loot and adds it to the creature.

        Parameters
        ----------
        exp_text: :class:`str`
            The text containing experience.
        """
        m = EXP_PATTERN.search(exp_text)
        if m:
            self.experience = int(m.group(1))
        m = LOOT_PATTERN.search(exp_text)
        if m:
            self.loot = m.group(1)

    def _parse_hp_text(self, hp_text):
        """Parse the text containing the creatures hitpoints, containing weaknesses, immunities and more and adds it.

        Parameters
        ----------
        hp_text: :class:`str`
            The text containing hitpoints.
        """
        m = HP_PATTERN.search(hp_text)
        if m:
            self.hitpoints = int(m.group(1))
        m = IMMUNE_PATTERN.search(hp_text)
        if m:
            self._parse_elements(self.immune_to, m.group(1))
        if "cannot be paralysed" in hp_text:
            self.immune_to.append("paralyze")
        m = WEAK_PATTERN.search(hp_text)
        if m:
            self._parse_elements(self.weak_against, m.group(1))
        m = STRONG_PATTERN.search(hp_text)
        if m:
            self._parse_elements(self.strong_against, m.group(1))
        m = MANA_COST.search(hp_text)
        if m:
            self.mana_cost = int(m.group(1))
            if "summon or convince" in hp_text:
                self.convinceable = True
                self.summonable = True
            if "cannot be summoned" in hp_text:
                self.convinceable = True
            if "cannot be convinced" in hp_text:
                self.summonable = True
        if "sense invisible" in hp_text:
            self.immune_to.append("invisible")

    @classmethod
    def _parse_elements(cls, collection, text):
        """Parse the elements found in a string, adding them to the collection.

        Parameters
        ----------
        collection: :class:`list`
            The collection where found elements will be added to.
        text: :class:`str`
            The text containing the elements.
        """
        for element in cls._valid_elements:
            if element in text:
                collection.append(element)
