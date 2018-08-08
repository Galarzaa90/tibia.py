import abc
import urllib.parse

from .const import CHARACTER_URL


class Character(metaclass=abc.ABCMeta):
    __slots__ = ("name", )

    def __eq__(self, o: object) -> bool:
        """Two characters are considered equal if their names are equal."""
        if isinstance(o, self.__class__):
            return self.name.lower() == o.name.lower()
        return False

    @property
    def url(self):
        """
        :class:`str`: The URL of the character's information page on Tibia.com
        """
        return CHARACTER_URL + urllib.parse.quote(self.name.encode('iso-8859-1'))
