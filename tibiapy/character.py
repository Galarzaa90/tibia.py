import datetime
import json
import re
import urllib.parse
from collections import OrderedDict
from typing import List

import bs4

from tibiapy import abc
from tibiapy.enums import AccountStatus, try_enum, Sex
from tibiapy.guild import Guild
from tibiapy.house import CharacterHouse
from tibiapy.utils import parse_tibia_date, parse_tibia_datetime, parse_tibiadata_date, parse_tibiadata_datetime

deleted_regexp = re.compile(r'([^,]+), will be deleted at (.*)')
# Extracts the death's level and killers.
death_regexp = re.compile(r'Level (?P<level>\d+) by (?P<killers>.*)\.</td>')
# From the killers list, filters out the assists.
death_assisted = re.compile(r'(?P<killers>.+)\.<br/>Assisted by (?P<assists>.+)')
# From a killer entry, extracts the summoned creature
death_summon = re.compile(r'(?P<summon>.+) of <a[^>]+>(?P<name>[^<]+)</a>')
# Extracts the contents of a tag
link_content = re.compile(r'>([^<]+)<')
# Extracts reason from TibiaData death
death_reason = re.compile(r'by (?P<killers>[^.]+)(?:\.\s+Assisted by (?P<assists>.+))?', re.DOTALL)

house_regexp = re.compile(r'paid until (.*)')
guild_regexp = re.compile(r'([\s\w]+)\sof the\s(.+)')



