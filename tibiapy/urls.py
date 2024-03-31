"""Functions to generate urls to Tibia.com."""
from __future__ import annotations

import datetime
import urllib.parse
from typing import Optional, Set, TYPE_CHECKING, Tuple, Union

if TYPE_CHECKING:
    from tibiapy.enums import (BazaarType, HighscoresBattlEyeType, HighscoresCategory, HighscoresProfession, HouseOrder,
                               HouseStatus, HouseType, PvpTypeFilter, SpellGroup, SpellSorting, SpellType,
                               SpellVocationFilter)
    from tibiapy.models import AuctionFilters


def get_tibia_url(
        section: str,
        subtopic: str = None,
        *args: Tuple[str, Union[str, int]],
        anchor: str = None,
        test: bool = False,
        **kwargs: Union[str, int],
) -> str:
    """Build a URL to Tibia.com with the given parameters.

    Parameters
    ----------
    section: :class:`str`
        The desired section (e.g., community, abouttibia, manual, library)
    subtopic: :class:`str`, optional
        The desired subtopic (e.g., characters, guilds, houses, etc.)
    anchor: :class:`str`
        A link anchor to add to the link.
    args:
        A list of key-value pairs to add as query parameters.
        This allows passing multiple parameters with the same name.
    kwargs:
        Additional parameters to pass to the url as query parameters (e.g., name, world, houseid, etc.)
    test: :class:`bool`
        Whether to use the test website or not.

    Returns
    -------
    :class:`str`
        The generated Tibia.com URL.

    Examples
    --------
    >>> get_tibia_url("community", "houses", page="view", houseid=55302, world="Gladera")
    https://www.tibia.com/community/?subtopic=houses&page=view&houseid=55302&world=Gladera

    You can also build a dictionary and pass it like:

    >>> params = {'world': "Gladera"}
    >>> get_tibia_url("community", "worlds", **params)
    https://www.tibia.com/community/?subtopic=worlds&world=Gladera
    """
    base_url = "www.test.tibia.com" if test else "www.tibia.com"
    url = f"https://{base_url}/{section}/?"
    params = {"subtopic": subtopic} if subtopic else {}
    if kwargs:
        for key, value in kwargs.items():
            if isinstance(value, str):
                value = value.encode("iso-8859-1")

            if value is None:
                continue

            params[key] = value

    url += urllib.parse.urlencode(params)
    if args:
        url += "&"
        url += urllib.parse.urlencode(args)

    if anchor:
        url += f"#{anchor}"

    return url


def get_static_file_url(*path: str) -> str:
    """Build a URL to a static file in Tibia.com.

    Parameters
    ----------
    path:
        The path to the static file.

    Examples
    --------
    >>> get_static_file_url("images", "global", "content", "newsicon_community_big.gif")
    https://static.tibia.com/images/global/content/newsicon_community_big.gif
    """
    return urllib.parse.urljoin("https://static.tibia.com/", "/".join(path))


def get_character_url(name: str) -> str:
    """Get the URL to a character in Tibia.com.

    Parameters
    ----------
    name: :class:`str`
        The name of the character.

    Returns
    -------
    :class:`str`
        The URL to the character's page in Tibia.com.
    """
    return get_tibia_url("community", "characters", name=name)


def get_world_guilds_url(world: str) -> str:
    """Get the URL to the guild list of a specific world.

    Parameters
    ----------
    world: :class:`str`
        The name of the world.

    Returns
    -------
    :class:`str`
        The URL to the guild list's page in Tibia.com.
    """
    return get_tibia_url("community", "guilds", world=world)


def get_guild_url(name: str) -> str:
    """Get the URL to a guild's page.

    Parameters
    ----------
    name: :class:`str`
        The name of the guild.

    Returns
    -------
    :class:`str`
        The URL to the guild's page in Tibia.com.
    """
    return get_tibia_url("community", "guilds", page="view", GuildName=name)


def get_guild_wars_url(name: str) -> str:
    """Get the Tibia.com URL for the guild wars of a guild with a given name.

    Parameters
    ----------
    name: :class:`str`
        The name of the guild.

    Returns
    -------
    :class:`str`
        The URL to the guild's wars' page.
    """
    return get_tibia_url("community", "guilds", page="guildwars", action="view", GuildName=name)


