from abc import ABC, abstractmethod
from typing import List, Optional
from shared.schemas.raw import RawProfile, RawPost, RawComment
from .types import ScrapeResult

class BaseScraper(ABC):
    """
    Abstract contract for platform-specific scrapers.
    Must handle degradation gracefully.
    """
    
    def __init__(self, platform: str):
        self.platform = platform
        
    @abstractmethod
    async def scrape_profile(self, handle: str) -> Optional[RawProfile]:
        """
        Fetches basic profile metadata.
        Returns None if profile is private/not found.
        """
        pass
        
    @abstractmethod
    async def scrape_posts(self, profile: RawProfile, limit: int = 30) -> List[RawPost]:
        """
        Fetches recent posts.
        Should handle partial failures (e.g., first 10 posts only).
        """
        pass
        
    @abstractmethod
    async def scrape_comments(self, post: RawPost, limit: int = 50) -> List[RawComment]:
        """
        Fetches comments for a post.
        Returns empty list if comments are blocked/disabled.
        """
        pass
    
    @abstractmethod
    async def run_scan(self, handle: str) -> ScrapeResult:
        """
        Orchestrates the full scan pipeline:
        1. Profile
        2. Posts
        3. Comments (sampled)
        4. Evidence Capture
        """
        pass
