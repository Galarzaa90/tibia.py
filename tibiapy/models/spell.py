"""Models related to the spells section in the library."""
from __future__ import annotations
from typing import List, Optional

from pydantic import BaseModel

from tibiapy import VocationSpellFilter, SpellGroup, SpellType, SpellSorting
from tibiapy.utils import get_tibia_url

__all__ = (
    'SpellsSection',
    'Spell',
    'SpellEntry',
    'Rune'
)


def to_yes_no(value: Optional[bool]):
    if value is None:
        return None
    return "yes" if value else "no"


class Rune(BaseModel):
    """Information about runes created by spells."""

    name: str
    """The name of the rune."""
    vocations: List[str]
    """The vocations that can use this rune."""
    group: SpellGroup
    """The cooldown group of the rune."""
    exp_level: int
    """The experience level required to use the rune."""
    mana: Optional[int]
    """The amount of mana needed to use the rune. It will be :obj:`None` if not applicable."""
    magic_level: int
    """The magic level required to use the rune."""
    magic_type: Optional[str]
    """The type of magic of this rune. Influenced by specialized magic level attributes."""


class SpellEntry(BaseModel):
    """A spell listed on the spells section."""

    identifier: str
    """The internal identifier of the spell. This is used as a key for links and images."""
    name: str
    """The name of the spell."""
    words: str
    """The words to cast the spell."""
    group: SpellGroup
    """The cooldown group of the spell."""
    spell_type: SpellType
    """The type of the spell"""
    exp_level: Optional[int] = None
    """The required level to cast the spell."""
    mana: Optional[int] = None
    """The mana required to use the spell. If :obj:`None`, the mana cost is variable."""
    price: int
    """The price in gold coins to learn the spell."""
    premium: bool
    """Whether the spell requires a premium account to learn and use it."""

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
    """A spell listed on the spells section."""

    description: str
    """A description of the spells effect and history."""
    vocations: List[str]
    """The vocations that can use this spell."""
    cooldown: int
    """The individual cooldown of this spell in seconds."""
    cooldown_group: Optional[int] = None
    """The group cooldown of this spell in seconds."""
    group_secondary: Optional[str] = None
    """The secondary cooldown group of this spell, if any."""
    cooldown_group_secondary: Optional[int] = None
    """The secondary cooldown of this spell in seconds."""
    soul_points: Optional[int] = None
    """The number of soul points consumed by this spell. It will be :obj:`None` if not applicable."""
    amount: Optional[int] = None
    """The amount of objects created by this spell. It will be :obj:`None` if not applicable."""
    magic_type: Optional[str] = None
    """The type of magic of this spell. Influenced by specialized magic level attributes."""
    cities: List[str]
    """The cities where this spell can be learned."""
    rune: Optional[Rune]
    """Information of the rune created by this spell, if applicable."""


class SpellsSection(BaseModel):
    """The spells section in Tibia.com."""

    vocation: Optional[VocationSpellFilter] = None
    """The selected vocation filter. If :obj:`None`, spells for any vocation will be shown."""
    group: Optional[SpellGroup] = None
    """The selected spell group to display. If :obj:`None`, spells for any group will be shown."""
    spell_type: Optional[SpellType] = None
    """The selected spell type to display. If :obj:`None`, spells for any type will be shown."""
    premium: Optional[bool] = None
    """The premium status to filter in. :obj:`True` to show only premium spells,
        :obj:`False` to show free account spells and :obj:`None` will show any spells."""
    sort_by: SpellSorting
    """The sorting order of the displayed spells."""
    entries: List[SpellEntry] = []
    """The spells matching the selected filters."""

    @property
    def url(self):
        return self.get_url(vocation=self.vocation, group=self.group, spell_type=self.spell_type, premium=self.premium,
                            sort=self.sort_by)

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

