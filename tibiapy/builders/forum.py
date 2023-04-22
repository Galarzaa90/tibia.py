from tibiapy.models.forum import CMPostArchive, CMPost, ForumAnnouncement, ForumBoard, ForumThread


class CMPostArchiveBuilder:
    def __init__(self):
        self._start_date = None
        self._end_date = None
        self._current_page = 1
        self._total_pages = 1
        self._results_count = 0
        self._entries = []

    def start_date(self, start_date):
        self._start_date = start_date
        return self

    def end_date(self, end_date):
        self._end_date = end_date
        return self

    def current_page(self, current_page):
        self._current_page = current_page
        return self

    def total_pages(self, total_pages):
        self._total_pages = total_pages
        return self

    def results_count(self, results_count):
        self._results_count = results_count
        return self

    def entries(self, entries):
        self._entries = entries
        return self

    def add_entry(self, entry):
        self._entries.append(entry)
        return self

    def build(self):
        return CMPostArchive(
            start_date=self._start_date,
            end_date=self._end_date,
            current_page=self._current_page,
            total_pages=self._total_pages,
            results_count=self._results_count,
            entries=self._entries,
        )


class CMPostBuilder:
    def __init__(self, **kwargs):
        self._post_id = kwargs.get("post_id")
        self._date = kwargs.get("date")
        self._board = kwargs.get("board")
        self._thread_title = kwargs.get("thread_title")

    def post_id(self, post_id):
        self._post_id = post_id
        return self

    def date(self, date):
        self._date = date
        return self

    def board(self, board):
        self._board = board
        return self

    def thread_title(self, thread_title):
        self._thread_title = thread_title
        return self

    def build(self):
        return CMPost(
            post_id=self._post_id,
            date=self._date,
            board=self._board,
            thread_title=self._thread_title,
        )


class ForumAnnouncementBuilder:
    def __init__(self, **kwargs):
        self._announcement_id = kwargs.get("announcement_id")
        self._board = kwargs.get("board")
        self._section = kwargs.get("section")
        self._board_id = kwargs.get("board_id")
        self._section_id = kwargs.get("section_id")
        self._author = kwargs.get("author")
        self._title = kwargs.get("title")
        self._content = kwargs.get("content")
        self._start_date = kwargs.get("start_date")
        self._end_date = kwargs.get("end_date")

    def announcement_id(self, announcement_id):
        self._announcement_id = announcement_id
        return self

    def board(self, board):
        self._board = board
        return self

    def section(self, section):
        self._section = section
        return self

    def board_id(self, board_id):
        self._board_id = board_id
        return self

    def section_id(self, section_id):
        self._section_id = section_id
        return self

    def author(self, author):
        self._author = author
        return self

    def title(self, title):
        self._title = title
        return self

    def content(self, content):
        self._content = content
        return self

    def start_date(self, start_date):
        self._start_date = start_date
        return self

    def end_date(self, end_date):
        self._end_date = end_date
        return self


    def build(self):
        return ForumAnnouncement(
            announcement_id=self._announcement_id,
            board=self._board,
            section=self._section,
            board_id=self._board_id,
            section_id=self._section_id,
            author=self._author,
            title=self._title,
            content=self._content,
            start_date=self._start_date,
            end_date=self._end_date,
        )


class _BaseBoardBuilder:
    def __init__(self):
        self._board_id = 0

    def board_id(self, board_id: int):
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

    def name(self, name):
        self._name = name
        return self

    def section(self, section):
        self._section = section
        return self

    def section_id(self, section_id):
        self._section_id = section_id
        return self

    def current_page(self, current_page):
        self._current_page = current_page
        return self

    def total_pages(self, total_pages):
        self._total_pages = total_pages
        return self

    def age(self, age):
        self._age = age
        return self

    def announcements(self, announcements):
        self._announcements = announcements
        return self

    def add_announcement(self, announcement):
        self._announcements.append(announcement)
        return self

    def entries(self, entries):
        self._entries = entries
        return self

    def add_entry(self, entry):
        self._entries.append(entry)
        return self

    def build(self):
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
    def __init__(self, **kwargs):
        self._title = kwargs.get("title")
        self._thread_id = kwargs.get("thread_id") or 0
        self._board = kwargs.get("board")
        self._section = kwargs.get("section")
        self._previous_topic_number = kwargs.get("previous_topic_number") or 0
        self._next_topic_number = kwargs.get("next_topic_number") or 0
        self._total_pages = kwargs.get("total_pages") or 1
        self._current_page = kwargs.get("current_page") or 1
        self._posts = kwargs.get("posts") or []
        self._golden_frame = kwargs.get("golden_frame") or False
        self._anchored_post = kwargs.get("anchored_post")

    def title(self, title):
        self._title = title
        return self

    def thread_id(self, thread_id):
        self._thread_id = thread_id
        return self

    def board(self, board):
        self._board = board
        return self

    def section(self, section):
        self._section = section
        return self

    def previous_topic_number(self, previous_topic_number):
        self._previous_topic_number = previous_topic_number
        return self

    def next_topic_number(self, next_topic_number):
        self._next_topic_number = next_topic_number
        return self

    def total_pages(self, total_pages):
        self._total_pages = total_pages
        return self

    def current_page(self, current_page):
        self._current_page = current_page
        return self

    def posts(self, posts):
        self._posts = posts
        return self

    def golden_frame(self, golden_frame):
        self._golden_frame = golden_frame
        return self

    def anchored_post(self, anchored_post):
        self._anchored_post = anchored_post
        return self

    def add_post(self, post):
        self._posts.append(post)
        return self

    def build(self):
        return ForumThread(
            title=self._title,
            thread_id=self._thread_id,
            board=self._board,
            section=self._section,
            previous_topic_number=self._previous_topic_number,
            next_topic_number=self._next_topic_number,
            total_pages=self._total_pages,
            current_page=self._current_page,
            posts=self._posts,
            golden_frame=self._golden_frame,
            anchored_post=self._anchored_post,
        )