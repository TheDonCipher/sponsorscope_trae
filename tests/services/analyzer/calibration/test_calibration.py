import unittest
from shared.schemas.models import PillarScore
from shared.schemas.domain import DataCompleteness
from services.analyzer.graph.signals import CoordinationSignals
from services.analyzer.calibration.engine import ScoreCalibrator

class TestScoreCalibrator(unittest.TestCase):
    
    def setUp(self):
        self.calibrator = ScoreCalibrator()
        from shared.schemas.models import ConfidenceInterval
        self.base_pillar = PillarScore(
            score=80.0, 
            confidence_interval=ConfidenceInterval(lower=75, upper=85, confidence_score=0.9), 
            flags=[]
        )
        self.clean_signals = CoordinationSignals(
            timing_concentration=0.1,
            commenter_overlap=0.1,
            edge_reuse_ratio=0.1,
            reciprocity_score=0.1,
            sample_size=100,
            confidence=1.0
        )
        
    def test_clean_pass(self):
        """No signals should mean no change."""
        envelope = self.calibrator.calibrate(
            self.base_pillar, self.clean_signals, DataCompleteness.FULL
        )
        self.assertEqual(envelope.adjusted_score, 80.0)
        self.assertEqual(len(envelope.applied_adjustments), 0)
        
    def test_multi_signal_penalty(self):
        """Two strong signals should trigger penalty."""
        bad_signals = self.clean_signals.model_copy(update={
            "timing_concentration": 0.8,
            "edge_reuse_ratio": 0.8
        })
        
        envelope = self.calibrator.calibrate(
            self.base_pillar, bad_signals, DataCompleteness.FULL
        )
        
        # Penalty: 2 signals * 5% = 10%
        # 80 * 0.9 = 72
        self.assertAlmostEqual(envelope.adjusted_score, 72.0)
        self.assertIn("timing_concentration", envelope.applied_adjustments)
        self.assertIn("edge_reuse_ratio", envelope.applied_adjustments)
        
    def test_single_signal_suppression(self):
        """One signal is not enough (Corroboration Rule)."""
        one_bad_signal = self.clean_signals.model_copy(update={
            "timing_concentration": 0.9
        })
        
        envelope = self.calibrator.calibrate(
            self.base_pillar, one_bad_signal, DataCompleteness.FULL
        )
        
        self.assertEqual(envelope.adjusted_score, 80.0)
        self.assertIn("timing_concentration", envelope.suppressed_signals)
        
    def test_low_confidence_suppression(self):
        """Low graph confidence should suppress even strong signals."""
        unreliable_signals = self.clean_signals.model_copy(update={
            "timing_concentration": 0.9,
            "edge_reuse_ratio": 0.9,
            "confidence": 0.4 # Below 0.6 threshold
        })
        
        envelope = self.calibrator.calibrate(
            self.base_pillar, unreliable_signals, DataCompleteness.FULL
        )
        
        self.assertEqual(envelope.adjusted_score, 80.0)
        self.assertIn("graph_low_confidence", envelope.suppressed_signals)
        # Check uncertainty widening (Confidence dropped 10% -> 0.81)
        # Width = 6 + (1 - 0.81)*20 = 6 + 3.8 = 9.8 => ±4.9
        band_width = envelope.uncertainty_band[1] - envelope.uncertainty_band[0]
        self.assertTrue(band_width > 6.0)

if __name__ == '__main__':
    unittest.main()
