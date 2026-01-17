import pytest
import asyncio
import json
import os
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from shared.schemas.domain import Platform, DataCompleteness
from shared.schemas.raw import RawProfile, RawPost, RawComment
from services.scraper.adapters.instagram_playwright import InstagramPlaywrightScraper


class TestInstagramPlaywrightScraper:
    """Unit tests for InstagramPlaywrightScraper degradation paths."""
    
    @pytest.fixture
    def scraper(self):
        """Create scraper instance for testing."""
        return InstagramPlaywrightScraper()
        
    @pytest.fixture
    def mock_page(self):
        """Create mock page object."""
        page = AsyncMock()
        page.goto = AsyncMock()
        page.wait_for_selector = AsyncMock()
        page.query_selector_all = AsyncMock(return_value=[])
        page.get_attribute = AsyncMock(return_value=None)
        page.inner_text = AsyncMock(return_value="")
        page.evaluate = AsyncMock(return_value=None)
        return page
        
    @pytest.fixture
    def mock_browser_context(self, mock_page):
        """Create mock browser context."""
        context = AsyncMock()
        context.new_page = AsyncMock(return_value=mock_page)
        context.add_init_script = AsyncMock()
        context.close = AsyncMock()
        return context
        
    @pytest.fixture
    def mock_browser(self, mock_browser_context):
        """Create mock browser."""
        browser = AsyncMock()
        browser.new_context = AsyncMock(return_value=mock_browser_context)
        browser.version = AsyncMock(return_value="Chrome/120.0.0.0")
        browser.close = AsyncMock()
        return browser
        
    @pytest.fixture
    def mock_playwright(self, mock_browser):
        """Create mock playwright instance."""
        pw = MagicMock()
        pw.chromium = MagicMock()
        pw.chromium.launch = AsyncMock(return_value=mock_browser)
        return pw
        
    @pytest.mark.asyncio
    async def test_login_wall_detection(self, scraper, mock_page):
        """Test detection of login wall."""
        # Mock login form elements
        mock_page.query_selector_all = AsyncMock(side_effect=[
            [MagicMock()],  # Login elements found
            [],  # No rate limiting
            [],  # No challenge
            [],  # Not private
            []   # Not 404
        ])
        
        scraper.page = mock_page
        errors = await scraper._detect_blocking_mechanisms()
        
        assert "Login wall detected" in errors
        
    @pytest.mark.asyncio
    async def test_rate_limiting_detection(self, scraper, mock_page):
        """Test detection of rate limiting."""
        mock_page.query_selector_all = AsyncMock(side_effect=[
            [],  # No login wall
            [MagicMock()],  # Rate limiting detected
            [],  # No challenge
            [],  # Not private
            []   # Not 404
        ])
        
        scraper.page = mock_page
        errors = await scraper._detect_blocking_mechanisms()
        
        assert "Rate limiting detected" in errors
        
    @pytest.mark.asyncio
    async def test_challenge_captcha_detection(self, scraper, mock_page):
        """Test detection of challenge/captcha."""
        mock_page.query_selector_all = AsyncMock(side_effect=[
            [],  # No login wall
            [],  # No rate limiting
            [MagicMock()],  # Challenge detected
            [],  # Not private
            []   # Not 404
        ])
        
        scraper.page = mock_page
        errors = await scraper._detect_blocking_mechanisms()
        
        assert "Challenge/captcha detected" in errors
        
    @pytest.mark.asyncio
    async def test_private_profile_detection(self, scraper, mock_page):
        """Test detection of private profile."""
        mock_page.query_selector_all = AsyncMock(side_effect=[
            [],  # No login wall
            [],  # No rate limiting
            [],  # No challenge
            [MagicMock()],  # Private profile detected
            []   # Not 404
        ])
        
        scraper.page = mock_page
        errors = await scraper._detect_blocking_mechanisms()
        
        assert "Private profile detected" in errors
        
    @pytest.mark.asyncio
    async def test_profile_not_found_detection(self, scraper, mock_page):
        """Test detection of 404/profile not found."""
        mock_page.query_selector_all = AsyncMock(side_effect=[
            [],  # No login wall
            [],  # No rate limiting
            [],  # No challenge
            [],  # Not private
            [MagicMock()]  # 404 detected
        ])
        
        scraper.page = mock_page
        errors = await scraper._detect_blocking_mechanisms()
        
        assert "Profile not found (404)" in errors
        
    @pytest.mark.asyncio
    async def test_comments_disabled_detection(self, scraper, mock_page):
        """Test handling of disabled comments."""
        # Mock post data
        post = RawPost(
            id="test_post_1",
            platform=Platform.INSTAGRAM,
            url="https://instagram.com/p/test/",
            timestamp=datetime.utcnow(),
            like_count=100,
            comment_count=0,
            media_urls=[]
        )
        
        # Mock comments disabled
        mock_page.query_selector_all = AsyncMock(side_effect=[
            [MagicMock()],  # Comments disabled found
            []  # No comment elements
        ])
        
        scraper.page = mock_page
        comments = await scraper._extract_comments(post)
        
        assert len(comments) == 0
        
    @pytest.mark.asyncio
    async def test_parse_count_formats(self, scraper):
        """Test parsing of various Instagram count formats."""
        # Test various formats
        assert scraper._parse_count("1,234") == 1234
        assert scraper._parse_count("1.2K") == 1200
        assert scraper._parse_count("1.5M") == 1500000
        assert scraper._parse_count("2B") == 2000000000
        assert scraper._parse_count("123") == 123
        assert scraper._parse_count("invalid") == 0
        assert scraper._parse_count("") == 0
        
    @pytest.mark.asyncio
    async def test_profile_extraction_with_blocking(self, scraper, mock_page):
        """Test profile extraction when blocking mechanisms are detected."""
        # Mock blocking detection
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        
        with patch.object(scraper, '_detect_blocking_mechanisms', return_value=["Login wall detected"]):
            scraper.page = mock_page
            result = await scraper._extract_profile_data("test_user")
            
        assert result is None
        
    @pytest.mark.asyncio
    async def test_run_scan_with_login_wall(self, scraper, mock_page, mock_browser_context, mock_browser, mock_playwright):
        """Test complete scan when login wall is encountered."""
        with patch('playwright.async_api.async_playwright') as mock_pw_factory:
            mock_pw_factory.return_value.__aenter__.return_value = mock_playwright
            
            # Mock blocking detection
            mock_page.query_selector_all = AsyncMock(side_effect=[
                [MagicMock()],  # Login wall detected
                [], [], [], []
            ])
            
            result = await scraper.run_scan("test_user")
            
            assert result.data_completeness == DataCompleteness.UNAVAILABLE
            assert "Login wall detected" in result.errors
            assert result.profile is None
            
    @pytest.mark.asyncio
    async def test_run_scan_with_private_profile(self, scraper, mock_page, mock_browser_context, mock_browser, mock_playwright):
        """Test complete scan when profile is private."""
        with patch('playwright.async_api.async_playwright') as mock_pw_factory:
            mock_pw_factory.return_value.__aenter__.return_value = mock_playwright
            
            # Mock private profile detection
            mock_page.query_selector_all = AsyncMock(side_effect=[
                [], [], [], [MagicMock()], []  # Private profile detected
            ])
            
            result = await scraper.run_scan("private_user")
            
            assert result.data_completeness == DataCompleteness.UNAVAILABLE
            assert "Private profile detected" in result.errors
            assert result.profile is None
            
    @pytest.mark.asyncio
    async def test_run_scan_with_rate_limiting(self, scraper, mock_page, mock_browser_context, mock_browser, mock_playwright):
        """Test complete scan when rate limited."""
        with patch('playwright.async_api.async_playwright') as mock_pw_factory:
            mock_pw_factory.return_value.__aenter__.return_value = mock_playwright
            
            # Mock successful profile extraction but rate limiting on posts
            mock_page.query_selector_all = AsyncMock(side_effect=[
                [], [], [], [], []  # No blocking mechanisms
            ])
            
            # Mock profile data extraction
            mock_page.get_attribute = AsyncMock(return_value="1,234 followers, 567 following, 89 posts")
            
            with patch.object(scraper, '_extract_posts', side_effect=Exception("Rate limited")):
                result = await scraper.run_scan("test_user")
                
                assert "Post extraction error: Rate limited" in result.errors
                
    @pytest.mark.asyncio
    async def test_log_scrape_metadata(self, scraper, tmp_path):
        """Test structured logging of scrape metadata."""
        # Mock logs directory
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        
        with patch('os.path.dirname', return_value=str(tmp_path)), \
             patch('os.makedirs'):
            
            await scraper._log_scrape_metadata(
                "test_user",
                ["Login wall detected"],
                DataCompleteness.UNAVAILABLE
            )
            
            # Check log file was created
            log_files = list(logs_dir.glob("*.jsonl"))
            assert len(log_files) == 1
            
            # Verify log content
            with open(log_files[0], 'r') as f:
                log_entry = json.loads(f.readline())
                
            assert log_entry['handle'] == "test_user"
            assert log_entry['platform'] == "instagram"
            assert log_entry['failure_reason'] == "Login wall detected"
            assert log_entry['data_completeness'] == "UNAVAILABLE"
            
    @pytest.mark.asyncio
    async def test_cleanup_resources(self, scraper, mock_page, mock_browser_context, mock_browser):
        """Test proper cleanup of browser resources."""
        scraper.page = mock_page
        scraper.context = mock_browser_context
        scraper.browser = mock_browser
        
        await scraper.cleanup()
        
        mock_page.close.assert_called_once()
        mock_browser_context.close.assert_called_once()
        mock_browser.close.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_browser_initialization_failure(self, scraper):
        """Test handling of browser initialization failure."""
        with patch('playwright.async_api.async_playwright', side_effect=Exception("Browser failed")):
            result = await scraper.run_scan("test_user")
            
            assert result.data_completeness == DataCompleteness.FAILED
            assert "Browser initialization failed" in result.errors
            
    @pytest.mark.asyncio
    async def test_partial_data_extraction(self, scraper, mock_page, mock_browser_context, mock_browser, mock_playwright):
        """Test scan with partial data extraction (some data available)."""
        with patch('playwright.async_api.async_playwright') as mock_pw_factory:
            mock_pw_factory.return_value.__aenter__.return_value = mock_playwright
            
            # Mock successful profile extraction
            mock_page.get_attribute = AsyncMock(return_value="1,234 followers, 567 following, 89 posts")
            
            # Mock some posts but fail on comments
            with patch.object(scraper, '_extract_posts', return_value=[
                RawPost(
                    id="post_1",
                    platform=Platform.INSTAGRAM,
                    url="https://instagram.com/p/test1/",
                    timestamp=datetime.utcnow(),
                    like_count=100,
                    comment_count=10,
                    media_urls=[]
                )
            ]):
                with patch.object(scraper, '_extract_comments', side_effect=Exception("Comments blocked")):
                    result = await scraper.run_scan("test_user")
                    
                    assert result.profile is not None
                    assert len(result.posts) == 1
                    assert len(result.comments) == 0
                    assert "Comments blocked on 1 posts" in result.errors
                    
    @pytest.mark.asyncio
    async def test_empty_profile_data_fallback(self, scraper, mock_page):
        """Test fallback behavior when profile data extraction returns empty."""
        # Mock empty extraction results
        mock_page.get_attribute = AsyncMock(return_value=None)
        mock_page.inner_text = AsyncMock(return_value="")
        mock_page.query_selector_all = AsyncMock(return_value=[])
        
        scraper.page = mock_page
        
        with patch.object(scraper, '_detect_blocking_mechanisms', return_value=[]):
            result = await scraper._extract_profile_data("test_user")
            
            # Should still return a profile with default values
            assert result is not None
            assert result.handle == "test_user"
            assert result.follower_count == 0
            assert result.following_count == 0
            assert result.post_count == 0
            assert result.bio == ""
            assert result.is_verified == False