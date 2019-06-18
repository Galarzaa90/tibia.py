import bs4

from tibiapy import abc, InvalidContent

__all__ = (
    "BoostedCreature",
)

BOOSTED_ALT = "Today's boosted creature: "


class BoostedCreature(abc.Serializable):
    """Represents a boosted creature entry.

    This creature changes every server save and applies to all Game Worlds.
    Boosted creatures yield twice the amount of experience points, carry more loot and respawn at a faster rate.

    Attributes
    ----------
    name: :class:`str`
        The name of the boosted creature.
    image_url: :class:`str`
        An URL containing the boosted creature's image.
    """
    __slots__ = (
        "name",
        "image_url",
    )

    def __init__(self, name, image_url):
        self.name = name
        self.image_url = image_url

    def __repr__(self):
        return "<{0.__class__.__name__} name={0.name!r} image_url={0.image_url!r}>".format(self)

    @classmethod
    def from_content(cls, content):
        """
        Gets the boosted creature from any Tibia.com page.


        Parameters
        ----------
        content: :class:`str`
            The HTML content of a Tibia.com page.

        Returns
        -------
        :class:`News`
            The boosted article shown.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a Tibia.com's page.
        """
        try:
            parsed_content = bs4.BeautifulSoup(content.replace('ISO-8859-1', 'utf-8'), "lxml",
                                               parse_only=bs4.SoupStrainer("div", attrs={"id": "RightArtwork"}))
            img = parsed_content.find("img", attrs={"id": "Monster"})
            name = img["title"].replace(BOOSTED_ALT, "").strip()
            image_url = img["src"]
            return cls(name, image_url)
        except TypeError:
            raise InvalidContent("content is not from Tibia.com")

