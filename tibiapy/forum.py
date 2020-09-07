import datetime
import re
from typing import List, Optional

import bs4

from tibiapy import abc, errors, GuildMembership
from tibiapy.enums import ThreadStatus, Vocation
from tibiapy.utils import convert_line_breaks, get_tibia_url, parse_tibia_datetime, parse_tibia_forum_datetime, \
    parse_tibiacom_content, split_list, try_enum

__all__ = (
    'CMPost',
    'CMPostArchive',
    'ForumAnnouncement',
    'ForumBoard',
    'ForumEmoticon',
    'ForumPost',
    'ForumThread',
    'LastPost',
    'ListedAnnouncement',
    'ListedBoard',
    'ListedThread',
    'ForumAuthor',
)

section_id_regex = re.compile(r'sectionid=(\d+)')
board_id_regex = re.compile(r'boardid=(\d+)')
post_id_regex = re.compile(r'postid=(\d+)')
thread_id_regex = re.compile(r'threadid=(\d+)')
announcement_id_regex = re.compile(r'announcementid=(\d+)')
page_number_regex = re.compile(r'pagenumber=(\d+)')
timezone_regex = re.compile(r'times are (CEST?)')
filename_regex = re.compile(r'([\w_]+.gif)')
pages_regex = re.compile(r'\(Pages[^)]+\)')

author_info_regex = re.compile(r'Inhabitant of (\w+)\nVocation: ([\w\s]+)\nLevel: (\d+)')
author_posts_regex = re.compile(r'Posts: (\d+)')
guild_regexp = re.compile(r'([\s\w()]+)\sof the\s(.+)')
guild_title_regexp = re.compile(r'([^(]+)\s\(([^)]+)\)')
post_dates_regex = re.compile(r'(\d{2}\.\d{2}\.\d{4}\s\d{2}:\d{2}:\d{2})')
edited_by_regex = re.compile(r'Edited by (.*) on \d{2}')

signature_separator = "________________"


class CMPost(abc.BasePost, abc.Serializable):
    """Represents a CM Post entry.

    .. versionadded:: 3.0.0

    Attributes
    ----------
    post_id: :class:`int`
        The ID of the post.
    date: :class:`datetime.date`
        The date when the post was made.
    board: :class:`str`
        The name of the board where the post was made.
    thread_title: :class:`str`
        The title of the thread where the post is.
    """

    __slots__ = (
        "post_id",
        "date",
        "board",
        "thread_title",
    )

    def __init__(self, **kwargs):
        self.post_id: int = kwargs.get("post_id")
        self.date: datetime.datetime = kwargs.get("date")
        self.board: str = kwargs.get("board")
        self.thread_title: str = kwargs.get("thread_title")

    def __repr__(self):
        return f"<{self.__class__.__name__} post_id={self.post_id} date={self.date!r} " \
               f"thread_title={self.thread_title!r} board={self.board}>"


