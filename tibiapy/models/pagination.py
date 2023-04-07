from pydantic import BaseModel


class PaginationData(BaseModel):
    current_page: int = 1
    total_pages: int = 1
    results_count: int = 0