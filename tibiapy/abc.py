import abc
import datetime
import enum
import json
from collections import OrderedDict

from tibiapy.enums import HouseOrder, HouseStatus, HouseType
from tibiapy.utils import get_tibia_url


class Serializable:
    """Contains methods to make a class convertible to JSON.

    Only attributes defined in ``__slots__`` will be serialized.

    .. note::
        | There's no way to convert JSON strings back to their original object.
        | Attempting to do so may result in data loss.
    """

    _serializable_properties = ()
    """:class:`tuple` of :class:`str`: Additional properties to serialize."""

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
        slots.extend(getattr(cls, "_serializable_properties", []))
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
            if isinstance(obj, datetime.timedelta):
                return obj.total_seconds()
            if isinstance(obj, enum.Flag):
                return [str(i) for i in obj]
            if isinstance(obj, enum.Enum):
                return str(obj)
            return {k: v for k, v in dict(obj).items() if v is not None}
        except TypeError:
            return str(obj)

    def to_json(self, *, indent=None, sort_keys=False):
        """Gets the object's JSON representation.

        Parameters
        ----------
        indent: :class:`int`, optional
            Number of spaces used as indentation, :obj:`None` will return the shortest possible string.
        sort_keys: :class:`bool`, optional
            Whether keys should be sorted alphabetically or preserve the order defined by the object.

        Returns
        -------
        :class:`str`
            JSON representation of the object.
        """
        return json.dumps({k: v for k, v in dict(self).items() if v is not None}, indent=indent, sort_keys=sort_keys,
                          default=self._try_dict)


class BaseAnnouncement(metaclass=abc.ABCMeta):
    """Base class for all announcement classes.

    Implement common properties and methods for announcements.

    The following implement this class:

    - :class:`.ForumAnnouncement`
    - :class:`.ListedAnnouncement`

    Attributes
    ----------
    announcement_id: :class:`int`
        The ID of the announcement.
    """

    __slots__ = ("announcement_id",)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return other.announcement_id == self.announcement_id
        return False

    @property
    def url(self):
        """:class:`str` Gets the URL to this announcement."""
        return self.get_url(self.announcement_id)

    @classmethod
    def get_url(cls, announcement_id):
        """Gets the URL to an announcement with a given ID.

        Parameters
        ----------
        announcement_id: :class:`int`
            The ID of the announcement

        Returns
        -------
        :class:`str`
            The URL of the announcement.
        """
        return get_tibia_url("forum", None, action="announcement", announcementid=announcement_id)


class BaseBoard(metaclass=abc.ABCMeta):
    """Base class for all board classes.

    Implements common properties and methods for boards.

    The following implement this class:

    - :class:`.ForumBoard`
    - :class:`.ListedBoard`

    Attributes
    ----------
    board_id: :class:`int`
        The ID of the board.
    """

    __slots__ = ("board_id",)

    def __eq__(self, o: object) -> bool:
        """Two characters are considered equal if their names are equal."""
        if isinstance(o, self.__class__):
            return self.board_id == o.board_id
        return False

    def __repr__(self):
        return "<{0.__class__.__name__} name={0.name!r}>".format(self, )

    @property
    def url(self):
        """:class:`str`: The URL of this board."""
        return self.get_url(self.board_id)

    @classmethod
    def get_url(cls, board_id, page=1, age=30):
        """Gets the Tibia.com URL to a board with a given id.

        Parameters
        ----------
        board_id: :class:`int`
            The ID of the board.
        page: :class:`int`
            The page to go to.
        age: :class:`int`
            The age in days of the threads to display.

        Returns
        -------
        :class:`str`
            The URL to the board.
        """
        return get_tibia_url("forum", None, action="board", boardid=board_id, pagenumber=page, threadage=age)

    @classmethod
    def get_world_boards_url(cls):
        """Gets the URL to the World Boards section in Tibia.com
        
        Returns
        -------
        :class:`str`:
            The URL to the World Boards.
        """
        return get_tibia_url("forum", "worldboards")

    @classmethod
    def get_trade_boards_url(cls):
        """Gets the URL to the Trade Boards section in Tibia.com

        Returns
        -------
        :class:`str`:
            The URL to the Trade Boards.
        """
        return get_tibia_url("forum", "tradeboards")

    @classmethod
    def get_community_boards_url(cls):
        """Gets the URL to the Community Boards section in Tibia.com

        Returns
        -------
        :class:`str`:
            The URL to the Community Boards.
        """
        return get_tibia_url("forum", "communityboards")

    @classmethod
    def get_support_boards_url(cls):
        """Gets the URL to the Support Boards section in Tibia.com

        Returns
        -------
        :class:`str`:
            The URL to the Support Boards.
        """
        return get_tibia_url("forum", "supportboards")


