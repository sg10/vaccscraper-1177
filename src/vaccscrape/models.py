import datetime
from typing import List, Literal, Union

from pydantic import BaseModel, Field


class ScrapeSuccess(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    kind: Literal["SCRAPE_SUCCESS"] = "SCRAPE_SUCCESS"
    headlines: List[str]


class ScrapeError(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    kind: Literal["SCRAPE_ERROR"] = "SCRAPE_ERROR"
    error_message: str


ScrapeResult = Union[ScrapeSuccess, ScrapeError]