def get_house_url(world: str, house_id: int) -> str:
    """Get the URL to a house's page in Tibia.com.

    Parameters
    ----------
    world: :class:`str`
        The world where the house is located.
    house_id: :class:`int`
        The ID of the house.

    Returns
    -------
    :class:`str`
        The URL to the house's page in Tibia.com.
    """
    return get_tibia_url("community", "houses", page="view", houseid=house_id, world=world)


def get_fansites_url() -> str:
    """Get the Tibia.com URL for the fansites section.

    Returns
    -------
    :class:`str`
        The URL to the fansites section.
    """
    return get_tibia_url("community", "fansites")


def get_world_overview_url() -> str:
    """Get the URL to world overview section in Tibia.com.

    Returns
    -------
    :class:`str`
        The URL to the world overview section in Tibia.com.
    """
    return get_tibia_url("community", "worlds")


def get_world_url(name: str) -> str:
    """Get the URL to the World's information page on Tibia.com.

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


def get_news_archive_url() -> str:
    """Get the URL to Tibia.com's news archive page.

    Notes
    -----
    It is not possible to perform a search using query parameters.
    News searches can only be performed using POST requests sending the parameters as form-data.

    Returns
    -------
    :class:`str`
        The URL to the news archive page.
    """
    return get_tibia_url("news", "newsarchive")


def get_news_url(news_id: int) -> str:
    """Get the URL to a news article.

    Parameters
    ----------
    news_id: :class:`int`
        The ID of the article.

    Returns
    -------
    :class:`str`
        The URL to the article's page on Tibia.com
    """
    return get_tibia_url("news", "newsarchive", id=news_id)


def get_forum_section_url(section_id: int) -> str:
    """Get the URL to a forum section in Tibia.com.

    Parameters
    ----------
    section_id: :class:`int`
        The ID of the section.

    Returns
    -------
    :class:`str`
        The URL to forum section.
    """
    return get_tibia_url("forum", action="main", sectionid=section_id)


def get_forum_section_url_by_name(section_name: str) -> str:
    """Get the URL to a forum section in Tibia.com by its name.

    Parameters
    ----------
    section_name: :class:`str`
        The name of the section.

    Returns
    -------
    :class:`str`
        The URL to forum section.
    """
    return get_tibia_url("forum", section_name)


def get_world_boards_url() -> str:
    """Get the URL to the World Boards section in Tibia.com.

    Returns
    -------
    :class:`str`:
        The URL to the World Boards.
    """
    return get_tibia_url("forum", "worldboards")


def get_trade_boards_url() -> str:
    """Get the URL to the Trade Boards section in Tibia.com.

    Returns
    -------
    :class:`str`:
        The URL to the Trade Boards.
    """
    return get_tibia_url("forum", "tradeboards")


def get_community_boards_url() -> str:
    """Get the URL to the Community Boards section in Tibia.com.

    Returns
    -------
    :class:`str`:
        The URL to the Community Boards.
    """
    return get_tibia_url("forum", "communityboards")


def get_support_boards_url() -> str:
    """Get the URL to the Support Boards section in Tibia.com.

    Returns
    -------
    :class:`str`:
        The URL to the Support Boards.
    """
    return get_tibia_url("forum", "supportboards")


def get_forum_board_url(board_id: int, page: int = 1, thread_age: int = None) -> str:
    """Get the URL to a forum board.

    Parameters
    ----------
    board_id: :class:`int`
        The ID of the board.
    page: :class:`int`
        The page to display.
    thread_age: :class:`int`
        The maximum age in days for the threads to be shown.

        ``-1`` means any age.

    Returns
    -------
    :class:`str`
        The URL to forum board.
    """
    return get_tibia_url("forum", None, action="board", boardid=board_id, pagenumber=page, threadage=thread_age)


def get_forum_announcement_url(announcement_id: int) -> str:
    """Get the URL to a forum announcement.

    Parameters
    ----------
    announcement_id: :class:`int`
        The ID of the announcement.

    Returns
    -------
    :class:`str`
        The URL to forum announcement.
    """
    return get_tibia_url("forum", None, action="announcement", announcementid=announcement_id)


def get_forum_thread_url(thread_id: int, page: int = 1) -> str:
    """Get the URL to a forum board.

    Parameters
    ----------
    thread_id: :class:`int`
        The ID of the thread.
    page: :class:`int`
        The page to display.

    Returns
    -------
    :class:`str`
        The URL to forum thread.
    """
    return get_tibia_url("forum", None, action="thread", threadid=thread_id, pagenumber=page)


def get_forum_post_url(post_id: int) -> str:
    """Get the URL to a specific post.

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


