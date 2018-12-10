import abc
import datetime
import json
import urllib.parse

from tibiapy.const import CHARACTER_URL, CHARACTER_URL_TIBIADATA


class Serializable(abc.ABC):
    """Implements methods to make a class convertible to JSON.

    Note that there's no way to convert JSON strings back to their original object and that some data might be lost."""
    @classmethod
    def __slots_inherited__(cls):
        slots = []
        for base in cls.__bases__:
            for slot in base.__slots__:
                if slot not in slots:
                    slots.append(slot)
        for slot in cls.__slots__:
            if slot not in slots:
                slots.append(slot)
        return tuple(slots)

    def keys(self):
        return list(self.__slots_inherited__())

    def __getitem__(self, item):
        try:
            return getattr(self, item)
        except AttributeError:
            raise KeyError(item) from None

    @staticmethod
    def _try_dict(obj):
        try:
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            return {k:v for k,v in dict(obj).items() if v is not None}
        except TypeError:
            return str(obj)

    def to_json(self, *, indent=None, sort_keys = False):
        """Gets the object's JSON representation.

        Parameters
        ----------
        indent: :class:`int`, optional
            Number of spaces used as indentation, ``None`` will return the shortest possible string.
        sort_keys: :class:`bool`, optional
            Whether keys should be sorted alphabetically or preserve the order defined by the object.

        Returns
        -------
        :class:`str`
            JSON representation of the object.
        """
        return json.dumps({k:v for k,v in dict(self).items() if v is not None}, indent=indent, sort_keys=sort_keys,
                          default=self._try_dict)

class Character(Serializable, metaclass=abc.ABCMeta):
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
        return "<{0.__class__.__name__} name={0.name!r}>".format(self,)

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