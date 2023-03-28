from typing import Optional, List

from tibiapy import VocationSpellFilter, SpellGroup, SpellSorting, SpellType
from tibiapy.models import SpellEntry, SpellsSection, Spell, Rune


class SpellSectionBuilder:
    def __init__(self, **kwargs):
        self._vocation = kwargs.get("vocation")
        self._group = kwargs.get("group")
        self._spell_type = kwargs.get("spell_type")
        self._premium = kwargs.get("premium")
        self._sort_by = kwargs.get("sort_by")
        self._entries = kwargs.get("entries", [])

    def vocation(self, vocation: Optional[VocationSpellFilter]) -> 'SpellSectionBuilder':
        self._vocation = vocation
        return self

    def group(self, group: Optional[SpellGroup]) -> 'SpellSectionBuilder':
        self._group = group
        return self

    def spell_type(self, spell_type: Optional[VocationSpellFilter]) -> 'SpellSectionBuilder':
        self._spell_type = spell_type
        return self

    def premium(self, premium: Optional[bool]) -> 'SpellSectionBuilder':
        self._premium = premium
        return self

    def sort_by(self, sort_by: SpellSorting) -> 'SpellSectionBuilder':
        self._sort_by = sort_by
        return self

    def entries(self, entries: List[SpellEntry]) -> 'SpellSectionBuilder':
        self._entries = entries
        return self

    def add_entry(self, spell: SpellEntry) -> 'SpellSectionBuilder':
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
    def __init__(self, **kwargs):
        self._identifier = kwargs.get("identifier")
        self._name = kwargs.get("name")
        self._words = kwargs.get("words")
        self._group = kwargs.get("group")
        self._spell_type = kwargs.get("spell_type")
        self._exp_level = kwargs.get("exp_level")
        self._mana = kwargs.get("mana")
        self._price = kwargs.get("price")
        self._premium = kwargs.get("premium")

    def identifier(self, identifier: str) -> 'SpellEntryBuilder':
        self._identifier = identifier
        return self

    def name(self, name: str) -> 'SpellEntryBuilder':
        self._name = name
        return self

    def words(self, words: str) -> 'SpellEntryBuilder':
        self._words = words
        return self

    def group(self, group: SpellGroup) -> 'SpellEntryBuilder':
        self._group = group
        return self

    def spell_type(self, spell_type: SpellType) -> 'SpellEntryBuilder':
        self._spell_type = spell_type
        return self

    def exp_level(self, exp_level: int) -> 'SpellEntryBuilder':
        self._exp_level = exp_level
        return self

    def mana(self, mana: Optional[int]) -> 'SpellEntryBuilder':
        self._mana = mana
        return self

    def price(self, price: int) -> 'SpellEntryBuilder':
        self._price = price
        return self

    def premium(self, premium: bool) -> 'SpellEntryBuilder':
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._description = kwargs.get("description")
        self._vocations = kwargs.get("vocations")
        self._cooldown = kwargs.get("cooldown")
        self._cooldown_group = kwargs.get("cooldown_group")
        self._group_secondary = kwargs.get("group_secondary")
        self._cooldown_group_secondary = kwargs.get("cooldown_group_secondary")
        self._soul_points = kwargs.get("soul_points")
        self._amount = kwargs.get("amount")
        self._magic_type = kwargs.get("magic_type")
        self._cities = kwargs.get("cities")
        self._rune = kwargs.get("rune")

    def description(self, description: str) -> 'SpellEntryBuilder':
        self._description = description
        return self

    def vocations(self, vocations: str) -> 'SpellEntryBuilder':
        self._vocations = vocations
        return self

    def cooldown(self, cooldown: int) -> 'SpellEntryBuilder':
        self._cooldown = cooldown
        return self

    def cooldown_group(self, cooldown_group: Optional[int]) -> 'SpellEntryBuilder':
        self._cooldown_group = cooldown_group
        return self

    def cooldown_group_secondary(self, cooldown_group_secondary: Optional[int]) -> 'SpellEntryBuilder':
        self._cooldown_group_secondary = cooldown_group_secondary
        return self

    def group_secondary(self, group_secondary: SpellGroup) -> 'SpellEntryBuilder':
        self._group_secondary = group_secondary
        return self

    def soul_points(self, soul_points: SpellType) -> 'SpellEntryBuilder':
        self._soul_points = soul_points
        return self

    def amount(self, amount: int) -> 'SpellEntryBuilder':
        self._amount = amount
        return self

    def magic_type(self, magic_type: Optional[int]) -> 'SpellEntryBuilder':
        self._magic_type = magic_type
        return self

    def cities(self, cities: List[str]) -> 'SpellEntryBuilder':
        self._cities = cities
        return self

    def rune(self, rune: Rune) -> 'SpellEntryBuilder':
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
    def __init__(self, **kwargs):
        self._name = kwargs.get("name")
        self._vocations = kwargs.get("vocations")
        self._group = kwargs.get("group")
        self._exp_level = kwargs.get("exp_level")
        self._mana = kwargs.get("mana")
        self._magic_level = kwargs.get("magic_level")
        self._magic_type = kwargs.get("magic_type")

    def name(self, name: str) -> 'RuneBuilder':
        self._name = name
        return self

    def vocations(self, vocations: List[str]) -> 'RuneBuilder':
        self._vocations = vocations
        return self

    def group(self, group: SpellGroup) -> 'RuneBuilder':
        self._group = group
        return self

    def exp_level(self, exp_level: int) -> 'RuneBuilder':
        self._exp_level = exp_level
        return self

    def mana(self, mana: Optional[int]) -> 'RuneBuilder':
        self._mana = mana
        return self

    def magic_level(self, magic_level: int) -> 'RuneBuilder':
        self._magic_level = magic_level
        return self

    def magic_type(self, magic_type: Optional[str]) -> 'RuneBuilder':
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