import abc
import datetime
import json
import urllib.parse
from collections import OrderedDict
from enum import Enum

from tibiapy.enums import HouseType, HouseStatus, HouseOrder
from tibiapy.utils import get_tibia_url

CHARACTER_URL_TIBIADATA = "https://api.tibiadata.com/v2/characters/%s.json"
HOUSE_URL_TIBIADATA = "https://api.tibiadata.com/v2/house/%s/%d.json"
HOUSE_LIST_URL_TIBIADATA = "https://api.tibiadata.com/v2/houses/%s/%s/%s.json"
GUILD_URL_TIBIADATA = "https://api.tibiadata.com/v2/guild/%s.json"
GUILD_LIST_URL_TIBIADATA = "https://api.tibiadata.com/v2/guilds/%s.json"
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

    def to_json(self, *, indent=None, sort_keys=False):
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

    def __repr__(self):
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
        return get_tibia_url("community", "characters", name=name)

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
        return CHARACTER_URL_TIBIADATA % urllib.parse.quote(name)


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
        return get_tibia_url("community", "guilds", page="view", GuildName=name)

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
        return GUILD_URL_TIBIADATA % urllib.parse.quote(name)

    @classmethod
    def get_world_list_url(cls, world):
        """Gets the Tibia.com URL for the guild section of a specific world.

        Parameters
        ----------
        world: :class:`str`
            The name of the world.

        Returns
        -------
        :class:`str`
            The URL to the guild's page
        """
        return get_tibia_url("community", "guilds", world=world)

    @classmethod
    def get_world_list_url_tibiadata(cls, world):
        """Gets the TibiaData.com URL for the guild list of a specific world.

        Parameters
        ----------
        world: :class:`str`
            The name of the world.

        Returns
        -------
        :class:`str`
            The URL to the guild's page.
        """
        return GUILD_LIST_URL_TIBIADATA % urllib.parse.quote(world.title().encode('iso-8859-1'))


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
        The name of the world the house belongs to.
    status: :class:`HouseStatus`
        The current status of the house.
    type: :class:`HouseType`
        The type of the house.
    """
    __slots__ = ("name", "world", "status", "type")

    def __repr__(self):
        return "<{0.__class__.__name__} name={0.name!r} world={0.world!r} status={0.status!r} type={0.type!r}>"\
            .format(self,)

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
        return get_tibia_url("community", "houses", page="view", houseid=house_id, world=world)

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
        return HOUSE_URL_TIBIADATA % (world, house_id)

    @classmethod
    def get_list_url(cls, world, town, house_type: HouseType = HouseType.HOUSE, status: HouseStatus = None,
                     order=HouseOrder.NAME):
        """
        Gets the URL to the house list on Tibia.com with the specified parameters.

        Parameters
        ----------
        world: :class:`str`
            The name of the world.
        town: :class:`str`
            The name of the town.
        house_type: :class:`HouseType`
            Whether to search for houses or guildhalls.
        status: :class:`HouseStatus`, optional
            The house status to filter results. By default no filters will be applied.
        order: :class:`HouseOrder`, optional
            The ordering to use for the results. By default they are sorted by name.

        Returns
        -------
        :class:`str`
            The URL to the list matching the parameters.
        """
        house_type = "%ss" % house_type.value
        status = "" if status is None else status.value
        return get_tibia_url("community", "houses", world=world, town=town, type=house_type, status=status,
                             order=order.value)

    @classmethod
    def get_list_url_tibiadata(cls, world, town, house_type: HouseType = HouseType.HOUSE):
        """
        Gets the URL to the house list on Tibia.com with the specified parameters.

        Parameters
        ----------
        world: :class:`str`
            The name of the world.
        town: :class:`str`
            The name of the town.
        house_type: :class:`HouseType`
            Whether to search for houses or guildhalls.

        Returns
        -------
        :class:`str`
            The URL to the list matching the parameters.
        """
        house_type = "%ss" % house_type.value
        return HOUSE_LIST_URL_TIBIADATA % (urllib.parse.quote(world), urllib.parse.quote(town), house_type)


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
        The name of the world the house belongs to.
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


class BaseNews(Serializable, metaclass=abc.ABCMeta):
    """Base class for all news classes

    Implements the :py:attr:`id` attribute and common properties.

    The following implement this class:

    - :class:`.News`
    - :class:`.ListedNews`

    Attributes
    ----------
    id: :class:`int`
        The internal ID of the news entry.
    title: :class:`str`
        The title of the news entry.
    category: :class:`.NewsCategory`
        The category this belongs to.
    category_icon: :class:`str`
        The URL of the icon corresponding to the category.
    date: :class:`datetime.date`
        The date when the news were published.
    """
    __slots__ = (
        "id",
        "title",
        "category",
        "category_icon",
        "date",
    )

    def __eq__(self, o: object) -> bool:
        """Two news articles are considered equal if their names or ids are equal."""
        if isinstance(o, self.__class__):
            return self.id == o.id
        return False

    @property
    def url(self):
        """:class:`str`: The URL to the Tibia.com page of the news entry."""
        return self.get_url(self.id)

    @classmethod
    def get_url(cls, news_id):
        """Gets the Tibia.com URL for a news entry by its id.

        Parameters
        ------------
        news_id: :class:`int`
            The id of the news entry.

        Returns
        --------
        :class:`str`
            The URL to the news' page"""
        return get_tibia_url("news", "newsarchive", id=news_id)

    @classmethod
    def get_list_url(cls):
        """Gets the URL to Tibia.com's news archive page.

        Notes
        -----
        It is not possible to perform a search using query parameters.
        News searches can only be performed using POST requests sending the parameters as form-data.

        Returns
        -------
        :class:`str`
            The URL to the news archive page on Tibia.com.
        """
        return get_tibia_url("news", "newsarchive")


