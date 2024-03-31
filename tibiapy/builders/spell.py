from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING

from tibiapy.models import SpellEntry, SpellsSection, Spell, Rune

if TYPE_CHECKING:
    from typing_extensions import Self
    from tibiapy.enums import SpellVocationFilter, SpellGroup, SpellSorting, SpellType


class SpellSectionBuilder:
    def __init__(self):
        self._vocation = None
        self._group = None
        self._spell_type = None
        self._premium = None
        self._sort_by = None
        self._entries = []

    def vocation(self, vocation: Optional[SpellVocationFilter]) -> Self:
        self._vocation = vocation
        return self

    def group(self, group: Optional[SpellGroup]) -> Self:
        self._group = group
        return self

    def spell_type(self, spell_type: Optional[SpellVocationFilter]) -> Self:
        self._spell_type = spell_type
        return self

    def premium(self, premium: Optional[bool]) -> Self:
        self._premium = premium
        return self

    def sort_by(self, sort_by: SpellSorting) -> Self:
        self._sort_by = sort_by
        return self

    def entries(self, entries: List[SpellEntry]) -> Self:
        self._entries = entries
        return self

    def add_entry(self, spell: SpellEntry) -> Self:
        self._entries.append(spell)
        return self

    def build(self) -> SpellsSection:
        return SpellsSection(
            vocation=self._vocation,
            group=self._group,
            spell_type=self._spell_type,
            is_premium=self._premium,
            sort_by=self._sort_by,
            entries=self._entries,
        )


class SpellEntryBuilder:
    def __init__(self):
        self._identifier = None
        self._name = None
        self._words = None
        self._group = None
        self._spell_type = None
        self._exp_level = None
        self._mana = None
        self._price = None
        self._is_premium = None

    def identifier(self, identifier: str) -> Self:
        self._identifier = identifier
        return self

    def name(self, name: str) -> Self:
        self._name = name
        return self

    def words(self, words: str) -> Self:
        self._words = words
        return self

    def group(self, group: SpellGroup) -> Self:
        self._group = group
        return self

    def spell_type(self, spell_type: SpellType) -> Self:
        self._spell_type = spell_type
        return self

    def exp_level(self, exp_level: int) -> Self:
        self._exp_level = exp_level
        return self

    def mana(self, mana: Optional[int]) -> Self:
        self._mana = mana
        return self

    def price(self, price: int) -> Self:
        self._price = price
        return self

    def is_premium(self, is_premium: bool) -> Self:
        self._is_premium = is_premium
        return self

    def build(self) -> SpellEntry:
        return SpellEntry(
            identifier=self._identifier,
            name=self._name,
            words=self._words,
            group=self._group,
            spell_type=self._spell_type,
            exp_level=self._exp_level,
            mana=self._mana,
            price=self._price,
            is_premium=self._is_premium,
        )


class SpellBuilder(SpellEntryBuilder):

    def __init__(self):
        super().__init__()
        self._description = None
        self._vocations = None
        self._cooldown = None
        self._cooldown_group = None
        self._group_secondary = None
        self._cooldown_group_secondary = None
        self._soul_points = None
        self._amount = None
        self._magic_type = None
        self._cities = []
        self._rune = None

    def description(self, description: str) -> Self:
        self._description = description
        return self

    def vocations(self, vocations: List[str]) -> Self:
        self._vocations = vocations
        return self

    def cooldown(self, cooldown: int) -> Self:
        self._cooldown = cooldown
        return self

    def cooldown_group(self, cooldown_group: Optional[int]) -> Self:
        self._cooldown_group = cooldown_group
        return self

    def cooldown_group_secondary(self, cooldown_group_secondary: Optional[int]) -> Self:
        self._cooldown_group_secondary = cooldown_group_secondary
        return self

    def group_secondary(self, group_secondary: SpellGroup) -> Self:
        self._group_secondary = group_secondary
        return self

    def soul_points(self, soul_points: int) -> Self:
        self._soul_points = soul_points
        return self

    def amount(self, amount: int) -> Self:
        self._amount = amount
        return self

    def magic_type(self, magic_type: Optional[int]) -> Self:
        self._magic_type = magic_type
        return self

    def cities(self, cities: List[str]) -> Self:
        self._cities = cities
        return self

    def rune(self, rune: Rune) -> Self:
        self._rune = rune
        return self

    def build(self) -> Spell:
        return Spell(
            identifier=self._identifier,
            name=self._name,
            words=self._words,
            group=self._group,
            spell_type=self._spell_type,
            exp_level=self._exp_level,
            mana=self._mana,
            price=self._price,
            description=self._description,
            vocations=self._vocations,
            cooldown=self._cooldown,
            cooldown_group=self._cooldown_group,
            group_secondary=self._group_secondary,
            cooldown_group_secondary=self._cooldown_group_secondary,
            soul_points=self._soul_points,
            amount=self._amount,
            magic_type=self._magic_type,
            cities=self._cities,
            rune=self._rune,
            is_premium=self._is_premium,
        )


class RuneBuilder:
    def __init__(self):
        self._name = None
        self._vocations = None
        self._group = None
        self._exp_level = None
        self._mana = None
        self._magic_level = None
        self._magic_type = None

    def name(self, name: str) -> Self:
        self._name = name
        return self

    def vocations(self, vocations: List[str]) -> Self:
        self._vocations = vocations
        return self

    def group(self, group: SpellGroup) -> Self:
        self._group = group
        return self

    def exp_level(self, exp_level: int) -> Self:
        self._exp_level = exp_level
        return self

    def mana(self, mana: Optional[int]) -> Self:
        self._mana = mana
        return self

    def magic_level(self, magic_level: int) -> Self:
        self._magic_level = magic_level
        return self

    def magic_type(self, magic_type: Optional[str]) -> Self:
        self._magic_type = magic_type
        return self

    def build(self) -> Rune:
        return Rune(
            name=self._name,
            vocations=self._vocations,
            group=self._group,
            exp_level=self._exp_level,
            mana=self._mana,
            magic_level=self._magic_level,
            magic_type=self._magic_type,
        )
