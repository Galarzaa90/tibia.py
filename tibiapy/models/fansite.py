from typing import List, Optional

from tibiapy.models import BaseModel

__all__ = (
    "FansiteContent",
    "FansiteSocialMedia",
    "Fansite",
    "FansitesSection",
)


class FansiteContent(BaseModel):
    """An icon to represent a category of content."""

    name: str
    """The name of the content category."""
    icon_url: str
    """URL to the icon."""


class FansiteSocialMedia(BaseModel):
    """An icon to represent available social media for the fansite."""

    name: str
    """The name of the social media site."""
    icon_url: str
    """The URL to the icon."""


class Fansite(BaseModel):
    """Represents a fansite in the fansite programme."""

    name: str
    """The name of the fansite."""
    url: str
    """The URL to the fansite."""
    logo_url: str
    """URL to the fansite's logo."""
    contact: str
    """The name of the contact person."""
    content: List[FansiteContent]
    """A list of content categories for the site."""
    social_media: List[FansiteSocialMedia]
    """A list of the social media sites the fansite has."""
    languages: List[str]
    """A list of the languages the site is available in."""
    specials: List[str]
    """A description of features or highligts."""
    fansite_item_image_url: Optional[str]
    """The URL to the fansite item's icon, if available."""


class FansitesSection(BaseModel):
    """The fansites section of Tibia.com."""

    promoted_fansites: List[Fansite]
    """Promoted fansites."""
    supported_fansites: List[Fansite]
    """Supported fansites."""