class CMPostArchive(abc.Serializable):
    """Represents the CM Post Archive.

    The CM Post Archive is a collection of posts made in the forum by community managers.

    .. versionadded:: 3.0.0

    Attributes
    ----------
    start_date: :class:`datetime.date`
        The start date of the displayed posts.
    end_date: :class:`datetime.date`
        The end date of the displayed posts.
    page: :class:`int`
        The currently displayed page.
    total_pages: :class:`int`
        The number of pages available.
    results_count: :class:`int`
        The total number of results available in the selected date range.
    posts: :class:`list` of :class:`CMPost`
        The list of posts for the selected range."""

    __slots__ = (
        "start_date",
        "end_date",
        "page",
        "total_pages",
        "results_count",
        "posts",
    )

    def __init__(self, **kwargs):
        self.start_date: datetime.date = kwargs.get("start_date")
        self.end_date: datetime.date = kwargs.get("end_date")
        self.page: int = kwargs.get("page", 1)
        self.total_pages: int = kwargs.get("total_pages", 1)
        self.results_count: int = kwargs.get("results_count", 0)
        self.posts: List[CMPost] = kwargs.get("posts", [])

    def __repr__(self):
        return f"<{self.__class__.__name__} start_date={self.start_date!r} end_date={self.end_date!r} " \
               f"result_count={self.results_count} page={self.page} total_pages={self.total_pages}>"

    # region Properties

    @property
    def url(self):
        """:class:`str`: The URL of the CM Post Archive with the current parameters."""
        return self.get_url(self.start_date, self.end_date, self.page)

    @property
    def previous_page_url(self):
        """:class:`str`: The URL to the previous page of the current CM Post Archive results, if there's any."""
        return self.get_page_url(self.page - 1) if self.page > 1 else None

    @property
    def next_page_url(self):
        """:class:`str`: The URL to the next page of the current CM Post Archive results, if there's any."""
        return self.get_page_url(self.page + 1) if self.page < self.total_pages else None

    # endregion

    # region Public Methods

    def get_page_url(self, page):
        """Gets the URL of the CM Post Archive at a specific page, with the current date parameters.

        Parameters
        ----------
        page: :class:`int`
            The desired page.

        Returns
        -------
        :class:`str`
            The URL to the desired page.
        """
        if page <= 0:
            raise ValueError("page must be 1 or greater")
        return self.get_url(self.start_date, self.end_date, page)

    @classmethod
    def get_url(cls, start_date, end_date, page=1):
        """Gets the URL to the CM Post Archive for the given date range.

        Parameters
        ----------
        start_date: :class: `datetime.date`
            The start date to display.
        end_date: :class: `datetime.date`
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
        if not isinstance(start_date, datetime.date):
            raise TypeError(f"start_date: expected datetime.date instance, {type(start_date)} found.")
        if not isinstance(end_date, datetime.date):
            raise TypeError(f"start_date: expected datetime.date instance, {type(start_date)} found.")
        if end_date < start_date:
            raise ValueError("start_date can't be more recent than end_date.")
        if page < 1:
            raise ValueError("page must be 1 or greater.")
        return get_tibia_url("forum", "forum", action="cm_post_archive", startday=start_date.day,
                             startmonth=start_date.month, startyear=start_date.year, endday=end_date.day,
                             endmonth=end_date.month, endyear=end_date.year, currentpage=page)

    @classmethod
    def from_content(cls, content):
        """Parses the content of the CM Post Archive page from Tibia.com

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the CM Post Archive in Tibia.com

        Returns
        -------
        :class:`CMPostArchive`
            The CM Post archive found in the page.

        Raises
        ------
        InvalidContent
            If content is not the HTML content of the CM Post Archive in Tibia.com
        """
        parsed_content = parse_tibiacom_content(content)

        form = parsed_content.find("form")
        try:
            start_month_selector, start_day_selector, start_year_selector, \
             end_month_selector, end_day_selector, end_year_selector = form.find_all("select")
            start_date = cls._get_selected_date(start_month_selector, start_day_selector, start_year_selector)
            end_date = cls._get_selected_date(end_month_selector, end_day_selector, end_year_selector)
        except (AttributeError, ValueError) as e:
            raise errors.InvalidContent("content does not belong to the CM Post Archive in Tibia.com", e)
        cm_archive = cls(start_date=start_date, end_date=end_date)
        table = parsed_content.find("table", attrs={"class", "Table3"})
        if not table:
            return cm_archive
        inner_table_container = table.find("div", attrs={"class", "InnerTableContainer"})
        inner_table = inner_table_container.find("table")
        inner_table_rows = inner_table.find_all("tr")
        inner_table_rows = [e for e in inner_table_rows if e.parent == inner_table]
        table_content = inner_table_container.find("table", attrs={"class", "TableContent"})

        header_row, *rows = table_content.find_all("tr")

        for row in rows:
            columns = row.find_all("td")
            date_column = columns[0]
            date = parse_tibia_datetime(date_column.text.replace("\xa0", " "))
            board_thread_column = columns[1]
            convert_line_breaks(board_thread_column)
            board, thread = board_thread_column.text.splitlines()
            link_column = columns[2]
            post_link = link_column.find("a")
            post_link_url = post_link["href"]
            post_id = int(post_id_regex.search(post_link_url).group(1))
            cm_archive.posts.append(CMPost(date=date, board=board, thread_title=thread, post_id=post_id))
        if not cm_archive.posts:
            return cm_archive
        pages_column, results_column = inner_table_rows[-1].find_all("div")
        page_links = pages_column.find_all("a")
        listed_pages = [int(p.text) for p in page_links]
        if listed_pages:
            cm_archive.page = next((x for x in range(1, listed_pages[-1] + 1) if x not in listed_pages), 0)
            cm_archive.total_pages = max(int(page_links[-1].text), cm_archive.page)
            if not cm_archive.page:
                cm_archive.total_pages += 1
                cm_archive.page = cm_archive.total_pages

        cm_archive.results_count = int(results_column.text.split(":")[-1])
        return cm_archive

    # endregion

    # region Private Methods

    @classmethod
    def _get_selected_date(cls, month_selector, day_selector, year_selector):
        """Gets the date made from the selected options in the selectors.
        
        Parameters
        ----------
        month_selector: :class:`bs4.Tag`
            The month selector.
        day_selector: :class:`bs4.Tag`
            The day selector.
        year_selector: :class:`bs4.Tag`
            The year selector.
        Returns
        -------
        :class:`datetime.date`
            The selected date.
        """
        selected_month = month_selector.find("option", {"selected": True}) or month_selector.find("option")
        selected_day = day_selector.find("option", {"selected": True}) or day_selector.find("option")
        selected_year = year_selector.find("option", {"selected": True}) or year_selector.find("option")
        try:
            return datetime.date(year=int(selected_year["value"]), month=int(selected_month["value"]),
                                 day=int(selected_day["value"]))
        except ValueError:
            return None
    # endregion


class ForumAnnouncement(abc.BaseAnnouncement, abc.Serializable):
    """Represent's a forum announcement.

    These are a special kind of thread that are shown at the top of boards.
    They cannot be replied to and they show no view counts.

    .. versionadded:: 3.0.0

    Attributes
    ----------
    announcement_id: :class:`int`
        The id of the announcement.
    board: :class:`str`
        The board this thread belongs to.
    section: :class:`str`
        The board section this thread belongs to.
    board_id: :class:`int`
        The internal id of the board the post is in.
    section_id: :class:`int`
        The internal id of the section the post is in.
    author: :class:`ForumAuthor`
        The author of the announcement.
    title: :class:`str`
        The title of the announcement.
    content: :class:`str`
        The HTML content of the announcement.
    start_date: :class:`datetime.datetime`
        The starting date of the announcement.
    end_date: :class:`datetime.datetime`
        The end date of the announcement.
    """

    __slots__ = (
        "announcement_id",
        "board",
        "board_id",
        "section",
        "section_id",
        "author",
        "title",
        "content",
        "start_date",
        "end_date",
    )

    def __init__(self, **kwargs):
        self.title: str = kwargs.get("title")
        self.announcement_id: int = kwargs.get("announcement_id", 0)
        self.board: str = kwargs.get("board")
        self.board_id: int = kwargs.get("board_id", 0)
        self.section: str = kwargs.get("section")
        self.section_id: int = kwargs.get("section_id", 0)
        self.author: ForumAuthor = kwargs.get("author")
        self.content: str = kwargs.get("content")
        self.start_date: datetime.datetime = kwargs.get("start_date")
        self.end_date: datetime.datetime = kwargs.get("end_date")

    def __repr__(self):
        return f"<{self.__class__.__name__} title={self.title!r} board={self.announcement_id!r}>"

    @classmethod
    def from_content(cls, content, announcement_id=0):
        """Parses the content of an announcement's page from Tibia.com

        Parameters
        ----------
        content: :class:`str`
            The HTML content of an announcement in Tibia.com
        announcement_id: :class:`int`
            The id of the announcement. Since there is no way to obtain the id from the page,
            the id may be passed to assing.

        Returns
        -------
        :class:`ForumAnnouncement`
            The announcement contained in the page or :obj:`None` if not found.

        Raises
        ------
        InvalidContent
            If content is not the HTML content of an announcement page in Tibia.com
        """
        parsed_content = parse_tibiacom_content(content)
        tables = parsed_content.find_all("table", attrs={"width": "100%"})
        root_tables = [t for t in tables if "BoxContent" in t.parent.attrs.get("class", [])]
        if not root_tables:
            error_table = parsed_content.find("table", attrs={"class": "Table1"})
            if error_table and "not be found" in error_table.text:
                return None
            raise errors.InvalidContent("content is not a Tibia.com forum announcement.")
        forum_info_table, posts_table, footer_table = root_tables

        section_link, board_link, *_ = forum_info_table.find_all("a")
        section = section_link.text
        section_id = int(section_id_regex.search(section_link["href"]).group(1))
        board = board_link.text
        board_id = int(board_id_regex.search(board_link["href"]).group(1))

        announcement = cls(section=section, section_id=section_id, board=board, board_id=board_id,
                           announcement_id=announcement_id)

        timezone = timezone_regex.search(footer_table.text).group(1)
        offset = 1 if timezone == "CES" else 2

        announcement_container = posts_table.find("td", attrs={"class": "CipPost"})
        character_info_container = announcement_container.find("div", attrs={"class": "PostCharacterText"})
        announcement.author = ForumAuthor._parse_author_table(character_info_container)

        post_container = posts_table.find("div", attrs={"class": "PostText"})
        title_tag = post_container.find("b")
        announcement.title = title_tag.text
        dates_container = post_container.find("font")
        dates = post_dates_regex.findall(dates_container.text)
        announcement_content = post_container.encode_contents().decode()
        _, announcement_content = announcement_content.split("<hr/>", 1)
        announcement.content = announcement_content

        announcement.start_date, announcement.end_date = (parse_tibia_forum_datetime(date, offset) for date in dates)

        return announcement


class ForumAuthor(abc.BaseCharacter, abc.Serializable):
    """Represents a post's author.

    .. versionadded:: 3.0.0

    Attributes
    ----------
    name: :class:`str`
        The name of the character, author of the post.
    level: :class:`int`
        The level of the character.
    world: :class:`str`
        The world the character belongs to.
    position: :class:`str`
        The character's position, if any.
    title: :class:`str`
        The character's selected title, if any.
    vocation: :class:`Vocation`
        The vocation of the character.
    guild: :class:`GuildMembership`
        The guild the author belongs to, if any.
    posts: :class:`int`
        The number of posts this character has made.
    deleted: :class:`bool`
        Whether the author is deleted or not.
    """

    __slots__ = (
        "name",
        "level",
        "world",
        "vocation",
        "title",
        "position",
        "guild",
        "posts",
        "deleted",
    )

    def __init__(self, name, **kwargs):
        self.name: str = name
        self.level: int = kwargs.get("level", 2)
        self.world: str = kwargs.get("world")
        self.vocation: Vocation = try_enum(Vocation, kwargs.get("vocation"))
        self.title: Optional[str] = kwargs.get("title")
        self.position: Optional[str] = kwargs.get("position")
        self.guild: Optional[GuildMembership] = kwargs.get("guild")
        self.posts: int = kwargs.get("posts", 0)
        self.deleted: bool = kwargs.get("deleted", False)

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} level={self.level} world={self.world!r} " \
               f"vocation={self.vocation!r}>"

    @classmethod
    def _parse_author_table(cls, character_info_container):
        """Parses the table containing the author's information.

        Parameters
        ----------
        character_info_container: :class:`bs4.Tag`
            The cotnainer with the character's information.

        Returns
        -------
        :class:`ForumAuthor`
            The author's information.
        """
        # First link belongs to character
        char_link = character_info_container.find("a")
        if not char_link:
            return ForumAuthor(name=character_info_container.text, deleted=True)
        author = cls(char_link.text)

        position_info = character_info_container.find("font", attrs={"class": "ff_smallinfo"})
        # Position and titles are shown the same way. If we have two, the title is first and then the position.
        # However, if the character only has one of them, there's no way to know which is it unless we validate against
        # possible types
        if position_info and position_info.parent == character_info_container:
            convert_line_breaks(position_info)
            titles = [title for title in position_info.text.splitlines() if title]
            positions = ["Tutor", "Community Manager", "Customer Support", "Programmer", "Game Content Designer",
                         "Tester"]
            for _title in titles:
                if _title in positions:
                    author.position = _title
                else:
                    author.title = _title
        char_info = character_info_container.find("font", attrs={"class": "ff_infotext"})
        guild_info = char_info.find("font", attrs={"class": "ff_smallinfo"})
        convert_line_breaks(char_info)
        char_info_text = char_info.text
        info_match = author_info_regex.search(char_info_text)
        if info_match:
            author.world = info_match.group(1)
            author.vocation = try_enum(Vocation, info_match.group(2))
            author.level = int(info_match.group(3))
        if guild_info:
            guild_match = guild_regexp.search(guild_info.text)
            guild_name = guild_match.group(2)
            title_match = guild_title_regexp.search(guild_name)
            title = None
            if title_match:
                guild_name = title_match.group(1)
                title = title_match.group(2)
            author.guild = GuildMembership(name=guild_name, rank=guild_match.group(1), title=title)
        author.posts = int(author_posts_regex.search(char_info_text).group(1))
        return author


class ForumBoard(abc.BaseBoard, abc.Serializable):
    """Represents a forum's board.

    .. versionadded:: 3.0.0

    Attributes
    ----------
    name: :class:`str`
        The name of the board.
    section: :class:`str`
        The section of the board.
    current_page: :class:`int`
        The current page being viewed.
    pages: :class:`int`
        The number of total_pages the board has for the current display range.
    age: :class:`ìnt`
        The maximum age of the displayed threads, in days.

        -1 means all threads will be shown.
    announcements: list of :class:`ListedAnnouncement`
        The list of announcements currently visible.
    threads: list of :class:`ListedThread`
        The list of threads currently visible.
    """

    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name")
        self.section: str = kwargs.get("section")
        self.board_id: int = kwargs.get("board_id", 0)
        self.page: int = kwargs.get("page", 1)
        self.total_pages: int = kwargs.get("total_pages", 1)
        self.age: int = kwargs.get("age", 30)
        self.announcements: List[ListedAnnouncement] = kwargs.get("announcements", [])
        self.threads: List[ListedThread] = kwargs.get("threads", [])

    __slots__ = (
        "name",
        "section",
        "board_id",
        "page",
        "total_pages",
        "age",
        "announcements",
        "threads",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} section={self.section!r}>"

    # region Properties
    @property
    def url(self):
        """:class:`str`: The URL of this board."""
        return self.get_url(self.board_id, self.page, self.age)

    @property
    def previous_page_url(self):
        """:class:`str`: The URL to the previous page of the board, if there's any."""
        return self.get_page_url(self.page - 1) if self.page > 1 else None

    @property
    def next_page_url(self):
        """:class:`str`: The URL to the next page of the board, if there's any."""
        return self.get_page_url(self.page + 1) if self.page < self.total_pages else None

    # endregion

    # region Public Methods

    def get_page_url(self, page):
        """Gets the URL to a given page of the board.

        Parameters
        ----------
        page: :class:`int`
            The desired page.

        Returns
        -------
        :class:`str`
            The URL to the desired page.
        """
        if page <= 0:
            raise ValueError("page must be 1 or greater")
        return self.get_url(self.board_id, page, self.age)

    @classmethod
    def from_content(cls, content):
        """Parses the board's HTML content from Tibia.com.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the board.

        Returns
        -------
        :class:`ForumBoard`
            The forum board contained.

        Raises
        ------
        InvalidContent`
            Content is not a board in Tibia.com
        """
        parsed_content = parse_tibiacom_content(content)
        tables = parsed_content.find_all("table")
        try:
            header_table, time_selector_table, threads_table, timezone_table, boardjump_table, *_ = tables
        except ValueError as e:
            raise errors.InvalidContent("content is not a forum board", e)
        header_text = header_table.text.strip()
        section, name = split_list(header_text, "|", "|")

        board = cls(name=name, section=section)
        thread_rows = threads_table.find_all("tr")

        age_selector = time_selector_table.find("select")
        if not age_selector:
            return cls(section=section, name=name)
        selected_age = age_selector.find("option", {"selected": True})
        if selected_age:
            board.age = int(selected_age["value"])

        board_selector = boardjump_table.find("select")
        selected_board = board_selector.find("option", {"selected": True})
        board.board_id = int(selected_board["value"])

        page_info = threads_table.find("td", attrs={"class": "ff_info"})
        if page_info:
            current_page_text = page_info.find("span")
            page_links = page_info.find_all("a")
            if current_page_text:
                board.page = int(current_page_text.text)
                board.total_pages = max(board.page, int(page_number_regex.search(page_links[-1]["href"]).group(1)))

        for thread_row in thread_rows[1:]:
            columns = thread_row.find_all("td")
            if len(columns) != 7:
                continue

            entry = cls._parse_thread_row(columns)
            if isinstance(entry, ListedThread):
                board.threads.append(entry)
                cip_border = thread_row.find("div", attrs={"class": "CipBorder"})
                if cip_border:
                    entry.golden_frame = True
            elif isinstance(entry, ListedAnnouncement):
                board.announcements.append(entry)

        return board

    # endregion

    # region Private Methods

    @classmethod
    def _parse_thread_row(cls, columns):
        """Parses the thread row, containing a single thread or announcement.

        Parameters
        ----------
        columns: :class:`bs4.ResultSet`
            The list of columns the thread contains.

        Returns
        -------
        :class:`ListedThread` or :class:`ListedAnnouncement`
        """
        # First Column: Thread's status
        status = None
        status_column = columns[0]
        status_img = status_column.find("img")
        status_icon = None
        if status_img:
            url = status_img["src"]
            filename = filename_regex.search(url).group(1)
            status_icon = url
            status = ThreadStatus.from_icon(filename)
        # Second column: Thread's emoticon
        emoticon = None
        emoticon_column = columns[1]
        emoticon_img = emoticon_column.find("img")
        if emoticon_img and emoticon_img.get("alt"):
            url = emoticon_img["src"]
            name = emoticon_img["alt"]
            emoticon = ForumEmoticon(name, url)
        # Third Column: Thread's title and number of total_pages
        pages = 1
        thread_column = columns[2]
        title = thread_column.text.strip()
        try:
            thread_link, *page_links = thread_column.find_all("a")
        except ValueError:
            return
        if page_links:
            last_page_link = page_links[-1]
            pages = int(page_number_regex.search(last_page_link["href"]).group(1))
            title = pages_regex.sub("", title).strip()
        thread_id_match = thread_id_regex.search(thread_link["href"])
        # Fourth Column: Thread startert
        thread_starter_column = columns[3]
        thread_starter = thread_starter_column.text.strip()
        if thread_id_match:
            thread_id = int(thread_id_match.group(1))
            # Fifth Column: Number of replies
            replies_column = columns[4]
            replies = int(replies_column.text)
            # Sixth Column: Number of views
            views_column = columns[5]
            views = int(views_column.text)
            # Seventh Column: Last post information
            last_post_column = columns[6]
            last_post = LastPost._parse_column(last_post_column)

            entry = ListedThread(title=title, thread_id=thread_id, thread_starter=thread_starter, replies=replies,
                                 views=views, last_post=last_post, emoticon=emoticon, status=status, pages=pages,
                                 status_icon=status_icon)
        else:
            title = title.replace("Announcement: ", "")
            announcement_id = int(announcement_id_regex.search(thread_link["href"]).group(1))
            entry = ListedAnnouncement(title=title, announcement_id=announcement_id, announcement_author=thread_starter)
        return entry

    # endregion