class Character(abc.Character):
    """Represents a Tibia character

    Attributes
    ---------------
    name: :class:`str`
        The name of the character.
    deletion_date: Optional[:class:`datetime.datetime`]
        The date where the character will be deleted if it is scheduled for deletion.
    former_names: List[:class:`str`]
        Previous names of this character.
    sex: :class:`str`
        The character's gender, either "male" or "female"
    vocation: :class:`str`
        The character's vocation.
    level: :class:`int`
        The character's level.
    achievement_points: :class:`int`
        The total of points the character has.
    world: :class:`str`
        The character's current world.
    former_world: Optional[:class:`str`]
        The previous world where the character was in, in the last 6 months.
    residence: :class:`str`
        The current hometown of the character.
    married_to: Optional[:class:`str`]
        The name of the character's spouse/husband.
    house: Optional[:class:`CharacterHouse`]
        The house currently owned by the character.
    guild_membership: Optional[:class:`dict`]
        The guild the character is a member of. The dictionary contains a key for the rank and a key for the name.
    last_login: Optional[:class:`datetime.datetime`]
        The last time the character logged in. It will be None if the character has never logged in.
    comment: Optional[:class:`str`]
        The displayed comment.
    account_status: :class:`str`
        Whether the character's account is Premium or Free.
    achievements: List[:class:`dict`]
        The achievements chosen to be displayed.
    deaths: lsit of  :class:`Death`
        The character's recent deaths.
    account_information: :class:`dict`
        The character's account information, if visible.
    other_characters: List[:class:`OtherCharacter`]
        Other characters in the same account, if visible.
    """
    __slots__ = ("former_names", "sex", "vocation", "level", "achievement_points", "world", "former_world", "residence",
                 "married_to", "house", "guild_membership", "last_login", "account_status", "comment", "achievements",
                 "deaths", "account_information", "other_characters", "deletion_date")

    def __init__(self, name=None, world=None, vocation=None, level=0, sex=None, **kwargs):
        self.name = name
        self.former_names = kwargs.get("former_names", [])
        self.sex = try_enum(Sex, sex)
        self.vocation = vocation
        self.level = level
        self.achievement_points = kwargs.get("achievement_points", 0)
        self.world = world
        self.former_world = kwargs.get("former_world")
        self.residence = kwargs.get("residence")
        self.married_to = kwargs.get("married_to")
        self.house = kwargs.get("house")
        self.guild_membership = kwargs.get("guild_membership")
        self.last_login = kwargs.get("last_login")
        self.account_status = try_enum(AccountStatus, kwargs.get("account_status"))
        self.comment = kwargs.get("comment")
        self.achievements = kwargs.get("achievements",[])
        self.deaths = kwargs.get("deaths", [])
        self.account_information = kwargs.get("account_information")
        self.other_characters = kwargs.get("other_characters", [])
        self.deletion_date = kwargs.get("deletion_date")

    @property
    def deleted(self):
        """:class:`bool`: Whether the character is scheduled for deletion or not."""
        return self.deletion_date is not None

    @property
    def guild_name(self):
        """:class:`str`: The name of the guild the character belongs to, or ``None``."""
        return self.guild_membership["guild"] if self.guild_membership else None

    @property
    def guild_rank(self):
        """:class:`str`: The character's rank in the guild they belong to, or ``None``."""
        return self.guild_membership["rank"] if self.guild_membership else None

    @property
    def guild_url(self):
        """:class:`str`: The character's rank in the guild they belong to, or ``None``."""
        return Guild.get_url(self.guild_membership["guild"]) if self.guild_membership else None

    @property
    def married_to_url(self):
        """:class:`str`: The URL to the husband/spouse information page on Tibia.com, if applicable."""
        return self.get_url(self.married_to) if self.married_to else None

    @classmethod
    def _beautiful_soup(cls, content):
        """
        Parses HTML content into a BeautifulSoup object.
        Parameters
        ----------
        content: :class:`str`
            The HTML content.

        Returns
        -------
        :class:`bs4.BeautifulSoup`: The parsed content.
        """
        return bs4.BeautifulSoup(content, 'html.parser', parse_only=bs4.SoupStrainer("div", class_="BoxContent"))

    @classmethod
    def _parse(cls, content):
        """
        Parses the character's page HTML content into a dictionary.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the character's page.

        Returns
        -------
        :class:`dict[str, Any]`
            A dictionary containing all the character's information.
        """
        parsed_content = cls._beautiful_soup(content)
        tables = cls._parse_tables(parsed_content)
        char = {}
        if "Character Information" in tables.keys():
            cls._parse_character_information(char, tables["Character Information"])
        else:
            return {}
        cls._parse_achievements(char, tables.get("Account Achievements", []))
        cls._parse_deaths(char, tables.get("Character Deaths", []))
        cls._parse_account_information(char, tables.get("Account Information", []))
        cls._parse_other_characters(char, tables.get("Characters", []))
        return char

    @classmethod
    def _parse_account_information(cls, char, rows):
        """
        Parses the character's account information

        Parameters
        ----------
        char: :class:`dict`[str,Any]
            Dictionary where information will be stored.
        rows: List[:class:`bs4.Tag`]
            A list of all rows contained in the table.
        """
        char["account_information"] = {}
        for row in rows:
            cols_raw = row.find_all('td')
            cols = [ele.text.strip() for ele in cols_raw]
            field, value = cols
            field = field.replace("\xa0", "_").replace(" ", "_").replace(":", "").lower()
            value = value.replace("\xa0", " ")
            char["account_information"][field] = value

    @classmethod
    def _parse_achievements(cls, char, rows):
        """
        Parses the character's displayed achievements

        Parameters
        ----------
        char: :class:`dict`[str,Any]
            Dictionary where information will be stored.
        rows: List[:class:`bs4.Tag`]
            A list of all rows contained in the table.
        """
        achievements = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) != 2:
                continue
            field, value = cols
            grade = str(field).count("achievement-grade-symbol")
            achievement = value.text.strip()
            achievements.append({
                "grade": grade,
                "name": achievement
            })
        char["achievements"] = achievements

    @classmethod
    def _parse_character_information(cls, char, rows):
        """
        Parses the character's basic information.

        Parameters
        ----------
        char: :class:`dict`[str,Any]
            Dictionary where information will be stored.
        rows: List[:class:`bs4.Tag`]
            A list of all rows contained in the table.
        """
        int_rows = ["level", "achievement_points"]
        for row in rows:
            cols_raw = row.find_all('td')
            cols = [ele.text.strip() for ele in cols_raw]
            field, value = cols
            field = field.replace("\xa0", "_").replace(" ", "_").replace(":", "").lower()
            value = value.replace("\xa0", " ")
            # This is a special case cause we need to see the link
            if field == "house":
                house_text = value
                paid_until = house_regexp.search(house_text).group(1)
                paid_until_date = parse_tibia_date(paid_until)
                house_link = cols_raw[1].find('a')
                url = urllib.parse.urlparse(house_link["href"])
                query = urllib.parse.parse_qs(url.query)
                char["house"] = CharacterHouse(int(query["houseid"][0]), house_link.text.strip(), query["town"][0],
                                               char["name"], paid_until_date)
                continue
            if field in int_rows:
                value = int(value)
            char[field] = value
        m = deleted_regexp.match(char["name"])
        if m:
            char["name"] = m.group(1)
            char["deletion_date"] = m.group(2)
        else:
            char["deletion_date"] = None

        if "guild_membership" in char:
            m = guild_regexp.match(char["guild_membership"])
            char["guild_membership"] = {
                'rank': m.group(1),
                'guild': m.group(2)
            }
        else:
            char["guild_membership"] = None

        if "former_names" in char:
            former_names = [fn.strip() for fn in char["former_names"].split(",")]
            char["former_names"] = former_names
        else:
            char["former_names"] = []

        if "married_to" not in char:
            char["married_to"] = None

    @classmethod
    def _parse_deaths(cls, char, rows):
        """
        Parses the character's recent deaths

        Parameters
        ----------
        char: :class:`dict`[str,Any]
            Dictionary where information will be stored.
        rows: List[:class:`bs4.Tag`]
            A list of all rows contained in the table.
        """
        deaths = []
        for row in rows:
            cols = row.find_all('td')
            death_time = cols[0].text.strip()
            death = str(cols[1]).replace("\xa0", " ")
            death_time = death_time.replace("\xa0", " ")
            death_info = death_regexp.search(death)
            if death_info:
                level = int(death_info.group("level"))
                killers_str = death_info.group("killers")
            else:
                continue
            assists = []
            # Check if the killers list contains assists
            assist_match = death_assisted.search(killers_str)
            if assist_match:
                # Filter out assists
                killers_str = assist_match.group("killers")
                # Split assists into a list.
                assists = cls._split_list(assist_match.group("assists"))
            killers = cls._split_list(killers_str)
            for i, killer in enumerate(killers):
                killer_dict = cls._parse_killer(killer)
                killers[i] = killer_dict
            for (i, assist) in enumerate(assists):
                # Extract names from character links in assists list.
                assists[i] = {"name": link_content.search(assist).group(1), "player": True}
            try:
                deaths.append({'time': death_time, 'level': level, 'killers': killers, 'assists': assists})
            except ValueError:
                # Some pvp deaths have no level, so they are raising a ValueError, they will be ignored for now.
                continue
        char["deaths"] = deaths

    @classmethod
    def _parse_killer(cls, killer):
        """Parses a killer into a dictionary.

        Parameters
        ----------
        killer: :class:`str`
            The killer's raw HTML string.

        Returns
        -------
        :class:`dict`: A dictionary containing the killer's info.
        """
        # If the killer contains a link, it is a player.
        if "href" in killer:
            killer_dict = {"name": link_content.search(killer).group(1), "player": True}
        else:
            killer_dict = {"name": killer, "player": False}
        # Check if it contains a summon.
        m = death_summon.search(killer)
        if m:
            killer_dict["summon"] = m.group("summon")
        return killer_dict

    @classmethod
    def _parse_other_characters(cls, char, rows):
        """
        Parses the character's other visible characters.

        Parameters
        ----------
        char: :class:`dict`[str,Any]
            Dictionary where information will be stored.
        rows: List[:class:`bs4.Tag`]
            A list of all rows contained in the table.
        """
        char["other_characters"] = []
        for row in rows:
            cols_raw = row.find_all('td')
            cols = [ele.text.strip() for ele in cols_raw]
            if len(cols) != 5:
                continue
            _name, world, status, __, __ = cols
            _name = _name.replace("\xa0", " ").split(". ")[1]
            char["other_characters"].append(
                {'name': _name, 'world': world, 'online': status == "online", 'deleted': status == "deleted"})

    @classmethod
    def _parse_tables(cls, parsed_content):
        """
        Parses the information tables contained in a character's page.

        Parameters
        ----------
        parsed_content: :class:`bs4.BeautifulSoup`
            A :class:`BeautifulSoup` object containing all the content.

        Returns
        -------
        :class:`OrderedDict`[str, List[:class:`bs4.Tag`]]
            A dictionary containing all the table rows, with the table headers as keys.
        """
        tables = parsed_content.find_all('table', attrs={"width": "100%"})
        output = OrderedDict()
        for table in tables:
            title = table.find("td").text
            output[title] = table.find_all("tr")[1:]
        return output

    # Todo: This might be turned into a function if it's needed elsewhere
    @classmethod
    def _split_list(cls, items, separator=",", last_separator=" and "):
        """
        Splits a string listing elements into an actual list.

        Parameters
        ----------
        items: :class:`str`
            A string listing elements.
        separator: :class:`str`
            The separator between each item. A comma by default.
        last_separator: :class:`str`
            The separator used for the last item. ' and ' by default.

        Returns
        -------
        List[:class:`str`]
            A list containing each one of the items.
        """
        if items is None:
            return None
        items = items.split(separator)
        last_item = items[-1]
        last_split = last_item.split(last_separator)
        if len(last_split) > 1:
            items[-1] = last_split[0]
            items.append(last_split[1])
        return [e.strip() for e in items]

    @classmethod
    def from_content(cls, content):
        """Creates an instance of the class from the html content of the character's page.

        Parameters
        -----------
        content: :class:`str`
            The HTML content of the page.

        Returns
        ----------
        :class:`Character`
            The character contained in the page, or None if the character doesn't exist.
        """
        char_json = cls._parse(content)
        if not char_json:
            return None
        try:
            if char_json["deletion_date"]:
                char_json["deletion_date"] = parse_tibia_datetime(char_json["deletion_date"])
            else:
                char_json["deletion_date"] = None

            # Some attributes require converting
            if "never" in char_json["last_login"]:
                char_json["last_login"] = None
            else:
                char_json["last_login"] = parse_tibia_datetime(char_json["last_login"])
            deaths = []
            for d in char_json["deaths"]:
                death = Death(**d)
                death.name = char_json["name"]
                deaths.append(death)
            char_json["deaths"] = deaths
            other_characters = []
            if char_json["other_characters"]:
                for o_char in char_json["other_characters"]:
                    other_characters.append(OtherCharacter(**o_char))
            char_json["other_characters"] = other_characters

            char = cls(**char_json)

        except KeyError as e:
            print(e)
            return None
        return char

    @classmethod
    def from_tibiadata(cls, content):
        """Builds a character object from a TibiaData character response"""
        try:
            json_content = json.loads(content)
        except json.JSONDecodeError:
            return None
        character = json_content["characters"]
        character_data = character["data"]
        char = cls()
        if "error" in character:
            return None
        try:
            char.name = character_data["name"]
            char.world = character_data["world"]
            char.level = character_data["level"]
            char.achievement_points = character_data["achievement_points"]
            char.sex = character_data["sex"]
            char.vocation = character_data["vocation"]
            char.residence = character_data["residence"]
            char.account_status = character_data["account_status"]
        except KeyError:
            return None
        char.former_names = character_data.get("former_names", [])
        if "deleted" in character_data:
            char.deletion_date = parse_tibiadata_datetime(character_data["deleted"])
        char.married_to = character_data.get("married_to")
        char.former_world = character_data.get("former_world")
        if "guild" in character_data:
            char.guild_membership = {"rank": character_data["guild"]["rank"], "guild": character_data["guild"]["name"]}
        if "house" in character_data:
            house = character_data["house"]
            paid_until_date = parse_tibiadata_date(house["paid"])
            char.house = CharacterHouse(house["houseid"], house["name"], house["town"], char.name, paid_until_date)
        char.comment = character_data.get("comment")
        if len(character_data["last_login"]) > 0:
            char.last_login = parse_tibiadata_datetime(character_data["last_login"][0])
        for achievement in character["achievements"]:
            char.achievements.append({"grade": achievement["stars"], "name": achievement["name"]})

        cls._parse_deaths_tibiadata(char, character.get("deaths", []))

        for other_char in character["other_characters"]:
            char.other_characters.append(OtherCharacter(other_char["name"], other_char["world"],
                                                        other_char["status"] == "online",
                                                        other_char["status"] == "deleted"))

        if character["account_information"]:
            char.account_information = {}
            for key, value in character["account_information"].items():
                if key == "created":
                    value = parse_tibiadata_datetime(value)
                char.account_information[key] = value

        return char

    @classmethod
    def _parse_deaths_tibiadata(cls, char, deaths):
        for death in deaths:
            level = death["level"]
            death_time = parse_tibiadata_datetime(death["date"])
            m = death_reason.search(death["reason"])
            killers_str = []
            assists_str = []
            killers = []
            assists = []
            involved = [i["name"] for i in death["involved"]]
            if m and m.group("killers"):
                killers_str = [k.strip() for k in cls._split_list(m.group("killers").strip())]
            if m and m.group("assists"):
                assists_str = [a.strip() for a in cls._split_list(m.group("assists").strip())]
            for killer in killers_str:
                killers.append(Killer(killer, killer in involved))
            for assist in assists_str:
                assists.append(Killer(assist, assist in involved))
            char.deaths.append(Death(char.name, level, time=death_time, killers=killers, assists=assists))


