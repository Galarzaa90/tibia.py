from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING

from tibiapy.models import SpellEntry, SpellsSection, Spell, Rune

if TYPE_CHECKING:
    from tibiapy import VocationSpellFilter, SpellGroup, SpellSorting, SpellType


class SpellSectionBuilder:
    def __init__(self):
        self._vocation = None
        self._group = None
        self._spell_type = None
        self._premium = None
        self._sort_by = None
        self._entries = []

    def vocation(self, vocation: Optional[VocationSpellFilter]):
        self._vocation = vocation
        return self

    def group(self, group: Optional[SpellGroup]):
        self._group = group
        return self

    def spell_type(self, spell_type: Optional[VocationSpellFilter]):
        self._spell_type = spell_type
        return self

    def premium(self, premium: Optional[bool]):
        self._premium = premium
        return self

    def sort_by(self, sort_by: SpellSorting):
        self._sort_by = sort_by
        return self

    def entries(self, entries: List[SpellEntry]):
        self._entries = entries
        return self

    def add_entry(self, spell: SpellEntry):
        self._entries.append(spell)
        return self

    def build(self):
        return SpellsSection(
            vocation=self._vocation,
            group=self._group,
            spell_type=self._spell_type,
            premium=self._premium,
            sort_by=self._sort_by,
            entries=self._entries
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
        self._premium = None

    def identifier(self, identifier: str):
        self._identifier = identifier
        return self

    def name(self, name: str):
        self._name = name
        return self

    def words(self, words: str):
        self._words = words
        return self

    def group(self, group: SpellGroup):
        self._group = group
        return self

    def spell_type(self, spell_type: SpellType):
        self._spell_type = spell_type
        return self

    def exp_level(self, exp_level: int):
        self._exp_level = exp_level
        return self

    def mana(self, mana: Optional[int]):
        self._mana = mana
        return self

    def price(self, price: int):
        self._price = price
        return self

    def premium(self, premium: bool):
        self._premium = premium
        return self

    def build(self):
        return SpellEntry(
            identifier=self._identifier,
            name=self._name,
            words=self._words,
            group=self._group,
            spell_type=self._spell_type,
            exp_level=self._exp_level,
            mana=self._mana,
            price=self._price,
            premium=self._premium,
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

    def description(self, description: str):
        self._description = description
        return self

    def vocations(self, vocations: str):
        self._vocations = vocations
        return self

    def cooldown(self, cooldown: int):
        self._cooldown = cooldown
        return self

    def cooldown_group(self, cooldown_group: Optional[int]):
        self._cooldown_group = cooldown_group
        return self

    def cooldown_group_secondary(self, cooldown_group_secondary: Optional[int]):
        self._cooldown_group_secondary = cooldown_group_secondary
        return self

    def group_secondary(self, group_secondary: SpellGroup):
        self._group_secondary = group_secondary
        return self

    def soul_points(self, soul_points: SpellType):
        self._soul_points = soul_points
        return self

    def amount(self, amount: int):
        self._amount = amount
        return self

    def magic_type(self, magic_type: Optional[int]):
        self._magic_type = magic_type
        return self

    def cities(self, cities: List[str]):
        self._cities = cities
        return self

    def rune(self, rune: Rune):
        self._rune = rune
        return self

    def build(self):
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
            premium=self._premium,
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

    def name(self, name: str):
        self._name = name
        return self

    def vocations(self, vocations: List[str]):
        self._vocations = vocations
        return self

    def group(self, group: SpellGroup):
        self._group = group
        return self

    def exp_level(self, exp_level: int):
        self._exp_level = exp_level
        return self

    def mana(self, mana: Optional[int]):
        self._mana = mana
        return self

    def magic_level(self, magic_level: int):
        self._magic_level = magic_level
        return self

    def magic_type(self, magic_type: Optional[str]):
        self._magic_type = magic_type
        return self

    def build(self):
        return Rune(
            name=self._name,
            vocations=self._vocations,
            group=self._group,
            exp_level=self._exp_level,
            mana=self._mana,
            magic_level=self._magic_level,
            magic_type=self._magic_type,
        )
