import abc
import urllib.parse

import tibiapy


class Character(metaclass=abc.ABCMeta):
    __slots__ = ("name", "world", "level")

    @property
    def url(self):
        """
        The URL of the character's information page on Tibia.com

        Returns
        ---------
        str:
            The character's URL.
        """
        return tibiapy.CHARACTER_URL + urllib.parse.quote(self.name.encode('iso-8859-1'))
