from typing import List

import bs4

from tibiapy import InvalidContentError
from tibiapy.models.fansite import Fansite, FansiteContent, FansiteSocialMedia, FansitesSection
from tibiapy.utils import get_rows, parse_popup, parse_tibiacom_content


class FansitesSectionParser:
    """Parser for the fansites section."""

    @classmethod
    def from_content(cls, content: str) -> FansitesSection:
        """Get the list of available fansites from the HTML of the Tibia.com fansites section.

        Parameters
        ----------
        content:
            The HTML content of the page.

        Returns
        -------
            The fansites section.

        Raises
        ------
        InvalidContent
            If content is not the HTML of the fansites section's page.
        """
        try:
            parsed_content = parse_tibiacom_content(content, builder="html5lib")
            promoted_table = parsed_content.select_one("#promotedfansitesinnertable")
            supported_table = parsed_content.select_one("#supportedfansitesinnertable")
            return FansitesSection(
                promoted_fansites=cls._parse_fansites_table(promoted_table),
                supported_fansites=cls._parse_fansites_table(supported_table),
            )
        except (ValueError, IndexError) as e:
            raise InvalidContentError("content does not belong to the bazaar at Tibia.com", original=e) from e

    @classmethod
    def _parse_fansites_table(cls, table: bs4.Tag) -> List[Fansite]:
        fansites = []
        for row in get_rows(table)[1:]:
            cols = row.select("td")
            site_image = cols[0].select_one("img")
            site_link = cols[0].select_one("a")
            name = site_image["alt"]
            image_url = site_image["src"]
            site_url = site_link["href"]

            character = cols[1].select_one("a").text

            content = []
            content_poupups = cols[2].select("span")
            for content_span in content_poupups:
                _, popup = parse_popup(content_span["onmouseover"])
                content.append(FansiteContent(name=popup.text, icon_url=content_span.select_one("img")["src"]))

            social = []
            social_poupups = cols[3].select("span")
            for social_span in social_poupups:
                _, popup = parse_popup(social_span["onmouseover"])
                social.append(FansiteSocialMedia(name=popup.text, icon_url=social_span.select_one("img")["src"]))

            languages = []
            languages_poupups = cols[4].select("div.HelperDivIndicator")
            for language_div in languages_poupups:
                _, popup = parse_popup(language_div["onmouseover"])
                languages.append(popup.text)

            specials = [t.text for t in cols[5].select("li")]

            fansite_item_img = cols[6].select_one("img")
            item_url = fansite_item_img["src"] if fansite_item_img else None
            fansites.append(
                Fansite(
                    name=name,
                    url=site_url,
                    logo_url=image_url,
                    contact=character,
                    content=content,
                    social_media=social,
                    languages=languages,
                    specials=specials,
                    fansite_item_image_url=item_url,
                ),
            )
        return fansites