class ForumEmoticon(abc.Serializable):
    """Represents a forum's emoticon.

    .. versionadded:: 3.0.0

    Attributes
    ----------
    name: :class:`str`
        The emoticon's name.
    url: :class:`str`
        The URL to the emoticon`s image.
    """

    __slots__ = (
        "name",
        "url",
    )

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} url={self.url!r}>"


class ForumPost(abc.BasePost, abc.Serializable):
    """Represents a forum post.

    .. versionadded:: 3.0.0

    Attributes
    ----------
    author: :class:`ForumAuthor`
        The author of the post.
    emoticon: :class:`ForumEmoticon`
        The emoticon selected for the post.
    title: :class:`str`, optional
        The title of the post.
    content: :class:`str`
        The content of the post.
    signature: :class:`str`
        The signature of the post.
    post_id: :class:`int`
        The id of the post.
    posted_date: :class:`datetime.datetime`
        The date when the post was made.
    edited_date: :class:`datetime.datetime`, optional
        The date when the post was last edited, if applicable.
    edited_by: :class:`str`, optional
        The character that edited the post.

        This is usually the same author, but in some occasions staff members edit the posts of others.
    """

    __slots__ = (
        "author",
        "emoticon",
        "title",
        "signature",
        "emoticon",
        "post_id",
        "posted_date",
        "edited_date",
        "edited_by",
        "golden_frame",
        "content",
    )

    def __init__(self, **kwargs):
        self.author = kwargs.get("author")
        self.emoticon = kwargs.get("emoticon")
        self.title = kwargs.get("title")
        self.content = kwargs.get("content")
        self.signature = kwargs.get("signature")
        self.emoticon = kwargs.get("emoticon")
        self.post_id = kwargs.get("post_id")
        self.golden_frame = kwargs.get("golden_frame")
        self.posted_date = kwargs.get("posted_date")
        self.edited_date = kwargs.get("edited_date")
        self.edited_by = kwargs.get("edited_by")

    def __repr__(self):
        return f"<{self.__class__.__name__} title={self.title!r} post_id={self.post_id}>"


