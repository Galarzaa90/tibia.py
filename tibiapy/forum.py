import re

import bs4

from tibiapy import abc, GuildMembership
from tibiapy.enums import ThreadStatus, Vocation
from tibiapy.utils import get_tibia_url, parse_tibia_forum_datetime, parse_tibiacom_content, split_list, try_enum


__all__ = (
    'ForumBoard',
    'ForumEmoticon',
    'ForumPost',
    'ForumThread',
    'LastPost',
    'ListedBoard',
    'ListedThread',
    'PostAuthor',
)

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

signature_separator = "________________"


class ForumBoard(abc.Serializable):
    """Represents a forum's board.

    Attributes
    ----------
    name: :class:`str`
        The name of the board.
    section: :class:`str`
        The section of the board.
    displayed_range:
        The currently viewed display range.
    current_page: :class:`int`
        The current page being viewed.
    pages: :class:`int`
        The number of pages the board has for the current display range.
    announcements: list of :class:`ListedAnnouncement`
        The list of announcements currently visible.
    threads: list of :class:`ListedThread`
        The list of threads currently visible.
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.section = kwargs.get("section")
        self.displayed_range = kwargs.get("displayed_range")
        self.current_page = kwargs.get("current_page")
        self.pages = kwargs.get("pages")
        self.announcements = kwargs.get("announcements")
        self.threads = kwargs.get("threads")

    __slots__ = (
        "name",
        "section",
        "displayed_range",
        "current_page",
        "pages",
        "announcements",
        "threads",
    )

    def __repr__(self):
        return "<{0.__class__.__name__} name={0.name!r} section={0.section!r}>".format(self)

    @classmethod
    def get_url(cls, board_id):
        return get_tibia_url("forum", None, action="board", boardid=board_id)

    @classmethod
    def from_content(cls, content):
        parsed_content = parse_tibiacom_content(content)
        tables = parsed_content.find_all("table", attrs={"width": "100%"})
        # TODO: Parse proposals board, it has a different style
        header_table, time_selector_table, threads_table, timezone_table, boardjump_table = tables
        header_text = header_table.text.strip()
        section, name = split_list(header_text, "|", "|")
        thread_rows = threads_table.find_all("tr")
        entries = []
        announcements = []
        for thread_row in thread_rows[1:]:
            columns = thread_row.find_all("td")
            if len(columns) != 7:
                continue

            entry = cls._parse_thread_row(columns)
            if isinstance(entry, ListedThread):
                entries.append(entry)
            elif isinstance(entry, ListedAnnouncement):
                announcements.append(entry)

        board = cls(name=name, section=section, threads=entries, announcements=announcements)
        return board

    @classmethod
    def _parse_thread_row(cls, columns):
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
        # Third Column: Thread's title and number of pages
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


class ForumEmoticon(abc.Serializable):
    """Represents a forum's emoticon.

    Attributes
    ----------
    name: :class:`str`
        The emoticon's name.
    url: :class:`str`
        The URL to the emoticon`s image.
    """

    def __init__(self, name, url):
        self.name = name
        self.url = url

    __slots__ = (
        "name",
        "url",
    )


class ForumPost(abc.Serializable):
    """Represent's a forum post.

    Attributes
    ----------
    author: :class:`PostAuthor`
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
    """

    __slots__ = (
        "author",
        "emoticon",
        "title",
        "content",
        "signature",
        "emoticon",
        "post_id",
        "posted_date",
        "edited_date",
    )

    def __init__(self, **kwargs):
        self.author = kwargs.get("author")
        self.emoticon = kwargs.get("emoticon")
        self.title = kwargs.get("title")
        self.content = kwargs.get("content")
        self.signature = kwargs.get("signature")
        self.emoticon = kwargs.get("emoticon")
        self.post_id = kwargs.get("post_id")
        self.posted_date = kwargs.get("posted_date")
        self.edited_date = kwargs.get("edited_date")


class ForumThread(abc.Serializable):
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
        The number of pages this thread has.
    current_page: :class:`int`
        The page being viewed.
    posts: list of :class:`ForumPost`
        The list of posts the thread has.
    """
    __slots__ = (
        "title",
        "thread_id",
        "board",
        "section",
        "previous_topic_number",
        "next_topic_number",
        "pages",
        "current_page",
        "posts",
    )

    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.thread_id = kwargs.get("thread_id")
        self.board = kwargs.get("board")
        self.section = kwargs.get("section")
        self.previous_topic_number = kwargs.get("previous_topic_number")
        self.next_topic_number = kwargs.get("next_topic_number")
        self.pages = kwargs.get("pages")
        self.current_page = kwargs.get("current_page")
        self.posts = kwargs.get("posts")

    def __repr__(self):
        return "<{0.__class__.__name__} title={0.title!r} board={0.board!r} section={0.section!r}>".format(self)

    @classmethod
    def get_url(cls, thread_id):
        return get_tibia_url("forum", None, action="thread", threadid=thread_id)

    @classmethod
    def from_content(cls, content):
        parsed_content = parse_tibiacom_content(content)
        tables = parsed_content.find_all("table", attrs={"width": "100%"})
        root_tables = [t for t in tables if "BoxContent" in t.parent.attrs.get("class", [])]
        forum_info_table, title_table, posts_table, footer_table = root_tables

        header_text = forum_info_table.text
        section, board, *_ = split_list(header_text, "|", "|")

        thread_title = title_table.text.strip()
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
                     current_page=current_page, pages=pages, previous_topic_number=previous_id,
                     next_topic_number=next_id)
        return thread

    @classmethod
    def _parse_post_table(cls, post_table, offset=1):
        character_info_container = post_table.find("div", attrs={"class": "PostCharacterText"})
        # First link belongs to character
        char_link = character_info_container.find("a")
        author_name = char_link.text
        position = title = None
        position_info = character_info_container.find("font", attrs={"class": "ff_smallinfo"})
        if position_info and position_info.parent == character_info_container:
            for br in position_info.find_all("br"):
                br.replace_with("\n")
            titles = [title for title in position_info.text.splitlines() if title]
            positions = ["Tutor", "Community Manager", "Customer Support"]
            for _title in titles:
                if _title in positions:
                    position = _title
                else:
                    title = _title
        char_info = character_info_container.find("font", attrs={"class": "ff_infotext"})
        guild_info = char_info.find("font", attrs={"class": "ff_smallinfo"})
        for br in char_info.find_all("br"):
            br.replace_with("\n")
        char_info_text = char_info.text
        info_match = author_info_regex.search(char_info_text)
        world = info_match.group(1)
        vocation = try_enum(Vocation, info_match.group(2))
        level = int(info_match.group(3))
        guild = None
        if guild_info:
            guild_match = guild_regexp.search(guild_info.text)
            guild_name = guild_match.group(2)
            title_match = guild_title_regexp.search(guild_name)
            title = None
            if title_match:
                guild_name = title_match.group(1)
                title = title_match.group(2)
            guild = GuildMembership(name=guild_name, rank=guild_match.group(1), title=title)
        posts = int(author_posts_regex.search(char_info_text).group(1))
        author = PostAuthor(name=author_name, title=title, position=position, world=world, vocation=vocation,
                            level=level, posts=posts, guild=guild)
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
        posted_date = parse_tibia_forum_datetime(dates[0], offset)
        if len(dates) > 1:
            edited_date = parse_tibia_forum_datetime(dates[1], offset)
        post_details = post_table.find('div', attrs={"class": "AdditionalBox"})
        post_number = post_details.text.replace("Post #", "")
        post_id = int(post_number)
        post = ForumPost(author=author, content=content, signature=signature, posted_date=posted_date,
                         edited_date=edited_date, post_id=post_id, title=title, emoticon=emoticon)
        return post


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
        return "<{0.__class__.__name__} author={0.author!r} post_id={0.post_id} date={0.date!r}>".format(self)

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

class ListedBoard(abc.Serializable):
    """Represents a board in the list of boards.

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
        self.name = kwargs.get("name")
        self.board_id = kwargs.get("board_id")
        self.description = kwargs.get("description")
        self.posts = kwargs.get("posts")
        self.threads = kwargs.get("threads")
        self.last_post = kwargs.get("last_post")

    __slots__ = (
        "name",
        "board_id",
        "description",
        "posts",
        "threads",
        "last_post",
    )

    def __repr__(self):
        return "<{0.__class__.__name__} name={0.name!r} board_id={0.board_id} posts={0.posts} threads={0.threads}" \
               " description={0.description!r}>".format(self)

    @classmethod
    def get_world_boards_url(cls):
        return get_tibia_url("forum", "worldboards")

    @classmethod
    def get_trade_boards_url(cls):
        return get_tibia_url("forum", "tradeboards")

    @classmethod
    def get_community_boards_url(cls):
        return get_tibia_url("forum", "communityboards")

    @classmethod
    def get_support_boards_url(cls):
        return get_tibia_url("forum", "supportboards")

    @classmethod
    def list_from_content(cls, content):
        parsed_content = parse_tibiacom_content(content)
        tables = parsed_content.find_all("table", attrs={"width": "100%"})
        _, board_list_table, timezone_table = tables
        _, *board_rows = board_list_table.find_all("tr")
        timezone_text = timezone_table.text
        timezone = timezone_regex.search(timezone_text).group(1)
        offset = 1 if timezone == "CES" else 2
        boards = []
        for board_row in board_rows[:-3]:
            board = cls._parse_board_row(board_row, offset)
            boards.append(board)
        return boards

    @classmethod
    def _parse_board_row(cls, board_row, offset):
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


class ListedThread(abc.Serializable):
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
        The number of pages the thread has.
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
        self.pages = kwargs.get("pages", 1)

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
    )

    def __repr__(self):
        return "<{0.__class__.__name__} title={0.title!r} thread_id={0.thread_id} " \
               "thread_starter={0.thread_starter!r} replies={0.replies} views={0.views}>".format(self)


class PostAuthor(abc.BaseCharacter):
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
        The character's title, if any.
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

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.level = kwargs.get("level")
        self.world = kwargs.get("world")
        self.vocation = kwargs.get("vocation")
        self.title = kwargs.get("title")
        self.position = kwargs.get("position")
        self.guild = kwargs.get("guild")
        self.posts = kwargs.get("posts")
