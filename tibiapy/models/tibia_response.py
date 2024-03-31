"""Models used to wrap responses from Tibia.com."""
import datetime
from typing import Generic, TypeVar

from pydantic import computed_field
from typing_extensions import Self

from tibiapy.models.base import BaseModel

__all__ = (
    "TibiaResponse",
)

T = TypeVar("T")

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

    @computed_field
    @property
    def time_left(self) -> datetime.timedelta:
        """:class:`datetime.timedelta`: The time left for the cache of this response to expire."""
        return (datetime.timedelta(seconds=CACHE_LIMIT - self.age)
                - (datetime.datetime.now(datetime.timezone.utc) - self.timestamp))

    @property
    def seconds_left(self) -> int:
        """:class:`int`: The time left in seconds for this response's cache to expire."""
        return self.time_left.seconds

    @classmethod
    def from_raw(cls, raw_response, data: T, parsing_time: float = None) -> Self:
        """Build an instance from a raw response."""
        return cls(
            timestamp=raw_response.timestamp,
            cached=raw_response.cached,
            age=raw_response.age,
            fetching_time=raw_response.fetching_time,
            parsing_time=parsing_time,
            data=data,
        )
