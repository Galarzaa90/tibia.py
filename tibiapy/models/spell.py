"""Models related to the spells section in the library."""
from __future__ import annotations

from pydantic import computed_field

from tibiapy.enums import SpellGroup, SpellSorting, SpellType, SpellVocationFilter
from tibiapy.models import BaseModel
from tibiapy.urls import get_spell_url, get_spells_section_url, get_static_file_url

__all__ = (
    "SpellsSection",
    "Spell",
    "SpellEntry",
    "Rune",
)


class Rune(BaseModel):
    """Information about runes created by spells."""

    name: str
    """The name of the rune."""
    vocations: list[str]
    """The vocations that can use this rune."""
    group: SpellGroup
    """The cooldown group of the rune."""
    exp_level: int
    """The experience level required to use the rune."""
    mana: int | None = None
    """The amount of mana needed to use the rune. It will be `None` if not applicable."""
    magic_level: int
    """The magic level required to use the rune."""
    magic_type: str | None = None
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
    exp_level: int | None = None
    """The required level to cast the spell. If obj:`None`, the spell is obtained through a Revelation Perk."""
    mana: int | None = None
    """The mana required to use the spell. If `None`, the mana cost is variable."""
    price: int
    """The price in gold coins to learn the spell."""
    is_premium: bool
    """Whether the spell requires a premium account to learn and use it."""

    @property
    def url(self) -> str:
        """The URL to the spell."""
        return get_spell_url(self.identifier)

    @computed_field
    @property
    def image_url(self) -> str:
        """The URL to this spell's image."""
        return get_static_file_url("images", "library", f"{self.identifier}.png")


class Spell(SpellEntry):
    """A spell listed on the spells section."""

    description: str
    """A description of the spells effect and history."""
    vocations: list[str]
    """The vocations that can use this spell."""
    cooldown: int
    """The individual cooldown of this spell in seconds."""
    cooldown_group: int | None = None
    """The group cooldown of this spell in seconds."""
    group_secondary: str | None = None
    """The secondary cooldown group of this spell, if any."""
    cooldown_group_secondary: int | None = None
    """The secondary cooldown of this spell in seconds."""
    soul_points: int | None = None
    """The number of soul points consumed by this spell. It will be `None` if not applicable."""
    amount: int | None = None
    """The amount of objects created by this spell. It will be `None` if not applicable."""
    magic_type: str | None = None
    """The type of magic of this spell. Influenced by specialized magic level attributes."""
    cities: list[str]
    """The cities where this spell can be learned."""
    rune: Rune | None = None
    """Information of the rune created by this spell, if applicable."""


class SpellsSection(BaseModel):
    """The spells section in Tibia.com."""

    vocation: SpellVocationFilter | None = None
    """The selected vocation filter. If `None`, spells for any vocation will be shown."""
    group: SpellGroup | None = None
    """The selected spell group to display. If `None`, spells for any group will be shown."""
    spell_type: SpellType | None = None
    """The selected spell type to display. If `None`, spells for any type will be shown."""
    is_premium: bool | None = None
    """The premium status to filter in. `True` to show only premium spells,
        `False` to show free account spells and `None` will show any spells."""
    sort_by: SpellSorting
    """The sorting order of the displayed spells."""
    entries: list[SpellEntry]
    """The spells matching the selected filters."""

    @property
    def url(self) -> str:
        """The URL to the spells section in Tibia.com."""
        return get_spells_section_url(
            vocation=self.vocation,
            group=self.group,
            spell_type=self.spell_type,
            is_premium=self.is_premium,
            sort=self.sort_by,
        )