def get_highscores_url(
        world: str = None,
        category: HighscoresCategory = None,
        vocation: HighscoresProfession = None,
        page: int = 1,
        battleye_type: HighscoresBattlEyeType = None,
        pvp_types: Set[PvpTypeFilter] = None,
) -> str:
    """Get the Tibia.com URL of the highscores for the given parameters.

    Parameters
    ----------
    world:
        The game world of the desired highscores. If no world is passed, ALL worlds are shown.
    category:
        The desired highscores category.
    vocation:
        The vocation filter to apply. By default, all vocations will be shown.
    page:
        The page of highscores to show.
    battleye_type:
        The battleEye filters to use.
    pvp_types:
        The list of PvP types to filter the results for.

    Returns
    -------
        The URL to the Tibia.com highscores.
    """
    pvp_types = pvp_types or []
    pvp_params = [("worldtypes[]", p.value) for p in pvp_types]
    return get_tibia_url("community", "highscores", *pvp_params,
                         world=world,
                         category=category.value if category else None,
                         profession=vocation.value if vocation else None,
                         currentpage=page,
                         beprotection=battleye_type.value if battleye_type else None,
                         )


def get_kill_statistics_url(world: str) -> str:
    """Get the Tibia.com URL of the kill statistics of a world.

    Parameters
    ----------
    world: :class:`str`
        The game world of the desired kill statistics.

    Returns
    -------
    :class:`str`
        The URL to the Tibia.com kill statistics for this world.
    """
    return get_tibia_url("community", "killstatistics", world=world)


def get_event_schedule_url(month: int = None, year: int = None) -> str:
    """Get the URL to the Event Schedule or Event Calendar on Tibia.com.

    Notes
    -----
    If no parameters are passed, it will show the calendar for the current month and year.

    Tibia.com limits the dates that the calendar displays, passing a month and year far from the current ones may
    result in the response being for the current month and year instead.

    Parameters
    ----------
    month: :class:`int`, optional
        The desired month.
    year: :class:`int`, optional
        The desired year.

    Returns
    -------
    :class:`str`
        The URL to the calendar with the given parameters.
    """
    return get_tibia_url("news", "eventcalendar", calendarmonth=month, calendaryear=year)


def get_houses_section_url(world: str, town: str, house_type: HouseType, status: HouseStatus = None,
                           order: HouseOrder = None) -> str:
    """Get the URL to the house list on Tibia.com with the specified filters.

    Parameters
    ----------
    world: :class:`str`
        The world to search in.
    town: :class:`str`
        The town to show results for.
    house_type: :class:`HouseType`
        The type of houses to show.
    status: :class:`HouseStatus`
        The status of the houses to show.
    order: :class:`HouseOrder`
        The sorting parameter to use for the results.

    Returns
    -------
    :class:`str`
        The URL to the list matching the parameters.
    """
    params = {
        "world": world,
        "town": town,
        "type": house_type.plural if house_type else None,
        "state": status.value if status else None,
        "order": order.value if order else None,
    }
    return get_tibia_url("community", "houses", **{k: v for k, v in params.items() if v is not None})


def get_auction_url(auction_id: int) -> str:
    """Get the URL to the Tibia.com detail page of an auction with a given id.

    Parameters
    ----------
    auction_id: :class:`int`
        The ID of the auction.

    Returns
    -------
    :class:`str`
        The URL to the auction's detail page.
    """
    return get_tibia_url("charactertrade", "currentcharactertrades", page="details", auctionid=auction_id)


def get_bazaar_url(type: BazaarType, page: int = 1, filters: AuctionFilters = None) -> str:
    """Get the URL to the list of current auctions in Tibia.com.

    Parameters
    ----------
    type: :class:`BazaarType`
        The type of bazaar to show.
    page: :class:`int`
        The page to show the URL for.
    filters: :class:`AuctionFilters`
        The filtering criteria to use.

    Returns
    -------
    :class:`str`
        The URL to the current auctions section in Tibia.com
    """
    query_params = filters.query_params if filters else {}
    return get_tibia_url("charactertrade", type.subtopic, currentpage=page, **query_params)