class ForumThread(abc.BaseThread, abc.Serializable):
    """Represents a forum thread.

    .. versionadded:: 3.0.0

    Attributes
    ----------
    title: :class:`str`
        The title of the thread.
    thread_id: :class:`int`
        The thread's number.
    board: :class:`str`
        The board this thread belongs to.
    section: :class:`str`
        The board section this thread belongs to.
    previous_topic_number: :class:`int`
        The number of the previous topic.
    next_topic_number: :class:`int`
        The number of the next topic.
    pages: :class:`int`
        The number of total_pages this thread has.
    current_page: :class:`int`
        The page being viewed.
    posts: list of :class:`ForumPost`
        The list of posts the thread has.
    golden_frame: :class:`bool`
        Whether the thread has a golden frame or not.

        In the Proposals board,a golden frame means the thread has a reply by a staff member.
    anchored_post: :class:`ForumPost`
        The post where the page is anchored to, if any.

        When a post is fetched directly, the thread that contains it is displayed, anchored to the specific post.
    """
    __slots__ = (
        "title",
        "thread_id",
        "board",
        "section",
        "previous_topic_number",
        "next_topic_number",
        "page",
        "total_pages",
        "golden_frame",
        "anchored_post",
        "posts",
    )

    def __init__(self, **kwargs):
        self.title: str = kwargs.get("title")
        self.thread_id: int = kwargs.get("thread_id", 0)
        self.board: str = kwargs.get("board")
        self.section: str = kwargs.get("section")
        self.previous_topic_number: int = kwargs.get("previous_topic_number", 0)
        self.next_topic_number: int = kwargs.get("next_topic_number", 0)
        self.page: int = kwargs.get("page", 1)
        self.total_pages: int = kwargs.get("total_pages", 1)
        self.posts: List[ForumPost] = kwargs.get("posts", [])
        self.golden_frame: bool = kwargs.get("golden_frame", False)
        self.anchored_post: Optional[ForumPost] = None

    def __repr__(self):
        return f"<{self.__class__.__name__} title={self.title!r} board={self.board!r} section={self.section!r}>"

    # region Properties
    @property
    def url(self):
        """:class:`str`: The URL of this thread and current page."""
        return self.get_url(self.thread_id, self.page)

    @property
    def previous_page_url(self):
        """:class:`str`: The URL to the previous page of the thread, if there's any."""
        return self.get_page_url(self.page - 1) if self.page > 1 else None

    @property
    def next_page_url(self):
        """:class:`str`: The URL to the next page of the thread, if there's any."""
        return self.get_page_url(self.page + 1) if self.page < self.total_pages else None

    @property
    def previous_thread_url(self):
        """:class:`str`: The URL to the previous topic of the board, if there's any."""
        return self.get_url(self.previous_topic_number) if self.previous_topic_number else None

    @property
    def next_thread_url(self):
        """:class:`str`: The URL to the next topic of the board, if there's any."""
        return self.get_url(self.next_topic_number) if self.next_topic_number else None

    # endregion

    # region Public Methods

    def get_page_url(self, page):
        """Gets the URL to a given page of the board.

        Parameters
        ----------
        page: :class:`int`
            The desired page.

        Returns
        -------
        :class:`str`
            The URL to the desired page.
        """
        if page <= 0:
            raise ValueError("page must be 1 or greater")
        return self.get_url(self.thread_id, page)

    @classmethod
    def from_content(cls, content):
        """Creates an instance of the class from the html content of the thread's page.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the page.

        Returns
        -------
        :class:`ForumThread`
            The thread contained in the page, or None if the thread doesn't exist

        Raises
        ------
        InvalidContent
            If content is not the HTML of a thread's page.
        """
        parsed_content = parse_tibiacom_content(content)
        tables = parsed_content.find_all("table")
        root_tables = [t for t in tables if "BoxContent" in t.parent.attrs.get("class", [])]
        if not root_tables:
            error_table = parsed_content.find("table", attrs={"class": "Table1"})
            if error_table and "not found" in error_table.text:
                return None
            raise errors.InvalidContent("content is not a Tibia.com forum thread.")
        try:
            if len(root_tables) == 4:
                forum_info_table, title_table, posts_table, footer_table = root_tables
            else:
                forum_info_table, title_table, footer_table = root_tables
                posts_table = None
        except ValueError as e:
            raise errors.InvalidContent("content is not a Tibia.com forum thread.", e)

        header_text = forum_info_table.text
        section, board, *_ = split_list(header_text, "|", "|")

        thread = cls(section=section, board=board)

        thread.title = title_table.text.strip()
        golden_frame = title_table.find("div", attrs={"class": "CipPost"})
        thread.golden_frame = golden_frame is not None

        timezone = timezone_regex.search(footer_table.text).group(1)
        time_page_column, navigation_column = footer_table.find_all("td", attrs={"class", "ff_white"})
        page_links = time_page_column.find_all("a")
        if page_links:
            last_link = page_links[-1]["href"]
            thread.page = int(footer_table.find("span").text)
            thread.total_pages = max(int(page_number_regex.search(last_link).group(1)), thread.page)

        navigation_links = navigation_column.find_all("a")
        if len(navigation_links) == 2:
            prev_link, next_link = navigation_links
            prev_link_url = prev_link["href"]
            thread.previous_topic_number = int(thread_id_regex.search(prev_link_url).group(1))
            next_link_url = next_link["href"]
            thread.next_topic_number = int(thread_id_regex.search(next_link_url).group(1))
        elif "Previous" in navigation_links[0].text:
            prev_link_url = navigation_links[0]["href"]
            thread.previous_topic_number = int(thread_id_regex.search(prev_link_url).group(1))
        else:
            next_link_url = navigation_links[0]["href"]
            thread.next_topic_number = int(thread_id_regex.search(next_link_url).group(1))
        offset = 1 if timezone == "CES" else 2

        if posts_table:
            thread_info_table, *post_tables = posts_table.find_all("div", attrs={"class": "ForumPost"})
            inner_info_table = thread_info_table.find("table")
            thread_num_col, thread_pages_col, thread_navigation_col = inner_info_table.find_all("td")
            thread.thread_id = int(thread_num_col.text.replace("Thread #", ""))
            for post_table in post_tables:
                post = cls._parse_post_table(post_table, offset)
                thread.posts.append(post)
        return thread

    # endregion

    # region Private Methods

    @classmethod
    def _parse_post_table(cls, post_table, offset=1):
        """Parses the table containing a single posts, extracting its information.

        Parameters
        ----------
        post_table: :class:`bs4.Tag`
            The parsed HTML content of the table.
        offset: :class:`int`
            The UTC offset used for the timestamps.

            Since the timestamps found in the post contain no timezone information, the offset is extracted from
            another section and passed here to adjust them accordingly.

        Returns
        -------
        :class:`ForumPost`
            The post contained in the table.
        """
        golden_frame = post_table.find("div", attrs={"class": "CipBorderTop"})
        character_info_container = post_table.find("div", attrs={"class": "PostCharacterText"})
        post_author = ForumAuthor._parse_author_table(character_info_container)
        content_container = post_table.find("div", attrs={"class": "PostText"})
        content = content_container.encode_contents().decode()
        title = None
        signature = None
        if signature_separator in content:
            content, _ = content.split(signature_separator)
        title_raw, content = content.split("<br/><br/>", 1)
        emoticon = None
        if title_raw:
            title_html = bs4.BeautifulSoup(title_raw, 'lxml')
            emoticon_img = title_html.find("img")
            if emoticon_img:
                emoticon = ForumEmoticon(emoticon_img["alt"], emoticon_img["src"])
            title_tag = title_html.find("b")
            if title_tag:
                title = title_tag.text
        signature_container = post_table.find("td", attrs={"class": "ff_pagetext"})
        if signature_container:
            signature = signature_container.encode_contents().decode()
        post_details = post_table.find('div', attrs={"class": "PostDetails"})
        dates = post_dates_regex.findall(post_details.text)
        edited_date = None
        edited_by = None
        posted_date = parse_tibia_forum_datetime(dates[0], offset)
        if len(dates) > 1:
            edited_date = parse_tibia_forum_datetime(dates[1], offset)
            edited_by = edited_by_regex.search(post_details.text).group(1)
        post_details = post_table.find('div', attrs={"class": "AdditionalBox"})
        post_number = post_details.text.replace("Post #", "")
        post_id = int(post_number)
        post = ForumPost(author=post_author, content=content, signature=signature, posted_date=posted_date,
                         edited_date=edited_date, edited_by=edited_by, post_id=post_id, title=title, emoticon=emoticon,
                         golden_frame=golden_frame is not None)
        return post

    # endregion


