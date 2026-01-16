import asyncio
import hashlib
import random
from typing import List, Optional
from datetime import datetime, timedelta
from shared.schemas.raw import RawProfile, RawPost, RawComment
from shared.schemas.domain import Platform, DataCompleteness
from services.scraper.core.interface import BaseScraper
from services.scraper.core.types import ScrapeResult

class InstagramScraper(BaseScraper):
    def __init__(self):
        super().__init__(platform=Platform.INSTAGRAM)
        
    def _get_seed(self, handle: str) -> int:
        """Generate a deterministic seed from the handle string."""
        return int(hashlib.sha256(handle.encode('utf-8')).hexdigest(), 16)

    async def scrape_profile(self, handle: str) -> Optional[RawProfile]:
        # Deterministic simulation to replace static mock data
        # This allows the app to demonstrate functionality with any handle
        if handle.lower() == "private_user":
            return None
        
        seed = self._get_seed(handle)
        random.seed(seed)
        
        # Simulate tiered influencers
        follower_tier = random.choice([
            (1000, 10000),      # Nano
            (10000, 100000),    # Micro
            (100000, 1000000),  # Macro
            (1000000, 50000000) # Mega
        ])
        
        follower_count = random.randint(*follower_tier)
        following_count = random.randint(100, 5000)
        post_count = random.randint(50, 5000)
        is_verified = True if follower_count > 100000 and random.random() > 0.3 else False
        
        return RawProfile(
            handle=handle,
            platform=self.platform,
            follower_count=follower_count,
            following_count=following_count,
            post_count=post_count,
            bio=f"Official account for {handle}. Creating content about life, tech, and future. #SponsorScope",
            is_verified=is_verified
        )
        
    async def scrape_posts(self, profile: RawProfile, limit: int = 30) -> List[RawPost]:
        seed = self._get_seed(profile.handle)
        random.seed(seed + 1) # Different seed for posts
        
        posts = []
        # Return up to 20 posts for the simulation
        num_posts = min(limit, 20) 
        
        for i in range(num_posts):
            # Engagement curve simulation (some variance per post)
            engagement_rate = random.uniform(0.005, 0.08) # 0.5% to 8%
            base_likes = int(profile.follower_count * engagement_rate)
            
            # Add some outliers (viral posts)
            if random.random() < 0.1:
                base_likes *= random.randint(3, 10)
            
            posts.append(RawPost(
                id=f"post_{profile.handle}_{i}",
                platform=self.platform,
                url=f"https://instagram.com/p/{profile.handle}_{i}",
                timestamp=datetime.utcnow() - timedelta(days=i*random.randint(1, 3)),
                like_count=base_likes,
                comment_count=int(base_likes * random.uniform(0.01, 0.05)),
                media_urls=["https://picsum.photos/400/400"] # Use random placeholder images if displayed
            ))
        return posts
        
    async def scrape_comments(self, post: RawPost, limit: int = 50) -> List[RawComment]:
        seed = self._get_seed(post.id) # Use post ID for deterministic comments
        random.seed(seed)
        
        comments = []
        num_comments = min(limit, post.comment_count, 10)
        
        phrases = [
            "Great content!", "Love this", "Amazing shot", "Collab?", "Check DM", 
            "So true", "🔥", "😍", "Where is this?", "Can't wait for more",
            "SponsorScope sent me here", "Interesting perspective"
        ]
        
        for i in range(num_comments):
            comments.append(RawComment(
                id=f"comment_{post.id}_{i}",
                text=random.choice(phrases),
                timestamp=post.timestamp + timedelta(minutes=random.randint(1, 120)),
                author_id=f"user_{random.randint(1000, 9999)}"
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
                data_completeness=DataCompleteness.UNAVAILABLE,
                errors=["Profile not found or private"]
            )
            
        # 2. Posts
        posts = []
        try:
            posts = await self.scrape_posts(profile)
        except Exception as e:
            errors.append(f"Post error: {str(e)}")
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
             
        return ScrapeResult(
            profile=profile,
            posts=posts,
            comments=all_comments,
            data_completeness=completeness,
            errors=errors
        )
