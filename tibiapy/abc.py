import abc
import urllib.parse

from .const import CHARACTER_URL, CHARACTER_URL_TIBIADATA


class Character(metaclass=abc.ABCMeta):
    """Base class for all character classes.

    Implements common properties.

    Attributes
    ----------
    name: :class:`str`
    """
    __slots__ = ("name", )

    def __eq__(self, o: object) -> bool:
        """Two characters are considered equal if their names are equal."""
        if isinstance(o, self.__class__):
            return self.name.lower() == o.name.lower()
        return False

    def __repr__(self) -> str:
        attributes = ""
        for attr in self.__slots__:
            if attr in ["name"]:
                continue
            v = getattr(self, attr)
            if isinstance(v, int) and v == 0 and not isinstance(v, bool):
                continue
            if isinstance(v, list) and len(v) == 0:
                continue
            if v is None:
                continue
            attributes += ",%s=%r" % (attr, v)
        return "{0.__class__.__name__}({0.name!r}{1}".format(self, attributes)

    @property
    def url(self):
        """
        :class:`str`: The URL of the character's information page on Tibia.com
        """
        return CHARACTER_URL + urllib.parse.quote(self.name.encode('iso-8859-1'))

    @property
    def url_tibiadata(self):
        """
        :class:`str`: The URL of the character's information on TibiaData
        """
        return CHARACTER_URL_TIBIADATA % urllib.parse.quote(self.name.encode('iso-8859-1'))
