"""Events related to the forum section."""
from __future__ import annotations

import datetime
import re
import urllib.parse
from typing import Optional, TYPE_CHECKING

from tibiapy import InvalidContentError, errors
from tibiapy.builders import CMPostArchiveBuilder, ForumAnnouncementBuilder, ForumBoardBuilder, ForumThreadBuilder
from tibiapy.enums import ThreadStatus, Vocation
from tibiapy.models import (AnnouncementEntry, BoardEntry, CMPost, CMPostArchive, ForumAnnouncement, ForumAuthor,
                            ForumBoard, ForumEmoticon, ForumPost, ForumSection, ForumThread, GuildMembership, LastPost,
                            ThreadEntry)
from tibiapy.utils import (clean_text, convert_line_breaks, get_rows, parse_form_data, parse_integer, parse_link_info,
                           parse_pagination,
                           parse_tables_map, parse_tibia_datetime, parse_tibia_forum_datetime, parse_tibiacom_content,
                           split_list, try_enum)

if TYPE_CHECKING:
    import bs4

__all__ = (
    "CMPostArchiveParser",
    "ForumAnnouncementParser",
    "ForumBoardParser",
    "ForumSectionParser",
    "ForumThreadParser",
)

timezone_regex = re.compile(r"times are (CES?T)")
filename_regex = re.compile(r"(\w+.gif)")
pages_regex = re.compile(r"\(Pages[^)]+\)")

author_info_regex = re.compile(r"Inhabitant of (\w+)\nVocation: ([\w\s]+)\nLevel: (\d+)")
author_posts_regex = re.compile(r"Posts: (\d+)")
guild_regexp = re.compile(r"([\s\w()]+)\sof the\s(.+)")
guild_title_regexp = re.compile(r"([^(]+)\s\(([^)]+)\)")
post_dates_regex = re.compile(r"(\d{2}\.\d{2}\.\d{4}\s\d{2}:\d{2}:\d{2})")
edited_by_regex = re.compile(r"Edited by (.*) on \d{2}")

signature_separator = "________________"

FORUM_POSITIONS = ["Tutor", "Community Manager", "Customer Support", "Programmer", "Game Content Designer", "Tester"]
"""Special positions displayed for characters in the forums."""