class Death(abc.Serializable):
    """
    Represents a death by a character

    Attributes
    -----------
    name: :class:`str`
        The name of the character this death belongs to.
    level: :class:`int`
        The level at which the death occurred.
    killers: List[:class:`Killer`]
        A list of all the killers involved.
    assists: List[:class:`Killer`]
        A list of characters that were involved, without dealing damage.
    time: :class:`datetime.datetime`
        The time at which the death occurred.
    """
    __slots__ = ("level", "killers", "time", "assists", "name")

    def __init__(self, name=None, level=0, **kwargs):
        self.name = name
        self.level = level
        self.killers = kwargs.get("killers", [])
        if self.killers and isinstance(self.killers[0], dict):
            self.killers = [Killer(**k) for k in self.killers]
        self.assists = kwargs.get("assists", [])
        if self.assists and isinstance(self.assists[0], dict):
            self.assists = [Killer(**k) for k in self.assists]
        time = kwargs.get("time")
        if isinstance(time, datetime.datetime):
            self.time = time
        elif isinstance(time, str):
            self.time = parse_tibia_datetime(time)
        else:
            self.time = None

    def __repr__(self):
        attributes = ""
        for attr in self.__slots__:
            if attr in ["name", "level"]:
                continue
            v = getattr(self, attr)
            if isinstance(v, int) and v == 0 and not isinstance(v, bool):
                continue
            if isinstance(v, list) and len(v) == 0:
                continue
            if v is None:
                continue
            attributes += ",%s=%r" % (attr, v)
        return "{0.__class__.__name__}({0.name!r},{0.level!r}{1})".format(self, attributes)

    @property
    def killer(self):
        """Optional[:class:`Killer`]: The first killer in the list.

        This is usually the killer that gave the killing blow."""
        return self.killers[0] if self.killers else None

    @property
    def by_player(self):
        """:class:`bool`: Whether the kill involves other characters."""
        return any([k.player and self.name != k.name for k in self.killers])