class LastPost(abc.BasePost, abc.Serializable):
    """Represents a forum thread.

    .. versionadded:: 3.0.0

    Attributes
    ----------
    author: :class:`str`
        The name of the character that made the last post.
    post_id: :class:`int`
        The internal id of the post.
    date: :class:`datetime.datetime`
        The date when the last post was made.
    deleted: :class:`bool`
        Whether the last post's author is a character that is already deleted.
    """

    def __init__(self, author, post_id, date, *, deleted=False):
        self.author: str = author
        self.post_id: int = post_id
        self.date: datetime.datetime = date
        self.deleted: bool = deleted

    __slots__ = (
        "author",
        "post_id",
        "date",
        "deleted",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} author={self.author!r} post_id={self.post_id} date={self.date!r}>"

    @property
    def author_url(self):
        """:class:`str`: The URL to the author's character information page."""
        return abc.BaseCharacter.get_url(self.author)

    @classmethod
    def _parse_column(cls, last_post_column, offset=1):
        """Parses the column containing the last post information and extracts its data.

        Parameters
        ----------
        last_post_column: :class:`bs4.Tag`:
            The column containing the last post.
        offset: :class:`int`
            Since the timestamps have no offset information, it may be passed to fill it out.

        Returns
        -------
        Optional[:class:`LastPost`]:
            The last post described in the column, if any.
        """
        last_post_info = last_post_column.find("div", attrs={"class": "LastPostInfo"})
        if last_post_info is None:
            return None
        permalink = last_post_info.find("a")
        link = permalink['href']
        post_id = int(post_id_regex.search(link).group(1))
        date_text = last_post_info.text.replace("\xa0", " ").strip()
        last_post_date = parse_tibia_forum_datetime(date_text, offset)

        last_post_author_tag = last_post_column.find("font")
        author_link = last_post_author_tag.find("a")
        deleted = author_link is None
        author = last_post_author_tag.text.replace("by", "", 1).replace("\xa0", " ").strip()

        return cls(author, post_id, last_post_date, deleted=deleted)


