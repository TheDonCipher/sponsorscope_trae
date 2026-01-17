"""
AI Refinement Boundary Auditor for SponsorScope.ai

This module implements comprehensive auditing for AI-driven score refinements,
ensuring LLM adjustments stay within ±15 boundaries while maintaining confidence
integrity under partial data conditions.

Key Features:
- Real-time boundary monitoring (±15 limits)
- Confidence validation under partial data conditions
- Reasoning string verification
- Cultural slang and mixed sentiment handling
- Comprehensive audit trails and reporting
"""

import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from shared.schemas.domain import DataCompleteness
from .types import LLMRefinementResult

logger = logging.getLogger(__name__)


class BoundaryViolationType(Enum):
    """Types of boundary violations that can occur."""
    ADJUSTMENT_EXCEEDED = "adjustment_exceeded"
    CONFIDENCE_INCREASE_PARTIAL_DATA = "confidence_increase_partial_data"
    MISSING_REASONING = "missing_reasoning"
    SARCASTIC_CONTENT_UNHANDLED = "sarcastic_content_unhandled"
    CULTURAL_SLANG_MISINTERPRETED = "cultural_slang_misinterpreted"
    MIXED_SENTIMENT_CONFUSION = "mixed_sentiment_confusion"


@dataclass
class BoundaryAuditRecord:
    """Record of a boundary audit check."""
    timestamp: datetime
    handle: str
    platform: str
    raw_heuristic_score: float
    llm_adjusted_score: float
    adjustment_delta: float
    original_confidence: float
    final_confidence: float
    confidence_delta: float
    data_completeness: DataCompleteness
    reasoning_string: str
    boundary_violations: List[BoundaryViolationType]
    sarcastic_content_detected: bool
    cultural_slang_detected: bool
    mixed_sentiment_detected: bool
    justification: str
    audit_score: float  # 0-100, higher is better compliance


@dataclass
class AuditSummary:
    """Summary of multiple boundary audits."""
    total_audits: int
    compliant_audits: int
    violation_count: int
    violation_types: Dict[BoundaryViolationType, int]
    average_adjustment_delta: float
    average_confidence_delta: float
    compliance_rate: float
    risk_score: float  # 0-100, lower is better