class Killer(abc.Serializable):
    """
    Represents a killer.

    A killer can be:

    a) Another character.
    b) A creature.
    c) A creature summoned by a character.

    Attributes
    -----------
    name: :class:`str`
        The name of the killer.
    player: :class:`bool`
        Whether the killer is a player or not.
    summon: Optional[:class:`str`]
        The name of the summoned creature, if applicable.
    """
    __slots__ = ("name", "player", "summon")

    def __init__(self, name=None, player=False, summon=None):
        self.name = name
        self.player = player
        self.summon = summon

    def __repr__(self):
        attributes = ""
        for attr in self.__slots__:
            if attr in ["name"]:
                continue
            v = getattr(self, attr)
            if isinstance(v, int) and v == 0 and not isinstance(v, bool):
                continue
            if isinstance(v, list) and len(v) == 0:
                continue
            if v is None:
                continue
            attributes += ",%s=%r" % (attr, v)
        return "{0.__class__.__name__}({0.name!r}{1})".format(self, attributes)

    @property
    def url(self):
        """
        Optional[:class:`str`]: The URL of the character’s information page on Tibia.com, if applicable.
        """
        return Character.get_url(self.name) if self.player else None


class OtherCharacter(abc.Character):
    """
    Represents other character's displayed in the Character's information page.

    Attributes
    ----------
    name: :class:`str`
        The name of the character.
    world: :class:`str`
        The name of the world.
    online: :class:`bool`
        Whether the character is online or not.
    deleted: :class:`bool`
        Whether the character is scheduled for deletion or not.
    """
    __slots__ = ("world", "online", "deleted")

    def __init__(self, name=None, world=None, online=False, deleted=False):
        self.name = name
        self.world = world
        self.online = online
        self.deleted = deleted


class OnlineCharacter(abc.Character):
    """Representes an online character."""
    __slots__ = ("name", "world", "vocation", "level")

    def __init__(self, name, world, level, vocation):
        self.name = name
        self.world = world
        self.level = int(level)
        self.vocation = vocation
