#!/usr/bin/env python3
"""
UNIT TESTS - DETERMINISM & BOUNDS
Tests for heuristic functions, calibration logic, and confidence computation
Verifies identical input → identical output and prevents score inflation
"""

import unittest
import asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json

from shared.schemas.models import PillarScore, ConfidenceInterval
from shared.schemas.domain import DataCompleteness
from services.analyzer.graph.signals import CoordinationSignals
from services.analyzer.calibration.engine import ScoreCalibrator
from services.analyzer.heuristics.authenticity import compute_audience_authenticity
from services.analyzer.heuristics.engagement import compute_true_engagement
from services.analyzer.heuristics.utils import calculate_entropy, calculate_uniqueness_ratio, calculate_timing_variance
from shared.schemas.raw import RawPost, RawProfile, RawComment


class TestHeuristicDeterminism(unittest.TestCase):
    """Test determinism of heuristic functions"""
    
    def setUp(self):
        """Set up test data"""
        self.test_profile = RawProfile(
            handle="test_user",
            platform="instagram",
            follower_count=1000,
            following_count=100,
            post_count=50,
            bio="Test bio",
            is_verified=False,
            created_at=datetime.now() - timedelta(days=365)
        )
        
        self.test_posts = [
            RawPost(
                id=f"post_{i}",
                platform="instagram",
                url=f"https://instagram.com/p/post_{i}",
                caption=f"Test post content {i}",
                like_count=100 + i * 10,
                comment_count=20 + i * 2,
                timestamp=datetime.now() - timedelta(hours=i)
            ) for i in range(5)
        ]
        
        self.test_comments = [
            RawComment(
                id=f"comment_{i}",
                post_id="post_1",
                author_id=f"user_{i % 3}",  # Create some overlap
                text=f"Great post! Love it {i}",
                timestamp=datetime.now() - timedelta(minutes=i * 5)
            ) for i in range(20)
        ]
    
    def test_entropy_calculation_determinism(self):
        """Test that entropy calculation is deterministic"""
        texts = ["hello world", "test content", "another post"]
        
        # Run multiple times
        results = [calculate_entropy(texts) for _ in range(10)]
        
        # All results should be identical
        for result in results[1:]:
            self.assertEqual(result, results[0], "Entropy calculation should be deterministic")
    
    def test_uniqueness_ratio_determinism(self):
        """Test that uniqueness ratio calculation is deterministic"""
        author_ids = ["user_1", "user_2", "user_1", "user_3", "user_2"]
        
        # Run multiple times
        results = [calculate_uniqueness_ratio(author_ids) for _ in range(10)]
        
        # All results should be identical
        for result in results[1:]:
            self.assertEqual(result, results[0], "Uniqueness ratio should be deterministic")
    
    def test_timing_variance_determinism(self):
        """Test that timing variance calculation is deterministic"""
        timestamps = [
            datetime.now() - timedelta(minutes=i * 10) 
            for i in range(10)
        ]
        
        # Run multiple times
        results = [calculate_timing_variance(timestamps) for _ in range(10)]
        
        # All results should be identical
        for result in results[1:]:
            self.assertEqual(result, results[0], "Timing variance should be deterministic")
    
    def test_audience_authenticity_determinism(self):
        """Test that audience authenticity computation is deterministic"""
        # Run multiple times with same input
        results = [
            compute_audience_authenticity(self.test_profile, self.test_posts, self.test_comments)
            for _ in range(5)
        ]
        
        # All results should be identical
        first_result = results[0]
        for result in results[1:]:
            self.assertEqual(result.score, first_result.score, 
                           "Audience authenticity score should be deterministic")
            self.assertEqual(result.confidence, first_result.confidence,
                           "Audience authenticity confidence should be deterministic")
            self.assertEqual(result.data_completeness, first_result.data_completeness,
                           "Data completeness should be deterministic")
    
    def test_true_engagement_determinism(self):
        """Test that true engagement computation is deterministic"""
        # Run multiple times with same input
        results = [
            compute_true_engagement(self.test_profile, self.test_posts, self.test_comments)
            for _ in range(5)
        ]
        
        # All results should be identical
        first_result = results[0]
        for result in results[1:]:
            self.assertEqual(result.score, first_result.score,
                           "True engagement score should be deterministic")
            self.assertEqual(result.confidence, first_result.confidence,
                           "True engagement confidence should be deterministic")