class CMPostArchiveParser:
    """Parser for the content of the CM Post Archive page in Tibia.com."""

    @classmethod
    def from_content(cls, content: str) -> CMPostArchive:
        """Parse the content of the CM Post Archive page from Tibia.com.

        Parameters
        ----------
        content:
            The HTML content of the CM Post Archive in Tibia.com

        Returns
        -------
            The CM Post archive found in the page.

        Raises
        ------
        InvalidContent
            If content is not the HTML content of the CM Post Archive in Tibia.com
        """
        parsed_content = parse_tibiacom_content(content)

        form = parsed_content.select_one("form")
        try:
            (start_month_selector, start_day_selector, start_year_selector,
             end_month_selector, end_day_selector, end_year_selector) = form.select("select")
            start_date = cls._get_selected_date(start_month_selector, start_day_selector, start_year_selector)
            end_date = cls._get_selected_date(end_month_selector, end_day_selector, end_year_selector)
        except (AttributeError, ValueError) as e:
            raise errors.InvalidContentError("content does not belong to the CM Post Archive in Tibia.com", e) from e

        builder = CMPostArchiveBuilder().from_date(start_date).to_date(end_date)
        table = parsed_content.select_one("table.Table3")
        if not table:
            return builder.build()

        inner_table_container = table.select_one("div.InnerTableContainer")
        inner_table = inner_table_container.select_one("table")
        inner_table_rows = get_rows(inner_table)
        inner_table_rows = [e for e in inner_table_rows if e.parent == inner_table]
        table_content = inner_table_container.select_one("table.TableContent")

        header_row, *rows = get_rows(table_content)

        for row in rows:
            columns = row.select("td")
            date_column = columns[0]
            date = parse_tibia_datetime(clean_text(date_column))
            board_thread_column = columns[1]
            convert_line_breaks(board_thread_column)
            board, thread = board_thread_column.text.splitlines()
            link_column = columns[2]
            post_link_tag = link_column.select_one("a")
            post_link = parse_link_info(post_link_tag)
            post_id = int(post_link["query"]["postid"])
            builder.add_entry(CMPost(posted_on=date, board=board, thread_title=thread, post_id=post_id))

        if not rows:
            return builder.build()

        page, total_pages, results = parse_pagination(inner_table_rows[-1])
        builder.current_page(page).total_pages(total_pages).results_count(results)
        return builder.build()

    # endregion

    # region Private Methods

    @classmethod
    def _get_selected_date(
            cls,
            month_selector: bs4.Tag,
            day_selector: bs4.Tag,
            year_selector: bs4.Tag,
    ) -> Optional[datetime.date]:
        """Get the date made from the selected options in the selectors.

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
        selected_month = month_selector.select_one("option[selected]") or month_selector.select_one("option")
        selected_day = day_selector.select_one("option[selected]") or day_selector.select_one("option")
        selected_year = year_selector.select_one("option[selected]") or year_selector.select_one("option")
        try:
            return datetime.date(year=int(selected_year["value"]), month=int(selected_month["value"]),
                                 day=int(selected_day["value"]))
        except ValueError:
            return None
    # endregion


class ForumSectionParser:
    """Parser for forum sections, such as world boards, trade boards, etcetera."""

    @classmethod
    def from_content(cls, content: str) -> ForumSection:
        """Parse a forum section from Tibia.com.

        Parameters
        ----------
        content:
            The HTML content from Tibia.com

        Returns
        -------
            The forum section found in the page.
        """
        parsed_content = parse_tibiacom_content(content)
        tables = parse_tables_map(parsed_content)
        if "Boards" not in tables:
            raise InvalidContentError("Boards table not found.")

        rows = tables["Boards"].select("table.TableContent > tr:not(.LabelH)")
        section_link = parse_link_info(parsed_content.select_one("p.ForumWelcome > a"))
        redirect = section_link["query"]["redirect"]
        redirect_qs = urllib.parse.parse_qs(urllib.parse.urlparse(redirect).query)
        section_id = redirect_qs["sectionid"][0]
        time_label = parsed_content.select_one("div.CurrentTime")
        offset = 2 if "CEST" in time_label.text else 1
        boards = [board for row in rows if (board := cls._parse_board_row(row, offset)) is not None]
        return ForumSection(section_id=int(section_id), entries=boards)

    @classmethod
    def _parse_board_row(cls, board_row: bs4.Tag, offset: int = 1) -> Optional[BoardEntry]:
        """Parse a row containing a board and extracts its information.

        Parameters
        ----------
        board_row: :class:`bs4.Tag`
            The row's parsed content.
        offset: :class:`int`
            Since the displayed dates do not contain information, it is neccessary to extract the used timezone from
            somewhere else and pass it to this method to adjust them accordingly.

        Returns
        -------
        :class:`BoardEntry`
            The board contained in this row.
        """
        columns = board_row.select("td")
        # Second Column: Name and description
        if len(columns) < 5:
            return None

        name_column = columns[1]
        board_link_tag = name_column.select_one("a")
        description_tag = name_column.select_one("font")
        description = description_tag.text
        board_link = parse_link_info(board_link_tag)
        name = board_link["text"]
        board_id = int(board_link["query"]["boardid"])
        # Third Column: Post count
        posts_column = columns[2]
        posts = parse_integer(posts_column.text)
        # Fourth Column: View count
        threads_column = columns[3]
        threads = parse_integer(threads_column.text)
        # Fifth Column: Last post information
        last_post_column = columns[4]
        last_post = LastPostParser._parse_column(last_post_column, offset)
        return BoardEntry(name=name, board_id=board_id, description=description, posts=posts, threads=threads,
                          last_post=last_post)


class ForumAnnouncementParser:
    """Parser for forum announcements posted by CipSoft."""

    @classmethod
    def from_content(cls, content: str, announcement_id: int = 0) -> Optional[ForumAnnouncement]:
        """Parse the content of an announcement's page from Tibia.com.

        Parameters
        ----------
        content:
            The HTML content of an announcement in Tibia.com
        announcement_id:
            The id of the announcement. Since there is no way to obtain the id from the page,
            the id may be passed to assign.

        Returns
        -------
            The announcement contained in the page or :obj:`None` if not found.

        Raises
        ------
        InvalidContent
            If content is not the HTML content of an announcement page in Tibia.com
        """
        parsed_content = parse_tibiacom_content(content)

        forum_breadcrumbs = parsed_content.select_one("div.ForumBreadCrumbs")
        if not forum_breadcrumbs:
            message_box = parsed_content.select_one("div.TableContainer")
            if not message_box or "error" not in message_box.text.lower():
                raise errors.InvalidContentError("content is not a Tibia.com forum announcement.")

            return None

        section_link, board_link, *_ = forum_breadcrumbs.select("a")
        section_link_info = parse_link_info(section_link)
        section = section_link_info["text"]
        section_id = parse_integer(section_link_info["query"]["sectionid"])
        board_link_info = parse_link_info(board_link)
        board = board_link_info["text"]
        board_id = parse_integer(board_link_info["query"]["boardid"])

        builder = (ForumAnnouncementBuilder()
                   .section(section)
                   .section_id(section_id)
                   .board(board)
                   .board_id(board_id)
                   .announcement_id(announcement_id))

        times_container = parsed_content.select_one("div.ForumContentFooterLeft")
        offset = 2 if times_container.text == "CEST" else 1

        post_container = parsed_content.select_one("div.ForumPost")
        character_info_container = post_container.select_one("div.PostCharacterText")
        builder.author(ForumAuthorParser._parse_author_table(character_info_container))
        post_text_container = post_container.select_one("div.PostText")
        title_tag = post_text_container.select_one("b")
        builder.title(title_tag.text)
        dates_container = post_text_container.select_one("font")
        dates = post_dates_regex.findall(dates_container.text)
        announcement_content = post_text_container.encode_contents().decode()
        _, announcement_content = announcement_content.split("<hr/>", 1)
        builder.content(announcement_content)

        start_date, end_date = (parse_tibia_forum_datetime(date, offset) for date in dates)
        builder.from_date(start_date).to_date(end_date)
        return builder.build()


class ForumAuthorParser:

    @classmethod
    def _parse_author_table(cls, character_info_container: bs4.Tag) -> ForumAuthor:
        """Parse the table containing the author's information.

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
        char_link = character_info_container.select_one("a")
        if not char_link:
            name = character_info_container.text
            deleted = True
            traded = False
            if "(traded)" in name:
                name = name.replace("(traded)", "").strip()
                deleted = False
                traded = True

            return ForumAuthor(name=name, is_author_deleted=deleted, is_author_traded=traded)

        author = ForumAuthor(name=char_link.text)
        char_info = character_info_container.select_one("font.ff_infotext")
        position_info = character_info_container.select_one("font.ff_smallinfo")
        # Position and titles are shown the same way. If we have two, the title is first and then the position.
        # However, if the character only has one of them, there's no way to know which is it unless we validate against
        # possible types
        if position_info and (not char_info or position_info.parent != char_info):
            convert_line_breaks(position_info)
            titles = [title for title in position_info.text.splitlines() if title]
            for _title in titles:
                if _title in FORUM_POSITIONS:
                    author.position = _title
                else:
                    author.title = _title

        guild_info = char_info.select_one("font.ff_smallinfo")
        convert_line_breaks(char_info)
        char_info_text = char_info.text
        if info_match := author_info_regex.search(char_info_text):
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


