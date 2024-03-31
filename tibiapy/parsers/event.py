"""Models related to the event schedule section in Tibia.com."""

import datetime
import re
import time
from typing import Dict, List, Tuple

import bs4

from tibiapy.builders import EventScheduleBuilder
from tibiapy.models import EventEntry, EventSchedule
from tibiapy.utils import parse_popup, parse_tibiacom_content

__all__ = (
    "EventScheduleParser",
)

month_year_regex = re.compile(r"([A-z]+)\s(\d+)")


class EventScheduleParser:
    """Parser for the event schedule from Tibia.com."""

    @classmethod
    def from_content(cls, content: str) -> EventSchedule:
        """Create an instance of the class from the html content of the event's calendar.

        Parameters
        ----------
        content:
            The HTML content of the page.

        Returns
        -------
            The event calendar contained in the page

        Raises
        ------
        InvalidContent
            If content is not the HTML of the event's schedule page.
        """
        parsed_content = parse_tibiacom_content(content)

        month, year = cls._calculate_month_year(parsed_content.select_one("div.eventscheduleheaderdateblock"))
        builder = EventScheduleBuilder().year(year).month(month)
        events_table = parsed_content.select_one("#eventscheduletable")
        day_cells = events_table.select("td")

        ongoing_events = []
        ongoing_day = 1
        first_day = True

        for day_cell in day_cells:
            day, today_events = cls._process_day_cell(day_cell)
            month, year = cls._adjust_date(ongoing_day, day, month, year)
            ongoing_day = day + 1

            # Check which of the ongoing events did not show up today, meaning it has ended now
            for pending_event in ongoing_events[:]:
                # If it didn't show up today, it means it ended yesterday.
                if pending_event not in today_events:
                    end_date = datetime.date(day=day, month=month, year=year) - datetime.timedelta(days=1)
                    pending_event.end_date = end_date
                    builder.add_event(pending_event)
                    ongoing_events.remove(pending_event)

            for event in today_events:
                # Unless today is the first day of the calendar, then we don't know for sure.
                if event in ongoing_events:
                    continue
                # Only add a start date if this is not the first day of the calendar
                # We do not know the actual start date of the event.
                if not first_day:
                    event.start_date = datetime.date(day=day, month=month, year=year)

                ongoing_events.append(event)

            first_day = False
        # Add any leftover ongoing events without an end date, as we don't know when they end.
        for event in ongoing_events:
            builder.add_event(event)

        return builder.build()

    @classmethod
    def _adjust_date(cls, ongoing_day: int, day: int, month: int, year: int) -> Tuple[int, int]:
        if ongoing_day < day:
            # The first cells may belong to the previous month
            month -= 1

        if day < ongoing_day:
            # The last cells may belong to the last month
            month += 1

        if month > 12:
            # Set to january of next year
            month = 1
            year += 1

        if month < 1:
            # Set to december of previous year
            month = 12
            year -= 1

        return month, year

    @classmethod
    def _parse_inline_style(cls, style_content: str) -> Dict[str, str]:
        attrs = style_content.split(";")
        values = {}
        for attr in attrs:
            if not attr.strip():
                continue

            key, value = attr.split(":")
            values[key.strip()] = value.strip()

        return values

    @classmethod
    def _process_day_cell(cls, day_cell: bs4.Tag) -> Tuple[int, List[EventEntry]]:
        day_div = day_cell.select_one("div")
        day = int(day_div.text)
        today_events = []

        for popup in day_cell.select("span.HelperDivIndicator"):
            colored_blocks = popup.select("div:not([class])")
            event_colors = {}
            for block in colored_blocks:
                style_values = cls._parse_inline_style(block.get("style"))
                block_title = block.text.replace("*", "")
                event_colors[block_title] = style_values["background"]

            title, popup_content = parse_popup(popup["onmouseover"])
            divs = popup_content.select("div")
            # Multiple events can be described in the same popup, they come in pairs, title and content.
            for title, content in zip(*[iter(d.text for d in divs)] * 2):
                title = title.replace(":", "")
                content = content.replace("• ", "")
                event = EventEntry(title=title, description=content, color=event_colors.get(title))
                today_events.append(event)

        return day, today_events

    @classmethod
    def _calculate_month_year(cls, month_year_div: bs4.Tag) -> Tuple[int, int]:
        month, year = month_year_regex.search(month_year_div.text).groups()
        month = time.strptime(month, "%B").tm_mon
        year = int(year)
        return month, year
