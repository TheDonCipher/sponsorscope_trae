from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from shared.schemas.domain import DataCompleteness
from shared.schemas.raw import RawProfile, RawPost, RawComment

class ScrapeResult(BaseModel):
    """
    Standard output for the scraping layer.
    """
    profile: Optional[RawProfile] = None
    posts: List[RawPost] = Field(default_factory=list)
    comments: List[RawComment] = Field(default_factory=list)
    data_completeness: DataCompleteness
    errors: List[str] = Field(default_factory=list)
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