class ForumBoardParser:
    """A parser for forum boards from Tibia.com."""

    @classmethod
    def from_content(cls, content: str) -> Optional[ForumBoard]:
        """Parse the board's HTML content from Tibia.com.

        Parameters
        ----------
        content:
            The HTML content of the board.

        Returns
        -------
            The forum board contained.

        Raises
        ------
        InvalidContent`
            Content is not a board in Tibia.com
        """
        parsed_content = parse_tibiacom_content(content)
        forum_breadcrumbs = parsed_content.select_one("div.ForumBreadCrumbs")
        if not forum_breadcrumbs:
            message_box = parsed_content.select_one("div.InnerTableContainer")
            if not message_box or "board you requested" not in message_box.text:
                raise errors.InvalidContentError("content does not belong to a board.")

            return None

        tables = parsed_content.select("table.TableContent")

        header_text = forum_breadcrumbs.text.strip()
        section, name = split_list(header_text, "|", "|")
        link_info = parse_link_info(forum_breadcrumbs.select_one("a"))
        section_id = int(link_info["query"]["sectionid"])

        builder = ForumBoardBuilder().name(name).section(section).section_id(section_id)

        forms = parsed_content.select("form")
        post_age_form = forms[0]
        data = parse_form_data(post_age_form)
        if "threadage" in data.values:
            builder.age(parse_integer(data.values["threadage"]))
        else:
            return builder.build()

        pagination_block = parsed_content.select_one("small")
        pages, total, count = parse_pagination(pagination_block) if pagination_block else (0, 0, 0)
        builder.current_page(pages)
        builder.total_pages(total)

        *thread_rows, times_row = get_rows(tables[-1])
        for thread_row in thread_rows[1:]:
            columns = thread_row.select("td")
            entry = cls._parse_thread_row(columns)
            if "ClassifiedProposal" in thread_row.attrs.get("class"):
                entry.golden_frame = True

            builder.add_entry(entry)

        if len(tables) > 1:
            announcement_rows = get_rows(tables[0])
            for announcement_row in announcement_rows[1:]:
                author_link, title_link = announcement_row.select("a")
                author = author_link.text.strip()
                announcement_link = parse_link_info(title_link)
                entry = AnnouncementEntry(
                    title=announcement_link["text"],
                    announcement_id=int(announcement_link["query"]["announcementid"]),
                    announcement_author=author,
                )
                builder.add_announcement(entry)

        if len(forms) > 2:
            board_selector_form = forms[2]
            data = parse_form_data(board_selector_form)
            builder.board_id(parse_integer(data.values["boardid"]))

        return builder.build()

    # endregion

    # region Private Methods

    @classmethod
    def _parse_thread_row(cls, columns: bs4.ResultSet) -> Optional[ThreadEntry]:
        """Parse the thread row, containing a single thread.

        Parameters
        ----------
        columns: :class:`bs4.ResultSet`
            The list of columns the thread contains.

        Returns
        -------
        :class:`ThreadEntry`
        """
        # First Column: Thread's status
        status = None
        status_column = columns[0]
        status_img = status_column.select_one("img")
        status_icon = None
        if status_img:
            url = status_img["src"]
            filename = filename_regex.search(url).group(1)
            status_icon = url
            status = ThreadStatus.from_icon(filename)
        # Second column: Thread's emoticon
        emoticon = None
        emoticon_column = columns[1]
        emoticon_img = emoticon_column.select_one("img")
        if emoticon_img and emoticon_img.get("alt"):
            url = emoticon_img["src"]
            name = emoticon_img["alt"]
            emoticon = ForumEmoticon(name=name, url=url)
        # Third Column: Thread's title and number of pages
        pages = 1
        thread_column = columns[2]
        title = thread_column.text.strip()
        try:
            thread_link, *page_links = thread_column.select("a")
        except ValueError:
            return None

        if page_links:
            last_page_link = page_links[-1]
            link_info = parse_link_info(last_page_link)
            pages = int(link_info["query"]["pagenumber"])
            title = pages_regex.sub("", title).strip()

        link_info = parse_link_info(thread_link)
        thread_id = int(link_info["query"]["threadid"])
        # Fourth Column: Thread starter
        thread_starter_column = columns[3]
        thread_starter = thread_starter_column.text.strip()
        # Fifth Column: Number of replies
        replies_column = columns[4]
        replies = parse_integer(replies_column.text)
        # Sixth Column: Number of views
        views_column = columns[5]
        views = parse_integer(views_column.text)
        # Seventh Column: Last post information
        last_post_column = columns[6]
        last_post = LastPostParser._parse_column(last_post_column)

        author_link = columns[3].select_one("a")
        traded = False
        if "(traded)" in thread_starter:
            traded = True
            thread_starter = thread_starter.replace("(traded)", "").strip()

        return ThreadEntry(
            title=title,
            thread_id=thread_id,
            thread_starter=thread_starter,
            replies=replies,
            views=views,
            last_post=last_post,
            emoticon=emoticon,
            status=status,
            total_pages=pages,
            status_icon=status_icon,
            thread_starter_traded=traded,
            thread_starter_deleted=author_link is None and not traded,
        )

    # endregion


