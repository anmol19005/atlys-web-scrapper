from pydantic import BaseModel
from typing import Optional


class ScrapeSettings(BaseModel):
    pages: int
    proxy: Optional[str] = None


class ScrapeResponse(BaseModel):
    scraped: int
