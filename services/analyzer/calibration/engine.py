from typing import List
from shared.schemas.models import PillarScore
from services.analyzer.graph.signals import CoordinationSignals
from services.analyzer.calibration.schema import CalibratedScoreEnvelope
from shared.schemas.domain import DataCompleteness

class ScoreCalibrator:
    """
    Applies safety rules and soft penalties to Phase 1 scores based on Phase 2 signals.
    """
    
    def calibrate(
        self,
        pillar_score: PillarScore,
        coordination_signals: CoordinationSignals,
        data_completeness: DataCompleteness
    ) -> CalibratedScoreEnvelope:
        
        base_score = pillar_score.score
        # Extract confidence from nested interval if available, else default to 1.0 (legacy fallback)
        base_confidence = 1.0
        if pillar_score.confidence_interval:
             base_confidence = pillar_score.confidence_interval.confidence_score
        
        # Initialize
        adjusted_score = base_score
        confidence = base_confidence
        applied_adjustments = []
        suppressed_signals = []
        
        # --- Safety Check: Signal Confidence ---
        # Rule: If graph confidence < 0.6, suppress all signals
        if coordination_signals.confidence < 0.6:
            suppressed_signals.append("graph_low_confidence")
            # Return early with widened uncertainty
            return self._build_envelope(
                base_score, base_score, confidence * 0.9, [], suppressed_signals
            )
            
        # --- Rule 3: Multi-Signal Corroboration ---
        # At least 2 signals > 0.7 required
        strong_signals = []
        if coordination_signals.timing_concentration > 0.7:
            strong_signals.append("timing_concentration")
        if coordination_signals.edge_reuse_ratio > 0.7:
            strong_signals.append("edge_reuse_ratio")
        if coordination_signals.commenter_overlap > 0.7:
            strong_signals.append("commenter_overlap")
            
        if len(strong_signals) < 2:
            suppressed_signals.extend(strong_signals)
            strong_signals = [] # Clear them so no penalty applies
            
        # --- Rule 2: Confidence Before Score ---
        # Penalties reduce confidence first.
        confidence_penalty = 0.0
        if strong_signals:
            confidence_penalty = 0.2 # Flat penalty for coordinated behavior
            
        confidence = max(0.0, confidence - confidence_penalty)
        
        # If confidence drops below 0.5, STOP score adjustment
        if confidence < 0.5:
            suppressed_signals.append("low_resultant_confidence")
            return self._build_envelope(
                base_score, base_score, confidence, [], suppressed_signals + applied_adjustments
            )
            
        # --- Rule 1: Soft Penalty ---
        # Max 15% reduction
        score_penalty_factor = 1.0
        if strong_signals:
            # Simple logic: 5% per signal, max 15%
            penalty = min(0.15, len(strong_signals) * 0.05)
            score_penalty_factor = 1.0 - penalty
            applied_adjustments.extend(strong_signals)
            
        adjusted_score = base_score * score_penalty_factor
        
        return self._build_envelope(
            base_score, adjusted_score, confidence, applied_adjustments, suppressed_signals
        )
        
    def _build_envelope(
        self, 
        base: float, 
        adjusted: float, 
        confidence: float, 
        applied: List[str], 
        suppressed: List[str]
    ) -> CalibratedScoreEnvelope:
        
        # Uncertainty Band Calculation
        # Base width = 6 (±3)
        # Low confidence expands width
        # Width = 6 + (1 - confidence) * 20
        # e.g. Conf 1.0 -> Width 6 (±3)
        # e.g. Conf 0.5 -> Width 16 (±8)
        # e.g. Conf 0.0 -> Width 26 (±13)
        
        width = 6.0 + (1.0 - confidence) * 20.0
        half_width = width / 2.0
        
        low = max(0.0, adjusted - half_width)
        high = min(100.0, adjusted + half_width)
        
        return CalibratedScoreEnvelope(
            base_score=base,
            adjusted_score=adjusted,
            uncertainty_band=(low, high),
            confidence=confidence,
            applied_adjustments=applied,
            suppressed_signals=suppressed
        )
