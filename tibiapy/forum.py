import re

from tibiapy import abc
from tibiapy.utils import parse_tibia_forum_datetime, parse_tibiacom_content

board_id_regex = re.compile(r'boardid=(\d+)')
post_id_regex = re.compile(r'postid=(\d+)')
timezone_regex = re.compile(r'times are (CEST?)')


class ListedBoard:
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

    def __repr__(self):
        return "<{0.__class__.__name__} name={0.name!r} board_id={0.board_id} posts={0.posts} threads={0.threads}" \
               " description={0.description!r}>".format(self)

    @classmethod
    def list_from_content(cls, content):
        parsed_content = parse_tibiacom_content(content)
        tables = parsed_content.find_all("table", attrs={"width": "100%"})
        tables_text = [t.text for t in tables]
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
            last_post_info = last_post_column.find("div", attrs={"class": "LastPostInfo"})
            permalink = last_post_info.find("a")
            link = permalink['href']
            post_id = int(post_id_regex.search(link).group(1))
            date_text = last_post_info.text.replace("\xa0", " ").strip()
            last_post_date = parse_tibia_forum_datetime(date_text, offset)

            last_post_author_tag = last_post_column.find("font")
            author = last_post_author_tag.text.replace("by", "", 1).replace("\xa0", " ").strip()

            last_post = LastPost(author, post_id,last_post_date)

            boards.append(cls(name=name, board_id=board_id, description=description, posts=posts, threads=threads,
                              last_post=last_post))
        pass


class ListedThread:
    """Represents a thread in a forum board.

    Attributes
    ----------
    title: :class:`str`
        The title of the thread.
    thread_started: :class:`str`
        The character that started the thread.
    replies: :class:`int`
        The number of replies.
    views: :class:`int`
        The number of views.
    last_post_by: :class:`name`
        The name of the character that posted the last post.
    last_post_date: :class:`datetime.datetime`
        The date of the last post in this thread.
    emoticon: :class:`str`
        The emoticon used for the thread.
    """
    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.thread_starter = kwargs.get("thread_starter")
        self.replies = kwargs.get("replies")
        self.views = kwargs.get("views")
        self.last_post_by = kwargs.get("last_post_by")
        self.last_post_date = kwargs.get("last_post_date")
        self.status = kwargs.get("status")
        self.emoticon = kwargs.get("emoticon")


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


class ForumThread:
    """Represents a forum thread.

    Attributes
    ----------
    title: :class:`str`
        The title of the thread.
    thread_number: :class:`int`
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


class LastPost:
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

    def __repr__(self):
        return "<{0.__class__.__name__} author={0.author!r} post_id={0.post_id} date={0.date!r}>".format(self)
