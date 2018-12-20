import abc
import datetime
import json
import urllib.parse
from collections import OrderedDict
from enum import Enum

CHARACTER_URL = "https://www.tibia.com/community/?subtopic=characters&name=%s"
CHARACTER_URL_TIBIADATA = "https://api.tibiadata.com/v2/characters/%s.json"
URL_HOUSE = "https://www.tibia.com/community/?subtopic=houses&page=view&houseid=%d&world=%s"
URL_HOUSE_TIBIADATA = "https://api.tibiadata.com/v2/house/%s/%d.json"
GUILD_URL = "https://www.tibia.com/community/?subtopic=guilds&page=view&GuildName=%s"
GUILD_URL_TIBIADATA = "https://api.tibiadata.com/v2/guild/%s.json"
WORLD_URL = "https://www.tibia.com/community/?subtopic=worlds&world=%s"
WORLD_URL_TIBIADATA = "https://api.tibiadata.com/v2/world/%s.json"


class Serializable:
    """Contains methods to make a class convertible to JSON.

    .. note::
        | There's no way to convert JSON strings back to their original object.
        | Attempting to do so may result in data loss.
    """
    @classmethod
    def __slots_inherited__(cls):
        slots = []
        for base in cls.__bases__:
            try:
                # noinspection PyUnresolvedReferences
                slots.extend(base.__slots_inherited__())
            except AttributeError:
                continue
        slots.extend(getattr(cls, "__slots__", []))
        return tuple(OrderedDict.fromkeys(slots))

    def keys(self):
        return list(self.__slots_inherited__())

    def __getitem__(self, item):
        if item in self.keys():
            try:
                return getattr(self, item)
            except AttributeError:
                return None
        else:
            raise KeyError(item)

    def __setitem__(self, key, value):
        if key in self.keys():
            setattr(self, key, value)
        else:
            raise KeyError(key)

    @staticmethod
    def _try_dict(obj):
        try:
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            if isinstance(obj, Enum):
                return obj.value
            return {k: v for k, v in dict(obj).items() if v is not None}
        except TypeError:
            return str(obj)

    def to_json(self, *, indent=None, sort_keys = False):
        """Gets the object's JSON representation.

        Parameters
        ----------
        indent: :class:`int`, optional
            Number of spaces used as indentation, ``None`` will return the shortest possible string.
        sort_keys: :class:`bool`, optional
            Whether keys should be sorted alphabetically or preserve the order defined by the object.

        Returns
        -------
        :class:`str`
            JSON representation of the object.
        """
        return json.dumps({k: v for k, v in dict(self).items() if v is not None}, indent=indent, sort_keys=sort_keys,
                          default=self._try_dict)


class BaseCharacter(Serializable, metaclass=abc.ABCMeta):
    """Base class for all character classes.

    Implements common properties methods for characters.

    The following implement this class:

    - :class:`.Character`
    - :class:`.GuildInvite`
    - :class:`.GuildMember`
    - :class:`.OnlineCharacter`
    - :class:`.OtherCharacter`

    Attributes
    ----------
    name: :class:`str`
        The name of the character.
    """
    __slots__ = ("name", )

    def __eq__(self, o: object) -> bool:
        """Two characters are considered equal if their names are equal."""
        if isinstance(o, self.__class__):
            return self.name.lower() == o.name.lower()
        return False

    def __repr__(self) -> str:
        return "<{0.__class__.__name__} name={0.name!r}>".format(self,)

    @property
    def url(self):
        """
        :class:`str`: The URL of the character's information page on Tibia.com
        """
        return self.get_url(self.name)

    @property
    def url_tibiadata(self):
        """
        :class:`str`: The URL of the character's information on TibiaData.com.
        """
        return self.get_url_tibiadata(self.name)

    @classmethod
    def get_url(cls, name):
        """Gets the Tibia.com URL for a given character name.

        Parameters
        ------------
        name: :class:`str`
            The name of the character.

        Returns
        --------
        :class:`str`
            The URL to the character's page."""
        return CHARACTER_URL % urllib.parse.quote(name.encode('iso-8859-1'))

    @classmethod
    def get_url_tibiadata(cls, name):
        """Gets the TibiaData.com URL for a given character name.

        Parameters
        ------------
        name: :class:`str`
            The name of the character.

        Returns
        --------
        :class:`str`
            The URL to the character's page on TibiaData.com."""
        return CHARACTER_URL_TIBIADATA % urllib.parse.quote(name.encode('iso-8859-1'))


class BaseGuild(Serializable, metaclass=abc.ABCMeta):
    """Base class for Guild classes.

    The following implement this class:

    - :class:`.Guild`
    - :class:`.GuildMembership`

    Attributes
    ----------
    name: :class:`str`
        The name of the guild.
    """
    __slots__ = ("name",)

    def __repr__(self):
        return "<{0.__class__.__name__} name={0.name!r}>".format(self)

    @property
    def url(self):
        """:class:`str`: The URL to the guild's information page on Tibia.com."""
        return self.get_url(self.name)

    @property
    def url_tibiadata(self):
        """:class:`str`: The URL to the guild on TibiaData.com."""
        return self.get_url_tibiadata(self.name)

    @classmethod
    def get_url(cls, name):
        """Gets the Tibia.com URL for a given guild name.

        Parameters
        ------------
        name: :class:`str`
            The name of the guild.

        Returns
        --------
        :class:`str`
            The URL to the guild's page"""
        return GUILD_URL % urllib.parse.quote(name.encode('iso-8859-1'))

    @classmethod
    def get_url_tibiadata(cls, name):
        """Gets the TibiaData.com URL for a given guild name.

        Parameters
        ------------
        name: :class:`str`
            The name of the guild.

        Returns
        --------
        :class:`str`
            The URL to the guild's page on TibiaData.com."""
        return GUILD_URL_TIBIADATA % urllib.parse.quote(name.encode('iso-8859-1'))


