"""Models related to the forums."""
import datetime
from typing import Any, List, Optional

from tibiapy.enums import ThreadStatus, Vocation
from tibiapy.models import GuildMembership
from tibiapy.models.base import BaseCharacter, BaseModel
from tibiapy.models.pagination import PaginatedWithUrl
from tibiapy.urls import (get_character_url, get_cm_post_archive_url, get_forum_announcement_url, get_forum_board_url,
                          get_forum_post_url, get_forum_section_url, get_forum_thread_url)

__all__ = (
    "AnnouncementEntry",
    "BaseAnnouncement",
    "BaseBoard",
    "BasePost",
    "BaseThread",
    "BoardEntry",
    "CMPost",
    "CMPostArchive",
    "ForumAnnouncement",
    "ForumAuthor",
    "ForumBoard",
    "ForumEmoticon",
    "ForumPost",
    "ForumSection",
    "ForumThread",
    "LastPost",
    "ThreadEntry",
)


class BaseAnnouncement(BaseModel):
    """Base class for all announcement classes.

    Implement common properties and methods for announcements.

    The following implement this class:

    - :class:`.ForumAnnouncement`
    - :class:`.AnnouncementEntry`
    """

    announcement_id: int
    """The ID of the announcement."""

    def __eq__(self, other: Any):
        if isinstance(other, self.__class__):
            return other.announcement_id == self.announcement_id

        return False

    @property
    def url(self) -> str:
        """Get the URL to this announcement."""
        return get_forum_announcement_url(self.announcement_id)


class BaseBoard(BaseModel):
    """Base class for all board classes.

    Implements common properties and methods for boards.

    The following implement this class:

    - :class:`.ForumBoard`
    - :class:`.BoardEntry`
    """

    board_id: int
    """The ID of the board."""

    @property
    def url(self) -> str:
        """The URL of this board."""
        return get_forum_board_url(self.board_id)

    def __eq__(self, o: object) -> bool:
        """Two boards are considered equal if their ids are equal."""
        return self.board_id == o.board_id if isinstance(o, self.__class__) else False


class BasePost(BaseModel):
    """Base class for post classes.

    The following implement this class:

    - :class:`.CMPost`
    - :class:`.ForumPost`
    - :class:`.LastPost`
    """

    post_id: int
    """The internal ID of the post."""

    def __eq__(self, other: Any):
        if isinstance(other, self.__class__):
            return self.post_id == other.post_id

        return False

    @property
    def url(self) -> str:
        """Get the URL to this specific post."""
        return get_forum_post_url(self.post_id)


class BaseThread(BaseModel):
    """Base class for thread classes.

    The following implement this class:

    - :class:`.ThreadEntry`
    - :class:`.ForumThread`
    """

    thread_id: int
    """The internal ID of the thread."""

    @property
    def url(self) -> str:
        """:class:`str`: The URL to the thread in Tibia.com."""
        return get_forum_thread_url(self.thread_id)

    def __eq__(self, other: Any):
        if isinstance(other, self.__class__):
            return self.thread_id == other.thread_id

        return False


class CMPost(BasePost):
    """Represents a CM Post entry."""

    post_id: int
    """The ID of the post."""
    posted_on: datetime.datetime
    """The date when the post was made."""
    board: str
    """The name of the board where the post was made."""
    thread_title: str
    """The title of the thread where the post is."""


class CMPostArchive(PaginatedWithUrl[CMPost]):
    """Represents the CM Post Archive.

    The CM Post Archive is a collection of posts made in the forum by community managers.
    """

    from_date: datetime.date
    """The start date of the displayed posts."""
    to_date: datetime.date
    """The end date of the displayed posts."""
    entries: List[CMPost] = []
    """The list of posts for the selected range."""

    @property
    def url(self) -> str:
        """The URL of the CM Post Archive with the current parameters."""
        return get_cm_post_archive_url(self.from_date, self.to_date, self.current_page)

    def get_page_url(self, page: int) -> str:
        """Get the URL of the CM Post Archive at a specific page, with the current date parameters.

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

        return get_cm_post_archive_url(self.from_date, self.to_date, page)


class ForumEmoticon(BaseModel):
    """Represents a forum's emoticon."""

    name: str
    """The emoticon's name."""
    url: str
    """The URL to the emoticon's image."""


class LastPost(BasePost):
    """Represents a forum thread."""

    author: str
    """The name of the character that made the last post."""
    post_id: int
    """The internal id of the post."""
    posted_on: datetime.datetime
    """The date when the last post was made."""
    is_author_deleted: bool
    """Whether the last post's author is a character that is already deleted."""
    is_author_traded: bool
    """Whether the last post's author was recently traded."""

    @property
    def author_url(self) -> str:
        """The URL to the author's character information page."""
        return get_character_url(self.author)


class ForumAuthor(BaseCharacter):
    """Represents a post's author."""

    name: str
    """The name of the character, author of the post."""
    level: Optional[int] = None
    """The level of the character."""
    world: Optional[str] = None
    """The world the character belongs to."""
    position: Optional[str] = None
    """The character's position, if any."""
    title: Optional[str] = None
    """The character's selected title, if any."""
    vocation: Optional[Vocation] = None
    """The vocation of the character."""
    guild: Optional[GuildMembership] = None
    """The guild the author belongs to, if any."""
    posts: Optional[int] = None
    """The number of posts this character has made."""
    is_author_deleted: bool = False
    """Whether the author is deleted or not."""
    is_author_traded: bool = False
    """Whether the author is traded or not."""


