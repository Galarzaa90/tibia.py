from __future__ import annotations
from typing import List, TYPE_CHECKING

from tibiapy.models.creature import CreatureEntry, Creature

if TYPE_CHECKING:
    from typing_extensions import Self


class CreatureEntryBuilder:

    def __init__(self):
        self._name = None
        self._identifier = None

    def name(self, name: str) -> Self:
        self._name = name
        return self

    def identifier(self, identifier: str) -> Self:
        self._identifier = identifier
        return self

    def build(self) -> CreatureEntry:
        return CreatureEntry(
            name=self._name,
            identifier=self._identifier,
        )


class CreatureBuilder:
    def __init__(self):
        self._name = None
        self._identifier = None
        self._description = None
        self._hitpoints = None
        self._experience = None
        self._immune_to = []
        self._weak_against = []
        self._strong_against = []
        self._loot = None
        self._mana_cost = None
        self._summonable = False
        self._convinceable = False

    def name(self, name: str) -> Self:
        self._name = name
        return self

    def identifier(self, identifier: str) -> Self:
        self._identifier = identifier
        return self

    def description(self, description: str) -> Self:
        self._description = description
        return self

    def hitpoints(self, hitpoints: int) -> Self:
        self._hitpoints = hitpoints
        return self

    def experience(self, experience: int) -> Self:
        self._experience = experience
        return self

    def immune_to(self, immune_to: List[str]) -> Self:
        self._immune_to = immune_to
        return self

    def weak_against(self, weak_against: List[str]) -> Self:
        self._weak_against = weak_against
        return self

    def strong_against(self, strong_against: List[str]) -> Self:
        self._strong_against = strong_against
        return self

    def loot(self, loot: str) -> Self:
        self._loot = loot
        return self

    def mana_cost(self, mana_cost: int) -> Self:
        self._mana_cost = mana_cost
        return self

    def summonable(self, summonable: bool) -> Self:
        self._summonable = summonable
        return self

    def convinceable(self, convinceable: bool) -> Self:
        self._convinceable = convinceable
        return self

    def build(self) -> Creature:
        return Creature(
            name=self._name,
            identifier=self._identifier,
            description=self._description,
            hitpoints=self._hitpoints,
            experience=self._experience,
            immune_to=self._immune_to,
            weak_against=self._weak_against,
            strong_against=self._strong_against,
            loot=self._loot,
            mana_cost=self._mana_cost,
            summonable=self._summonable,
            convinceable=self._convinceable,
        )