def get_cm_post_archive_url(from_date: datetime.date, to_date: datetime.date, page: int = 1) -> str:
    """Get the URL to the CM Post Archive for the given date range.

    Parameters
    ----------
    from_date: :class: `datetime.date`
        The start date to display.
    to_date: :class: `datetime.date`
        The end date to display.
    page: :class:`int`
        The desired page to display.

    Returns
    -------
    :class:`str`
        The URL to the CM Post Archive

    Raises
    ------
    TypeError:
        Either of the dates is not an instance of :class:`datetime.date`
    ValueError:
        If ``start_date`` is more recent than ``end_date``.
    """
    if not isinstance(from_date, datetime.date):
        raise TypeError(f"start_date: expected datetime.date instance, {type(from_date)} found.")

    if not isinstance(to_date, datetime.date):
        raise TypeError(f"start_date: expected datetime.date instance, {type(from_date)} found.")

    if to_date < from_date:
        raise ValueError("start_date can't be more recent than end_date.")

    if page < 1:
        raise ValueError("page must be 1 or greater.")

    return get_tibia_url("forum", "forum", action="cm_post_archive", startday=from_date.day,
                         startmonth=from_date.month, startyear=from_date.year, endday=to_date.day,
                         endmonth=to_date.month, endyear=to_date.year, currentpage=page)


def get_leaderboards_url(world: str, rotation_id: int = None, page: int = 1) -> str:
    """Get the URL to the leaderboards of a world.

    Parameters
    ----------
    world: :class:`str`
        The desired world.
    rotation_id: :class:`int`
        The ID of the desired rotation. If undefined, the current rotation is shown.
    page: :class:`int`
        The desired page. By default, the first page is returned.

    Returns
    -------
    :class:`str`
        The URL to the leaderboard with the desired parameters.

    Raises
    ------
    ValueError
        If the specified page is zer or less.
    """
    if page <= 0:
        raise ValueError("page must be 1 or greater")

    return get_tibia_url("community", "leaderboards", world=world, rotation=rotation_id, currentpage=page)


def get_creatures_section_url() -> str:
    """Get the URL to the Tibia.com library section.

    Returns
    -------
    :class:`str`:
        The URL to the Tibia.com library section.
    """
    return get_tibia_url("library", "creature")


def get_creature_url(identifier: str) -> str:
    """Get the URL to the creature's detail page on Tibia.com.

    Parameters
    ----------
    identifier: :class:`str`
        The race's internal name.

    Returns
    -------
    :class:`str`
        The URL to the detail page.
    """
    return get_tibia_url("library", "creatures", race=identifier)


def get_boostable_bosses_url() -> str:
    """Get the URL to the Tibia.com boostable bosses.

    Returns
    -------
    :class:`str`:
        The URL to the Tibia.com library section.
    """
    return get_tibia_url("library", "boostablebosses")


def _to_yes_no(value: Optional[bool]) -> Optional[str]:
    if value is None:
        return None

    return "yes" if value else "no"


def get_spells_section_url(
        vocation: SpellVocationFilter = None,
        group: SpellGroup = None,
        spell_type: SpellType = None,
        is_premium: bool = None,
        sort: SpellSorting = None,
) -> str:
    """Get the URL to the spells section with the desired filtering parameters.

    Parameters
    ----------
    vocation: :class:`SpellVocationFilter`, optional
        The vocation to filter in spells for.
    group: :class:`SpellGroup`, optional
        The spell's primary cooldown group.
    spell_type: :class:`SpellType`, optional
        The type of spells to show.
    is_premium: :class:`bool`, optional
        The type of premium requirement to filter. :obj:`None` means any premium requirement.
    sort: :class:`SpellSorting`, optional
        The field to sort spells by.

    Returns
    -------
    :class:`str`
        The URL to the spells section with the provided filtering parameters.
    """
    params = {
        "vocation": vocation.value if vocation else None,
        "group": group.value if group else None,
        "type": spell_type.value if spell_type else None,
        "sort": sort.value if sort else None,
        "premium": _to_yes_no(is_premium),
    }
    return get_tibia_url("library", "spells", **params)


def get_spell_url(identifier: str) -> str:
    """Get the URL to a spell in the Tibia.com spells section.

    Parameters
    ----------
    identifier: :class:`str`
        The identifier of the spell.

    Returns
    -------
    :class:`str`
        The URL to the spell.
    """
    return get_tibia_url("library", "spells", spell=identifier.lower())
