import unittest
from datetime import datetime, timedelta
from typing import List

from shared.schemas.raw import RawProfile, RawPost, RawComment, Platform
from shared.schemas.domain import DataCompleteness
from services.analyzer.heuristics import compute_true_engagement, compute_audience_authenticity

class TestHeuristics(unittest.TestCase):
    
    def setUp(self):
        self.base_time = datetime.utcnow()
        self.profile = RawProfile(
            handle="@test",
            platform=Platform.INSTAGRAM,
            follower_count=1000,
            following_count=100,
            post_count=10,
            scraped_at=self.base_time
        )
        
    def create_posts(self, count: int, likes: int, comments: int) -> List[RawPost]:
        posts = []
        for i in range(count):
            posts.append(RawPost(
                id=f"post_{i}",
                platform=Platform.INSTAGRAM,
                url=f"http://test.com/{i}",
                timestamp=self.base_time - timedelta(days=i),
                like_count=likes,
                comment_count=comments
            ))
        return posts
        
    def create_comments(self, count: int, texts: List[str]) -> List[RawComment]:
        comments = []
        for i in range(count):
            text = texts[i % len(texts)]
            comments.append(RawComment(
                id=f"comment_{i}",
                text=text,
                timestamp=self.base_time - timedelta(minutes=i),
                author_id=f"user_{i}"
            ))
        return comments

    def test_engagement_normal(self):
        # 10 posts, 50 likes, 5 comments each.
        # Raw Rate = (50 + 5*3) / 1000 = 65 / 1000 = 0.065 (6.5%)
        # This is > 6.0%, so score should be > 90.
        posts = self.create_posts(10, 50, 5)
        comments = self.create_comments(50, ["Great!", "Nice"])
        
        result = compute_true_engagement(self.profile, posts, comments)
        
        self.assertAlmostEqual(result.raw_value, 0.065)
        self.assertTrue(result.score > 90)
        self.assertEqual(result.data_completeness, DataCompleteness.FULL)
        self.assertEqual(result.confidence, 1.0)
        
    def test_engagement_zero(self):
        posts = self.create_posts(10, 0, 0)
        result = compute_true_engagement(self.profile, posts, [])
        
        self.assertEqual(result.raw_value, 0.0)
        self.assertEqual(result.score, 0.0)
        
    def test_engagement_partial_no_comments(self):
        # Posts say 5 comments, but comments list is empty
        posts = self.create_posts(10, 50, 5)
        result = compute_true_engagement(self.profile, posts, [])
        
        self.assertEqual(result.data_completeness, DataCompleteness.PARTIAL_NO_COMMENTS)
        self.assertTrue(result.confidence < 1.0)
        # Score calculation should still work based on counts
        self.assertAlmostEqual(result.raw_value, 0.065)

    def test_authenticity_high(self):
        # Diverse comments, unique authors
        # Generate 20 unique comments
        texts = [f"This is unique comment number {i} with some random words" for i in range(20)]
        comments = self.create_comments(20, texts)
        posts = self.create_posts(5, 100, 4)
        
        result = compute_audience_authenticity(self.profile, posts, comments)
        
        self.assertTrue(result.score > 80, f"Score {result.score} should be > 80. Raw: {result.raw_value}") # Expect high authenticity
        self.assertTrue(result.raw_value < 0.2) # Expect low bot prob
        
    def test_authenticity_bot_behavior(self):
        # Repetitive comments, few authors (simulated by same text, though create_comments uses unique author_id by default)
        # Let's force non-unique authors
        comments = []
        for i in range(20):
            comments.append(RawComment(
                id=f"c_{i}",
                text="Great pic", # Low entropy
                timestamp=self.base_time, # Zero variance
                author_id="bot_net_1" # Zero uniqueness
            ))
            
        result = compute_audience_authenticity(self.profile, [], comments)
        
        # Bot prob should be very high (1.0), so authenticity 0.0
        self.assertAlmostEqual(result.score, 0.0)
        self.assertAlmostEqual(result.raw_value, 1.0)

    def test_authenticity_no_comments(self):
        posts = self.create_posts(5, 10, 5) # Expects comments
        result = compute_audience_authenticity(self.profile, posts, [])
        
        self.assertEqual(result.data_completeness, DataCompleteness.PARTIAL_NO_COMMENTS)
        self.assertEqual(result.score, 50.0) # Fallback
        self.assertTrue(result.confidence <= 0.1)

if __name__ == '__main__':
    unittest.main()
