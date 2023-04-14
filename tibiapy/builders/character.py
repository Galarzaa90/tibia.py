from tibiapy.models import Character


class CharacterBuilder:

    def __init__(self, **kwargs):
        self._name = kwargs.get("name")
        self._traded = kwargs.get("traded") or False
        self._deletion_date = kwargs.get("deletion_date")
        self._former_names = kwargs.get("former_names") or []
        self._title = kwargs.get("title")
        self._unlocked_titles = kwargs.get("unlocked_titles") or 0
        self._sex = kwargs.get("sex")
        self._vocation = kwargs.get("vocation")
        self._level = kwargs.get("level")
        self._achievement_points = kwargs.get("achievement_points")
        self._world = kwargs.get("world")
        self._former_world = kwargs.get("former_world")
        self._residence = kwargs.get("residence")
        self._married_to = kwargs.get("married_to")
        self._houses = kwargs.get("houses") or []
        self._guild_membership = kwargs.get("guild_membership")
        self._last_login = kwargs.get("last_login")
        self._position = kwargs.get("position")
        self._comment = kwargs.get("comment")
        self._account_status = kwargs.get("account_status")
        self._account_badges = kwargs.get("account_badges") or []
        self._achievements = kwargs.get("achievements") or []
        self._deaths = kwargs.get("deaths") or []
        self._deaths_truncated = kwargs.get("deaths_truncated") or False
        self._account_information = kwargs.get("account_information")
        self._other_characters = kwargs.get("other_characters") or []

    def name(self, name):
        self._name = name
        return self

    def traded(self, traded):
        self._traded = traded
        return self

    def deletion_date(self, deletion_date):
        self._deletion_date = deletion_date
        return self

    def former_names(self, former_names):
        self._former_names = former_names
        return self

    def title(self, title):
        self._title = title
        return self

    def unlocked_titles(self, unlocked_titles):
        self._unlocked_titles = unlocked_titles
        return self

    def sex(self, sex):
        self._sex = sex
        return self

    def vocation(self, vocation):
        self._vocation = vocation
        return self

    def level(self, level):
        self._level = level
        return self

    def achievement_points(self, achievement_points):
        self._achievement_points = achievement_points
        return self

    def world(self, world):
        self._world = world
        return self

    def former_world(self, former_world):
        self._former_world = former_world
        return self

    def residence(self, residence):
        self._residence = residence
        return self

    def married_to(self, married_to):
        self._married_to = married_to
        return self

    def houses(self, houses):
        self._houses = houses
        return self

    def add_house(self, house):
        self._houses.append(house)
        return self

    def guild_membership(self, guild_membership):
        self._guild_membership = guild_membership
        return self

    def last_login(self, last_login):
        self._last_login = last_login
        return self

    def position(self, position):
        self._position = position
        return self

    def comment(self, comment):
        self._comment = comment
        return self

    def account_status(self, account_status):
        self._account_status = account_status
        return self

    def account_badges(self, account_badges):
        self._account_badges = account_badges
        return self

    def achievements(self, achievements):
        self._achievements = achievements
        return self

    def deaths(self, deaths):
        self._deaths = deaths
        return self

    def add_death(self, death):
        self._deaths.append(death)
        return self

    def deaths_truncated(self, deaths_truncated):
        self._deaths_truncated = deaths_truncated
        return self

    def account_information(self, account_information):
        self._account_information = account_information
        return self

    def other_characters(self, other_characters):
        self._other_characters = other_characters
        return self

    def build(self):
        return Character(
            name=self._name,
            traded=self._traded,
            deletion_date=self._deletion_date,
            former_names=self._former_names,
            title=self._title,
            unlocked_titles=self._unlocked_titles,
            sex=self._sex,
            vocation=self._vocation,
            level=self._level,
            achievement_points=self._achievement_points,
            world=self._world,
            former_world=self._former_world,
            residence=self._residence,
            married_to=self._married_to,
            houses=self._houses,
            guild_membership=self._guild_membership,
            last_login=self._last_login,
            position=self._position,
            comment=self._comment,
            account_status=self._account_status,
            account_badges=self._account_badges,
            achievements=self._achievements,
            deaths=self._deaths,
            deaths_truncated=self._deaths_truncated,
            account_information=self._account_information,
            other_characters=self._other_characters,
        )
