"""Base models for paginated classes."""
from abc import abstractmethod, ABC
from typing import TypeVar, Generic, List, Optional

from tibiapy.models import BaseModel

__all__ = (
    "Paginated",
    "PaginatedWithUrl",
    "AjaxPaginator",
)

T = TypeVar("T")


class Paginated(BaseModel, Generic[T]):
    """An entity made of multiple pages."""

    current_page: int = 1
    """The currently viewed page."""
    total_pages: int = 1
    """The total number of pages."""
    results_count: int = 0
    """The total number of entries across all pages."""
    entries: List[T] = []
    """The entries in this page."""


class PaginatedWithUrl(Paginated[T], Generic[T], ABC):
    """An entity made of multiple pages with URLs."""

    @property
    def next_page_url(self) -> Optional[str]:
        """The URL to the next page of the results, if available."""
        return None if self.current_page == self.total_pages else self.get_page_url(self.current_page + 1)

    @property
    def previous_page_url(self) -> Optional[str]:
        """The URL to the previous page of the results, if available."""
        return None if self.current_page == 1 else self.get_page_url(self.current_page - 1)

    @abstractmethod
    def get_page_url(self, page: int) -> str:
        """Get the URL to a specific page of the results."""
        ...


class AjaxPaginator(Paginated[T], Generic[T]):
    """A paginator that can be fetched via AJAX requests."""

    is_fully_fetched: bool = False
    """Whether this result set was fully fetched or not."""