class BaseTournament(Serializable, metaclass=abc.ABCMeta):
    """Base class for tournament classes.

    Attributes
    ----------
    title: :class:`str`
        The tournament's title.
    cycle: :class:`int`
        The tournament's cycle.
    """
    __slots__ = (
        "title",
        "cycle",
    )

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.title.lower() == other.title.lower()
        return False

    @property
    def url(self):
        """:class:`str`: The URL to the tournament's information page."""
        return self.get_url(self.cycle)

    @classmethod
    def get_url(cls, tournament_cycle):
        """Gets the URL to a tournament's information page if its cycle is provided,
        otherwise it shows the current tournament.

        Parameters
        ----------
        tournament_cycle: :class:`int`
            The tournament's cycle.

        Returns
        -------
        :class:`str`
            The URL to the specified tournament.
        """
        params = None
        if tournament_cycle:
            params = {
                "tournamentcycle": tournament_cycle,
                "action": "archive",
            }
        return get_tibia_url("community", "tournament", **params)


class BaseWorld(Serializable, metaclass=abc.ABCMeta):
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
        Whether the server is currently protected with BattlEye or not.
    battleye_date: :class:`datetime.date`
        The date when BattlEye was added to this world.
        If this is ``None`` and the world is protected, it means the world was protected from the beginning.
    experimental: :class:`bool`
        Whether the world is experimental or not.
    tournament_world_type: :class:`TournamentWorldType`
        The type of tournament world. ``None`` if this is not a tournament world.
    premium_only: :class:`bool`
        Whether only premium account players are allowed to play in this server.
    """
    __slots__ = (
        "name",
        "status",
        "location",
        "online_count",
        "pvp_type",
        "battleye_protected",
        "battleye_date",
        "experimental",
        "premium_only",
        "tournament_world_type",
        "transfer_type"
    )

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
        return get_tibia_url("community", "worlds", world=name.title())

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
