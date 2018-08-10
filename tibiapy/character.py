import json
import re
import urllib.parse
from typing import Optional

from bs4 import BeautifulSoup, SoupStrainer

from . import abc
from .const import CHARACTER_URL
from .utils import parse_tibia_datetime

deleted_regexp = re.compile(r'([^,]+), will be deleted at (.*)')
death_regexp = re.compile(r'Level (\d+) by ([^.]+)')
house_regexp = re.compile(r'paid until (.*)')
guild_regexp = re.compile(r'([\s\w]+)\sof the\s(.+)')


class Character(abc.Character):
    """Represents a Tibia character

    Attributes
    ---------------
    name: :class:`str`
        The name of the character.

    deletion_date: Optional[:class:`datetime.datetime`]
        The date where the character will be deleted.

    former_names: :class:`list`
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
        The character's current world

    former_world: Optional[:class:`str`]
        The previous world where the character was in.

    residence: :class:`str`
        The current hometown of the character.

    married_to: Optional[:class:`str`]
        The name of the character's spouse/husband.

    house: Optional[:class:`dict`]
        The house currently owned by the character.

    guild_membership: Optional[:class:`dict`]
        The guild the character is a member of. The dictionary contains a key for the rank and a key for the name.

    last_login: Optional[:class:`datetime.datetime`]
        The last time the character logged in.

    comment: Optional[:class:`str`]
        The displayed comment.

    account_status: :class:`str`
        Whether the character's account is Premium or Free.

    achievements: :class:`list` of :class:`dict`
        The achievement chosen to be displayed.

    deaths: :class:`list` of :class:`Death`
        The character's recent deaths.

    account_information: :class:`dict`
        The character's account information, if visible.

    other_characters: List[:class:`OtherCharacter`]
        Other characters in the same account, if visible.
    """
    __slots__ = ("former_names", "sex", "vocation", "level", "achievement_points", "world", "former_world", "residence",
                 "married_to", "house", "guild_membership", "last_login", "account_status", "comment", "achievements",
                 "deaths", "account_information", "other_characters", "deletion_date")

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def guild_name(self):
        """Optional[:class:`str`]: The name of the guild the character belongs to, or `None`."""
        return None if self.guild_membership is None else self.guild_membership["guild"]

    @property
    def guild_rank(self):
        """Optional[:class:`str`]: The character's rank in the guild they belong to, or `None`."""
        return None if self.guild_membership is None else self.guild_membership["rank"]

    @staticmethod
    def _parse(content):
        parsed_content = BeautifulSoup(content, 'html.parser', parse_only=SoupStrainer("div", class_="BoxContent"))
        tables = parsed_content.find_all('table', attrs={"width": "100%"})
        char = {}
        achievements = []
        deaths = []
        other_characters = []
        account_information = {}
        if len(tables) == 1:
            # This happens when an unsupported symbol was in the name.
            # Should I handle this as a separate case?
            return {}
        for table in tables:
            header = table.find('td')
            rows = table.find_all('tr')
            if "Could not find" in header.text:
                return {}
            if "Character Information" in header.text:
                for row in rows:
                    cols_raw = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols_raw]
                    if len(cols) != 2:
                        continue
                    field, value = cols
                    field = field.replace("\xa0", "_").replace(" ", "_").replace(":", "").lower()
                    value = value.replace("\xa0", " ")
                    # This is a special case cause we need to see the link
                    if field == "house":
                        house_text = value
                        paid_until = house_regexp.search(house_text).group(1)
                        house_link = cols_raw[1].find('a')
                        url = urllib.parse.urlparse(house_link["href"])
                        query = urllib.parse.parse_qs(url.query)
                        char["house"] = {
                            "town": query["town"][0],
                            "id": int(query["houseid"][0]),
                            "name": house_link.text.strip(),
                            "paid_until": paid_until
                        }
                        continue
                    char[field] = value
            elif "Achievements" in header.text:
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
            elif "Deaths" in header.text:
                for row in rows:
                    cols_raw = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols_raw]
                    if len(cols) != 2:
                        continue
                    death_time, death = cols
                    death_time = death_time.replace("\xa0", " ")
                    death_info = death_regexp.search(death)
                    if death_info:
                        level = death_info.group(1)
                        killer = death_info.group(2)
                    else:
                        continue
                    death_link = cols_raw[1].find('a')
                    death_player = False
                    if death_link:
                        death_player = True
                        killer = death_link.text.strip().replace("\xa0", " ")
                    try:
                        deaths.append({'time': death_time, 'level': int(level), 'killer': killer,
                                       'is_player': death_player})
                    except ValueError:
                        # Some pvp deaths have no level, so they are raising a ValueError, they will be ignored for now.
                        continue
            elif "Account Information" in header.text:
                for row in rows:
                    cols_raw = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols_raw]
                    if len(cols) != 2:
                        continue
                    field, value = cols
                    field = field.replace("\xa0", "_").replace(" ", "_").replace(":", "").lower()
                    value = value.replace("\xa0", " ")
                    account_information[field] = value
            elif "Characters" in header.text:
                for row in rows:
                    cols_raw = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols_raw]
                    if len(cols) != 5:
                        continue
                    _name, world, status, __, __ = cols
                    _name = _name.replace("\xa0", " ").split(". ")[1]
                    other_characters.append(
                        {'name': _name, 'world': world, 'online': status == "online", 'deleted': status == "deleted"})
        # Converting values to int
        m = deleted_regexp.match(char["name"])
        if m:
            char["name"] = m.group(1)
            char["deletion_date"] = m.group(2)
        char["deletion_date"] = None
        char["level"] = int(char["level"])
        char["achievement_points"] = int(char["achievement_points"])
        if "house" not in char:
            char["house"] = None
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
        char["achievements"] = achievements
        char["deaths"] = deaths
        char["account_information"] = account_information
        char["other_characters"] = other_characters
        return char

    @staticmethod
    def parse_to_json(content, indent=None):
        """Static method that creates a JSON string from the html content of the character's page.

        Parameters
        -------------
        content: str
            The HTML content of the page.
        indent: int
            The number of spaces to indent the output with.

        Returns
        ------------
        :class:`str`
            A string in JSON format."""
        char_dict = Character._parse(content)
        return json.dumps(char_dict, indent=indent)

    @staticmethod
    def from_content(content) -> Optional['Character']:
        """Creates an instance of the class from the html content of the character's page.


        Parameters
        -----------
        content: str
            The HTML content of the page.

        Returns
        ----------
        Optional[:class:`Character`]
            The character contained in the page, or None if the character doesn't exist.
        """
        char = Character._parse(content)
        if not char:
            return None
        try:
            character = Character()
            character.name = char["name"]
            if char["deletion_date"]:
                character.deletion_date = parse_tibia_datetime(char["deletion_date"])
            else:
                character.deletion_date = None
            character.former_names = char["former_names"]
            character.sex = char["sex"]
            character.vocation = char["vocation"]
            character.level = char["level"]
            character.achievement_points = char["achievement_points"]
            character.world = char["world"]
            character.former_world = char.get("former_world")
            character.residence = char["residence"]
            character.house = char["house"]
            character.married_to = char["married_to"]
            character.comment = char.get("comment")
            character.account_status = char["account_status"]
            character.guild_membership = char["guild_membership"]

            character.other_characters = []
            if char["other_characters"]:
                for o_char in char["other_characters"]:
                    character.other_characters.append(OtherCharacter(o_char["name"], o_char["world"], o_char["online"],
                                                                     o_char["deleted"]))

            if "never" in char["last_login"]:
                character.last_login = None
            else:
                character.last_login = parse_tibia_datetime(char["last_login"])
            character.account_information = char["account_information"]
            character.deaths = []
            character.achievements = char["achievements"]
            for d in char["deaths"]:
                death = Death(d["level"], d["killer"], d["time"], d["is_player"])
                death.name = character.name
                character.deaths.append(death)
        except KeyError as e:
            print(e)
            return None

        return character

    @staticmethod
    def get_url(name):
        """Gets the Tibia.com URl for a given character name.

        Parameters
        ------------
        name: str
            The name of the character

        Returns
        --------
        str
            The URL to the character's page"""
        return CHARACTER_URL + urllib.parse.quote(name.encode('iso-8859-1'))

class Death:
    """
    Represents a death by a character

    Attributes
    -----------
    name: :class:`str`
        The name of the character this death belongs to.

    level: :class:`int`
        The level at which the level occurred.

    killer: :class:`str`
        The main killer.

    date: :class:`datetime.datetime`
        The time at which the death occurred.

    by_player: :class:`bool`
        True if the killer is a player, False otherwise.

    participants: :class:`list`
        List of all participants in the death.
    """
    __slots__ = ("name", "level", "killer", "date", "by_player", "participants")

    def __init__(self, level, killer, date, by_player, **kwargs):
        self.level = level
        self.killer = killer
        if date is not None:
            self.date = parse_tibia_datetime(date)
        else:
            self.date = date
        self.by_player = by_player
        self.participants = kwargs.get("participants", [])
        self.name = kwargs.get("name")


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

    def __init__(self, name, world, online = False, deleted = False):
        self.name = name
        self.world = world
        self.online = online
        self.deleted = deleted