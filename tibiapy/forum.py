import datetime
import re
from typing import List, Optional

import bs4

from tibiapy import abc, errors, GuildMembership
from tibiapy.enums import ThreadStatus, Vocation
from tibiapy.utils import convert_line_breaks, get_tibia_url, parse_tibia_forum_datetime, parse_tibiacom_content, \
    split_list, try_enum


__all__ = (
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


class ForumAnnouncement(abc.Serializable):
    """Represent's a forum announcement.

    These are a special kind of thread that are shown at the top of boards.
    They cannot be replied to and they show no view counts.

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
            The announcement contained in the page or ```None`` if not found.

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

        post_container = posts_table.find("div", attrs={"class":"PostText"})
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
    age: :class:ìnt`
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


class ForumPost(abc.Serializable):
    """Represent's a forum post.

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
    emoticon: :Class:`str`
        The URL to the post's emoticon.
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


class ForumThread(abc.BaseThread, abc.Serializable):
    """Represents a forum thread.

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
        "posts",
    )

    def __init__(self, **kwargs):
        self.title: str = kwargs.get("title")
        self.thread_id: int = kwargs.get("thread_id")
        self.board: str = kwargs.get("board")
        self.section: str = kwargs.get("section")
        self.previous_topic_number: int = kwargs.get("previous_topic_number", 0)
        self.next_topic_number: int = kwargs.get("next_topic_number", 0)
        self.page: int = kwargs.get("page", 1)
        self.total_pages: int = kwargs.get("total_pages", 1)
        self.posts: List[ForumPost] = kwargs.get("posts", [])
        self.golden_frame: bool = kwargs.get("golden_frame", False)

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
        parsed_content = parse_tibiacom_content(content)
        tables = parsed_content.find_all("table", attrs={"width": "100%"})
        root_tables = [t for t in tables if "BoxContent" in t.parent.attrs.get("class", [])]
        forum_info_table, title_table, posts_table, footer_table = root_tables

        header_text = forum_info_table.text
        section, board, *_ = split_list(header_text, "|", "|")

        thread_title = title_table.text.strip()
        golden_frame = title_table.find("div", attrs={"class": "CipPost"})
        entries = []
        thread_info_table, *post_tables = posts_table.find_all("div", attrs={"class": "ForumPost"})
        inner_info_table = thread_info_table.find("table")
        thread_num_col, thread_pages_col, thread_navigation_col = inner_info_table.find_all("td")
        thread_number = int(thread_num_col.text.replace("Thread #", ""))

        page_links = thread_pages_col.find_all("a")
        current_page = pages = 1
        if page_links:
            last_link = page_links[-1]["href"]
            pages = int(page_number_regex.search(last_link).group(1))
            current_page = int(thread_pages_col.find("span").text)

        navigation_links = thread_navigation_col.find_all("a")
        previous_id = next_id = None
        if navigation_links:
            if len(navigation_links) == 2:
                prev_link, next_link = navigation_links
                prev_link_url = prev_link["href"]
                previous_id = int(thread_id_regex.search(prev_link_url).group(1))
                next_link_url = next_link["href"]
                next_id = int(thread_id_regex.search(next_link_url).group(1))
            elif "Previous" in navigation_links[0].text:
                prev_link_url = navigation_links[0]["href"]
                previous_id = int(thread_id_regex.search(prev_link_url).group(1))
            else:
                next_link_url = navigation_links[0]["href"]
                next_id = int(thread_id_regex.search(next_link_url).group(1))

        timezone = timezone_regex.search(footer_table.text).group(1)
        offset = 1 if timezone == "CES" else 2

        for post_table in post_tables:
            post = cls._parse_post_table(post_table, offset)
            entries.append(post)

        thread = cls(title=thread_title, section=section, board=board, posts=entries, thread_id=thread_number,
                     page=current_page, total_pages=pages, previous_topic_number=previous_id,
                     next_topic_number=next_id, golden_frame=golden_frame is not None)
        return thread

    # endregion

    # region Private Methods

    @classmethod
    def _parse_post_table(cls, post_table, offset=1):
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


class LastPost(abc.Serializable):
    """Represents a forum thread.

    Attributes
    ----------
    author: :class:`str`
        The name of the character that made the last post.
    post_id: :class:`int`
        The internal id of the post.
    date: :class:`str`
        The date when the last post was made.
    """

    def __init__(self, author, post_id, date):
        self.author = author
        self.post_id = post_id
        self.date = date

    __slots__ = (
        "author",
        "post_id",
        "date",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} author={self.author!r} post_id={self.post_id} date={self.date!r}>"

    @classmethod
    def _parse_column(cls, last_post_column, offset=1):
        last_post_info = last_post_column.find("div", attrs={"class": "LastPostInfo"})
        if last_post_info is None:
            return None
        permalink = last_post_info.find("a")
        link = permalink['href']
        post_id = int(post_id_regex.search(link).group(1))
        date_text = last_post_info.text.replace("\xa0", " ").strip()
        last_post_date = parse_tibia_forum_datetime(date_text, offset)

        last_post_author_tag = last_post_column.find("font")
        author = last_post_author_tag.text.replace("by", "", 1).replace("\xa0", " ").strip()

        return cls(author, post_id, last_post_date)


class ListedAnnouncement(abc.Serializable):
    """Represents an announcement in the forum boards.

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

    Attributes
    ----------
    name: :class:`str`
        The name of the board.
    board_id: :class:`inst`
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

    Attributes
    ----------
    title: :class:`str`
        The title of the thread.
    thread_id: class:`int`
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
        return "<{0.__class__.__name__} title={0.title!r} thread_id={0.thread_id} " \
               "thread_starter={0.thread_starter!r} replies={0.replies} views={0.views}>".format(self)
