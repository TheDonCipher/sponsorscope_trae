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

class InstagramPlaywrightScraper(BaseScraper):
    def __init__(self):
        super().__init__(platform=Platform.INSTAGRAM)
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
            'platform': 'instagram',
            'session_start': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Browser initialized: {self.session_metadata}")
        
    async def _detect_blocking_mechanisms(self) -> List[str]:
        """Detect Instagram's blocking mechanisms."""
        errors = []
        
        if not self.page:
            return ["Browser not initialized"]
            
        try:
            # Check for login wall
            login_elements = await self.page.query_selector_all('[data-testid="login-form"], input[name="username"], r"._ab3w"')
            if login_elements:
                errors.append("Login wall detected")
                
            # Check for rate limiting messages
            rate_limit_elements = await self.page.query_selector_all('text=/rate.limited|too.many.requests|try.again.later/i')
            if rate_limit_elements:
                errors.append("Rate limiting detected")
                
            # Check for challenge/captcha
            challenge_elements = await self.page.query_selector_all('[data-testid="challenge"], text=/challenge|suspicious|verify/i')
            if challenge_elements:
                errors.append("Challenge/captcha detected")
                
            # Check for private profile
            private_elements = await self.page.query_selector_all('text=/private.account|follow.to.see|this.account.is.private/i')
            if private_elements:
                errors.append("Private profile detected")
                
            # Check for 404/not found
            not_found_elements = await self.page.query_selector_all('text=/sorry|page.not.found|couldn.t.find/i')
            if not_found_elements:
                errors.append("Profile not found (404)")
                
        except Exception as e:
            logger.error(f"Error detecting blocking mechanisms: {e}")
            errors.append(f"Detection error: {str(e)}")
            
        return errors
        
    async def _extract_profile_data(self, handle: str) -> Optional[RawProfile]:
        """Extract profile data from Instagram page."""
        if not self.page:
            return None
            
        try:
            # Navigate to profile page
            profile_url = f"https://www.instagram.com/{handle}/"
            await self.page.goto(profile_url, wait_until='networkidle', timeout=30000)
            
            # Wait for profile content to load
            await self.page.wait_for_selector('header', timeout=10000)
            
            # Check for blocking mechanisms
            blocking_errors = await self._detect_blocking_mechanisms()
            if blocking_errors:
                logger.warning(f"Blocking mechanisms detected for {handle}: {blocking_errors}")
                return None
            
            # Extract profile data using multiple strategies
            profile_data = {}
            
            # Strategy 1: Try to extract from meta tags
            try:
                meta_description = await self.page.get_attribute('meta[property="og:description"]', 'content')
                if meta_description:
                    # Parse follower/following/post counts from meta description
                    numbers = re.findall(r'([\d,]+)\s+(\w+)', meta_description)
                    for number, metric in numbers:
                        number_clean = int(number.replace(',', ''))
                        if 'follower' in metric.lower():
                            profile_data['follower_count'] = number_clean
                        elif 'following' in metric.lower():
                            profile_data['following_count'] = number_clean
                        elif 'post' in metric.lower():
                            profile_data['post_count'] = number_clean
            except Exception as e:
                logger.debug(f"Meta extraction failed: {e}")
                
            # Strategy 2: Extract from page structure
            try:
                # Look for follower count elements
                follower_elements = await self.page.query_selector_all('a[href*="/followers/"] span')
                if follower_elements and len(follower_elements) > 0:
                    try:
                        follower_text = await follower_elements[0].inner_text()
                        profile_data['follower_count'] = self._parse_count(follower_text)
                    except Exception as e:
                        logger.debug(f"Failed to extract follower count: {e}")
                
                # Look for following count
                following_elements = await self.page.query_selector_all('a[href*="/following/"] span')
                if following_elements and len(following_elements) > 1:
                    try:
                        following_text = await following_elements[1].inner_text()
                        profile_data['following_count'] = self._parse_count(following_text)
                    except Exception as e:
                        logger.debug(f"Failed to extract following count: {e}")
                    
                # Look for post count
                post_elements = await self.page.query_selector_all('header span')
                for element in post_elements:
                    try:
                        text = await element.inner_text()
                        if 'post' in text.lower() or re.match(r'^\d+[kKmM]?$', text):
                            profile_data['post_count'] = self._parse_count(text)
                            break
                    except Exception as e:
                        logger.debug(f"Failed to extract post count from element: {e}")
                        continue
                        
            except Exception as e:
                logger.debug(f"Structure extraction failed: {e}")
                
            # Strategy 3: Extract bio and verification
            try:
                # Extract bio
                bio_elements = await self.page.query_selector_all('header h1, header div[class*="bio"]')
                if bio_elements and len(bio_elements) > 0:
                    try:
                        profile_data['bio'] = await bio_elements[0].inner_text()
                    except Exception as e:
                        logger.debug(f"Failed to extract bio: {e}")
                    
                # Check for verification badge
                verified_elements = await self.page.query_selector_all('[aria-label="Verified"]')
                profile_data['is_verified'] = len(verified_elements) > 0
                
            except Exception as e:
                logger.debug(f"Bio/verification extraction failed: {e}")
                
            # Strategy 4: Extract from JavaScript objects
            try:
                # Look for window._sharedData or similar
                shared_data = await self.page.evaluate('window._sharedData')
                if shared_data:
                    logger.debug(f"Found shared data: {type(shared_data)}")
                    # Parse shared data if available
                    
            except Exception as e:
                logger.debug(f"JavaScript data extraction failed: {e}")
                
            # Fill in defaults for missing data
            profile_data.setdefault('follower_count', 0)
            profile_data.setdefault('following_count', 0)
            profile_data.setdefault('post_count', 0)
            profile_data.setdefault('bio', '')
            profile_data.setdefault('is_verified', False)
            
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
        """Parse Instagram count format (e.g., '1.2K' -> 1200)."""
        text = text.strip().lower()
        
        # Remove commas
        text = text.replace(',', '')
        
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
        """Extract recent posts from profile page."""
        posts = []
        
        if not self.page:
            return posts
            
        try:
            # Scroll to load posts
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            # Look for post links
            post_links = await self.page.query_selector_all('a[href*="/p/"], article a')
            
            for i, link in enumerate(post_links[:limit]):
                try:
                    post_url = await link.get_attribute('href')
                    if not post_url:
                        continue
                        
                    # Make full URL
                    if not post_url.startswith('http'):
                        post_url = urljoin('https://www.instagram.com', post_url)
                        
                    # Extract basic post data
                    post_data = {
                        'id': f"post_{profile.handle}_{i}",
                        'url': post_url,
                        'timestamp': datetime.utcnow() - timedelta(days=i),
                        'like_count': 0,
                        'comment_count': 0,
                        'media_urls': [],
                        'is_video': False
                    }
                    
                    # Try to extract engagement data from the post element
                    try:
                        # Look for like/comment indicators
                        engagement_elements = await link.query_selector_all('span, div[class*="like"], div[class*="comment"]')
                        for element in engagement_elements:
                            text = await element.inner_text()
                            if any(indicator in text.lower() for indicator in ['like', '❤', '♥']):
                                post_data['like_count'] = self._parse_count(text)
                            elif any(indicator in text.lower() for indicator in ['comment', '💬']):
                                post_data['comment_count'] = self._parse_count(text)
                    except Exception as e:
                        logger.debug(f"Failed to extract engagement for post {i}: {e}")
                        
                    # Create RawPost
                    posts.append(RawPost(
                        id=post_data['id'],
                        platform=self.platform,
                        url=post_data['url'],
                        timestamp=post_data['timestamp'],
                        like_count=post_data['like_count'],
                        comment_count=post_data['comment_count'],
                        media_urls=post_data['media_urls'],
                        is_video=post_data['is_video']
                    ))
                    
                except Exception as e:
                    logger.error(f"Failed to extract post {i}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to extract posts: {e}")
            
        return posts
        
    async def _extract_comments(self, post: RawPost, limit: int = 50) -> List[RawComment]:
        """Extract comments from a specific post."""
        comments = []
        
        if not self.page:
            return comments
            
        try:
            # Navigate to post page
            await self.page.goto(post.url, wait_until='networkidle', timeout=30000)
            
            # Wait for comments to load
            await self.page.wait_for_selector('article', timeout=10000)
            
            # Check if comments are disabled
            disabled_elements = await self.page.query_selector_all('text=/comments.disabled|no.comments/i')
            if disabled_elements:
                logger.info(f"Comments disabled for post {post.id}")
                return comments
                
            # Look for comment elements
            comment_elements = await self.page.query_selector_all('ul[class*="comment"], div[class*="comment"], article ul li')
            
            for i, comment_element in enumerate(comment_elements[:limit]):
                try:
                    # Extract comment text
                    text_elements = await comment_element.query_selector_all('span, div[class*="text"]')
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
                    author_elements = await comment_element.query_selector_all('a[href*="/"], h3, h4')
                    author_id = "unknown"
                    if author_elements and len(author_elements) > 0:
                        try:
                            author_href = await author_elements[0].get_attribute('href')
                            if author_href:
                                author_id = author_href.strip('/').split('/')[0] if '/' in author_href else f"user_{i}"
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
            logger.error(f"Failed to extract comments for post {post.id}: {e}")
            
        return comments
        
    async def _log_scrape_metadata(self, handle: str, errors: List[str], data_completeness: DataCompleteness):
        """Log structured scrape metadata."""
        log_entry = {
            'handle': handle,
            'platform': 'instagram',
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
        log_file = os.path.join(logs_dir, f'instagram_scrape_{datetime.utcnow().strftime("%Y%m%d")}.jsonl')
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write scrape metadata log: {e}")
            
    async def scrape_profile(self, handle: str) -> Optional[RawProfile]:
        """Scrape Instagram profile data."""
        if not self.page:
            await self._setup_browser()
            
        return await self._extract_profile_data(handle)
        
    async def scrape_posts(self, profile: RawProfile, limit: int = 12) -> List[RawPost]:
        """Scrape recent posts from profile."""
        return await self._extract_posts(profile, limit)
        
    async def scrape_comments(self, post: RawPost, limit: int = 50) -> List[RawComment]:
        """Scrape comments from a specific post."""
        return await self._extract_comments(post, limit)
        
    async def run_scan(self, handle: str) -> ScrapeResult:
        """Run complete scan: profile, posts, and comments."""
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
            
        # 2. Posts
        posts = []
        try:
            posts = await self.scrape_posts(profile)
            if not posts and profile.post_count > 0:
                errors.append("No posts extracted despite profile showing posts")
                completeness = DataCompleteness.PARTIAL_NO_POSTS
        except Exception as e:
            errors.append(f"Post extraction error: {str(e)}")
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
                logger.debug(f"Comment extraction failed for post {post.id}: {e}")
                comments_blocked_count += 1
                
        # Update completeness based on comment availability
        if comments_blocked_count == len(posts) and len(posts) > 0:
            if completeness == DataCompleteness.FULL:
                completeness = DataCompleteness.PARTIAL_NO_COMMENTS
            errors.append("Comments blocked on all posts")
        elif comments_blocked_count > 0:
            errors.append(f"Comments blocked on {comments_blocked_count} posts")
            
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