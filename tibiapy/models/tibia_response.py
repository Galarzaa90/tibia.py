import datetime
from typing import Generic, TypeVar

from tibiapy.models.base import BaseModel

__all__ = (
    "TibiaResponse",
)

T = TypeVar('T')

# Tibia.com's cache for the community section is 5 minutes.
# This limit is not sent anywhere, so there's no way to automate it.
CACHE_LIMIT = 300


class TibiaResponse(BaseModel, Generic[T]):
    """Represents a response from Tibia.com."""

    timestamp: datetime.datetime
    """The date and time when the page was fetched, in UTC."""
    cached: bool
    """Whether the response is cached or it is a fresh response."""
    age: int
    """The age of the cache in seconds."""
    fetching_time: float
    """The time in seconds it took for Tibia.com to respond."""
    parsing_time: float
    """The time in seconds it took for the response to be parsed into data."""
    data: T
    """The data contained in the response."""

    @property
    def time_left(self):
        """:class:`datetime.timedelta`: The time left for the cache of this response to expire."""
        if not self.age:
            return datetime.timedelta()
        return (datetime.timedelta(seconds=CACHE_LIMIT - self.age)
                - (datetime.datetime.now(datetime.timezone.utc) - self.timestamp))

    @property
    def seconds_left(self):
        """:class:`int`: The time left in seconds for this response's cache to expire."""
        return self.time_left.seconds

    @classmethod
    def from_raw(cls, raw_response, data: T, parsing_time=None):
        return cls(
            timestamp=raw_response.timestamp,
            cached=raw_response.cached,
            age=raw_response.age,
            fetching_time=raw_response.fetching_time,
            parsing_time=parsing_time,
            data=data
        )
