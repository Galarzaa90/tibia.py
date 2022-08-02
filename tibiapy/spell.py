"""Models related to the spells section in the library."""
import os
import re
import urllib.parse
from typing import Dict, List, Optional

import bs4

from tibiapy import abc, errors
from tibiapy.enums import SpellGroup, SpellSorting, SpellType, VocationSpellFilter
from tibiapy.utils import get_tibia_url, parse_form_data, parse_integer, parse_tibiacom_content, parse_tibiacom_tables, \
    try_enum

__all__ = (
    'SpellsSection',
    'SpellEntry',
    'Spell',
    'Rune',
)

spell_name = re.compile(r"([^(]+)\(([^)]+)\)")
group_pattern = re.compile(r"(?P<group>\w+)(?: \(Secondary Group: (?P<secondary>[^)]+))?")
cooldown_pattern = re.compile(
    r"(?P<cooldown>\d+)s \(Group: (?P<group_cooldown>\d+)s(?: ,Secondary Group: (?P<secondary_group_cooldown>\d+))?")


def to_yes_no(value: Optional[bool]):
    if value is None:
        return None
    return "yes" if value else "no"


class SpellsSection(abc.Serializable):
    """The spells section in Tibia.com.

    .. versionadded:: 5.0.0

    Attributes
    ----------
    vocation: :class:`VocationSpellFilter`
        The selected vocation filter. If :obj:`None`, spells for any vocation will be shown.
    group: :class:`SpellGroup`
        The selected spell group to display. If :obj:`None`, spells for any group will be shown.
    spell_type: :class:`SpellType`
        The selected spell type to display. If :obj:`None`, spells for any type will be shown.
    premium: :class:`bool`
        The premium status to filter in. :obj:`True` to show only premium spells,
        :obj:`False` to show free account spells and :obj:`None` will show any spells.
    sort_by: :class:`SpellSorting`
        The sorting order of the displayed spells.
    entries: :class:`SpellEntry`
        The spells matching the selected filters.
    """

    __slots__ = (
        "vocation",
        "group",
        "spell_type",
        "premium",
        "sort_by",
        "entries",
    )

    def __init__(self, **kwargs):
        self.vocation: VocationSpellFilter = kwargs.get("vocation")
        self.group: SpellGroup = kwargs.get("group")
        self.spell_type: SpellType = kwargs.get("spell_type")
        self.premium: Optional[bool] = kwargs.get("premium")
        self.sort_by: SpellSorting = kwargs.get("sort_by")
        self.entries: List[SpellEntry] = kwargs.get("entries", [])

    def __repr__(self):
        return (f"<{self.__class__.__name__} vocation={self.vocation!r} group={self.group!r} "
                f"spell_type={self.spell_type!r} len(entries)={len(self.entries)}>")

    @property
    def url(self):
        return self.get_url(vocation=self.vocation, group=self.group, spell_type=self.spell_type, premium=self.premium,
                            sort=self.sort_by)

    @classmethod
    def from_content(cls, content):
        """Parse the content of the spells section.

        Parameters
        -----------
        content: :class:`str`
            The HTML content of the page.

        Returns
        ----------
        :class:`SpellsSection`
            The spells contained and the filtering information.

        Raises
        ------
        InvalidContent
            If content is not the HTML of the spells section.
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            table_content_container = parsed_content.find("div", attrs={"class": "InnerTableContainer"})
            spells_table = table_content_container.find("table", class_=lambda t: t != "TableContent")
            spell_rows = spells_table.find_all("tr", {'bgcolor': ["#D4C0A1", "#F1E0C6"]})
            spells_section = cls()
            for row in spell_rows:
                columns = row.find_all("td")
                if len(columns) != 7:
                    continue
                spell_link = columns[0].find("a")
                url = urllib.parse.urlparse(spell_link["href"])
                query = urllib.parse.parse_qs(url.query)
                cols_text = [c.text for c in columns]
                identifier = query["spell"][0]
                match = spell_name.findall(cols_text[0])
                name, words = match[0]
                group = try_enum(SpellGroup, cols_text[1])
                spell_type = try_enum(SpellType, cols_text[2])
                level = int(cols_text[3])
                mana = parse_integer(cols_text[4], None)
                price = parse_integer(cols_text[5], 0)
                premium = "yes" in cols_text[6]
                spell = SpellEntry(name=name.strip(), words=words.strip(), spell_type=spell_type, level=level, group=group,
                                   mana=mana, premium=premium, price=price, identifier=identifier)
                spells_section.entries.append(spell)
            form = parsed_content.find("form")
            data = parse_form_data(form)
            spells_section.vocation = try_enum(VocationSpellFilter, data["vocation"])
            spells_section.group = try_enum(SpellGroup, data["group"])
            spells_section.premium = try_enum(SpellGroup, data["group"])
            spells_section.spell_type = try_enum(SpellType, data["type"])
            spells_section.sort_by = try_enum(SpellSorting, data["sort"])
            spells_section.premium = "yes" in data["premium"] if data["premium"] else None
            return spells_section
        except (AttributeError, TypeError, KeyError) as e:
            raise errors.InvalidContent("content does not belong to the Spells section", e)

    @classmethod
    def get_url(cls, *, vocation=None, group=None, spell_type=None, premium=None, sort=None):
        """Get the URL to the spells section with the desired filtering parameters.

        Parameters
        ----------
        vocation: :class:`VocationSpellFilter`, optional
            The vocation to filter in spells for.
        group: :class:`SpellGroup`, optional
            The spell's primary cooldown group.
        spell_type: :class:`SpellType`, optional
            The type of spells to show.
        premium: :class:`bool`, optional
            The type of premium requirement to filter. :obj:`None` means any premium requirement.
        sort: :class:`SpellSorting`, optional
            The field to sort spells by.

        Returns
        -------
        :class:`str`
            The URL to the spells section with the provided filtering parameters.
        """
        params = {
            "vocation": vocation.value if vocation else None,
            "group": group.value if group else None,
            "type": spell_type.value if spell_type else None,
            "sort": sort.value if sort else None,
            "premium": to_yes_no(premium),
        }
        return get_tibia_url("library", "spells", **params)


class SpellEntry(abc.Serializable):
    """A spell listed on the spells section.

    .. versionadded:: 5.0.0

    Attributes
    ----------
    identifier: :class:`str`
        The internal identifier of the spell. This is used as a key for links and images.
    name: :class:`str`
        The name of the spell.
    words: :class:`str`
        The words to cast the spell.
    group: :class:`SpellGroup`
        The cooldown group of the spell.
    spell_type: :class:`SpellType`
        The type of the spell
    exp_level: :class:`int`
        The required level to cast the spell.
    mana: :class:`int`, optional.
        The mana required to use the spell. If :obj:`None`, the mana cost is variable.
    price: :class:`int`
        The price in gold coins to learn the spell.
    premium: :class:`bool`
        Whether the spell requires a premium account to learn and use it.
    """

    __slots__ = (
        "identifier",
        "name",
        "words",
        "group",
        "spell_type",
        "exp_level",
        "mana",
        "price",
        "premium",
    )

    _serializable_properties = (
        "image_url",
    )

    def __init__(self, identifier, name, words, **kwargs):
        self.identifier: str = identifier
        self.name: str = name
        self.words: str = words
        self.group: SpellGroup = kwargs.get("group")
        self.spell_type: SpellType = kwargs.get("spell_type")
        self.exp_level: int = kwargs.get("exp_level")
        self.mana: Optional[int] = kwargs.get("mana")
        self.price: int = kwargs.get("price")
        self.premium: bool = kwargs.get("premium")

    def __repr__(self):
        return f"<{self.__class__.__name__} identifier={self.identifier!r} name={self.name!r} words={self.words!r} " \
               f"group={self.group!r} spell_type={self.spell_type!r}>"

    @property
    def url(self):
        """:class:`str`: The URL to the spell."""
        return self.get_url(self.identifier)

    @property
    def image_url(self):
        """:class:`str`: The URL to this spell's image."""
        return f"https://static.tibia.com/images/library/{self.identifier}.png"

    @classmethod
    def get_url(cls, identifier):
        """Get the URL to a spell in the Tibia.com spells section.

        Parameters
        ----------
        identifier: :class:`str`
            The identifier of the spell.

        Returns
        -------
        :class:`str`
            The URL to the spell.
        """
        return get_tibia_url("library", "spells", spell=identifier.lower())