class AnnouncementEntry(BaseAnnouncement):
    """Represents an announcement in the forum boards."""

    title: str
    """The title of the announcement."""
    announcement_id: int
    """The internal id of the announcement."""
    announcement_author: str
    """The character that made the announcement."""


class BoardEntry(BaseBoard):
    """Represents a board in the list of boards.

    This is the board information available when viewing a section (e.g. World, Trade, Community)
    """

    name: str
    """The name of the board."""
    board_id: int
    """The board's internal id."""
    description: str
    """The description of the board."""
    posts: int
    """The number of posts in this board."""
    threads: int
    """The number of threads in this board."""
    last_post: Optional[LastPost] = None
    """The information of the last post made in this board."""


class ForumSection(BaseModel):
    """A forum section, containing a list of boards."""

    section_id: int
    """The internal ID of the section."""
    entries: List[BoardEntry]
    """The boards in the forum section."""

    @property
    def url(self) -> str:
        """The URL to this forum section."""
        return get_forum_section_url(self.section_id)


class ThreadEntry(BaseThread):
    """Represents a thread in a forum board."""

    title: str
    """The title of the thread."""
    thread_id: int
    """The internal id of the thread."""
    thread_starter: str
    """The character that started the thread."""
    thread_starter_traded: bool
    """Whether the thread starter was recently traded or not."""
    thread_starter_deleted: bool
    """Whether the thread starter was recently deleted or not."""
    replies: int
    """The number of replies."""
    views: int
    """The number of views."""
    last_post: Optional[LastPost] = None
    """The information of the last post made in this board."""
    status: ThreadStatus
    """The status of the thread."""
    status_icon: str
    """The URL of the icon displayed as status."""
    emoticon: Optional[ForumEmoticon] = None
    """The emoticon used for the thread."""
    total_pages: int
    """The number of pages the thread has."""
    golden_frame: bool = False
    """Whether the thread has a gold frame or not.

    In the Proposals board, the gold frame indicates that a staff member has replied in the thread."""


class ForumAnnouncement(BaseAnnouncement):
    """Represents a forum announcement.

    These are a special kind of thread that are shown at the top of boards.
    They cannot be replied to, and they show no view counts.
    """

    announcement_id: int
    """The id of the announcement."""
    board: str
    """The board this thread belongs to."""
    section: str
    """The board section this thread belongs to."""
    board_id: int
    """The internal id of the board the post is in."""
    section_id: int
    """The internal id of the section the post is in."""
    author: ForumAuthor
    """The author of the announcement."""
    title: str
    """The title of the announcement."""
    content: str
    """The HTML content of the announcement."""
    start_date: datetime.datetime
    """The starting date of the announcement."""
    end_date: datetime.datetime
    """The end date of the announcement."""


class ForumBoard(PaginatedWithUrl[ThreadEntry], BaseBoard):
    """Represents a forum's board."""

    name: str
    """The name of the board."""
    section: str
    """The section of the board."""
    section_id: int
    """The internal ID of the section the board belongs to."""
    age: int
    """The maximum age of the displayed threads, in days.

    -1 means all threads will be shown."""
    announcements: List[AnnouncementEntry]
    """The list of announcements currently visible."""
    entries: List[ThreadEntry]
    """The list of threads currently visible."""

    def get_page_url(self, page: int) -> str:
        """Get the URL to a given page of the board.

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

        return get_forum_board_url(self.board_id, page, self.age)


class ForumPost(BasePost):
    """Represents a forum post."""

    author: ForumAuthor
    """The author of the post."""
    emoticon: Optional[ForumEmoticon] = None
    """The emoticon selected for the post."""
    title: Optional[str] = None
    """The title of the post."""
    content: str
    """The content of the post."""
    signature: Optional[str] = None
    """The signature of the post."""
    post_id: int
    """The id of the post."""
    posted_date: datetime.datetime
    """The date when the post was made."""
    edited_date: Optional[datetime.datetime] = None
    """The date when the post was last edited, if applicable."""
    edited_by: Optional[str] = None
    """The character that edited the post.

    This is usually the same author, but in some occasions staff members edit the posts of others."""
    golden_frame: bool = False


class ForumThread(PaginatedWithUrl[ForumPost], BaseThread):
    """Represents a forum thread."""

    title: str
    """The title of the thread."""
    board: str
    """The board this thread belongs to."""
    board_id: int
    """The ID of the board this thread belongs to."""
    section: str
    """The board section this thread belongs to."""
    section_id: int
    """The ID of the board section this thread belongs to."""
    previous_topic_number: Optional[int] = None
    """The number of the previous topic."""
    next_topic_number: Optional[int] = None
    """The number of the next topic."""
    entries: List[ForumPost] = []
    """The list of posts the thread has."""
    golden_frame: bool = False
    """Whether the thread has a golden frame or not.

    In the Proposals board,a golden frame means the thread has a reply by a staff member."""
    anchored_post: Optional[ForumPost] = None
    """The post where the page is anchored to, if any.

    When a post is fetched directly, the thread that contains it is displayed, anchored to the specific post."""

    @property
    def previous_thread_url(self) -> str:
        """The URL to the previous topic of the board, if there's any."""
        return get_forum_thread_url(self.previous_topic_number) if self.previous_topic_number else None

    @property
    def next_thread_url(self) -> str:
        """The URL to the next topic of the board, if there's any."""
        return get_forum_thread_url(self.next_topic_number) if self.next_topic_number else None

    def get_page_url(self, page: int) -> str:
        """Get the URL to a given page of the board.

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

        return get_forum_thread_url(self.thread_id, page)