class ListedAnnouncement(abc.BaseAnnouncement, abc.Serializable):
    """Represents an announcement in the forum boards.

    .. versionadded:: 3.0.0

    Attributes
    ----------
    title: :class:`str`
        The title of the announcement.
    announcement_id: class:`int`
        The internal id of the announcement.
    announcement_author: :class:`str`
        The character that made the announcement.
    """

    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.announcement_id = kwargs.get("announcement_id")
        self.announcement_author = kwargs.get("announcement_author")

    __slots__ = (
        "title",
        "announcement_id",
        "announcement_author",
    )

    def __repr__(self):
        return "<{0.__class__.__name__} title={0.title!r} announcement_id={0.announcement_id} " \
               "announcement_author={0.announcement_author!r}>".format(self)


class ListedBoard(abc.BaseBoard, abc.Serializable):
    """Represents a board in the list of boards.

    This is the board information available when viewing a section (e.g. World, Trade, Community)

    .. versionadded:: 3.0.0

    Attributes
    ----------
    name: :class:`str`
        The name of the board.
    board_id: :class:`int`
        The board's internal id.
    description: :class:`str`
        The description of the board.
    posts: :class:`int`
        The number of posts in this board.
    threads: :class:`int`
        The number of threads in this board.
    last_post: :class:`LastPost`
        The information of the last post made in this board.
    """
    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name")
        self.board_id: int = kwargs.get("board_id")
        self.description: str = kwargs.get("description")
        self.posts: int = kwargs.get("posts")
        self.threads: int = kwargs.get("threads")
        self.last_post: Optional[LastPost] = kwargs.get("last_post")

    __slots__ = (
        "name",
        "board_id",
        "description",
        "posts",
        "threads",
        "last_post",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} board_id={self.board_id} posts={self.posts} " \
               f"threads={self.threads} description={self.description!r}>"

    # region Public Methods
    @classmethod
    def list_from_content(cls, content):
        """Parses the content of a board list Tibia.com into a list of boards.

        Parameters
        ----------
        content: :class:`str`
            The raw HTML response from the board list.

        Returns
        -------
        :class:`list` of :class:`ListedBoard`

        Raises
        ------
        InvalidContent`
            Content is not a board list in Tibia.com
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            tables = parsed_content.find_all("table", attrs={"width": "100%"})
            _, board_list_table, timezone_table = tables
            _, *board_rows = board_list_table.find_all("tr")
            timezone_text = timezone_table.text
            timezone = timezone_regex.search(timezone_text).group(1)
            offset = 1 if timezone == "CES" else 2
            boards = []
            for board_row in board_rows[:-3]:
                try:
                    board = cls._parse_board_row(board_row, offset)
                except IndexError:
                    continue
                else:
                    boards.append(board)
            return boards
        except ValueError as e:
            raise errors.InvalidContent("content does not belong to a forum section.", e)

    # endregion

    # region Private Methods
    @classmethod
    def _parse_board_row(cls, board_row, offset=1):
        """Parses a row containing a board and extracts its information.

        Parameters
        ----------
        board_row: :class:`bs4.Tag`
            The row's parsed content.
        offset: :class:`int`
            Since the displayed dates do not contain information, it is neccessary to extract the used timezone from
            somewhere else and pass it to this method to adjust them accordingly.

        Returns
        -------
        :class:`ListedBoard`
            The board contained in this row.
        """
        columns = board_row.find_all("td")
        # Second Column: Name and description
        name_column = columns[1]
        board_link_tag = name_column.find("a")
        description_tag = name_column.find("font")
        description = description_tag.text
        name = board_link_tag.text
        link = board_link_tag['href']
        board_id = int(board_id_regex.search(link).group(1))
        # Third Column: Post count
        posts_column = columns[2]
        posts = int(posts_column.text)
        # Fourth Column: View count
        threads_column = columns[3]
        threads = int(threads_column.text)
        # Fifth Column: Last post information
        last_post_column = columns[4]
        last_post = LastPost._parse_column(last_post_column, offset)
        return cls(name=name, board_id=board_id, description=description, posts=posts, threads=threads,
                   last_post=last_post)
    # endregion


class ListedThread(abc.BaseThread, abc.Serializable):
    """Represents a thread in a forum board.

    .. versionadded:: 3.0.0

    Attributes
    ----------
    title: :class:`str`
        The title of the thread.
    thread_id: :class:`int`
        The internal id of the thread.
    thread_started: :class:`str`
        The character that started the thread.
    replies: :class:`int`
        The number of replies.
    views: :class:`int`
        The number of views.
    last_post: :class:`LastPost`
        The information of the last post made in this board.
    status: :class:`ThreadStatus`
        The status of the thread.
    status_icon: :class:`str`
        The URL of the icon displayed as status.
    emoticon: :class:`ForumEmoticon`
        The emoticon used for the thread.
    pages: :class:`int`
        The number of total_pages the thread has.
    golden_frame: :class:`bool`
        Whether the thread has a gold frame or not.

        In the Proposals board, the gold frame indicates that a staff member has replied in the thread.
    """
    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.thread_id = kwargs.get("thread_id")
        self.thread_starter = kwargs.get("thread_starter")
        self.replies = kwargs.get("replies")
        self.views = kwargs.get("views")
        self.last_post = kwargs.get("last_post")
        self.status = kwargs.get("status")
        self.status_icon = kwargs.get("status_icon")
        self.icon = kwargs.get("icon")
        self.emoticon = kwargs.get("emoticon")
        self.pages = kwargs.get("total_pages", 1)
        self.golden_frame = kwargs.get("golden_frame", False)

    __slots__ = (
        "title",
        "thread_id",
        "thread_starter",
        "replies",
        "views",
        "last_post",
        "status",
        "status_icon",
        "emoticon",
        "pages",
        "golden_frame",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} title={self.title!r} thread_id={self.thread_id} " \
               f"thread_starter={self.thread_starter!r} replies={self.replies} views={self.views}>"
