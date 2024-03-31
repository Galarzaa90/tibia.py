"""Models related to the creatures section in the library."""
import os
import re
import urllib.parse
from typing import List, Optional, Tuple

import bs4

from tibiapy.builders import CreatureBuilder
from tibiapy.errors import InvalidContentError
from tibiapy.models import CreatureEntry, CreaturesSection, BoostedCreatures, BossEntry, BoostableBosses, Creature
from tibiapy.utils import parse_tibiacom_content, convert_line_breaks

__all__ = (
    "BoostableBossesParser",
    "BoostedCreaturesParser",
    "CreatureParser",
    "CreaturesSectionParser",
)

BOOSTED_ALT = re.compile(r"Today's boosted \w+: ")

HP_PATTERN = re.compile(r"have (\d+) hitpoints")
EXP_PATTERN = re.compile(r"yield (\d+) experience")
IMMUNE_PATTERN = re.compile(r"immune to ([^.]+)")
WEAK_PATTERN = re.compile(r"weak against ([^.]+)")
STRONG_PATTERN = re.compile(r"strong against ([^.]+)")
LOOT_PATTERN = re.compile(r"They carry (.*) with them.")
MANA_COST = re.compile(r"takes (\d+) mana")


class BoostedCreaturesParser:
    """Parser for boosted creatures and bosses."""

    @classmethod
    def _parse_boosted_platform(cls, parsed_content: bs4.BeautifulSoup, tag_id: str) -> Tuple[str, str]:
        img = parsed_content.select_one(f"#{tag_id}")
        name = BOOSTED_ALT.sub("", img["title"]).strip()
        image_url = img["src"]
        identifier = image_url.split("/")[-1].replace(".gif", "")
        return name, identifier

    @classmethod
    def from_header(cls, content: str) -> BoostedCreatures:
        """Parse both boosted creature and boss from the content of any section in Tibia.com.

        Parameters
        ----------
        content:
            The HTML content of the page.

        Returns
        -------
            The boosted creature and boss.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a Tibia.com page.
        """
        try:
            parsed_content = bs4.BeautifulSoup(content.replace("ISO-8859-1", "utf-8"), "lxml",
                                               parse_only=bs4.SoupStrainer("div", attrs={"id": "RightArtwork"}))
            creature_name, creature_identifier = cls._parse_boosted_platform(parsed_content, "Monster")
            boss_name, boss_identifier = cls._parse_boosted_platform(parsed_content, "Boss")
            return BoostedCreatures(
                creature=CreatureEntry(name=creature_name, identifier=creature_identifier),
                boss=BossEntry(name=boss_name, identifier=boss_identifier),
            )
        except (TypeError, NameError, KeyError) as e:
            raise InvalidContentError("content is not from Tibia.com", e) from e


class BoostableBossesParser:
    """Parser for the boostable bosses section of Tibia.com."""

    @classmethod
    def from_content(cls, content: str) -> BoostableBosses:
        """Create an instance of the class from the html content of the boostable bosses library's page.

        Parameters
        ----------
        content:
            The HTML content of the page.

        Returns
        -------
            The Boostable Bosses section.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a creature library's page.
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            boosted_creature_table = parsed_content.select_one("div.TableContainer")
            boosted_creature_text = boosted_creature_table.select_one("div.Text")
            if not boosted_creature_text or "Boosted" not in boosted_creature_text.text:
                raise InvalidContentError("content is not from the boostable bosses section.")

            boosted_boss_tag = boosted_creature_table.select_one("b")
            boosted_boss_image = boosted_creature_table.select_one("img")
            image_url = urllib.parse.urlparse(boosted_boss_image["src"])
            boosted_boss = BossEntry(name=boosted_boss_tag.text,
                                     identifier=os.path.basename(image_url.path).replace(".gif", ""))

            list_table = parsed_content.find("div", style=lambda v: v and "display: table" in v)
            entries_container = list_table.find_all("div", style=lambda v: v and "float: left" in v)
            entries = []
            for entry_container in entries_container:
                name = entry_container.text.strip()
                image = entry_container.select_one("img")
                image_url = urllib.parse.urlparse(image["src"])
                identifier = os.path.basename(image_url.path).replace(".gif", "")
                entries.append(BossEntry(name=name, identifier=identifier))

            return BoostableBosses(boosted_boss=boosted_boss, bosses=entries)
        except (AttributeError, ValueError) as e:
            raise InvalidContentError("content is not the boosted boss's library", e) from e

    @classmethod
    def boosted_boss_from_header(cls, content: str) -> BossEntry:
        """Get the boosted boss from any Tibia.com page.

        Parameters
        ----------
        content:
            The HTML content of a Tibia.com page.

        Returns
        -------
            The boosted boss of the day.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a Tibia.com's page.
        """
        return BoostedCreaturesParser.from_header(content).boss


class CreaturesSectionParser:
    """Parser for the creatures section in the library from Tibia.com."""

    @classmethod
    def boosted_creature_from_header(cls, content: str) -> CreatureEntry:
        """Get the boosted creature from any Tibia.com page.

        Parameters
        ----------
        content:
            The HTML content of a Tibia.com page.

        Returns
        -------
            The boosted creature of the day.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a Tibia.com's page.
        """
        return BoostedCreaturesParser.from_header(content).creature

    @classmethod
    def from_content(cls, content: str) -> CreaturesSection:
        """Create an instance of the class from the html content of the creature library's page.

        Parameters
        ----------
        content:
            The HTML content of the page.

        Returns
        -------
            The creatures section from Tibia.com.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a creature library's page.
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            boosted_creature_table = parsed_content.select_one("div.TableContainer")
            boosted_creature_text = boosted_creature_table.select_one("div.Text")
            if not boosted_creature_text or "Boosted" not in boosted_creature_text.text:
                raise InvalidContentError("content is not from the creatures section.")

            boosted_creature_link = boosted_creature_table.select_one("a")
            url = urllib.parse.urlparse(boosted_creature_link["href"])
            query = urllib.parse.parse_qs(url.query)
            boosted_creature = CreatureEntry(name=boosted_creature_link.text, identifier=query["race"][0])

            list_table = parsed_content.find("div", style=lambda v: v and "display: table" in v)
            entries_container = list_table.find_all("div", style=lambda v: v and "float: left" in v)
            entries = []
            for entry_container in entries_container:
                name = entry_container.text.strip()
                link = entry_container.select_one("a")
                url = urllib.parse.urlparse(link["href"])
                query = urllib.parse.parse_qs(url.query)
                entries.append(CreatureEntry(name=name, identifier=query["race"][0]))

            return CreaturesSection(boosted_creature=boosted_creature, creatures=entries)
        except (AttributeError, ValueError) as e:
            raise InvalidContentError("content is not the creature's library", e) from e