class AIRefinementBoundaryAuditor:
    """
    Comprehensive auditor for AI refinement boundaries.
    
    This class implements the core auditing logic to ensure LLM adjustments
    stay within specified boundaries and maintain epistemic integrity.
    """
    
    def __init__(self, adjustment_boundary: float = 15.0):
        """
        Initialize the boundary auditor.
        
        Args:
            adjustment_boundary: Maximum allowed adjustment (±15 by default)
        """
        self.adjustment_boundary = adjustment_boundary
        self.audit_log: List[BoundaryAuditRecord] = []
        
        # Cultural slang and sarcasm detection patterns
        self.sarcasm_indicators = [
            "yeah right", "sure", "obviously", "brilliant", "fantastic",
            "amazing", "wonderful", "perfect", "exactly what i wanted",
            "just what i needed", "couldn't be better"
        ]
        
        self.cultural_slang_patterns = {
            "american": ["dope", "lit", "fire", "sick", "tight", "gucci"],
            "british": ["brilliant", "bloody", "chuffed", "gutted", "knackered"],
            "australian": ["arvo", "barbie", "brekkie", "servo", "thongs"],
            "gen_z": ["bet", "cap", "no cap", "slay", "queen", "king"],
            "internet": ["lol", "lmao", "omg", "wtf", "smh", "tbh"]
        }
        
        self.mixed_sentiment_indicators = [
            "but", "however", "although", "though", "yet", "still",
            "nevertheless", "nonetheless", "despite", "while"
        ]
    
    def audit_refinement(
        self,
        heuristic_result: Any,
        refinement_result: LLMRefinementResult,
        handle: str,
        platform: str,
        sample_content: Optional[List[str]] = None
    ) -> BoundaryAuditRecord:
        """
        Perform comprehensive boundary audit on an LLM refinement.
        
        Args:
            heuristic_result: Original heuristic analysis result
            refinement_result: LLM refinement result to audit
            handle: Social media handle being analyzed
            platform: Platform (Instagram, TikTok, etc.)
            sample_content: Sample content for cultural/sentiment analysis
            
        Returns:
            BoundaryAuditRecord with detailed audit findings
        """
        
        timestamp = datetime.utcnow()
        violations = []
        
        # Calculate deltas
        adjustment_delta = refinement_result.adjustment
        confidence_delta = refinement_result.confidence - heuristic_result.confidence
        
        # 1. Check adjustment boundary (±15 limit)
        if abs(adjustment_delta) > self.adjustment_boundary:
            violations.append(BoundaryViolationType.ADJUSTMENT_EXCEEDED)
            logger.warning(
                f"Adjustment boundary exceeded: {adjustment_delta} > ±{self.adjustment_boundary} "
                f"for {handle} on {platform}"
            )
        
        # 2. Check confidence increase under partial data
        if (heuristic_result.data_completeness != DataCompleteness.FULL and 
            confidence_delta > 0):
            violations.append(BoundaryViolationType.CONFIDENCE_INCREASE_PARTIAL_DATA)
            logger.warning(
                f"Confidence increased under partial data conditions: "
                f"{confidence_delta:+.2f} for {handle} on {platform}"
            )
        
        # 3. Check reasoning string presence and quality
        if not refinement_result.explanation or len(refinement_result.explanation.strip()) < 10:
            violations.append(BoundaryViolationType.MISSING_REASONING)
            logger.warning(f"Missing or insufficient reasoning for {handle} on {platform}")
        
        # 4. Analyze content for sarcasm, cultural slang, and mixed sentiment
        content_analysis = self._analyze_content_characteristics(sample_content or [])
        
        # Check if sarcastic content was properly handled
        if (content_analysis['sarcasm_detected'] and 
            not self._is_sarcasm_handled_in_reasoning(refinement_result.explanation)):
            violations.append(BoundaryViolationType.SARCASTIC_CONTENT_UNHANDLED)
        
        # Check if cultural slang was misinterpreted
        if (content_analysis['cultural_slang_detected'] and 
            not self._is_cultural_context_acknowledged(refinement_result.explanation)):
            violations.append(BoundaryViolationType.CULTURAL_SLANG_MISINTERPRETED)
        
        # Check if mixed sentiment caused confusion
        if (content_analysis['mixed_sentiment_detected'] and 
            not self._is_sentiment_nuance_recognized(refinement_result.explanation)):
            violations.append(BoundaryViolationType.MIXED_SENTIMENT_CONFUSION)
        
        # Generate justification
        justification = self._generate_audit_justification(
            violations, adjustment_delta, confidence_delta, content_analysis
        )
        
        # Calculate audit score (0-100, higher is better compliance)
        audit_score = self._calculate_audit_score(violations, adjustment_delta, confidence_delta)
        
        audit_record = BoundaryAuditRecord(
            timestamp=timestamp,
            handle=handle,
            platform=platform,
            raw_heuristic_score=heuristic_result.score,
            llm_adjusted_score=refinement_result.refined_score,
            adjustment_delta=adjustment_delta,
            original_confidence=heuristic_result.confidence,
            final_confidence=refinement_result.confidence,
            confidence_delta=confidence_delta,
            data_completeness=heuristic_result.data_completeness,
            reasoning_string=refinement_result.explanation,
            boundary_violations=violations,
            sarcastic_content_detected=content_analysis['sarcasm_detected'],
            cultural_slang_detected=content_analysis['cultural_slang_detected'],
            mixed_sentiment_detected=content_analysis['mixed_sentiment_detected'],
            justification=justification,
            audit_score=audit_score
        )
        
        # Store in audit log
        self.audit_log.append(audit_record)
        
        return audit_record
    
    def _analyze_content_characteristics(self, content: List[str]) -> Dict[str, bool]:
        """
        Analyze content for sarcasm, cultural slang, and mixed sentiment.
        
        Args:
            content: List of content strings to analyze
            
        Returns:
            Dictionary with detection flags
        """
        if not content:
            return {
                'sarcasm_detected': False,
                'cultural_slang_detected': False,
                'mixed_sentiment_detected': False
            }
        
        combined_text = ' '.join(content).lower()
        
        # Detect sarcasm
        sarcasm_detected = any(indicator in combined_text for indicator in self.sarcasm_indicators)
        
        # Detect cultural slang
        cultural_slang_detected = False
        for slang_list in self.cultural_slang_patterns.values():
            if any(slang in combined_text for slang in slang_list):
                cultural_slang_detected = True
                break
        
        # Detect mixed sentiment
        mixed_sentiment_detected = any(indicator in combined_text for indicator in self.mixed_sentiment_indicators)
        
        return {
            'sarcasm_detected': sarcasm_detected,
            'cultural_slang_detected': cultural_slang_detected,
            'mixed_sentiment_detected': mixed_sentiment_detected
        }
    
    def _is_sarcasm_handled_in_reasoning(self, reasoning: str) -> bool:
        """Check if reasoning acknowledges sarcasm or irony."""
        reasoning_lower = reasoning.lower()
        sarcasm_keywords = ['sarcasm', 'irony', 'ironic', 'sarcastic', 'tone', 'context']
        return any(keyword in reasoning_lower for keyword in sarcasm_keywords)
    
    def _is_cultural_context_acknowledged(self, reasoning: str) -> bool:
        """Check if reasoning acknowledges cultural context."""
        reasoning_lower = reasoning.lower()
        cultural_keywords = ['cultural', 'context', 'slang', 'colloquial', 'regional', 'demographic']
        return any(keyword in reasoning_lower for keyword in cultural_keywords)
    
    def _is_sentiment_nuance_recognized(self, reasoning: str) -> bool:
        """Check if reasoning recognizes sentiment nuance."""
        reasoning_lower = reasoning.lower()
        nuance_keywords = ['nuance', 'complex', 'mixed', 'ambivalent', 'contradictory', 'multifaceted']
        return any(keyword in reasoning_lower for keyword in nuance_keywords)
    
    def _generate_audit_justification(
        self, 
        violations: List[BoundaryViolationType], 
        adjustment_delta: float,
        confidence_delta: float,
        content_analysis: Dict[str, bool]
    ) -> str:
        """Generate human-readable justification for audit findings."""
        
        if not violations:
            return "✅ All boundary checks passed. Refinement complies with safety guidelines."
        
        justification_parts = []
        
        for violation in violations:
            if violation == BoundaryViolationType.ADJUSTMENT_EXCEEDED:
                justification_parts.append(
                    f"❌ Adjustment boundary exceeded: {adjustment_delta:+.1f} exceeds ±{self.adjustment_boundary} limit"
                )
            elif violation == BoundaryViolationType.CONFIDENCE_INCREASE_PARTIAL_DATA:
                justification_parts.append(
                    f"⚠️  Confidence increased under partial data: {confidence_delta:+.2f} (should decrease or stay same)"
                )
            elif violation == BoundaryViolationType.MISSING_REASONING:
                justification_parts.append(
                    "❌ Insufficient reasoning provided for refinement decision"
                )
            elif violation == BoundaryViolationType.SARCASTIC_CONTENT_UNHANDLED:
                justification_parts.append(
                    "⚠️  Sarcastic content detected but not acknowledged in reasoning"
                )
            elif violation == BoundaryViolationType.CULTURAL_SLANG_MISINTERPRETED:
                justification_parts.append(
                    "⚠️  Cultural slang detected but context not properly considered"
                )
            elif violation == BoundaryViolationType.MIXED_SENTIMENT_CONFUSION:
                justification_parts.append(
                    "⚠️  Mixed sentiment detected but nuance not recognized"
                )
        
        # Add content analysis context
        if content_analysis['sarcasm_detected']:
            justification_parts.append("🎭 Sarcasm detected in content")
        if content_analysis['cultural_slang_detected']:
            justification_parts.append("🌍 Cultural slang detected")
        if content_analysis['mixed_sentiment_detected']:
            justification_parts.append("😐 Mixed sentiment detected")
        
        return " | ".join(justification_parts)
    
    def _calculate_audit_score(
        self, 
        violations: List[BoundaryViolationType], 
        adjustment_delta: float, 
        confidence_delta: float
    ) -> float:
        """
        Calculate audit compliance score (0-100, higher is better).
        
        Args:
            violations: List of boundary violations
            adjustment_delta: Score adjustment amount
            confidence_delta: Confidence change amount
            
        Returns:
            Audit score from 0-100
        """
        base_score = 100.0
        
        # Deduct for violations
        violation_penalties = {
            BoundaryViolationType.ADJUSTMENT_EXCEEDED: 30.0,
            BoundaryViolationType.CONFIDENCE_INCREASE_PARTIAL_DATA: 25.0,
            BoundaryViolationType.MISSING_REASONING: 20.0,
            BoundaryViolationType.SARCASTIC_CONTENT_UNHANDLED: 15.0,
            BoundaryViolationType.CULTURAL_SLANG_MISINTERPRETED: 15.0,
            BoundaryViolationType.MIXED_SENTIMENT_CONFUSION: 15.0
        }
        
        for violation in violations:
            base_score -= violation_penalties.get(violation, 10.0)
        
        # Additional penalties for extreme values
        if abs(adjustment_delta) > self.adjustment_boundary * 1.5:
            base_score -= 20.0
        
        if confidence_delta > 0.3:  # Large confidence increase
            base_score -= 15.0
        
        return max(0.0, base_score)
    
    def generate_audit_summary(self) -> AuditSummary:
        """Generate summary statistics for all audits."""
        
        if not self.audit_log:
            return AuditSummary(
                total_audits=0,
                compliant_audits=0,
                violation_count=0,
                violation_types={},
                average_adjustment_delta=0.0,
                average_confidence_delta=0.0,
                compliance_rate=0.0,
                risk_score=0.0
            )
        
        total_audits = len(self.audit_log)
        compliant_audits = sum(1 for audit in self.audit_log if not audit.boundary_violations)
        violation_count = sum(len(audit.boundary_violations) for audit in self.audit_log)
        
        # Count violation types
        violation_types = {}
        for audit in self.audit_log:
            for violation in audit.boundary_violations:
                violation_types[violation] = violation_types.get(violation, 0) + 1
        
        # Calculate averages
        avg_adjustment_delta = sum(audit.adjustment_delta for audit in self.audit_log) / total_audits
        avg_confidence_delta = sum(audit.confidence_delta for audit in self.audit_log) / total_audits
        
        compliance_rate = compliant_audits / total_audits
        
        # Calculate risk score (0-100, lower is better)
        risk_score = 100.0 - (compliance_rate * 100.0)
        if violation_count > total_audits * 0.5:  # More than 0.5 violations per audit
            risk_score += 20.0
        if abs(avg_adjustment_delta) > self.adjustment_boundary * 0.8:
            risk_score += 15.0
        
        risk_score = min(100.0, risk_score)
        
        return AuditSummary(
            total_audits=total_audits,
            compliant_audits=compliant_audits,
            violation_count=violation_count,
            violation_types=violation_types,
            average_adjustment_delta=avg_adjustment_delta,
            average_confidence_delta=avg_confidence_delta,
            compliance_rate=compliance_rate,
            risk_score=risk_score
        )
    
    def export_audit_report(self) -> Dict[str, Any]:
        """Export comprehensive audit report."""
        
        summary = self.generate_audit_summary()
        
        return {
            "audit_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "total_audits": summary.total_audits,
                "auditor_version": "1.0.0"
            },
            "compliance_summary": {
                "compliance_rate": summary.compliance_rate,
                "risk_score": summary.risk_score,
                "compliant_audits": summary.compliant_audits,
                "violation_count": summary.violation_count
            },
            "boundary_statistics": {
                "adjustment_boundary": self.adjustment_boundary,
                "average_adjustment_delta": summary.average_adjustment_delta,
                "average_confidence_delta": summary.average_confidence_delta,
                "max_adjustment_observed": max(
                    (abs(audit.adjustment_delta) for audit in self.audit_log), 
                    default=0.0
                )
            },
            "violation_breakdown": {
                violation_type.value: count 
                for violation_type, count in summary.violation_types.items()
            },
            "detailed_audits": [
                {
                    "timestamp": audit.timestamp.isoformat(),
                    "handle": audit.handle,
                    "platform": audit.platform,
                    "raw_heuristic_score": audit.raw_heuristic_score,
                    "llm_adjusted_score": audit.llm_adjusted_score,
                    "adjustment_delta": audit.adjustment_delta,
                    "original_confidence": audit.original_confidence,
                    "final_confidence": audit.final_confidence,
                    "confidence_delta": audit.confidence_delta,
                    "data_completeness": audit.data_completeness.value,
                    "boundary_violations": [
                        v.value for v in audit.boundary_violations
                    ],
                    "content_characteristics": {
                        "sarcasm_detected": audit.sarcastic_content_detected,
                        "cultural_slang_detected": audit.cultural_slang_detected,
                        "mixed_sentiment_detected": audit.mixed_sentiment_detected
                    },
                    "justification": audit.justification,
                    "audit_score": audit.audit_score
                }
                for audit in self.audit_log
            ]
        }