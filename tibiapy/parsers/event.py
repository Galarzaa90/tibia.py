"""Models related to the event schedule section in Tibia.com."""

import datetime
import re
import time
from typing import List

from tibiapy.builders.event import EventScheduleBuilder
from tibiapy.models.event import EventEntry
from tibiapy.utils import parse_popup, parse_tibiacom_content

__all__ = (
    'EventScheduleParser',
)

month_year_regex = re.compile(r'([A-z]+)\s(\d+)')


class EventScheduleParser:
    @classmethod
    def from_content(cls, content):
        """Create an instance of the class from the html content of the event's calendar.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the page.

        Returns
        -------
        :class:`EventSchedule`
            The event calendar contained in the page

        Raises
        ------
        InvalidContent
            If content is not the HTML of the event's schedule page.
        """
        parsed_content = parse_tibiacom_content(content)

        month_year_div = parsed_content.select_one("div.eventscheduleheaderdateblock")
        month, year = month_year_regex.search(month_year_div.text).groups()
        month = time.strptime(month, "%B").tm_mon
        year = int(year)

        builder = EventScheduleBuilder().year(year).month(month)

        events_table = parsed_content.select_one("#eventscheduletable")
        day_cells = events_table.select("td")
        # Keep track of events that are ongoing
        ongoing_events = []
        # Keep track of all events present in that day
        ongoing_day = 1
        first_day = True
        for day_cell in day_cells:
            day_div = day_cell.select_one("div")
            day = int(day_div.text)
            # The first cells may belong to the previous month
            if ongoing_day < day:
                month -= 1
            # The last cells may belong to the last month
            if day < ongoing_day:
                month += 1
            if month > 12:
                month = 1
                year += 1
            if month < 1:
                month = 12
                year -= 1
            ongoing_day = day + 1
            today_events = []
            popup_spans = day_cell.select('span.HelperDivIndicator')
            for popup in popup_spans:
                title, popup_content = parse_popup(popup["onmouseover"])
                divs = popup_content.select("div")
                # Multiple events can be described in the same popup, they come in pairs, title and content.
                for title, content in zip(*[iter(d.text for d in divs)] * 2):
                    title = title.replace(":", "")
                    content = content.replace("• ", "")
                    event = EventEntry(title=title, description=content)
                    today_events.append(event)
                    # If this is not an event that was already ongoing from previous days, add to list
                    if event not in ongoing_events:
                        # Only add a start date if this is not the first day of the calendar
                        # We do not know the actual start date of the event.
                        if not first_day:
                            event.start_date = datetime.date(day=day, month=month, year=year)
                        ongoing_events.append(event)
            # Check which of the ongoing events did not show up today, meaning it has ended now
            for pending_event in ongoing_events[:]:
                if pending_event not in today_events:
                    # If it didn't show up today, it means it ended yesterday.
                    end_date = datetime.date(day=day, month=month, year=year) - datetime.timedelta(days=1)
                    pending_event.end_date = end_date
                    builder.add_event(pending_event)
                    # Remove from ongoing
                    ongoing_events.remove(pending_event)
            first_day = False
        # Add any leftover ongoing events without an end date, as we don't know when they end.
        [builder.add_event(e) for e in ongoing_events]
        return builder.build()