class BaseHouse(Serializable, metaclass=abc.ABCMeta):
    """Base class for all house classes

    The following implement this class:

    - :class:`.abc.BaseHouseWithId`
    - :class:`.GuildHouse`

    Attributes
    ----------
    name: :class:`str`
        The name of the house.
    world: :class:`str`
        The name of the world where the house is.
    status: :class:`HouseStatus`
        The current status of the house.
    type: :class:`HouseType`
        The type of the house.
    """
    __slots__ = ("name", "world", "status", "type")

    def __eq__(self, o: object) -> bool:
        """Two houses are considered equal if their names are equal."""
        if isinstance(o, self.__class__):
            return self.name.lower() == o.name.lower()
        return False

    @classmethod
    def get_url(cls, house_id, world):
        """ Gets the Tibia.com URL for a house with the given id and world.

        Parameters
        ----------
        house_id: :class:`int`
            The internal id of the house.
        world: :class:`str`
            The world of the house.

        Returns
        -------
        The URL to the house in Tibia.com
        """
        return URL_HOUSE % (house_id, world)

    @classmethod
    def get_url_tibiadata(cls, house_id, world):
        """ Gets the TibiaData.com URL for a house with the given id and world.

        Parameters
        ----------
        house_id: :class:`int`
            The internal id of the house.
        world: :class:`str`
            The world of the house.

        Returns
        -------
        The URL to the house in TibiaData.com
        """
        return URL_HOUSE_TIBIADATA % (world, house_id)


class BaseHouseWithId(BaseHouse):
    """A derivative of :class:`BaseHouse`

    Implements the :py:attr:`id` attribute and dependant functions and properties.

    The following implement this class:

    - :class:`.House`
    - :class:`.CharacterHouse`

    Attributes
    ----------
    id: :class:`int`
        The internal ID of the house. This is used on the website to identify houses.
    name: :class:`str`
        The name of the house.
    world: :class:`str`
        The name of the world where the house is.
    status: :class:`HouseStatus`
        The current status of the house.
    type: :class:`HouseType`
        The type of the house.
    """
    __slots__ = ("id",)

    def __eq__(self, o: object) -> bool:
        """Two houses are considered equal if their names or ids are equal."""
        if isinstance(o, self.__class__):
            return self.name.lower() == o.name.lower() or self.id == o.id
        return False

    @property
    def url(self):
        """:class:`str`: The URL to the Tibia.com page of the house."""
        return self.get_url(self.id, self.world) if self.id and self.world else None

    @property
    def url_tibiadata(self):
        """:class:`str`: The URL to the TibiaData.com page of the house."""
        return self.get_url_tibiadata(self.id, self.world) if self.id and self.world else None


class BaseWorld(Serializable):
    """Base class for all World classes.

    The following implement this class:

    - :class:`.ListedWorld`
    - :class:`.World`

    Attributes
    ----------
    name: :class:`str`
        The name of the world.
    status: :class:`str`
        The current status of the world.
    online_count: :class:`int`
        The number of currently online players in the world.
    location: :class:`WorldLocation`
        The physical location of the game servers.
    pvp_type: :class:`PvpType`
        The type of PvP in the world.
    transfer_type: :class:`TransferType`
        The type of transfer restrictions this world has.
    battleye_protected: :class:`bool`
        Whether the server is currently protected with battleye or not.
    battleye_date: :class:`datetime.date`
        The date where battleye was added to this world.
        If this is ``None`` and the world is protected, it means the world was protected from the beginning.
    experimental: :class:`bool`
        Whether the world is experimental or not.
    premium_only: :class:`bool`
        Whether only premium account players are allowed to play in this server.
    """
    __slots__ = ("name", "status", "location", "online_count", "pvp_type", "battleye_protected", "battleye_date",
                 "experimental", "premium_only", "transfer_type")

    def __repr__(self):
        return "<{0.__class__.__name__} name={0.name!r} location={0.location!r} pvp_type={0.pvp_type!r}>".format(self)

    @property
    def url(self):
        """:class:`str`: URL to the world's information page on Tibia.com."""
        return self.get_url(self.name)

    @property
    def url_tibiadata(self):
        """:class:`str`: URL to the world's information page on TibiaData.com."""
        return self.get_url_tibiadata(self.name)

    @classmethod
    def get_url(cls, name):
        """Gets the URL to the World's information page on Tibia.com.

        Parameters
        ----------
        name: :class:`str`
            The name of the world.

        Returns
        -------
        :class:`str`
            The URL to the world's information page.
        """
        return WORLD_URL % name.title()

    @classmethod
    def get_url_tibiadata(cls, name):
        """Gets the URL to the World's information page on TibiaData.com.

        Parameters
        ----------
        name: :class:`str`
            The name of the world.

        Returns
        -------
        :class:`str`
            The URL to the world's information page on TibiaData.com.
        """
        return WORLD_URL_TIBIADATA % name.title()