class BaseCharacter(metaclass=abc.ABCMeta):
    """Base class for all character classes.

    Implements common properties methods for characters.

    The following implement this class:

    - :class:`.Character`
    - :class:`.GuildInvite`
    - :class:`.GuildMember`
    - :class:`.HighscoresEntry`
    - :class:`.LeaderboardEntry`
    - :class:`.OnlineCharacter`
    - :class:`.OtherCharacter`
    - :class:`.ListedAuction`
    - :class:`.AuctionDetails`

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


class BaseGuild(metaclass=abc.ABCMeta):
    """Base class for Guild classes.

    The following implement this class:

    - :class:`.Guild`
    - :class:`.GuildMembership`
    - :class:`.ListedGuild`

    Attributes
    ----------
    name: :class:`str`
        The name of the guild.
    """
    __slots__ = ("name",)

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r}>"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        return False

    @property
    def url(self):
        """:class:`str`: The URL to the guild's information page on Tibia.com."""
        return self.get_url(self.name)

    @property
    def url_wars(self):
        """:class:`str` The URL to the guild's wars page on Tibia.com.

        .. versionadded:: 3.0.0"""
        return self.get_url_wars(self.name)

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
    def get_url_wars(cls, name):
        """Gets the Tibia.com URL for the guild wars of a guild with a given name.

        .. versionadded:: 3.0.0

        Parameters
        ------------
        name: :class:`str`
            The name of the guild.

        Returns
        --------
        :class:`str`
            The URL to the guild's wars page."""
        return get_tibia_url("community", "guilds", page="guildwars", action="view", GuildName=name)

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


class BaseHouse(metaclass=abc.ABCMeta):
    """Base class for all house classes

    The following implement this class:

    - :class:`.House`
    - :class:`.GuildHouse`
    - :class:`.CharacterHouse`
    - :class:`.ListedHouse`

    Attributes
    ----------
    name: :class:`str`
        The name of the house.
    """
    __slots__ = (
        "name",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r}>"

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
        return get_tibia_url("community", "houses", world=world, town=town, type=house_type, state=status,
                             order=order.value)


class BaseNews(metaclass=abc.ABCMeta):
    """Base class for all news classes

    Implements the :py:attr:`id` attribute and common properties.

    The following implement this class:

    - :class:`.News`
    - :class:`.ListedNews`

    Attributes
    ----------
    id: :class:`int`
        The internal ID of the news entry.
    """
    __slots__ = (
        "id",
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


class BasePost(metaclass=abc.ABCMeta):
    """Base classs for post classes.

    The following implement this class:

    - :class:`.CMPost`
    - :class:`.ForumPost`
    - :class:`.LastPost`

    Attributes
    ----------
    post_id: :class:`int`
        The internal ID of the post.
    """

    __slots__ = ("post_id",)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.post_id == other.post_id
        return False

    @property
    def url(self):
        """:class:`str`: Gets the URL to this specific post."""
        return self.get_url(self.post_id)

    @classmethod
    def get_url(cls, post_id):
        """Gets the URL to a specific post.

        Parameters
        ----------
        post_id: :class:`int`
            The ID of the desired post.

        Returns
        -------
        :class:`str`
            The URL to the post.
        """
        return get_tibia_url("forum", None, anchor=f"post{post_id}", action="thread", postid=post_id)


class BaseThread(metaclass=abc.ABCMeta):
    """Base class for thread classes.

    The following implement this class:

    - :class:`.ListedThread`
    - :class:`.ForumThread`

    Attributes
    ----------
    thread_id: :class:`int`
        The internal ID of the thread.
    """

    __slots__ = (
        "thread_id",
    )

    @property
    def url(self):
        """:class:`str`: The URL to the thread in Tibia.com."""
        return self.get_url(self.thread_id)

    @classmethod
    def get_url(cls, thread_id, page=1):
        """Gets the URL to a thread with a given id.

        Parameters
        ----------
        thread_id: :class:`int`
            The id of the desired thread.
        page: :class:`int`
            The desired page, by default 1.

        Returns
        -------
        :class:`str`
            The URL to the thread.
        """
        return get_tibia_url("forum", None, action="thread", threadid=thread_id, pagenumber=page)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.thread_id == other.thread_id
        return False


class BaseTournament(metaclass=abc.ABCMeta):
    """Base class for tournament classes.

    The following implement this class:

    - :class:`.ListedTournament`
    - :class:`.Tournament`

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
        """Two tournaments are considered the same when they have the same title or cycle."""
        if isinstance(other, self.__class__):
            return self.title.lower() == other.title.lower() or (self.cycle > 0 and self.cycle == other.cycle)
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


class BaseWorld(metaclass=abc.ABCMeta):
    """Base class for all World classes.

    The following implement this class:

    - :class:`.ListedWorld`
    - :class:`.World`

    Attributes
    ----------
    name: :class:`str`
        The name of the world.
    """
    __slots__ = (
        "name",
    )

    def __repr__(self):
        return "<{0.__class__.__name__} name={0.name!r} location={0.location!r} pvp_type={0.pvp_type!r}>".format(self)

    @property
    def url(self):
        """:class:`str`: URL to the world's information page on Tibia.com."""
        return self.get_url(self.name)

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


class HouseWithId:
    """Implements the :py:attr:`id` attribute and dependant functions and properties.

    Subclasses mut also implement :class:`.BaseHouse`"""

    def __eq__(self, o: object) -> bool:
        """Two houses are considered equal if their names or ids are equal."""
        if isinstance(o, self.__class__):
            return self.name.lower() == o.name.lower() or self.id == o.id
        return False

    @property
    def url(self):
        """:class:`str`: The URL to the Tibia.com page of the house."""
        return self.get_url(self.id, self.world) if self.id and self.world else None
