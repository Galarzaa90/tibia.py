from tibiapy.models.creature import CreatureEntry, Creature


class CreatureEntryBuilder:

    def __init__(self, **kwargs):
        self._name = kwargs.get("name")
        self._identifier = kwargs.get("identifier")

    def name(self, name):
        self._name = name
        return self

    def identifier(self, identifier):
        self._identifier = identifier
        return self

    def build(self):
        return CreatureEntry(
            name=self._name,
            identifier=self._identifier,
        )


class CreatureBuilder:
    def __init__(self, **kwargs):
        self._name = kwargs.get("name")
        self._identifier = kwargs.get("identifier")
        self._description = kwargs.get("description")
        self._hitpoints = kwargs.get("hitpoints")
        self._experience = kwargs.get("experience")
        self._immune_to = kwargs.get("immune_to") or []
        self._weak_against = kwargs.get("weak_against") or []
        self._strong_against = kwargs.get("strong_against") or []
        self._loot = kwargs.get("loot")
        self._mana_cost = kwargs.get("mana_cost")
        self._summonable = kwargs.get("summonable") or False
        self._convinceable = kwargs.get("convinceable") or False

    def name(self, name):
        self._name = name
        return self

    def identifier(self, identifier):
        self._identifier = identifier
        return self

    def description(self, description):
        self._description = description
        return self

    def hitpoints(self, hitpoints):
        self._hitpoints = hitpoints
        return self

    def experience(self, experience):
        self._experience = experience
        return self

    def immune_to(self, immune_to):
        self._immune_to = immune_to
        return self

    def weak_against(self, weak_against):
        self._weak_against = weak_against
        return self

    def strong_against(self, strong_against):
        self._strong_against = strong_against
        return self

    def loot(self, loot):
        self._loot = loot
        return self

    def mana_cost(self, mana_cost):
        self._mana_cost = mana_cost
        return self

    def summonable(self, summonable):
        self._summonable = summonable
        return self

    def convinceable(self, convinceable):
        self._convinceable = convinceable
        return self

    def build(self):
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