class Spell(SpellEntry):
    """A spell listed on the spells section.

    .. versionadded:: 5.0.0

    Attributes
    ----------
    name: :class:`str`
        The name of the spell.
    words: :class:`str`
        The words to cast the spell.
    group: :class:`SpellGroup`
        The cooldown group of the spell.
    spell_type: :class:`SpellType`
        The type of the spell
    exp_level: :class:`int`
        The required level to cast the spell.
    mana: :class:`int`, optional.
        The mana required to use the spell. If :obj:`None`, the mana cost is variable.
    price: :class:`int`
        The price in gold coins to learn the spell.
    premium: :class:`bool`
        Whether the spell requires a premium account to learn and use it.
    description: :class:`str`
        A description of the spells effect and history.
    vocations: :class:`list` of :class:`str`
        The vocations that can use this spell.
    cooldown: :class:`int`
        The individual cooldown of this spell in seconds.
    cooldown_group: :class:`int`, optional
        The group cooldown of this spell in seconds.
    group_secondary: :class:`str`, optional
        The secondary cooldown group of this spell, if any.
    cooldown_group_secondary: :class:`int`, optional
        The secondary cooldown of this spell in seconds.
    soul_points: :class:`int`, optional
        The number of soul points consumed by this spell. It will be :obj:`None` if not applicable.
    amount: :class:`int`, optional
        The amount of objects created by this spell. It will be :obj:`None` if not applicable.
    magic_type: :class:`str`, optional
        The type of magic of this spell. Influenced by specialized magic level attributes.
    cities: :class:`list` of :class:`str`
        The cities where this spell can be learned.
    rune: :class:`Rune`, optinal
        Information of the rune created by this spell, if applicable.
    """

    __slots__ = (
        "description",
        "vocations",
        "cooldown",
        "group_secondary",
        "cooldown_group",
        "cooldown_group_secondary",
        "soul_points",
        "amount",
        "magic_type",
        "cities",
        "rune",
    )

    def __init__(self, identifier, name, words, **kwargs):
        super().__init__(identifier, name, words, **kwargs)
        self.description: str = kwargs.get("description")
        self.vocations: List[str] = kwargs.get("vocations")
        self.cooldown: int = kwargs.get("cooldown")
        self.group_secondary: Optional[str] = kwargs.get("group_secondary")
        self.cooldown_group: int = kwargs.get("cooldown_group")
        self.cooldown_group_secondary: Optional[int] = kwargs.get("cooldown_group_secondary")
        self.soul_points: Optional[int] = kwargs.get("soul_points")
        self.amount: Optional[int] = kwargs.get("amount")
        self.magic_type: Optional[str] = kwargs.get("magic_type")
        self.cities: List[str] = kwargs.get("cities")
        self.rune: Optional[Rune] = kwargs.get("rune")

    @classmethod
    def from_content(cls, content):
        """Parse the content of a spells page.

        Parameters
        -----------
        content: :class:`str`
            The HTML content of the page.

        Returns
        ----------
        :class:`Spell`
            The spell data. If the spell doesn't exist, this will be :obj:`None`.

        Raises
        ------
        InvalidContent
            If content is not the HTML of the spells section.
        """
        parsed_content = parse_tibiacom_content(content)
        try:
            tables = parse_tibiacom_tables(parsed_content)
            title_table = parsed_content.find("table", attrs={"class": False})
            spell_table = tables["Spell Information"]
            img = title_table.find("img")
            url = urllib.parse.urlparse(img["src"])
            filename = os.path.basename(url.path)
            identifier = str(filename.split(".")[0])
            next_sibling = title_table.next_sibling
            description = ""
            while next_sibling:
                if isinstance(next_sibling, bs4.Tag):
                    if next_sibling.name == "br":
                        description += "\n"
                    elif next_sibling.name in ["table", "div"]:
                        break
                    else:
                        description += next_sibling.text
                elif isinstance(next_sibling, bs4.NavigableString):
                    description += str(next_sibling)
                next_sibling = next_sibling.next_sibling
            spell = cls._parse_spells_table(identifier, spell_table)
            spell.description = description.strip()
            if "Rune Information" in tables:
                spell.rune = cls._parse_rune_table(tables["Rune Information"])
            return spell
        except (TypeError, AttributeError, IndexError, KeyError) as e:
            form = parsed_content.find("form")
            if form:
                data = parse_form_data(form)
                if "subtopic=spells" in data.get("__action__"):
                    return None
            raise errors.InvalidContent("content is not a spell page", e)

    @classmethod
    def _parse_rune_table(cls, table):
        """Parse the rune information table.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table containing the rune information.

        Returns
        -------
        :class:`Rune`
            The rune described in the table.
        """
        attrs = cls._parse_table_attributes(table)
        rune = Rune(name=attrs["name"], group=try_enum(SpellGroup, attrs["group"]))
        rune.vocations = [v.strip() for v in attrs["vocation"].split(",")]
        rune.magic_type = attrs.get("magic_type")
        rune.magic_level = parse_integer(attrs.get("mag_lvl"), 0)
        rune.exp_level = parse_integer(attrs.get("exp_lvl"), 0)
        rune.mana = parse_integer(attrs.get("mana"), None)
        return rune

    @classmethod
    def _parse_spells_table(cls, identifier, spell_table):
        """Parse the table containing spell information.

        Parameters
        ----------
        identifier: :class:`str`
            The identifier of the spell.
        spell_table: :class:`bs4.Tag`
            The table containing the spell information.

        Returns
        -------
        :class:`Spell`
            The spell described in the table.
        """
        attrs = cls._parse_table_attributes(spell_table)
        spell = cls(identifier, attrs["name"], attrs["formula"], premium="yes" in attrs["premium"],
                    exp_level=int(attrs["exp_lvl"]))
        spell.vocations = [s.strip() for s in attrs["vocation"].split(",")]
        spell.cities = [s.strip() for s in attrs["city"].split(",")]
        m = group_pattern.match(attrs["group"])
        groups = m.groupdict()
        spell.group = try_enum(SpellGroup, groups.get("group"))
        spell.group_secondary = groups.get("secondary")
        m = cooldown_pattern.match(attrs["cooldown"])
        cooldowns = m.groupdict()
        spell.cooldown = int(cooldowns["cooldown"])
        spell.cooldown_group = int(cooldowns["group_cooldown"])
        spell.cooldown_group_secondary = parse_integer(cooldowns.get("secondary_group_cooldown"), None)
        spell.spell_type = try_enum(SpellType, attrs["type"])
        spell.soul_points = parse_integer(attrs.get("soul_points"), None)
        spell.mana = parse_integer(attrs.get("mana"), None)
        spell.amount = parse_integer(attrs.get("amount"), None)
        spell.price = parse_integer(attrs.get("price"), 0)
        spell.magic_type = attrs.get("magic_type")
        return spell

    @classmethod
    def _parse_table_attributes(cls, table) -> Dict[str, str]:
        """Parse the attributes of a table.

        Create a dictionary where every key is the left column (cleaned up) and the value is the right column.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table to get the attributes from.

        Returns
        -------
        :class:`dict`
            The table attributes.
        """
        spell_rows = table.find_all("tr")
        attrs = {}
        for row in spell_rows:
            cols = row.find_all("td")
            cols_text = [c.text for c in cols]
            clean_name = cols_text[0].replace(":", "").replace(" ", "_").lower().strip()
            value = cols_text[1]
            attrs[clean_name] = value
        return attrs


class Rune(abc.Serializable):
    """Information about runes created by spells.

    .. versionadded:: 5.0.0

    Attributes
    ----------
    name: :class:`str`
        The name of the rune.
    vocations: :class:`list` of :class:`str`
        The vocations that can use this rune.
    group: :class:`SpellGroup`
        The cooldown group of the rune.
    exp_level: :class:`int`
        The experience level required to use the rune.
    mana: :class:`int`, optional
        The amount of mana needed to use the rune. It will be :obj:`None` if not applicable.
    magic_level: :class:`int`
        The magic level required to use the rune.
    magic_type: :class:`str`, optional
        The type of magic of this rune. Influenced by specialized magic level attributes.
    """

    __slots__ = (
        'name',
        'vocations',
        'group',
        'exp_level',
        'mana',
        'magic_level',
        'magic_type',
    )

    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name")
        self.vocations: List[str] = kwargs.get("vocations")
        self.group: SpellGroup = kwargs.get("group")
        self.exp_level: int = kwargs.get("exp_level")
        self.mana: Optional[int] = kwargs.get("mana")
        self.magic_level: int = kwargs.get("magic_level")
        self.magic_type: Optional[str] = kwargs.get("magic_type")
