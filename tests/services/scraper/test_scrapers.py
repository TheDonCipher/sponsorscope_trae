import unittest
from unittest.mock import MagicMock, AsyncMock
from shared.schemas.domain import DataCompleteness
from services.scraper.adapters.instagram import InstagramScraper
from services.scraper.adapters.tiktok import TikTokScraper

class TestInstagramScraper(unittest.IsolatedAsyncioTestCase):
    
    async def test_full_scan(self):
        scraper = InstagramScraper()
        result = await scraper.run_scan("test_user")
        
        self.assertEqual(result.data_completeness, DataCompleteness.FULL)
        self.assertIsNotNone(result.profile)
        self.assertTrue(len(result.posts) > 0)
        self.assertTrue(len(result.comments) > 0)
        
    async def test_private_profile(self):
        scraper = InstagramScraper()
        result = await scraper.run_scan("private_user")
        
        self.assertEqual(result.data_completeness, DataCompleteness.UNAVAILABLE)
        self.assertIsNone(result.profile)
        
    async def test_comments_blocked(self):
        scraper = InstagramScraper()
        # Mock scrape_comments to raise Exception
        scraper.scrape_comments = AsyncMock(side_effect=Exception("Login required"))
        
        result = await scraper.run_scan("test_user")
        
        self.assertEqual(result.data_completeness, DataCompleteness.PARTIAL_NO_COMMENTS)
        self.assertTrue(len(result.posts) > 0)
        self.assertEqual(len(result.comments), 0)
        self.assertIn("Comments blocked", result.errors[0])

class TestTikTokScraper(unittest.IsolatedAsyncioTestCase):
    
    async def test_full_scan(self):
        scraper = TikTokScraper()
        result = await scraper.run_scan("test_user")
        self.assertEqual(result.data_completeness, DataCompleteness.FULL)
        
    async def test_banned_user(self):
        scraper = TikTokScraper()
        result = await scraper.run_scan("banned_user")
        self.assertEqual(result.data_completeness, DataCompleteness.UNAVAILABLE)

if __name__ == '__main__':
    unittest.main()