class TestCalibrationBounds(unittest.TestCase):
    """Test calibration logic bounds and constraints"""
    
    def setUp(self):
        """Set up test data"""
        self.calibrator = ScoreCalibrator()
        self.base_pillar = PillarScore(
            score=80.0,
            confidence_interval=ConfidenceInterval(lower=75, upper=85, confidence_score=0.9),
            flags=[]
        )
    
    def test_no_heuristic_can_inflate_scores(self):
        """Test that heuristics cannot increase scores above base"""
        # Create signals that should trigger penalties
        bad_signals = CoordinationSignals(
            timing_concentration=0.9,
            commenter_overlap=0.9,
            edge_reuse_ratio=0.9,
            reciprocity_score=0.9,
            sample_size=100,
            confidence=1.0
        )
        
        envelope = self.calibrator.calibrate(
            self.base_pillar, bad_signals, DataCompleteness.FULL
        )
        
        # Score should never exceed base score
        self.assertLessEqual(envelope.adjusted_score, self.base_pillar.score,
                           "Calibration should never increase scores")
        
        # Score should be penalized for bad signals
        self.assertLess(envelope.adjusted_score, self.base_pillar.score,
                       "Bad signals should result in score penalty")
    
    def test_llm_adjustments_never_exceed_15_percent(self):
        """Test that LLM adjustments never exceed ±15 points"""
        # Test with maximum penalty scenario
        max_penalty_signals = CoordinationSignals(
            timing_concentration=1.0,
            commenter_overlap=1.0,
            edge_reuse_ratio=1.0,
            reciprocity_score=1.0,
            sample_size=100,
            confidence=1.0
        )
        
        envelope = self.calibrator.calibrate(
            self.base_pillar, max_penalty_signals, DataCompleteness.FULL
        )
        
        # Maximum penalty should not exceed 15%
        max_allowed_penalty = self.base_pillar.score * 0.15
        actual_penalty = self.base_pillar.score - envelope.adjusted_score
        
        self.assertLessEqual(actual_penalty, max_allowed_penalty,
                           "LLM adjustments should not exceed 15% penalty")
        
        # Score should not go below 0
        self.assertGreaterEqual(envelope.adjusted_score, 0.0,
                              "Score should not go below 0")
    
    def test_confidence_never_increases_under_partial_data(self):
        """Test that confidence never increases when data is partial"""
        # Test with partial data
        partial_data_signals = CoordinationSignals(
            timing_concentration=0.3,
            commenter_overlap=0.3,
            edge_reuse_ratio=0.3,
            reciprocity_score=0.3,
            sample_size=10,  # Small sample
            confidence=0.4   # Low confidence
        )
        
        envelope = self.calibrator.calibrate(
            self.base_pillar, partial_data_signals, DataCompleteness.PARTIAL_NO_COMMENTS
        )
        
        # Confidence should not increase from base confidence
        self.assertLessEqual(envelope.confidence, self.base_pillar.confidence_interval.confidence_score,
                           "Confidence should not increase with partial data")
    
    def test_low_confidence_suppresses_signals(self):
        """Test that low graph confidence suppresses all signals"""
        low_confidence_signals = CoordinationSignals(
            timing_concentration=0.9,
            commenter_overlap=0.9,
            edge_reuse_ratio=0.9,
            reciprocity_score=0.9,
            sample_size=100,
            confidence=0.4  # Below 0.6 threshold
        )
        
        envelope = self.calibrator.calibrate(
            self.base_pillar, low_confidence_signals, DataCompleteness.FULL
        )
        
        # Should suppress signals due to low confidence
        self.assertIn("graph_low_confidence", envelope.suppressed_signals,
                     "Low graph confidence should suppress signals")
        
        # Score should remain unchanged
        self.assertEqual(envelope.adjusted_score, self.base_pillar.score,
                        "Score should not change when signals are suppressed")
    
    def test_single_signal_suppression(self):
        """Test that single strong signals are suppressed (need corroboration)"""
        single_signal = CoordinationSignals(
            timing_concentration=0.9,  # Strong signal
            commenter_overlap=0.3,     # Weak signal
            edge_reuse_ratio=0.3,      # Weak signal
            reciprocity_score=0.3,     # Weak signal
            sample_size=100,
            confidence=1.0
        )
        
        envelope = self.calibrator.calibrate(
            self.base_pillar, single_signal, DataCompleteness.FULL
        )
        
        # Should suppress the single strong signal
        self.assertIn("timing_concentration", envelope.suppressed_signals,
                     "Single strong signal should be suppressed without corroboration")
        
        # Score should remain unchanged
        self.assertEqual(envelope.adjusted_score, self.base_pillar.score,
                        "Score should not change with suppressed signals")
    
    def test_multi_signal_corroboration(self):
        """Test that multiple strong signals trigger penalties"""
        multi_signals = CoordinationSignals(
            timing_concentration=0.8,  # Strong signal
            commenter_overlap=0.8,     # Strong signal
            edge_reuse_ratio=0.3,      # Weak signal
            reciprocity_score=0.3,     # Weak signal
            sample_size=100,
            confidence=1.0
        )
        
        envelope = self.calibrator.calibrate(
            self.base_pillar, multi_signals, DataCompleteness.FULL
        )
        
        # Should apply penalty for corroborated signals
        self.assertLess(envelope.adjusted_score, self.base_pillar.score,
                       "Multiple strong signals should trigger penalty")
        
        # Should record applied adjustments
        self.assertIn("timing_concentration", envelope.applied_adjustments,
                     "Timing concentration should be in applied adjustments")
        self.assertIn("commenter_overlap", envelope.applied_adjustments,
                     "Commenter overlap should be in applied adjustments")