class CreatureParser:
    """Parser for creatures."""

    _valid_elements = ("ice", "fire", "earth", "poison", "death", "holy", "physical", "energy")

    @classmethod
    def from_content(cls, content: str) -> Optional[Creature]:
        """Create an instance of the class from the html content of the creature library's page.

        Parameters
        ----------
        content:
            The HTML content of the page.

        Returns
        -------
            The creature contained in the page.
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            _, content_container = (
                parsed_content.find_all("div", style=lambda v: v and "position: relative" in v)
            )
            title_container, description_container = content_container.select("div")
            title = title_container.select_one("h2")
            name = title.text.strip()

            img = title_container.select_one("img")
            img_url = img["src"]
            race = img_url.split("/")[-1].replace(".gif", "")
            builder = CreatureBuilder().name(name).identifier(race)

            convert_line_breaks(description_container)
            paragraph_tags = description_container.select("p")
            paragraphs = [p.text for p in paragraph_tags]
            builder.description("\n".join(paragraphs[:-2]).strip())
            hp_text = paragraphs[-2]
            cls._parse_hp_text(builder, hp_text)

            exp_text = paragraphs[-1]
            cls._parse_exp_text(builder, exp_text)
            return builder.build()
        except ValueError:
            return None

    @classmethod
    def _parse_exp_text(cls, builder: CreatureBuilder, exp_text: str) -> None:
        """Parse the experience text, containing dropped loot and adds it to the creature.

        Parameters
        ----------
        builder: :class:`CreatureBuilder`
            The builder where data will be stored to.
        exp_text: :class:`str`
            The text containing experience.
        """
        if m := EXP_PATTERN.search(exp_text):
            builder.experience(int(m.group(1)))

        if m := LOOT_PATTERN.search(exp_text):
            builder.loot(m.group(1))

    @classmethod
    def _parse_hp_text(cls, builder: CreatureBuilder, hp_text: str) -> None:
        """Parse the text containing the creature's hitpoints, containing weaknesses, immunities and more and adds it.

        Parameters
        ----------
        builder: :class:`CreatureBuilder`
            The builder where data will be stored to.
        hp_text: :class:`str`
            The text containing hitpoints.
        """
        m = HP_PATTERN.search(hp_text)
        if m:
            builder.hitpoints(int(m.group(1)))

        m = IMMUNE_PATTERN.search(hp_text)
        immune = []
        if m:
            immune.extend(cls._parse_elements(m.group(1)))

        if "cannot be paralysed" in hp_text:
            immune.append("paralyze")

        if "sense invisible" in hp_text:
            immune.append("invisible")

        builder.immune_to(immune)
        if m := WEAK_PATTERN.search(hp_text):
            builder.weak_against(cls._parse_elements(m.group(1)))

        if m := STRONG_PATTERN.search(hp_text):
            builder.strong_against(cls._parse_elements(m.group(1)))

        if m := MANA_COST.search(hp_text):
            builder.mana_cost(int(m.group(1)))
            if "summon or convince" in hp_text:
                builder.convinceable(True)
                builder.summonable(True)

            if "cannot be summoned" in hp_text:
                builder.convinceable(True)

            if "cannot be convinced" in hp_text:
                builder.summonable(True)

    @classmethod
    def _parse_elements(cls, text: str) -> List[str]:
        """Parse the elements found in a string, adding them to the collection.

        Parameters
        ----------
        text: :class:`str`
            The text containing the elements.
        """
        return [element for element in cls._valid_elements if element in text]
