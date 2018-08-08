import abc
import urllib.parse

import tibiapy


class Character(metaclass=abc.ABCMeta):
    __slots__ = ("name", "world", "level")

    def __eq__(self, o: object) -> bool:
        """Two characters are considered equal if their names are equal."""
        if isinstance(o, self.__class__):
            return self.name.lower() == o.name.lower()
        return False

    @property
    def url(self):
        """
        The URL of the character's information page on Tibia.com
        """
        return tibiapy.CHARACTER_URL + urllib.parse.quote(self.name.encode('iso-8859-1'))