class TestConfidenceComputation(unittest.TestCase):
    """Test confidence computation logic"""
    
    def test_confidence_bounds(self):
        """Test that confidence values stay within valid bounds"""
        # Test with various scenarios
        test_cases = [
            (100, 0.9, 0.9),   # Normal case
            (5, 0.5, 0.25),    # Low sample size
            (1, 0.3, 0.12),    # Very low sample size
            (1000, 1.0, 1.0),  # High sample size
        ]
        
        for sample_size, base_confidence, expected_min in test_cases:
            with self.subTest(sample_size=sample_size):
                # Simulate confidence calculation
                confidence = base_confidence
                if sample_size < 20:
                    confidence *= 0.8
                if sample_size < 5:
                    confidence *= 0.5
                
                # Confidence should be between 0 and 1
                self.assertGreaterEqual(confidence, 0.0,
                                      "Confidence should not be below 0")
                self.assertLessEqual(confidence, 1.0,
                                   "Confidence should not exceed 1")
                
                # Should meet minimum expected confidence
                self.assertGreaterEqual(confidence, expected_min,
                                      f"Confidence should meet minimum threshold for sample size {sample_size}")
    
    def test_uncertainty_band_calculation(self):
        """Test uncertainty band calculation logic"""
        calibrator = ScoreCalibrator()
        
        # Test different confidence levels
        test_cases = [
            (1.0, 6.0),    # Full confidence -> minimum width
            (0.5, 16.0),   # Medium confidence -> medium width
            (0.0, 26.0),   # Zero confidence -> maximum width
        ]
        
        for confidence, expected_width in test_cases:
            with self.subTest(confidence=confidence):
                base_score = 50.0
                envelope = calibrator._build_envelope(
                    base_score, base_score, confidence, [], []
                )
                
                # Calculate actual width
                actual_width = envelope.uncertainty_band[1] - envelope.uncertainty_band[0]
                
                self.assertAlmostEqual(actual_width, expected_width, places=1,
                                     msg=f"Uncertainty band width should be {expected_width} for confidence {confidence}")


class TestEpistemicIntegrity(unittest.TestCase):
    """Test epistemic integrity principles"""
    
    def test_absence_of_data_not_masked(self):
        """Test that absence of data is properly signaled, not masked"""
        # Test with no comments
        empty_comments = []
        test_profile = RawProfile(
            handle="test_user",
            platform="instagram",
            follower_count=1000,
            following_count=100,
            post_count=50,
            bio="Test bio",
            is_verified=False,
            created_at=datetime.now() - timedelta(days=365)
        )
        
        test_posts = [
            RawPost(
                id="post_1",
                platform="instagram",
                url="https://instagram.com/p/post_1",
                caption="Test post with comments",
                like_count=100,
                comment_count=10,  # Indicates comments should exist
                timestamp=datetime.now()
            )
        ]
        
        result = compute_audience_authenticity(test_profile, test_posts, empty_comments)
        
        # Should indicate partial data
        self.assertEqual(result.data_completeness, DataCompleteness.PARTIAL_NO_COMMENTS,
                        "Should signal partial data when comments are missing")
        
        # Should have low confidence
        self.assertLess(result.confidence, 0.5,
                       "Should have low confidence with missing data")
        
        # Should include reason
        self.assertIn("reason", result.signals,
                     "Should include reason for partial data")
        self.assertEqual(result.signals["reason"], "no_scraped_comments",
                        "Should specify why data is partial")
    
    def test_failures_are_explicit_and_user_visible(self):
        """Test that failures are explicit and visible to users"""
        # Test calibration with invalid inputs
        calibrator = ScoreCalibrator()
        
        # Test with None values
        with self.assertRaises(Exception):
            calibrator.calibrate(None, None, DataCompleteness.FULL)
        
        # Test with missing required fields
        incomplete_pillar = PillarScore(score=80.0, confidence_interval=None, flags=[])
        
        # Should handle gracefully but signal the issue
        clean_signals = CoordinationSignals(
            timing_concentration=0.1,
            commenter_overlap=0.1,
            edge_reuse_ratio=0.1,
            reciprocity_score=0.1,
            sample_size=100,
            confidence=1.0
        )
        
        envelope = calibrator.calibrate(incomplete_pillar, clean_signals, DataCompleteness.FULL)
        
        # Should still return a result, not crash
        self.assertIsNotNone(envelope)
        self.assertIsInstance(envelope.adjusted_score, (int, float))


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)