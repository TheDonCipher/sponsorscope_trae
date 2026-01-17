"""
Enhanced AI Refinement Boundary Auditor for SponsorScope.ai

Advanced version with real-time monitoring, statistical analysis, and automated alerting.
This module provides comprehensive auditing for AI-driven score refinements with
enhanced content analysis and pattern recognition capabilities.
"""

import json
import logging
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import statistics

from shared.schemas.domain import DataCompleteness
from .types import LLMRefinementResult

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels for boundary violations."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ContentComplexity(Enum):
    """Content complexity levels for analysis."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ADVERSARIAL = "adversarial"


@dataclass
class EnhancedBoundaryAuditRecord:
    """Enhanced record with advanced analytics."""
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
    content_complexity: ContentComplexity
    violation_severity: float
    contextual_factors: Dict[str, Any]
    audit_score: float
    justification: str
    alert_level: AlertLevel = AlertLevel.INFO


@dataclass
class RealTimeMetrics:
    """Real-time monitoring metrics."""
    total_audits: int = 0
    violations_last_hour: int = 0
    violations_last_24h: int = 0
    average_adjustment_magnitude: float = 0.0
    confidence_drift_rate: float = 0.0
    content_complexity_distribution: Dict[str, int] = field(default_factory=dict)
    platform_violation_rates: Dict[str, float] = field(default_factory=dict)
    time_based_patterns: Dict[str, List[float]] = field(default_factory=dict)


@dataclass
class StatisticalProfile:
    """Statistical profile for pattern analysis."""
    violation_frequency: float
    adjustment_volatility: float
    confidence_stability: float
    content_risk_score: float
    platform_reliability: Dict[str, float]
    temporal_patterns: Dict[str, Any]
    anomaly_indicators: List[str]


class EnhancedAIRefinementBoundaryAuditor:
    """
    Enhanced auditor with real-time monitoring and advanced analytics.
    
    This class extends the basic boundary auditor with:
    - Real-time metrics tracking
    - Advanced content complexity analysis
    - Statistical pattern recognition
    - Automated alerting system
    - Comprehensive reporting capabilities
    """
    
    def __init__(self, adjustment_boundary: float = 15.0, alert_callback: Optional[Callable] = None):
        """
        Initialize the enhanced boundary auditor.
        
        Args:
            adjustment_boundary: Maximum allowed adjustment (±15 by default)
            alert_callback: Optional callback function for alerts
        """
        self.adjustment_boundary = adjustment_boundary
        self.alert_callback = alert_callback
        self.audit_log: List[EnhancedBoundaryAuditRecord] = []
        self.real_time_metrics = RealTimeMetrics()
        self.violation_history = deque(maxlen=1000)  # Keep last 1000 violations
        
        # Advanced content analysis patterns
        self.sarcasm_indicators = [
            "yeah right", "sure", "obviously", "brilliant", "fantastic",
            "amazing", "wonderful", "perfect", "exactly what i wanted",
            "just what i needed", "couldn't be better", "oh great", "wow such"
        ]
        
        self.cultural_slang_patterns = {
            "american": ["dope", "lit", "fire", "sick", "tight", "gucci", "bet", "fr fr"],
            "british": ["brilliant", "bloody", "chuffed", "gutted", "knackered", "mate", "proper"],
            "australian": ["arvo", "barbie", "brekkie", "servo", "thongs", "fair dinkum"],
            "gen_z": ["bet", "cap", "no cap", "slay", "queen", "king", "bussin", "ate", "period"],
            "internet": ["lol", "lmao", "omg", "wtf", "smh", "tbh", "ong"]
        }
        
        self.mixed_sentiment_indicators = [
            "but", "however", "although", "though", "yet", "still",
            "nevertheless", "nonetheless", "despite", "while", "whereas"
        ]
        
        self.adversarial_patterns = [
            "worst", "terrible", "disgusting", "garbage", "trash", "unfollowed",
            "waste of time", "can't believe", "who approves"
        ]
        
        # Statistical tracking
        self.hourly_violations = deque(maxlen=24)  # 24-hour rolling window
        self.daily_violations = deque(maxlen=30)     # 30-day rolling window
        self.platform_stats = defaultdict(lambda: {"total": 0, "violations": 0})
        
        # Alert thresholds
        self.alert_thresholds = {
            "violation_rate_hourly": 0.3,      # 30% violation rate triggers warning
            "adjustment_magnitude": 20.0,       # Adjustments >20 trigger critical
            "confidence_drift": 0.25,         # Confidence changes >0.25 trigger warning
            "consecutive_violations": 5         # 5+ consecutive violations trigger emergency
        }
    
    async def audit_refinement_with_monitoring(
        self,
        heuristic_result: Any,
        refinement_result: LLMRefinementResult,
        handle: str,
        platform: str,
        sample_content: Optional[List[str]] = None,
        contextual_factors: Optional[Dict[str, Any]] = None
    ) -> EnhancedBoundaryAuditRecord:
        """
        Perform enhanced boundary audit with real-time monitoring.
        
        Args:
            heuristic_result: Original heuristic analysis result
            refinement_result: LLM refinement result to audit
            handle: Social media handle being analyzed
            platform: Platform (Instagram, TikTok, etc.)
            sample_content: Sample content for cultural/sentiment analysis
            contextual_factors: Additional context for analysis
            
        Returns:
            EnhancedBoundaryAuditRecord with comprehensive audit findings
        """
        
        # Perform basic audit
        basic_audit = self._perform_basic_audit(
            heuristic_result, refinement_result, handle, platform, sample_content
        )
        
        # Enhance with advanced analytics
        enhanced_audit = self._enhance_audit_with_analytics(
            basic_audit, contextual_factors
        )
        
        # Update real-time metrics
        self._update_real_time_metrics(enhanced_audit)
        
        # Check for alerts
        await self._check_alerts(enhanced_audit)
        
        # Store in audit log
        self.audit_log.append(enhanced_audit)
        
        return enhanced_audit
    
    def _perform_basic_audit(self, heuristic_result, refinement_result, handle, platform, sample_content):
        """Perform the basic boundary audit logic."""
        
        timestamp = datetime.utcnow()
        violations = []
        
        # Calculate deltas
        adjustment_delta = refinement_result.adjustment
        confidence_delta = refinement_result.confidence - heuristic_result.confidence
        
        # Check adjustment boundary (±15 limit)
        if abs(adjustment_delta) > self.adjustment_boundary:
            violations.append(BoundaryViolationType.ADJUSTMENT_EXCEEDED)
        
        # Check confidence increase under partial data
        if (heuristic_result.data_completeness != DataCompleteness.FULL and 
            confidence_delta > 0):
            violations.append(BoundaryViolationType.CONFIDENCE_INCREASE_PARTIAL_DATA)
        
        # Check reasoning string presence and quality
        if not refinement_result.explanation or len(refinement_result.explanation.strip()) < 10:
            violations.append(BoundaryViolationType.MISSING_REASONING)
        
        # Analyze content characteristics
        content_analysis = self._analyze_content_characteristics(sample_content or [])
        
        # Check content handling
        if (content_analysis['sarcasm_detected'] and 
            not self._is_sarcasm_handled_in_reasoning(refinement_result.explanation)):
            violations.append(BoundaryViolationType.SARCASTIC_CONTENT_UNHANDLED)
        
        if (content_analysis['cultural_slang_detected'] and 
            not self._is_cultural_context_acknowledged(refinement_result.explanation)):
            violations.append(BoundaryViolationType.CULTURAL_SLANG_MISINTERPRETED)
        
        if (content_analysis['mixed_sentiment_detected'] and 
            not self._is_sentiment_nuance_recognized(refinement_result.explanation)):
            violations.append(BoundaryViolationType.MIXED_SENTIMENT_CONFUSION)
        
        # Calculate severity and complexity
        violation_severity = self._calculate_violation_severity(violations, adjustment_delta, confidence_delta)
        content_complexity = self._determine_content_complexity(content_analysis, sample_content)
        
        # Generate justification
        justification = self._generate_enhanced_justification(violations, adjustment_delta, confidence_delta, content_analysis)
        
        # Calculate audit score
        audit_score = self._calculate_enhanced_audit_score(violations, adjustment_delta, confidence_delta, content_complexity)
        
        return EnhancedBoundaryAuditRecord(
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
            content_complexity=content_complexity,
            violation_severity=violation_severity,
            contextual_factors={},
            justification=justification,
            audit_score=audit_score
        )
    
    def _enhance_audit_with_analytics(self, basic_audit, contextual_factors):
        """Enhance basic audit with advanced analytics."""
        
        # Add contextual factors
        if contextual_factors:
            basic_audit.contextual_factors = contextual_factors
        
        # Determine alert level based on violations and severity
        basic_audit.alert_level = self._determine_alert_level(basic_audit)
        
        return basic_audit
    
    def _analyze_content_characteristics(self, content: List[str]) -> Dict[str, Any]:
        """
        Advanced content analysis with complexity assessment.
        
        Args:
            content: List of content strings to analyze
            
        Returns:
            Dictionary with comprehensive content analysis
        """
        if not content:
            return {
                'sarcasm_detected': False,
                'cultural_slang_detected': False,
                'mixed_sentiment_detected': False,
                'adversarial_detected': False,
                'complexity_score': 0.0,
                'sentiment_volatility': 0.0
            }
        
        combined_text = ' '.join(content).lower()
        word_count = len(combined_text.split())
        
        # Detect various content types
        sarcasm_detected = any(indicator in combined_text for indicator in self.sarcasm_indicators)
        
        cultural_slang_detected = False
        cultural_categories = []
        for category, slang_list in self.cultural_slang_patterns.items():
            if any(slang in combined_text for slang in slang_list):
                cultural_slang_detected = True
                cultural_categories.append(category)
        
        mixed_sentiment_detected = any(indicator in combined_text for indicator in self.mixed_sentiment_indicators)
        
        adversarial_detected = any(pattern in combined_text for pattern in self.adversarial_patterns)
        
        # Calculate complexity score (0-1)
        complexity_factors = [
            sarcasm_detected * 0.25,
            cultural_slang_detected * 0.20,
            mixed_sentiment_detected * 0.20,
            adversarial_detected * 0.35,
            min(word_count / 100, 0.2)  # Longer content gets slight complexity boost
        ]
        complexity_score = sum(complexity_factors)
        
        # Calculate sentiment volatility based on transition words
        sentiment_transitions = combined_text.count('but') + combined_text.count('however') + combined_text.count('although')
        sentiment_volatility = min(sentiment_transitions / 5, 1.0)  # Normalize to 0-1
        
        return {
            'sarcasm_detected': sarcasm_detected,
            'cultural_slang_detected': cultural_slang_detected,
            'cultural_categories': cultural_categories,
            'mixed_sentiment_detected': mixed_sentiment_detected,
            'adversarial_detected': adversarial_detected,
            'complexity_score': complexity_score,
            'sentiment_volatility': sentiment_volatility
        }
    
    def _determine_content_complexity(self, content_analysis: Dict[str, Any], sample_content: List[str]) -> ContentComplexity:
        """Determine content complexity level."""
        
        complexity_score = content_analysis.get('complexity_score', 0.0)
        
        if content_analysis.get('adversarial_detected', False):
            return ContentComplexity.ADVERSARIAL
        elif complexity_score > 0.6:
            return ContentComplexity.COMPLEX
        elif complexity_score > 0.3:
            return ContentComplexity.MODERATE
        else:
            return ContentComplexity.SIMPLE
    
    def _calculate_violation_severity(self, violations: List[BoundaryViolationType], adjustment_delta: float, confidence_delta: float) -> float:
        """Calculate severity score for violations (0-1)."""
        
        if not violations:
            return 0.0
        
        severity_weights = {
            BoundaryViolationType.ADJUSTMENT_EXCEEDED: 0.4,
            BoundaryViolationType.CONFIDENCE_INCREASE_PARTIAL_DATA: 0.3,
            BoundaryViolationType.MISSING_REASONING: 0.2,
            BoundaryViolationType.SARCASTIC_CONTENT_UNHANDLED: 0.15,
            BoundaryViolationType.CULTURAL_SLANG_MISINTERPRETED: 0.15,
            BoundaryViolationType.MIXED_SENTIMENT_CONFUSION: 0.15
        }
        
        base_severity = sum(severity_weights.get(violation, 0.1) for violation in violations)
        
        # Amplify severity for extreme violations
        if abs(adjustment_delta) > self.adjustment_boundary * 1.5:
            base_severity += 0.3
        
        if confidence_delta > 0.3:
            base_severity += 0.2
        
        return min(base_severity, 1.0)
    
    def _determine_alert_level(self, audit_record: EnhancedBoundaryAuditRecord) -> AlertLevel:
        """Determine alert level based on violations and severity."""
        
        if not audit_record.boundary_violations:
            return AlertLevel.INFO
        
        # Check for critical conditions
        if (BoundaryViolationType.ADJUSTMENT_EXCEEDED in audit_record.boundary_violations and 
            abs(audit_record.adjustment_delta) > self.adjustment_boundary * 1.5):
            return AlertLevel.EMERGENCY
        
        if audit_record.violation_severity > 0.8:
            return AlertLevel.CRITICAL
        elif audit_record.violation_severity > 0.5:
            return AlertLevel.WARNING
        else:
            return AlertLevel.INFO
    
    def _update_real_time_metrics(self, audit_record: EnhancedBoundaryAuditRecord):
        """Update real-time monitoring metrics."""
        
        self.real_time_metrics.total_audits += 1
        
        if audit_record.boundary_violations:
            self.real_time_metrics.violations_last_24h += 1
            self.violation_history.append(audit_record)
            
            # Update hourly violations
            current_hour = datetime.utcnow().hour
            if len(self.hourly_violations) == 0 or self.hourly_violations[-1] != current_hour:
                self.hourly_violations.append(current_hour)
                self.real_time_metrics.violations_last_hour = 1
            else:
                self.real_time_metrics.violations_last_hour += 1
        
        # Update platform statistics
        self.platform_stats[audit_record.platform]["total"] += 1
        if audit_record.boundary_violations:
            self.platform_stats[audit_record.platform]["violations"] += 1
        
        # Update content complexity distribution
        complexity = audit_record.content_complexity.value
        self.real_time_metrics.content_complexity_distribution[complexity] = \
            self.real_time_metrics.content_complexity_distribution.get(complexity, 0) + 1
        
        # Update platform violation rates
        for platform, stats in self.platform_stats.items():
            if stats["total"] > 0:
                self.real_time_metrics.platform_violation_rates[platform] = \
                    stats["violations"] / stats["total"]
        
        # Update adjustment magnitude tracking
        if len(self.audit_log) > 1:
            recent_adjustments = [abs(audit.adjustment_delta) for audit in self.audit_log[-100:]]
            self.real_time_metrics.average_adjustment_magnitude = statistics.mean(recent_adjustments)
        
        # Update confidence drift tracking
        if len(self.audit_log) > 1:
            recent_confidence_changes = [abs(audit.confidence_delta) for audit in self.audit_log[-100:]]
            self.real_time_metrics.confidence_drift_rate = statistics.mean(recent_confidence_changes)
    
    async def _check_alerts(self, audit_record: EnhancedBoundaryAuditRecord):
        """Check for alert conditions and trigger alerts if necessary."""
        
        alerts_triggered = []
        
        # Check violation rate
        if self.real_time_metrics.violations_last_hour > 10:
            alerts_triggered.append({
                "type": "high_violation_rate",
                "level": AlertLevel.WARNING,
                "message": f"High violation rate: {self.real_time_metrics.violations_last_hour} violations in last hour"
            })
        
        # Check for extreme adjustments
        if abs(audit_record.adjustment_delta) > self.alert_thresholds["adjustment_magnitude"]:
            alerts_triggered.append({
                "type": "extreme_adjustment",
                "level": AlertLevel.CRITICAL,
                "message": f"Extreme adjustment detected: {audit_record.adjustment_delta:+.1f}"
            })
        
        # Check confidence drift
        if abs(audit_record.confidence_delta) > self.alert_thresholds["confidence_drift"]:
            alerts_triggered.append({
                "type": "confidence_drift",
                "level": AlertLevel.WARNING,
                "message": f"Significant confidence drift: {audit_record.confidence_delta:+.2f}"
            })
        
        # Check for adversarial content
        if audit_record.content_complexity == ContentComplexity.ADVERSARIAL:
            alerts_triggered.append({
                "type": "adversarial_content",
                "level": AlertLevel.CRITICAL,
                "message": f"Adversarial content detected for {audit_record.handle}"
            })
        
        # Trigger alerts if callback is provided
        if alerts_triggered and self.alert_callback:
            for alert in alerts_triggered:
                await self.alert_callback(alert, audit_record)
    
    def _generate_enhanced_justification(self, violations, adjustment_delta, confidence_delta, content_analysis):
        """Generate enhanced human-readable justification."""
        
        if not violations:
            return "✅ All boundary checks passed. Refinement complies with safety guidelines."
        
        justification_parts = []
        
        # Core violation explanations
        for violation in violations:
            if violation == BoundaryViolationType.ADJUSTMENT_EXCEEDED:
                severity = "CRITICAL" if abs(adjustment_delta) > self.adjustment_boundary * 1.5 else "HIGH"
                justification_parts.append(
                    f"❌ [{severity}] Adjustment boundary exceeded: {adjustment_delta:+.1f} exceeds ±{self.adjustment_boundary} limit"
                )
            elif violation == BoundaryViolationType.CONFIDENCE_INCREASE_PARTIAL_DATA:
                justification_parts.append(
                    f"⚠️  Confidence increased under partial data: {confidence_delta:+.2f} (violates epistemic integrity)"
                )
            elif violation == BoundaryViolationType.MISSING_REASONING:
                justification_parts.append(
                    "❌ Insufficient reasoning provided - undermines auditability"
                )
            elif violation == BoundaryViolationType.SARCASTIC_CONTENT_UNHANDLED:
                justification_parts.append(
                    "⚠️  Sarcastic content detected but not properly contextualized"
                )
            elif violation == BoundaryViolationType.CULTURAL_SLANG_MISINTERPRETED:
                justification_parts.append(
                    "⚠️  Cultural slang detected but context not adequately considered"
                )
            elif violation == BoundaryViolationType.MIXED_SENTIMENT_CONFUSION:
                justification_parts.append(
                    "⚠️  Mixed sentiment detected but nuance not properly recognized"
                )
        
        # Content analysis context
        if content_analysis.get('adversarial_detected'):
            justification_parts.append("🚨 ADVERSARIAL: Potentially manipulative content patterns detected")
        
        if content_analysis.get('complexity_score', 0) > 0.6:
            justification_parts.append(f"🧠 COMPLEXITY: High complexity score ({content_analysis['complexity_score']:.2f}) requires careful handling")
        
        if content_analysis.get('sentiment_volatility', 0) > 0.4:
            justification_parts.append(f"😐 SENTIMENT: High sentiment volatility detected ({content_analysis['sentiment_volatility']:.2f})")
        
        return " | ".join(justification_parts)
    
    def _calculate_enhanced_audit_score(self, violations, adjustment_delta, confidence_delta, content_complexity):
        """Calculate enhanced audit score with complexity considerations."""
        
        base_score = 100.0
        
        # Base violation penalties
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
        
        # Additional penalties for extreme violations
        if abs(adjustment_delta) > self.adjustment_boundary * 1.5:
            base_score -= 25.0
        elif abs(adjustment_delta) > self.adjustment_boundary:
            base_score -= 15.0
        
        if confidence_delta > 0.3:
            base_score -= 20.0
        elif confidence_delta > 0.15:
            base_score -= 10.0
        
        # Complexity-based adjustments
        complexity_multiplier = {
            ContentComplexity.SIMPLE: 1.0,
            ContentComplexity.MODERATE: 0.95,
            ContentComplexity.COMPLEX: 0.85,
            ContentComplexity.ADVERSARIAL: 0.7
        }
        
        base_score *= complexity_multiplier.get(content_complexity, 1.0)
        
        return max(0.0, base_score)
    
    def get_statistical_profile(self, handle: Optional[str] = None, platform: Optional[str] = None) -> StatisticalProfile:
        """Generate statistical profile for pattern analysis."""
        
        # Filter records based on criteria
        filtered_records = self.audit_log
        if handle:
            filtered_records = [r for r in filtered_records if r.handle == handle]
        if platform:
            filtered_records = [r for r in filtered_records if r.platform == platform]
        
        if not filtered_records:
            return StatisticalProfile(
                violation_frequency=0.0,
                adjustment_volatility=0.0,
                confidence_stability=1.0,
                content_risk_score=0.0,
                platform_reliability={},
                temporal_patterns={},
                anomaly_indicators=[]
            )
        
        # Calculate violation frequency
        total_records = len(filtered_records)
        violation_records = [r for r in filtered_records if r.boundary_violations]
        violation_frequency = len(violation_records) / total_records if total_records > 0 else 0.0
        
        # Calculate adjustment volatility
        adjustments = [abs(r.adjustment_delta) for r in filtered_records]
        adjustment_volatility = statistics.stdev(adjustments) if len(adjustments) > 1 else 0.0
        
        # Calculate confidence stability
        confidence_changes = [abs(r.confidence_delta) for r in filtered_records]
        confidence_stability = 1.0 - (statistics.mean(confidence_changes) if confidence_changes else 0.0)
        
        # Calculate content risk score
        complexity_scores = [r.violation_severity for r in filtered_records]
        content_risk_score = statistics.mean(complexity_scores) if complexity_scores else 0.0
        
        # Platform reliability analysis
        platform_reliability = {}
        for platform, stats in self.platform_stats.items():
            if stats["total"] > 0:
                platform_reliability[platform] = 1.0 - (stats["violations"] / stats["total"])
        
        # Temporal pattern analysis
        temporal_patterns = self._analyze_temporal_patterns(filtered_records)
        
        # Anomaly detection
        anomaly_indicators = self._detect_anomalies(filtered_records)
        
        return StatisticalProfile(
            violation_frequency=violation_frequency,
            adjustment_volatility=adjustment_volatility,
            confidence_stability=confidence_stability,
            content_risk_score=content_risk_score,
            platform_reliability=platform_reliability,
            temporal_patterns=temporal_patterns,
            anomaly_indicators=anomaly_indicators
        )
    
    def _analyze_temporal_patterns(self, records: List[EnhancedBoundaryAuditRecord]) -> Dict[str, Any]:
        """Analyze temporal patterns in audit data."""
        
        if not records:
            return {}
        
        # Group by hour of day
        hourly_patterns = defaultdict(list)
        for record in records:
            hour = record.timestamp.hour
            hourly_patterns[hour].append(record.violation_severity)
        
        # Calculate hourly violation tendencies
        hourly_tendencies = {}
        for hour, severities in hourly_patterns.items():
            hourly_tendencies[hour] = statistics.mean(severities) if severities else 0.0
        
        # Group by day of week
        daily_patterns = defaultdict(list)
        for record in records:
            day = record.timestamp.strftime("%A")
            daily_patterns[day].append(record.violation_severity)
        
        daily_tendencies = {}
        for day, severities in daily_patterns.items():
            daily_tendencies[day] = statistics.mean(severities) if severities else 0.0
        
        return {
            "hourly_tendencies": hourly_tendencies,
            "daily_tendencies": daily_tendencies,
            "peak_violation_hours": sorted(hourly_tendencies.items(), key=lambda x: x[1], reverse=True)[:3],
            "peak_violation_days": sorted(daily_tendencies.items(), key=lambda x: x[1], reverse=True)[:3]
        }
    
    def _detect_anomalies(self, records: List[EnhancedBoundaryAuditRecord]) -> List[str]:
        """Detect anomalies in audit patterns."""
        
        anomalies = []
        
        if not records:
            return anomalies
        
        # Check for sudden spike in violation severity
        recent_severities = [r.violation_severity for r in records[-10:]]
        if len(recent_severities) >= 5:
            recent_mean = statistics.mean(recent_severities)
            recent_stdev = statistics.stdev(recent_severities) if len(recent_severities) > 1 else 0.1
            
            for i, severity in enumerate(recent_severities[-3:], 1):
                if severity > recent_mean + (2 * recent_stdev):
                    anomalies.append(f"Sudden severity spike in recent audit #{i}")
                    break
        
        # Check for unusual adjustment patterns
        recent_adjustments = [abs(r.adjustment_delta) for r in records[-10:]]
        if len(recent_adjustments) >= 5:
            recent_mean = statistics.mean(recent_adjustments)
            if any(adj > recent_mean * 3 for adj in recent_adjustments[-3:]):
                anomalies.append("Unusual adjustment magnitude detected")
        
        # Check for confidence manipulation
        recent_confidence_changes = [abs(r.confidence_delta) for r in records[-10:]]
        if len(recent_confidence_changes) >= 5:
            if all(change > 0.2 for change in recent_confidence_changes[-3:]):
                anomalies.append("Potential confidence manipulation pattern")
        
        return anomalies
    
    def generate_comprehensive_report(self, format_type: str = "json") -> Dict[str, Any]:
        """Generate comprehensive audit report with all analytics."""
        
        summary = self.generate_audit_summary()
        statistical_profile = self.get_statistical_profile()
        
        base_report = self.export_audit_report()
        
        # Enhance with additional analytics
        enhanced_report = {
            **base_report,
            "enhanced_analytics": {
                "real_time_metrics": {
                    "violations_last_hour": self.real_time_metrics.violations_last_hour,
                    "violations_last_24h": self.real_time_metrics.violations_last_24h,
                    "average_adjustment_magnitude": self.real_time_metrics.average_adjustment_magnitude,
                    "confidence_drift_rate": self.real_time_metrics.confidence_drift_rate,
                    "content_complexity_distribution": self.real_time_metrics.content_complexity_distribution,
                    "platform_violation_rates": self.real_time_metrics.platform_violation_rates
                },
                "statistical_profile": {
                    "violation_frequency": statistical_profile.violation_frequency,
                    "adjustment_volatility": statistical_profile.adjustment_volatility,
                    "confidence_stability": statistical_profile.confidence_stability,
                    "content_risk_score": statistical_profile.content_risk_score,
                    "platform_reliability": statistical_profile.platform_reliability,
                    "temporal_patterns": statistical_profile.temporal_patterns,
                    "anomaly_indicators": statistical_profile.anomaly_indicators
                },
                "trend_analysis": self._generate_trend_analysis(),
                "risk_assessment": self._generate_risk_assessment()
            }
        }
        
        return enhanced_report
    
    def _generate_trend_analysis(self) -> Dict[str, Any]:
        """Generate trend analysis for the audit data."""
        
        if len(self.audit_log) < 10:
            return {"insufficient_data": True, "message": "Need at least 10 audits for trend analysis"}
        
        recent_records = self.audit_log[-50:]  # Last 50 records
        
        # Calculate moving averages
        violation_trend = []
        adjustment_trend = []
        confidence_trend = []
        
        for i in range(len(recent_records)):
            window = recent_records[max(0, i-9):i+1]  # 10-record rolling window
            
            violation_rate = len([r for r in window if r.boundary_violations]) / len(window)
            violation_trend.append(violation_rate)
            
            avg_adjustment = statistics.mean([abs(r.adjustment_delta) for r in window])
            adjustment_trend.append(avg_adjustment)
            
            avg_confidence_change = statistics.mean([abs(r.confidence_delta) for r in window])
            confidence_trend.append(avg_confidence_change)
        
        return {
            "violation_rate_trend": violation_trend,
            "adjustment_magnitude_trend": adjustment_trend,
            "confidence_change_trend": confidence_trend,
            "current_violation_rate": violation_trend[-1] if violation_trend else 0,
            "trend_direction": "improving" if violation_trend and violation_trend[-1] < violation_trend[0] else "worsening"
        }
    
    def _generate_risk_assessment(self) -> Dict[str, Any]:
        """Generate comprehensive risk assessment."""
        
        if not self.audit_log:
            return {"overall_risk": "low", "risk_score": 0.0, "recommendations": ["No data available for assessment"]}
        
        # Calculate risk factors
        recent_violation_rate = self.real_time_metrics.violations_last_24h / max(self.real_time_metrics.total_audits, 1)
        avg_severity = statistics.mean([r.violation_severity for r in self.audit_log[-50:]]) if len(self.audit_log) >= 50 else 0.0
        complexity_risk = statistics.mean([r.content_complexity.value for r in self.audit_log[-50:]]) if len(self.audit_log) >= 50 else 0.0
        
        # Calculate overall risk score (0-100)
        risk_score = (recent_violation_rate * 40 + avg_severity * 30 + complexity_risk * 30)
        
        # Determine risk level
        if risk_score > 70:
            risk_level = "critical"
            recommendations = [
                "Immediate review of LLM refinement parameters required",
                "Consider implementing stricter boundary controls",
                "Enhanced monitoring and alerting recommended"
            ]
        elif risk_score > 50:
            risk_level = "high"
            recommendations = [
                "Increase audit frequency and monitoring",
                "Review content analysis algorithms",
                "Consider additional safety mechanisms"
            ]
        elif risk_score > 30:
            risk_level = "medium"
            recommendations = [
                "Continue current monitoring levels",
                "Periodic review of violation patterns",
                "Maintain current safety protocols"
            ]
        else:
            risk_level = "low"
            recommendations = [
                "Current safety measures appear effective",
                "Maintain existing monitoring protocols",
                "Regular review still recommended"
            ]
        
        return {
            "overall_risk": risk_level,
            "risk_score": risk_score,
            "risk_factors": {
                "recent_violation_rate": recent_violation_rate,
                "average_severity": avg_severity,
                "complexity_risk": complexity_risk
            },
            "recommendations": recommendations
        }