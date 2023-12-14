"""Exceptions thrown by tibia.py."""
from __future__ import annotations

from typing import Type, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from enum import Enum


class TibiapyException(Exception):
    """Base exception for the tibiapy module.

    All exceptions thrown by the module are inherited from this.
    """

    pass


class InvalidContent(TibiapyException):
    """Exception thrown when the provided content is unrelated for the calling function.

    This usually means that the content provided belongs to a different website or section of the website.
    This serves as a way to differentiate those cases from a parsing that returned no results (e.g. Character not found)

    In some cases this can mean that Tibia.com's format has changed and the library needs updating.

    Attributes
    ----------
    original: :class:`Exception`
        The original exception that caused this exception.
    """

    def __init__(self, message, original=None):
        super().__init__(message)
        self.original = original


class NetworkError(TibiapyException):
    """Exception thrown when there was a network error trying to fetch a resource from the web.

    Attributes
    ----------
    original: :class:`Exception`
        The original exception that caused this exception.
    fetching_time: :class:`float`
        The time between the request and the response.
    """

    def __init__(self, message, original=None, fetching_time=0):
        super().__init__(message)
        self.original = original
        self.fetching_time = fetching_time


class Forbidden(NetworkError):
    """A subclass of :class:`NetworkError` thrown when Tibia.com returns a 403 status code.

    Tibia.com returns a 403 status code when it detects that too many requests are being done.
    This has its own subclass to let the user decide to treat this differently than other network errors.
    """


class SiteMaintenanceError(NetworkError):
    """A subclass of :class:`NetworkError` thrown when Tibia.com is down for maintenance.

    When Tibia.com is under maintenance, all sections of the website redirect to maintenance.tibia.com.
    """


class EnumValueError(ValueError):
    """Exception raised when the provided value cannot be converted to an enum."""

    def __init__(self, enum: Type[Enum], value: Any) -> None:
        self.enum = enum
        super().__init__(
            f"{value!r} is not a valid value for {enum.__name__}."
            f"Expected names ({self.names}) or values ({self.values})",
        )

    @property
    def names(self):
        return ", ".join(e.name for e in self.enum)

    @property
    def values(self):
        return ", ".join(str(e.value) for e in self.enum)
