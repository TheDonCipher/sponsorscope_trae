import asyncio
import json
import logging
import re
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from shared.schemas.raw import RawProfile, RawPost, RawComment
from shared.schemas.domain import Platform, DataCompleteness
from services.scraper.core.interface import BaseScraper
from services.scraper.core.types import ScrapeResult

logger = logging.getLogger(__name__)

class TikTokPlaywrightScraper(BaseScraper):
    def __init__(self):
        super().__init__(platform=Platform.TIKTOK)
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.session_metadata: Dict[str, Any] = {}
        
    async def _setup_browser(self):
        """Initialize Playwright browser with defensive settings."""
        playwright = await async_playwright().start()
        
        # Launch Chromium with defensive settings
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        # Create context with realistic viewport and user agent
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York'
        )
        
        # Add stealth script to avoid detection
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            window.chrome = {
                runtime: {},
            };
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
        """)
        
        self.page = await self.context.new_page()
        
        # Set session metadata
        self.session_metadata = {
            'browser_version': await self.browser.version(),
            'user_agent': await self.page.evaluate('navigator.userAgent'),
            'platform': 'tiktok',
            'session_start': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Browser initialized: {self.session_metadata}")
        
    async def _detect_blocking_mechanisms(self) -> List[str]:
        """Detect TikTok's blocking mechanisms."""
        errors = []
        
        if not self.page:
            return ["Browser not initialized"]
            
        try:
            # Check for login wall
            login_elements = await self.page.query_selector_all('[data-e2e="login-button"], [data-e2e="modal-login"], .login-container')
            if login_elements:
                errors.append("Login wall detected")
                
            # Check for rate limiting messages
            rate_limit_elements = await self.page.query_selector_all('text=/too.many.requests|rate.limited|try.again.later/i')
            if rate_limit_elements:
                errors.append("Rate limiting detected")
                
            # Check for challenge/captcha
            challenge_elements = await self.page.query_selector_all('[data-e2e="captcha"], .captcha-container, text=/verify|challenge|captcha/i')
            if challenge_elements:
                errors.append("Challenge/captcha detected")
                
            # Check for private profile
            private_elements = await self.page.query_selector_all('text=/private.account|follow.to.see|this.account.is.private/i')
            if private_elements:
                errors.append("Private profile detected")
                
            # Check for 404/not found
            not_found_elements = await self.page.query_selector_all('text=/user.not.found|page.not.available|couldn.t.find/i')
            if not_found_elements:
                errors.append("Profile not found (404)")
                
        except Exception as e:
            logger.error(f"Error detecting blocking mechanisms: {e}")
            errors.append(f"Detection error: {str(e)}")
            
        return errors
        
    async def _extract_profile_data(self, handle: str) -> Optional[RawProfile]:
        """Extract profile data from TikTok page."""
        if not self.page:
            return None
            
        try:
            # Navigate to profile page
            profile_url = f"https://www.tiktok.com/@{handle}"
            await self.page.goto(profile_url, wait_until='networkidle', timeout=30000)
            
            # Wait for profile content to load
            await self.page.wait_for_selector('[data-e2e="user-info"]', timeout=10000)
            
            # Check for blocking mechanisms
            blocking_errors = await self._detect_blocking_mechanisms()
            if blocking_errors:
                logger.warning(f"Blocking mechanisms detected for {handle}: {blocking_errors}")
                return None
            
            # Extract profile data using multiple strategies
            profile_data = {}
            
            # Strategy 1: Extract from user-info container
            try:
                user_info_elements = await self.page.query_selector_all('[data-e2e="user-info"]')
                if user_info_elements:
                    # Extract follower count
                    follower_elements = await self.page.query_selector_all('[data-e2e="followers-count"]')
                    if follower_elements and len(follower_elements) > 0:
                        try:
                            follower_text = await follower_elements[0].inner_text()
                            profile_data['follower_count'] = self._parse_count(follower_text)
                        except Exception as e:
                            logger.debug(f"Failed to extract follower count: {e}")
                    
                    # Extract following count
                    following_elements = await self.page.query_selector_all('[data-e2e="following-count"]')
                    if following_elements and len(following_elements) > 0:
                        try:
                            following_text = await following_elements[0].inner_text()
                            profile_data['following_count'] = self._parse_count(following_text)
                        except Exception as e:
                            logger.debug(f"Failed to extract following count: {e}")
                    
                    # Extract likes count (TikTok equivalent of post count)
                    likes_elements = await self.page.query_selector_all('[data-e2e="likes-count"]')
                    if likes_elements and len(likes_elements) > 0:
                        try:
                            likes_text = await likes_elements[0].inner_text()
                            profile_data['like_count'] = self._parse_count(likes_text)
                        except Exception as e:
                            logger.debug(f"Failed to extract likes count: {e}")
                        
            except Exception as e:
                logger.debug(f"User-info extraction failed: {e}")
                
            # Strategy 2: Extract from page structure
            try:
                # Look for stats in header or bio section
                stats_elements = await self.page.query_selector_all('h2[data-e2e="user-subtitle"], div[data-e2e="user-desc"] span')
                for element in stats_elements:
                    text = await element.inner_text()
                    if any(indicator in text.lower() for indicator in ['follower', 'following', 'like']):
                        # Parse numbers from text
                        numbers = re.findall(r'[\d,]+\.?\d*[kKmM]?', text)
                        for number in numbers:
                            if 'follower' in text.lower():
                                profile_data['follower_count'] = self._parse_count(number)
                            elif 'following' in text.lower():
                                profile_data['following_count'] = self._parse_count(number)
                            elif 'like' in text.lower():
                                profile_data['like_count'] = self._parse_count(number)
                                
            except Exception as e:
                logger.debug(f"Stats extraction failed: {e}")
                
            # Strategy 3: Extract bio and verification
            try:
                # Extract bio
                bio_elements = await self.page.query_selector_all('[data-e2e="user-desc"], .user-bio, h2[data-e2e="user-subtitle"]')
                if bio_elements:
                    profile_data['bio'] = await bio_elements[0].inner_text()
                    
                # Check for verification badge
                verified_elements = await self.page.query_selector_all('[data-e2e="user-verified"], .verified-badge, svg[fill*="verified"]')
                profile_data['is_verified'] = len(verified_elements) > 0
                
            except Exception as e:
                logger.debug(f"Bio/verification extraction failed: {e}")
                
            # Strategy 4: Extract from meta tags
            try:
                meta_description = await self.page.get_attribute('meta[property="og:description"]', 'content')
                if meta_description:
                    # Parse follower/following counts from meta description
                    numbers = re.findall(r'([\d,]+)\s+(\w+)', meta_description)
                    for number, metric in numbers:
                        number_clean = int(number.replace(',', ''))
                        if 'follower' in metric.lower():
                            profile_data['follower_count'] = number_clean
                        elif 'following' in metric.lower():
                            profile_data['following_count'] = number_clean
            except Exception as e:
                logger.debug(f"Meta extraction failed: {e}")
                
            # Fill in defaults for missing data
            profile_data.setdefault('follower_count', 0)
            profile_data.setdefault('following_count', 0)
            profile_data.setdefault('like_count', 0)
            profile_data.setdefault('bio', '')
            profile_data.setdefault('is_verified', False)
            
            # TikTok uses video count instead of post count
            profile_data['post_count'] = profile_data.get('like_count', 0)  # Fallback to likes if video count not available
            
            # Create RawProfile
            return RawProfile(
                handle=handle,
                platform=self.platform,
                follower_count=profile_data['follower_count'],
                following_count=profile_data['following_count'],
                post_count=profile_data['post_count'],
                bio=profile_data['bio'],
                is_verified=profile_data['is_verified']
            )
            
        except Exception as e:
            logger.error(f"Failed to extract profile data for {handle}: {e}")
            return None
            
    def _parse_count(self, text: str) -> int:
        """Parse TikTok count format (e.g., '1.2K' -> 1200)."""
        text = text.strip().lower()
        
        # Remove commas and extra whitespace
        text = text.replace(',', '').strip()
        
        # Handle K, M, B suffixes
        if text.endswith('k'):
            return int(float(text[:-1]) * 1000)
        elif text.endswith('m'):
            return int(float(text[:-1]) * 1000000)
        elif text.endswith('b'):
            return int(float(text[:-1]) * 1000000000)
        
        # Try to parse as plain number
        try:
            return int(float(text))
        except ValueError:
            return 0
            
    async def _extract_posts(self, profile: RawProfile, limit: int = 12) -> List[RawPost]:
        """Extract recent videos from TikTok profile page."""
        posts = []
        
        if not self.page:
            return posts
            
        try:
            # Scroll to load videos
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            # Look for video links
            video_links = await self.page.query_selector_all('[data-e2e="user-post-item"] a, a[href*="/video/"]')
            
            for i, link in enumerate(video_links[:limit]):
                try:
                    post_url = await link.get_attribute('href')
                    if not post_url:
                        continue
                        
                    # Make full URL
                    if not post_url.startswith('http'):
                        post_url = urljoin('https://www.tiktok.com', post_url)
                        
                    # Extract basic video data
                    post_data = {
                        'id': f"video_{profile.handle}_{i}",
                        'url': post_url,
                        'timestamp': datetime.utcnow() - timedelta(days=i),
                        'like_count': 0,
                        'comment_count': 0,
                        'share_count': 0,
                        'view_count': 0,
                        'media_urls': [],
                        'is_video': True
                    }
                    
                    # Try to extract engagement data from the video element
                    try:
                        # Look for engagement indicators (likes, comments, shares, views)
                        engagement_elements = await link.query_selector_all('[data-e2e="video-like-count"], [data-e2e="video-comment-count"], [data-e2e="video-share-count"], [data-e2e="video-view-count"], span[class*="like"], span[class*="comment"], span[class*="share"], span[class*="view"]')
                        
                        for element in engagement_elements:
                            text = await element.inner_text()
                            if any(indicator in text.lower() for indicator in ['like', '❤', '♥']):
                                post_data['like_count'] = self._parse_count(text)
                            elif any(indicator in text.lower() for indicator in ['comment', '💬']):
                                post_data['comment_count'] = self._parse_count(text)
                            elif any(indicator in text.lower() for indicator in ['share', '↗']):
                                post_data['share_count'] = self._parse_count(text)
                            elif any(indicator in text.lower() for indicator in ['view', 'play']):
                                post_data['view_count'] = self._parse_count(text)
                                
                    except Exception as e:
                        logger.debug(f"Failed to extract engagement for video {i}: {e}")
                        
                    # Create RawPost (TikTok videos are posts)
                    posts.append(RawPost(
                        id=post_data['id'],
                        platform=self.platform,
                        url=post_data['url'],
                        timestamp=post_data['timestamp'],
                        like_count=post_data['like_count'],
                        comment_count=post_data['comment_count'],
                        share_count=post_data['share_count'],
                        view_count=post_data['view_count'],
                        media_urls=post_data['media_urls'],
                        is_video=post_data['is_video']
                    ))
                    
                except Exception as e:
                    logger.error(f"Failed to extract video {i}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to extract videos: {e}")
            
        return posts
        
    async def _extract_comments(self, post: RawPost, limit: int = 50) -> List[RawComment]:
        """Extract comments from a specific TikTok video."""
        comments = []
        
        if not self.page:
            return comments
            
        try:
            # Navigate to video page
            await self.page.goto(post.url, wait_until='networkidle', timeout=30000)
            
            # Wait for comments to load
            await self.page.wait_for_selector('[data-e2e="video-comment"]', timeout=10000)
            
            # Check if comments are disabled
            disabled_elements = await self.page.query_selector_all('text=/comments.disabled|no.comments|comments.off/i')
            if disabled_elements:
                logger.info(f"Comments disabled for video {post.id}")
                return comments
                
            # Look for comment elements
            comment_elements = await self.page.query_selector_all('[data-e2e="video-comment"], [data-e2e="comment-item"], div[class*="comment"]')
            
            for i, comment_element in enumerate(comment_elements[:limit]):
                try:
                    # Extract comment text
                    text_elements = await comment_element.query_selector_all('[data-e2e="comment-text"], span[class*="text"], div[class*="text"]')
                    comment_text = ""
                    if text_elements and len(text_elements) > 0:
                        for text_element in text_elements:
                            try:
                                text = await text_element.inner_text()
                                if text and len(text) > 2:  # Filter out very short text
                                    comment_text = text
                                    break
                            except Exception as e:
                                logger.debug(f"Failed to extract comment text: {e}")
                                continue
                            
                    if not comment_text:
                        continue
                        
                    # Extract author
                    author_elements = await comment_element.query_selector_all('[data-e2e="comment-username"], a[href*="/@"], h3, h4')
                    author_id = "unknown"
                    if author_elements and len(author_elements) > 0:
                        try:
                            author_href = await author_elements[0].get_attribute('href')
                            if author_href:
                                # Extract username from TikTok URL format
                                author_id = author_href.strip('/@').split('/')[0] if '/@' in author_href else f"user_{i}"
                            else:
                                author_text = await author_elements[0].inner_text()
                                author_id = author_text.strip('@').split()[0]
                        except Exception as e:
                            logger.debug(f"Failed to extract author: {e}")
                            
                    # Create RawComment
                    comments.append(RawComment(
                        id=f"comment_{post.id}_{i}",
                        text=comment_text,
                        timestamp=post.timestamp + timedelta(minutes=i * 5),
                        author_id=author_id,
                        like_count=0,
                        reply_count=0
                    ))
                    
                except Exception as e:
                    logger.debug(f"Failed to extract comment {i}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to extract comments for video {post.id}: {e}")
            
        return comments
        
    async def _log_scrape_metadata(self, handle: str, errors: List[str], data_completeness: DataCompleteness):
        """Log structured scrape metadata."""
        log_entry = {
            'handle': handle,
            'platform': 'tiktok',
            'scraped_at': datetime.utcnow().isoformat(),
            'ip_session': self.session_metadata.get('session_id', 'unknown'),
            'browser_version': self.session_metadata.get('browser_version', 'unknown'),
            'failure_reason': errors[0] if errors else None,
            'data_completeness': data_completeness.value,
            'session_metadata': self.session_metadata
        }
        
        # Ensure logs directory exists
        import os
        logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Write log entry
        log_file = os.path.join(logs_dir, f'tiktok_scrape_{datetime.utcnow().strftime("%Y%m%d")}.jsonl')
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write scrape metadata log: {e}")
            
    async def scrape_profile(self, handle: str) -> Optional[RawProfile]:
        """Scrape TikTok profile data."""
        if not self.page:
            await self._setup_browser()
            
        return await self._extract_profile_data(handle)
        
    async def scrape_posts(self, profile: RawProfile, limit: int = 12) -> List[RawPost]:
        """Scrape recent videos from TikTok profile."""
        return await self._extract_posts(profile, limit)
        
    async def scrape_comments(self, post: RawPost, limit: int = 50) -> List[RawComment]:
        """Scrape comments from a specific TikTok video."""
        return await self._extract_comments(post, limit)
        
    async def run_scan(self, handle: str) -> ScrapeResult:
        """Run complete scan: profile, videos, and comments."""
        errors = []
        completeness = DataCompleteness.FULL
        
        # Initialize browser if needed
        if not self.page:
            try:
                await self._setup_browser()
            except Exception as e:
                errors.append(f"Browser initialization failed: {str(e)}")
                await self._log_scrape_metadata(handle, errors, DataCompleteness.FAILED)
                return ScrapeResult(
                    data_completeness=DataCompleteness.FAILED,
                    errors=errors
                )
                
        # Generate session ID for logging
        self.session_metadata['session_id'] = f"{handle}_{int(time.time())}"
        
        # 1. Profile
        profile = None
        try:
            profile = await self.scrape_profile(handle)
        except Exception as e:
            errors.append(f"Profile extraction error: {str(e)}")
            logger.error(f"Profile extraction failed for {handle}: {e}")
            
        if not profile:
            blocking_errors = await self._detect_blocking_mechanisms()
            if blocking_errors:
                errors.extend(blocking_errors)
                completeness = DataCompleteness.UNAVAILABLE
            else:
                errors.append("Profile not found or extraction failed")
                completeness = DataCompleteness.FAILED
                
            await self._log_scrape_metadata(handle, errors, completeness)
            return ScrapeResult(
                data_completeness=completeness,
                errors=errors
            )
            
        # 2. Videos (TikTok posts)
        posts = []
        try:
            posts = await self.scrape_posts(profile)
            if not posts and profile.post_count > 0:
                errors.append("No videos extracted despite profile showing videos")
                completeness = DataCompleteness.PARTIAL_NO_POSTS
        except Exception as e:
            errors.append(f"Video extraction error: {str(e)}")
            if profile.post_count > 0:
                completeness = DataCompleteness.PARTIAL_NO_POSTS
                
        # 3. Comments
        all_comments = []
        comments_blocked_count = 0
        
        for post in posts:
            try:
                post_comments = await self.scrape_comments(post)
                all_comments.extend(post_comments)
            except Exception as e:
                logger.debug(f"Comment extraction failed for video {post.id}: {e}")
                comments_blocked_count += 1
                
        # Update completeness based on comment availability
        if comments_blocked_count == len(posts) and len(posts) > 0:
            if completeness == DataCompleteness.FULL:
                completeness = DataCompleteness.PARTIAL_NO_COMMENTS
            errors.append("Comments blocked on all videos")
        elif comments_blocked_count > 0:
            errors.append(f"Comments blocked on {comments_blocked_count} videos")
            
        # Log scrape metadata
        await self._log_scrape_metadata(handle, errors, completeness)
        
        return ScrapeResult(
            profile=profile,
            posts=posts,
            comments=all_comments,
            data_completeness=completeness,
            errors=errors
        )
        
    async def cleanup(self):
        """Clean up browser resources."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            
    def __del__(self):
        """Ensure cleanup on deletion."""
        try:
            asyncio.get_event_loop().run_until_complete(self.cleanup())
        except Exception:
            pass