class ForumThreadParser:
    """A parser for forum threads from Tibia.com."""

    @classmethod
    def from_content(cls, content: str) -> Optional[ForumThread]:
        """Create an instance of the class from the html content of the thread's page.

        Parameters
        ----------
        content:
            The HTML content of the page.

        Returns
        -------
            The thread contained in the page, or None if the thread doesn't exist

        Raises
        ------
        InvalidContent
            If content is not the HTML of a thread's page.
        """
        parsed_content = parse_tibiacom_content(content)
        forum_breadcrumbs = parsed_content.select_one("div.ForumBreadCrumbs")
        if not forum_breadcrumbs:
            message_box = parsed_content.select_one("div.InnerTableContainer")
            if not message_box or "not found" not in message_box.text:
                raise errors.InvalidContentError("content does not belong to a thread.")

            return None

        header_text = forum_breadcrumbs.text.strip()
        section_link, board_link = (parse_link_info(t) for t in forum_breadcrumbs.select("a"))
        section, board, partial_title = split_list(header_text, "|", "|")

        builder = (ForumThreadBuilder()
                   .section(section)
                   .section_id(int(section_link["query"]["sectionid"]))
                   .board_id(int(board_link["query"]["boardid"]))
                   .board(board))
        forum_title_container = parsed_content.select_one("div.ForumTitleText")
        if not forum_title_container:
            builder.title(partial_title)
            return builder.build()

        builder.title(forum_title_container.text.strip())

        border = forum_title_container.parent.previous_sibling.previous_sibling
        gold_frame = "gold" in border["style"]
        builder.golden_frame(gold_frame)

        pagination_block = parsed_content.select_one("td.PageNavigation")
        pages, total, count = parse_pagination(pagination_block) if pagination_block else (0, 0, 0)
        builder.current_page(pages)
        builder.total_pages(total)

        posts_table = parsed_content.select_one("table.TableContent")

        thread_info_container = posts_table.select_one("div.ForumPostHeader")
        thread_info_text_container = thread_info_container.select_one("div.ForumPostHeaderText")
        thread_number, navigation_container = thread_info_text_container.children
        builder.thread_id(int(thread_number.split("#")[-1]))
        navigation_links = navigation_container.select("a")
        if len(navigation_links) == 2:
            prev_link_tag, next_link_tag = navigation_links
            prev_link = parse_link_info(prev_link_tag)
            builder.previous_topic_number(int(prev_link["query"]["threadid"]))
            next_link = parse_link_info(next_link_tag)
            builder.next_topic_number(int(next_link["query"]["threadid"]))
        elif "Previous" in navigation_links[0].text:
            prev_link = parse_link_info(navigation_links[0])
            builder.previous_topic_number(int(prev_link["query"]["threadid"]))
        else:
            next_link = parse_link_info(navigation_links[0])
            builder.next_topic_number(int(next_link["query"]["threadid"]))

        times_container = posts_table.select_one("div.ForumContentFooterLeft")
        offset = 2 if times_container.text == "CEST" else 1

        post_containers = posts_table.select("div.PostBody")
        for post_container in post_containers:
            post = cls._parse_post_table(post_container, offset)
            builder.add_entry(post)

        return builder.build()

    # endregion

    # region Private Methods

    @classmethod
    def _parse_post_table(cls, post_table: bs4.Tag, offset: int = 1) -> ForumPost:
        """Parse the table containing a single posts, extracting its information.

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
        golden_frame = "CipPostWithBorderImage" in post_table.parent.attrs.get("class")
        character_info_container = post_table.select_one("div.PostCharacterText")
        post_author = ForumAuthorParser._parse_author_table(character_info_container)
        content_container = post_table.select_one("div.PostText")
        emoticon = None
        title_tag = None
        # The first elements are the emoticon, the title, and the separator.
        while True:
            child = next(content_container.children)
            child.extract()
            if child.name == "img":
                emoticon = ForumEmoticon(name=child["alt"], url=child["src"])
            elif child.name == "b":
                title_tag = child
            elif child.name == "div":
                break
        # Remove the first line jump found in post content
        first_break = content_container.select_one("br")
        if first_break:
            first_break.extract()

        title = None
        signature = None
        signature_container = post_table.select_one("td.ff_pagetext")
        if signature_container:
            # Remove the signature's content from content container
            signature_container.extract()
            signature = signature_container.encode_contents().decode()

        content = content_container.encode_contents().decode()
        if signature_container:
            # The signature separator will still be part of the content container, so we remove it
            parts = content.split(signature_separator)
            # This will handle the post containing another signature separator within the content
            # We join back all the pieces except for the last one
            content = signature_separator.join(parts[:-1])

        if title_tag:
            title = title_tag.text

        post_details = post_table.select_one("div.PostDetails")
        dates = post_dates_regex.findall(post_details.text)
        edited_date = None
        edited_by = None
        posted_date = parse_tibia_forum_datetime(dates[0], offset)
        if len(dates) > 1:
            edited_date = parse_tibia_forum_datetime(dates[1], offset)
            edited_by = edited_by_regex.search(post_details.text).group(1)

        post_details = post_table.select_one("div.AdditionalBox")
        post_number = post_details.text.replace("Post #", "")
        post_id = int(post_number)
        return ForumPost(author=post_author, content=content, signature=signature, posted_date=posted_date,
                         edited_date=edited_date, edited_by=edited_by, post_id=post_id, title=title, emoticon=emoticon,
                         golden_frame=golden_frame)

    # endregion


class LastPostParser:

    @classmethod
    def _parse_column(cls, last_post_column: bs4.Tag, offset: int = 1) -> Optional[LastPost]:
        """Parse the column containing the last post information and extracts its data.

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
        last_post_info = last_post_column.select_one("div.LastPostInfo, span.LastPostInfo")
        if last_post_info is None:
            return None

        permalink_tag = last_post_info.select_one("a")
        permalink_info = parse_link_info(permalink_tag)
        post_id = int(permalink_info["query"]["postid"])
        date_text = clean_text(last_post_info)
        last_post_date = parse_tibia_forum_datetime(date_text, offset)

        last_post_author_tag = last_post_column.select_one("font")
        author_link = last_post_author_tag.select_one("a")
        deleted = author_link is None
        author = clean_text(last_post_author_tag).replace("by", "", 1)
        traded = False
        if "(traded)" in author:
            author = author.replace("(traded)", "").strip()
            traded = True
            deleted = False

        return LastPost(author=author, post_id=post_id, posted_on=last_post_date, is_author_deleted=deleted,
                        is_author_traded=traded)
