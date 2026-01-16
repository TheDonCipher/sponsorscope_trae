import asyncio
from typing import List, Optional
from datetime import datetime
from shared.schemas.raw import RawProfile, RawPost, RawComment
from shared.schemas.domain import Platform, DataCompleteness
from services.scraper.core.interface import BaseScraper
from services.scraper.core.types import ScrapeResult

class InstagramScraper(BaseScraper):
    def __init__(self):
        super().__init__(platform=Platform.INSTAGRAM)
        
    async def scrape_profile(self, handle: str) -> Optional[RawProfile]:
        # Mock implementation for scaffolding
        if handle == "private_user":
            return None
        
        return RawProfile(
            handle=handle,
            platform=self.platform,
            follower_count=10000,
            following_count=500,
            post_count=100,
            bio="Test Bio",
            is_verified=True
        )
        
    async def scrape_posts(self, profile: RawProfile, limit: int = 30) -> List[RawPost]:
        # Mock implementation
        posts = []
        for i in range(min(limit, 5)): # Return 5 mock posts
            posts.append(RawPost(
                id=f"post_{i}",
                platform=self.platform,
                url=f"https://instagram.com/p/{i}",
                timestamp=datetime.utcnow(),
                like_count=100 + i,
                comment_count=10,
                media_urls=["http://example.com/image.jpg"]
            ))
        return posts
        
    async def scrape_comments(self, post: RawPost, limit: int = 50) -> List[RawComment]:
        # Mock implementation
        comments = []
        for i in range(min(limit, 5)):
            comments.append(RawComment(
                id=f"comment_{post.id}_{i}",
                text=f"Nice post {i}",
                timestamp=datetime.utcnow(),
                author_id=f"user_{i}"
            ))
        return comments
        
    async def run_scan(self, handle: str) -> ScrapeResult:
        errors = []
        completeness = DataCompleteness.FULL
        
        # 1. Profile
        try:
            profile = await self.scrape_profile(handle)
        except Exception as e:
            errors.append(f"Profile error: {str(e)}")
            return ScrapeResult(
                data_completeness=DataCompleteness.FAILED,
                errors=errors
            )
            
        if not profile:
            return ScrapeResult(
                data_completeness=DataCompleteness.UNAVAILABLE, # type: ignore (Need to add UNAVAILABLE to Enum if not present, checking domain.py)
                errors=["Profile not found or private"]
            )
            
        # 2. Posts
        posts = []
        try:
            posts = await self.scrape_posts(profile)
        except Exception as e:
            errors.append(f"Post error: {str(e)}")
            # If we fail to get posts, is it archival or failed?
            # If we have 0 posts but profile says post_count > 0, it's partial or failed.
            if profile.post_count > 0:
                completeness = DataCompleteness.FAILED
        
        # 3. Comments
        all_comments = []
        comments_blocked_count = 0
        
        for post in posts:
            try:
                post_comments = await self.scrape_comments(post)
                all_comments.extend(post_comments)
            except Exception:
                comments_blocked_count += 1
                
        # Degradation Logic
        if comments_blocked_count == len(posts) and len(posts) > 0:
            completeness = DataCompleteness.PARTIAL_NO_COMMENTS
            errors.append("Comments blocked on all posts")
        elif comments_blocked_count > 0:
             errors.append(f"Comments blocked on {comments_blocked_count} posts")
             # Still mostly FULL unless total block
             
        return ScrapeResult(
            profile=profile,
            posts=posts,
            comments=all_comments,
            data_completeness=completeness,
            errors=errors
        )
