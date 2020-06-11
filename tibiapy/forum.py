import re

from tibiapy import abc
from tibiapy.utils import get_tibia_url, parse_tibia_forum_datetime, parse_tibiacom_content, split_list

board_id_regex = re.compile(r'boardid=(\d+)')
post_id_regex = re.compile(r'postid=(\d+)')
thread_id_regex = re.compile(r'threadid=(\d+)')
timezone_regex = re.compile(r'times are (CEST?)')


class ListedBoard(abc.Serializable):
    """Represents a board in the list of boards.

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
            columns = board_row.find_all("td")
            name_column = columns[1]
            board_link_tag = name_column.find("a")
            description_tag = name_column.find("font")
            description = description_tag.text
            name = board_link_tag.text
            link = board_link_tag['href']
            board_id = int(board_id_regex.search(link).group(1))

            posts_column = columns[2]
            posts = int(posts_column.text)

            threads_column = columns[3]
            threads = int(threads_column.text)

            last_post_column = columns[4]
            last_post = LastPost._parse_column(last_post_column)

            boards.append(cls(name=name, board_id=board_id, description=description, posts=posts, threads=threads,
                              last_post=last_post))
        return boards


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
    emoticon: :class:`str`
        The emoticon used for the thread.
    """
    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.thread_id = kwargs.get("thread_id")
        self.thread_starter = kwargs.get("thread_starter")
        self.replies = kwargs.get("replies")
        self.views = kwargs.get("views")
        self.last_post = kwargs.get("last_post")
        self.status = kwargs.get("status")
        self.emoticon = kwargs.get("emoticon")

    __slots__ = (
        "title",
        "thread_id",
        "thread_starter",
        "replies",
        "views",
        "last_post",
        "status",
        "emoticon",
    )

    def __repr__(self):
        return "<{0.__class__.__name__} title={0.title!r} thread_id={0.thread_id} " \
               "thread_starter={0.thread_starter!r} replies={0.replies} views={0.views}>".format(self)

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
    threads: list of :class:`ListedThread`
        The list of threads currently visible.
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.section = kwargs.get("section")
        self.displayed_range = kwargs.get("displayed_range")
        self.current_page = kwargs.get("current_page")
        self.pages = kwargs.get("pages")
        self.threads = kwargs.get("threads")

    __slots__ = (
        "name",
        "section",
        "displayed_range",
        "current_page",
        "pages",
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
        header_table, time_selector_table, threads_table, timezone_table, boardjump_table = tables
        header_text = header_table.text.strip()
        section, name = split_list(header_text, "|", "|")
        thread_rows = threads_table.find_all("tr")
        entries = []
        for thread_row in thread_rows[2:]:
            columns = thread_row.find_all("td")
            if len(columns) != 7:
                continue
            thread_column = columns[2]
            title = thread_column.text.strip()
            thread_link = thread_column.find("a")
            thread_id = int(thread_id_regex.search(thread_link["href"]).group(1))

            thread_starter_column = columns[3]
            thread_starter = thread_starter_column.text.strip()

            replies_column = columns[4]
            replies = int(replies_column.text)

            views_column = columns[5]
            views = int(views_column.text)

            last_post_column = columns[6]
            last_post = LastPost._parse_column(last_post_column)

            thread = ListedThread(title=title, thread_id=thread_id, thread_starter=thread_starter, replies=replies,
                                  views=views, last_post=last_post)
            entries.append(thread)

        board = cls(name=name, section=section, threads=entries)
        return board


class ForumAuthor(abc.BaseCharacter):
    """Represents a post's author.

    Attributes
    ----------
    name: :class:`str`
        The name of the character, author of the post.
    level: :class:`int`
        The level of the character.
    vocation: :class:`Vocation`
        The vocation of the character.
    guild: :class:`GuildMembership`
        The guild the author belongs to, if any.
    posts: :class:`int`
        The number of posts this character has made.

    """
    def __init__(self, **kwargs):
        pass


class ForumPost:
    """Represent's a forum post.

    Attributes
    ----------
    author: :class:`ForumAuthor`
        The author of the post.
    title: :class:`str`, optional
        The title of the post.
    content: :class:`str`
        The content of the post.
    emoticon: :Class:`str`
        The URL to the post's emoticon.
    post_number: :class:`int`
        The number of the post.
    posted_date: :class:`datetime.datetime`
        The date when the post was made.
    edited_date: :class:`datetime.datetime`, optional
        The date when the post was last edited, if applicable.
    """
    def __init__(self, **kwargs):
        pass


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
    board_category: :class:`str`
        The board category this thread belongs to.
    previous_topic_number: :class:`int`
        The number of the previous topic.
    next_topic_number: :class:`int`
        The number of the next topic.
    pages: :class:`int`
        The number of pages this thread has.
    current_page: :class:`int`
        The page being viewed.
    """
    def __init__(self, **kwargs):
        pass

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
