from __future__ import annotations

from typing import TYPE_CHECKING

from tibiapy.models.forum import CMPostArchive, CMPost, ForumAnnouncement, ForumBoard, ForumThread

if TYPE_CHECKING:
    from typing_extensions import Self


class CMPostArchiveBuilder:
    def __init__(self):
        self._from_date = None
        self._to_date = None
        self._current_page = 1
        self._total_pages = 1
        self._results_count = 0
        self._entries = []

    def from_date(self, from_date) -> Self:
        self._from_date = from_date
        return self

    def to_date(self, to_date) -> Self:
        self._to_date = to_date
        return self

    def current_page(self, current_page) -> Self:
        self._current_page = current_page
        return self

    def total_pages(self, total_pages) -> Self:
        self._total_pages = total_pages
        return self

    def results_count(self, results_count) -> Self:
        self._results_count = results_count
        return self

    def entries(self, entries) -> Self:
        self._entries = entries
        return self

    def add_entry(self, entry) -> Self:
        self._entries.append(entry)
        return self

    def build(self) -> CMPostArchive:
        return CMPostArchive(
            from_date=self._from_date,
            to_date=self._to_date,
            current_page=self._current_page,
            total_pages=self._total_pages,
            results_count=self._results_count,
            entries=self._entries,
        )


class CMPostBuilder:
    def __init__(self):
        self._post_id = None
        self._posted_on = None
        self._board = None
        self._thread_title = None

    def post_id(self, post_id) -> Self:
        self._post_id = post_id
        return self

    def posted_on(self, posted_on) -> Self:
        self._posted_on = posted_on
        return self

    def board(self, board) -> Self:
        self._board = board
        return self

    def thread_title(self, thread_title) -> Self:
        self._thread_title = thread_title
        return self

    def build(self) -> CMPost:
        return CMPost(
            post_id=self._post_id,
            posted_on=self._posted_on,
            board=self._board,
            thread_title=self._thread_title,
        )


class ForumAnnouncementBuilder:
    def __init__(self):
        self._announcement_id = None
        self._board = None
        self._section = None
        self._board_id = None
        self._section_id = None
        self._author = None
        self._title = None
        self._content = None
        self._from_date = None
        self._to_date = None

    def announcement_id(self, announcement_id) -> Self:
        self._announcement_id = announcement_id
        return self

    def board(self, board) -> Self:
        self._board = board
        return self

    def section(self, section) -> Self:
        self._section = section
        return self

    def board_id(self, board_id) -> Self:
        self._board_id = board_id
        return self

    def section_id(self, section_id) -> Self:
        self._section_id = section_id
        return self

    def author(self, author) -> Self:
        self._author = author
        return self

    def title(self, title) -> Self:
        self._title = title
        return self

    def content(self, content) -> Self:
        self._content = content
        return self

    def from_date(self, from_date) -> Self:
        self._from_date = from_date
        return self

    def to_date(self, to_date) -> Self:
        self._to_date = to_date
        return self

    def build(self) -> ForumAnnouncement:
        return ForumAnnouncement(
            announcement_id=self._announcement_id,
            board=self._board,
            section=self._section,
            board_id=self._board_id,
            section_id=self._section_id,
            author=self._author,
            title=self._title,
            content=self._content,
            start_date=self._from_date,
            end_date=self._to_date,
        )


class _BaseBoardBuilder:
    def __init__(self):
        self._board_id = 0

    def board_id(self, board_id: int) -> Self:
        self._board_id = board_id
        return self


class ForumBoardBuilder(_BaseBoardBuilder):
    def __init__(self):
        super().__init__()
        self._name = None
        self._section = None
        self._section_id = None
        self._current_page = 1
        self._total_pages = 1
        self._age = 0
        self._announcements = []
        self._entries = []

    def name(self, name) -> Self:
        self._name = name
        return self

    def section(self, section) -> Self:
        self._section = section
        return self

    def section_id(self, section_id) -> Self:
        self._section_id = section_id
        return self

    def current_page(self, current_page) -> Self:
        self._current_page = current_page
        return self

    def total_pages(self, total_pages) -> Self:
        self._total_pages = total_pages
        return self

    def age(self, age) -> Self:
        self._age = age
        return self

    def announcements(self, announcements) -> Self:
        self._announcements = announcements
        return self

    def add_announcement(self, announcement) -> Self:
        self._announcements.append(announcement)
        return self

    def entries(self, entries) -> Self:
        self._entries = entries
        return self

    def add_entry(self, entry) -> Self:
        self._entries.append(entry)
        return self

    def build(self) -> ForumBoard:
        return ForumBoard(
            board_id=self._board_id,
            name=self._name,
            section=self._section,
            section_id=self._section_id,
            current_page=self._current_page,
            total_pages=self._total_pages,
            age=self._age,
            announcements=self._announcements,
            entries=self._entries,
        )


class ForumThreadBuilder:
    def __init__(self):
        self._title = None
        self._thread_id = 0
        self._board = None
        self._board_id = None
        self._section = None
        self._section_id = None
        self._previous_topic_number = None
        self._next_topic_number = None
        self._total_pages = 1
        self._current_page = 1
        self._entries = []
        self._golden_frame = False
        self._anchored_post = None

    def title(self, title) -> Self:
        self._title = title
        return self

    def thread_id(self, thread_id) -> Self:
        self._thread_id = thread_id
        return self

    def board(self, board) -> Self:
        self._board = board
        return self

    def board_id(self, board_id) -> Self:
        self._board_id = board_id
        return self

    def section(self, section) -> Self:
        self._section = section
        return self

    def section_id(self, section_id) -> Self:
        self._section_id = section_id
        return self

    def previous_topic_number(self, previous_topic_number) -> Self:
        self._previous_topic_number = previous_topic_number
        return self

    def next_topic_number(self, next_topic_number) -> Self:
        self._next_topic_number = next_topic_number
        return self

    def total_pages(self, total_pages) -> Self:
        self._total_pages = total_pages
        return self

    def current_page(self, current_page) -> Self:
        self._current_page = current_page
        return self

    def entries(self, entries) -> Self:
        self._entries = entries
        return self

    def golden_frame(self, golden_frame) -> Self:
        self._golden_frame = golden_frame
        return self

    def anchored_post(self, anchored_post) -> Self:
        self._anchored_post = anchored_post
        return self

    def add_entry(self, entry) -> Self:
        self._entries.append(entry)
        return self

    def build(self) -> ForumThread:
        return ForumThread(
            title=self._title,
            thread_id=self._thread_id,
            board=self._board,
            board_id=self._board_id,
            section=self._section,
            section_id=self._section_id,
            previous_topic_number=self._previous_topic_number,
            next_topic_number=self._next_topic_number,
            total_pages=self._total_pages,
            current_page=self._current_page,
            entries=self._entries,
            golden_frame=self._golden_frame,
            anchored_post=self._anchored_post,
        )
