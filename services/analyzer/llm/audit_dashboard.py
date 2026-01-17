"""
AI Refinement Boundary Audit Dashboard

Real-time monitoring dashboard for AI refinement boundary auditing with:
- Live violation tracking and alerting
- Statistical analysis of refinement patterns
- Trend analysis and anomaly detection
- Comprehensive reporting and export capabilities
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import statistics

from .boundary_auditor import BoundaryAuditRecord, BoundaryViolationType, AuditSummary

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class DashboardAlert:
    """Dashboard alert for boundary violations."""
    timestamp: datetime
    level: AlertLevel
    title: str
    message: str
    handle: str
    platform: str
    violation_types: List[BoundaryViolationType]
    audit_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrendAnalysis:
    """Trend analysis results."""
    period: str  # "hourly", "daily", "weekly"
    violation_rate: float
    average_adjustment: float
    average_confidence_delta: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    anomaly_score: float  # 0-100, higher indicates more anomalous behavior
    risk_assessment: str  # "low", "medium", "high", "critical"


@dataclass
class PlatformReliability:
    """Platform-specific reliability metrics."""
    platform: str
    total_audits: int
    compliant_audits: int
    violation_rate: float
    average_audit_score: float
    reliability_score: float  # 0-100, higher is more reliable
    last_violation: Optional[datetime]
    common_violations: List[BoundaryViolationType]


@dataclass
class ContentComplexityProfile:
    """Content complexity analysis profile."""
    sarcasm_detection_rate: float
    cultural_slang_detection_rate: float
    mixed_sentiment_detection_rate: float
    complexity_score: float  # 0-100, higher indicates more complex content
    handling_accuracy: float  # How well the system handles complex content
    problematic_patterns: List[str]


class AuditMonitoringDashboard:
    """
    Real-time monitoring dashboard for AI refinement boundary auditing.
    
    Provides comprehensive monitoring, alerting, and analysis capabilities
    for tracking AI refinement boundary violations and system performance.
    """
    
    def __init__(
        self,
        update_interval: int = 60,  # seconds
        alert_callback: Optional[Callable[[DashboardAlert], None]] = None,
        max_alerts: int = 1000,
        enable_auto_analysis: bool = True
    ):
        """
        Initialize the monitoring dashboard.
        
        Args:
            update_interval: How often to update dashboard metrics (seconds)
            alert_callback: Optional callback for alert notifications
            max_alerts: Maximum number of alerts to keep in memory
            enable_auto_analysis: Whether to enable automatic trend analysis
        """
        self.update_interval = update_interval
        self.alert_callback = alert_callback
        self.max_alerts = max_alerts
        self.enable_auto_analysis = enable_auto_analysis
        
        # Dashboard state
        self.alerts: List[DashboardAlert] = []
        self.audit_records: List[BoundaryAuditRecord] = []
        self.is_running = False
        self.last_update = datetime.utcnow()
        
        # Statistical tracking
        self.hourly_stats = self._initialize_time_series()
        self.daily_stats = self._initialize_time_series()
        self.weekly_stats = self._initialize_time_series()
        
        # Platform tracking
        self.platform_stats: Dict[str, PlatformReliability] = {}
        self.content_complexity = ContentComplexityProfile(
            sarcasm_detection_rate=0.0,
            cultural_slang_detection_rate=0.0,
            mixed_sentiment_detection_rate=0.0,
            complexity_score=0.0,
            handling_accuracy=0.0,
            problematic_patterns=[]
        )
        
        # Trend analysis cache
        self.trend_cache: Dict[str, TrendAnalysis] = {}
        self.anomaly_history: List[Dict[str, Any]] = []
        
        logger.info(f"AuditMonitoringDashboard initialized with {update_interval}s update interval")
    
    def _initialize_time_series(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize time series data structure."""
        return {
            "violation_counts": [],
            "audit_scores": [],
            "adjustment_deltas": [],
            "confidence_deltas": [],
            "content_complexity": []
        }
    
    async def add_audit_record(self, audit_record: BoundaryAuditRecord):
        """
        Add a new audit record to the dashboard.
        
        Args:
            audit_record: The audit record to add
        """
        self.audit_records.append(audit_record)
        
        # Keep only recent records (last 30 days)
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        self.audit_records = [
            record for record in self.audit_records
            if record.timestamp > cutoff_date
        ]
        
        # Generate alerts for violations
        if audit_record.boundary_violations:
            await self._generate_violation_alert(audit_record)
        
        # Update statistics
        await self._update_statistics(audit_record)
        
        # Update platform statistics
        await self._update_platform_stats(audit_record)
        
        # Update content complexity analysis
        await self._update_content_complexity(audit_record)
        
        logger.debug(f"Added audit record for {audit_record.handle} on {audit_record.platform}")
    
    async def _generate_violation_alert(self, audit_record: BoundaryAuditRecord):
        """Generate alert for boundary violations."""
        
        # Determine alert level based on violations
        if BoundaryViolationType.ADJUSTMENT_EXCEEDED in audit_record.boundary_violations:
            level = AlertLevel.CRITICAL
            title = "Adjustment Boundary Exceeded"
        elif BoundaryViolationType.CONFIDENCE_INCREASE_PARTIAL_DATA in audit_record.boundary_violations:
            level = AlertLevel.WARNING
            title = "Confidence Increased Under Partial Data"
        elif len(audit_record.boundary_violations) >= 3:
            level = AlertLevel.CRITICAL
            title = "Multiple Boundary Violations"
        else:
            level = AlertLevel.WARNING
            title = "Boundary Violation Detected"
        
        # Create alert message
        violation_names = [v.value for v in audit_record.boundary_violations]
        message = (
            f"Boundary violations detected for {audit_record.handle} on {audit_record.platform}. "
            f"Violations: {', '.join(violation_names)}. "
            f"Audit score: {audit_record.audit_score:.1f}/100. "
            f"Adjustment: {audit_record.adjustment_delta:+.1f}, "
            f"Confidence delta: {audit_record.confidence_delta:+.2f}"
        )
        
        alert = DashboardAlert(
            timestamp=audit_record.timestamp,
            level=level,
            title=title,
            message=message,
            handle=audit_record.handle,
            platform=audit_record.platform,
            violation_types=audit_record.boundary_violations,
            audit_score=audit_record.audit_score,
            metadata={
                "adjustment_delta": audit_record.adjustment_delta,
                "confidence_delta": audit_record.confidence_delta,
                "data_completeness": audit_record.data_completeness.value,
                "reasoning_length": len(audit_record.reasoning_string)
            }
        )
        
        self.alerts.append(alert)
        
        # Keep only recent alerts
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts:]
        
        # Call alert callback if provided
        if self.alert_callback:
            try:
                # Handle both sync and async callbacks
                if asyncio.iscoroutinefunction(self.alert_callback):
                    await self.alert_callback(alert)
                else:
                    self.alert_callback(alert)
            except Exception as e:
                logger.error(f"Alert callback failed: {str(e)}")
        
        logger.warning(f"Generated {level.value} alert: {title}")
    
    async def _update_statistics(self, audit_record: BoundaryAuditRecord):
        """Update time series statistics."""
        
        timestamp = audit_record.timestamp
        
        # Update hourly stats
        if timestamp >= datetime.utcnow() - timedelta(hours=1):
            self._add_to_time_series(self.hourly_stats, audit_record)
        
        # Update daily stats
        if timestamp >= datetime.utcnow() - timedelta(days=1):
            self._add_to_time_series(self.daily_stats, audit_record)
        
        # Update weekly stats
        if timestamp >= datetime.utcnow() - timedelta(weeks=1):
            self._add_to_time_series(self.weekly_stats, audit_record)
    
    def _add_to_time_series(self, time_series: Dict[str, List], audit_record: BoundaryAuditRecord):
        """Add audit record to time series data."""
        
        violation_count = len(audit_record.boundary_violations)
        
        time_series["violation_counts"].append({
            "timestamp": audit_record.timestamp,
            "count": violation_count,
            "has_violations": violation_count > 0
        })
        
        time_series["audit_scores"].append({
            "timestamp": audit_record.timestamp,
            "score": audit_record.audit_score
        })
        
        time_series["adjustment_deltas"].append({
            "timestamp": audit_record.timestamp,
            "delta": audit_record.adjustment_delta
        })
        
        time_series["confidence_deltas"].append({
            "timestamp": audit_record.timestamp,
            "delta": audit_record.confidence_delta
        })
        
        time_series["content_complexity"].append({
            "timestamp": audit_record.timestamp,
            "sarcasm": audit_record.sarcastic_content_detected,
            "slang": audit_record.cultural_slang_detected,
            "mixed_sentiment": audit_record.mixed_sentiment_detected
        })
    
    async def _update_platform_stats(self, audit_record: BoundaryAuditRecord):
        """Update platform-specific statistics."""
        
        platform = audit_record.platform
        
        if platform not in self.platform_stats:
            self.platform_stats[platform] = PlatformReliability(
                platform=platform,
                total_audits=0,
                compliant_audits=0,
                violation_rate=0.0,
                average_audit_score=0.0,
                reliability_score=100.0,
                last_violation=None,
                common_violations=[]
            )
        
        stats = self.platform_stats[platform]
        stats.total_audits += 1
        
        if not audit_record.boundary_violations:
            stats.compliant_audits += 1
        else:
            stats.last_violation = audit_record.timestamp
        
        # Calculate violation rate
        stats.violation_rate = 1.0 - (stats.compliant_audits / stats.total_audits)
        
        # Update average audit score
        current_avg = stats.average_audit_score
        stats.average_audit_score = (
            (current_avg * (stats.total_audits - 1) + audit_record.audit_score) / 
            stats.total_audits
        )
        
        # Calculate reliability score (0-100, higher is better)
        compliance_factor = stats.compliant_audits / stats.total_audits
        recency_factor = 1.0
        if stats.last_violation:
            hours_since_violation = (datetime.utcnow() - stats.last_violation).total_seconds() / 3600
            recency_factor = min(1.0, hours_since_violation / 24)  # Penalty for recent violations
        
        stats.reliability_score = max(0.0, compliance_factor * recency_factor * 100)
        
        # Update common violations
        violation_counts = {}
        for violation in audit_record.boundary_violations:
            violation_counts[violation] = violation_counts.get(violation, 0) + 1
        
        # Get top 3 most common violations for this platform
        all_violations = []
        for record in self.audit_records:
            if record.platform == platform:
                all_violations.extend(record.boundary_violations)
        
        violation_frequency = {}
        for violation in all_violations:
            violation_frequency[violation] = violation_frequency.get(violation, 0) + 1
        
        stats.common_violations = sorted(
            violation_frequency.keys(),
            key=lambda v: violation_frequency[v],
            reverse=True
        )[:3]
    
    async def _update_content_complexity(self, audit_record: BoundaryAuditRecord):
        """Update content complexity analysis."""
        
        # Calculate detection rates
        total_records = len(self.audit_records)
        if total_records == 0:
            return
        
        sarcasm_count = sum(1 for r in self.audit_records if r.sarcastic_content_detected)
        slang_count = sum(1 for r in self.audit_records if r.cultural_slang_detected)
        sentiment_count = sum(1 for r in self.audit_records if r.mixed_sentiment_detected)
        
        self.content_complexity.sarcasm_detection_rate = sarcasm_count / total_records
        self.content_complexity.cultural_slang_detection_rate = slang_count / total_records
        self.content_complexity.mixed_sentiment_detection_rate = sentiment_count / total_records
        
        # Calculate complexity score (0-100)
        complexity_factors = [
            self.content_complexity.sarcasm_detection_rate,
            self.content_complexity.cultural_slang_detection_rate,
            self.content_complexity.mixed_sentiment_detection_rate
        ]
        self.content_complexity.complexity_score = sum(complexity_factors) * 100 / 3
        
        # Calculate handling accuracy
        # This measures how well the system handles complex content
        complex_content_audits = [
            r for r in self.audit_records
            if r.sarcastic_content_detected or r.cultural_slang_detected or r.mixed_sentiment_detected
        ]
        
        if complex_content_audits:
            good_handling = sum(1 for r in complex_content_audits if r.audit_score >= 80)
            self.content_complexity.handling_accuracy = (good_handling / len(complex_content_audits)) * 100
        
        # Identify problematic patterns
        self.content_complexity.problematic_patterns = []
        if self.content_complexity.sarcasm_detection_rate > 0.3:
            self.content_complexity.problematic_patterns.append("High sarcasm detection rate")
        if self.content_complexity.cultural_slang_detection_rate > 0.4:
            self.content_complexity.problematic_patterns.append("High cultural slang detection rate")
        if self.content_complexity.mixed_sentiment_detection_rate > 0.25:
            self.content_complexity.problematic_patterns.append("High mixed sentiment detection rate")
        if self.content_complexity.handling_accuracy < 70:
            self.content_complexity.problematic_patterns.append("Low handling accuracy for complex content")
    
    async def perform_trend_analysis(self, period: str = "daily") -> TrendAnalysis:
        """
        Perform trend analysis for the specified period.
        
        Args:
            period: "hourly", "daily", or "weekly"
            
        Returns:
            TrendAnalysis with trend information
        """
        
        if period in self.trend_cache:
            # Check if cached analysis is still valid (less than 5 minutes old)
            cached_time = datetime.utcnow() - timedelta(minutes=5)
            if self.trend_cache[period].get("cached_at", datetime.min) > cached_time:
                return self.trend_cache[period]["analysis"]
        
        # Select appropriate time series
        if period == "hourly":
            time_series = self.hourly_stats
            time_window = timedelta(hours=1)
        elif period == "daily":
            time_series = self.daily_stats
            time_window = timedelta(days=1)
        elif period == "weekly":
            time_series = self.weekly_stats
            time_window = timedelta(weeks=1)
        else:
            raise ValueError(f"Invalid period: {period}")
        
        # Calculate metrics
        violation_counts = [item["count"] for item in time_series["violation_counts"]]
        audit_scores = [item["score"] for item in time_series["audit_scores"]]
        adjustment_deltas = [item["delta"] for item in time_series["adjustment_deltas"]]
        confidence_deltas = [abs(item["delta"]) for item in time_series["confidence_deltas"]]
        
        violation_rate = sum(violation_counts) / max(1, len(violation_counts))
        avg_adjustment = statistics.mean(adjustment_deltas) if adjustment_deltas else 0.0
        avg_confidence_delta = statistics.mean(confidence_deltas) if confidence_deltas else 0.0
        
        # Determine trend direction
        if len(violation_counts) >= 2:
            recent_avg = sum(violation_counts[-10:]) / min(10, len(violation_counts))
            older_avg = sum(violation_counts[:-10]) / max(1, len(violation_counts) - 10)
            
            if recent_avg > older_avg * 1.2:
                trend_direction = "increasing"
            elif recent_avg < older_avg * 0.8:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "stable"
        
        # Calculate anomaly score
        anomaly_score = self._calculate_anomaly_score(
            violation_rate, avg_adjustment, avg_confidence_delta, audit_scores
        )
        
        # Determine risk assessment
        if anomaly_score > 80:
            risk_assessment = "critical"
        elif anomaly_score > 60:
            risk_assessment = "high"
        elif anomaly_score > 40:
            risk_assessment = "medium"
        else:
            risk_assessment = "low"
        
        analysis = TrendAnalysis(
            period=period,
            violation_rate=violation_rate,
            average_adjustment=avg_adjustment,
            average_confidence_delta=avg_confidence_delta,
            trend_direction=trend_direction,
            anomaly_score=anomaly_score,
            risk_assessment=risk_assessment
        )
        
        # Cache the analysis
        self.trend_cache[period] = {
            "analysis": analysis,
            "cached_at": datetime.utcnow()
        }
        
        return analysis
    
    def _perform_trend_analysis_sync(self, period: str = "daily") -> TrendAnalysis:
        """Synchronous version of trend analysis for dashboard summary."""
        
        # Select appropriate time series
        if period == "hourly":
            time_series = self.hourly_stats
        elif period == "daily":
            time_series = self.daily_stats
        elif period == "weekly":
            time_series = self.weekly_stats
        else:
            raise ValueError(f"Invalid period: {period}")
        
        # Calculate metrics
        violation_counts = [item["count"] for item in time_series["violation_counts"]]
        audit_scores = [item["score"] for item in time_series["audit_scores"]]
        adjustment_deltas = [item["delta"] for item in time_series["adjustment_deltas"]]
        confidence_deltas = [abs(item["delta"]) for item in time_series["confidence_deltas"]]
        
        violation_rate = sum(violation_counts) / max(1, len(violation_counts))
        avg_adjustment = statistics.mean(adjustment_deltas) if adjustment_deltas else 0.0
        avg_confidence_delta = statistics.mean(confidence_deltas) if confidence_deltas else 0.0
        
        # Determine trend direction
        if len(violation_counts) >= 2:
            recent_avg = sum(violation_counts[-10:]) / min(10, len(violation_counts))
            older_avg = sum(violation_counts[:-10]) / max(1, len(violation_counts) - 10)
            
            if recent_avg > older_avg * 1.2:
                trend_direction = "increasing"
            elif recent_avg < older_avg * 0.8:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "stable"
        
        # Calculate anomaly score
        anomaly_score = self._calculate_anomaly_score(
            violation_rate, avg_adjustment, avg_confidence_delta, audit_scores
        )
        
        # Determine risk assessment
        if anomaly_score > 80:
            risk_assessment = "critical"
        elif anomaly_score > 60:
            risk_assessment = "high"
        elif anomaly_score > 40:
            risk_assessment = "medium"
        else:
            risk_assessment = "low"
        
        return TrendAnalysis(
            period=period,
            violation_rate=violation_rate,
            average_adjustment=avg_adjustment,
            average_confidence_delta=avg_confidence_delta,
            trend_direction=trend_direction,
            anomaly_score=anomaly_score,
            risk_assessment=risk_assessment
        )

    def _calculate_anomaly_score(
        self, 
        violation_rate: float, 
        avg_adjustment: float, 
        avg_confidence_delta: float,
        audit_scores: List[float]
    ) -> float:
        """Calculate anomaly score based on various metrics."""
        
        score = 0.0
        
        # High violation rate (0-30 points)
        if violation_rate > 0.5:
            score += 30
        elif violation_rate > 0.3:
            score += 20
        elif violation_rate > 0.1:
            score += 10
        
        # Extreme adjustments (0-25 points)
        if abs(avg_adjustment) > 20:
            score += 25
        elif abs(avg_adjustment) > 15:
            score += 15
        elif abs(avg_adjustment) > 10:
            score += 10
        
        # Confidence anomalies (0-20 points)
        if avg_confidence_delta > 0.3:
            score += 20
        elif avg_confidence_delta > 0.2:
            score += 15
        elif avg_confidence_delta > 0.1:
            score += 10
        
        # Low audit scores (0-25 points)
        if audit_scores:
            avg_audit_score = statistics.mean(audit_scores)
            if avg_audit_score < 50:
                score += 25
            elif avg_audit_score < 70:
                score += 15
            elif avg_audit_score < 80:
                score += 10
        
        return min(100.0, score)
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get comprehensive dashboard summary."""
        
        total_audits = len(self.audit_records)
        total_violations = sum(len(r.boundary_violations) for r in self.audit_records)
        violation_rate = total_violations / max(1, total_audits)
        
        # Get recent trend analysis (synchronous version)
        hourly_trend = self._perform_trend_analysis_sync("hourly")
        daily_trend = self._perform_trend_analysis_sync("daily")
        weekly_trend = self._perform_trend_analysis_sync("weekly")
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_audits": total_audits,
                "total_violations": total_violations,
                "violation_rate": violation_rate,
                "active_alerts": len([a for a in self.alerts if a.level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]]),
                "last_update": self.last_update.isoformat()
            },
            "trend_analysis": {
                "hourly": {
                    "violation_rate": hourly_trend.violation_rate,
                    "trend_direction": hourly_trend.trend_direction,
                    "anomaly_score": hourly_trend.anomaly_score,
                    "risk_assessment": hourly_trend.risk_assessment
                },
                "daily": {
                    "violation_rate": daily_trend.violation_rate,
                    "trend_direction": daily_trend.trend_direction,
                    "anomaly_score": daily_trend.anomaly_score,
                    "risk_assessment": daily_trend.risk_assessment
                },
                "weekly": {
                    "violation_rate": weekly_trend.violation_rate,
                    "trend_direction": weekly_trend.trend_direction,
                    "anomaly_score": weekly_trend.anomaly_score,
                    "risk_assessment": weekly_trend.risk_assessment
                }
            },
            "platform_reliability": {
                platform: {
                    "total_audits": stats.total_audits,
                    "violation_rate": stats.violation_rate,
                    "reliability_score": stats.reliability_score,
                    "common_violations": [v.value for v in stats.common_violations]
                }
                for platform, stats in self.platform_stats.items()
            },
            "content_complexity": {
                "sarcasm_detection_rate": self.content_complexity.sarcasm_detection_rate,
                "cultural_slang_detection_rate": self.content_complexity.cultural_slang_detection_rate,
                "mixed_sentiment_detection_rate": self.content_complexity.mixed_sentiment_detection_rate,
                "complexity_score": self.content_complexity.complexity_score,
                "handling_accuracy": self.content_complexity.handling_accuracy,
                "problematic_patterns": self.content_complexity.problematic_patterns
            },
            "recent_alerts": [
                {
                    "timestamp": alert.timestamp.isoformat(),
                    "level": alert.level.value,
                    "title": alert.title,
                    "handle": alert.handle,
                    "platform": alert.platform,
                    "audit_score": alert.audit_score
                }
                for alert in self.alerts[-10:]  # Last 10 alerts
            ]
        }
    
    def export_dashboard_data(self) -> Dict[str, Any]:
        """Export complete dashboard data for external analysis."""
        
        summary = self.get_dashboard_summary()
        
        return {
            "export_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "dashboard_version": "1.0.0",
                "total_records": len(self.audit_records),
                "export_period_days": 30
            },
            "dashboard_summary": summary,
            "detailed_audit_records": [
                {
                    "timestamp": record.timestamp.isoformat(),
                    "handle": record.handle,
                    "platform": record.platform,
                    "raw_heuristic_score": record.raw_heuristic_score,
                    "llm_adjusted_score": record.llm_adjusted_score,
                    "adjustment_delta": record.adjustment_delta,
                    "original_confidence": record.original_confidence,
                    "final_confidence": record.final_confidence,
                    "confidence_delta": record.confidence_delta,
                    "data_completeness": record.data_completeness.value,
                    "boundary_violations": [v.value for v in record.boundary_violations],
                    "sarcastic_content_detected": record.sarcastic_content_detected,
                    "cultural_slang_detected": record.cultural_slang_detected,
                    "mixed_sentiment_detected": record.mixed_sentiment_detected,
                    "audit_score": record.audit_score,
                    "justification": record.justification
                }
                for record in self.audit_records
            ],
            "time_series_data": {
                "hourly": self._serialize_time_series(self.hourly_stats),
                "daily": self._serialize_time_series(self.daily_stats),
                "weekly": self._serialize_time_series(self.weekly_stats)
            },
            "all_alerts": [
                {
                    "timestamp": alert.timestamp.isoformat(),
                    "level": alert.level.value,
                    "title": alert.title,
                    "message": alert.message,
                    "handle": alert.handle,
                    "platform": alert.platform,
                    "violation_types": [v.value for v in alert.violation_types],
                    "audit_score": alert.audit_score,
                    "metadata": alert.metadata
                }
                for alert in self.alerts
            ]
        }
    
    def _serialize_time_series(self, time_series: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """Serialize time series data with proper datetime handling."""
        serialized = {}
        for key, data_list in time_series.items():
            serialized[key] = []
            for item in data_list:
                serialized_item = item.copy()
                if 'timestamp' in serialized_item and hasattr(serialized_item['timestamp'], 'isoformat'):
                    serialized_item['timestamp'] = serialized_item['timestamp'].isoformat()
                serialized[key].append(serialized_item)
        return serialized
    
    async def start_monitoring(self):
        """Start the monitoring dashboard."""
        self.is_running = True
        logger.info("Audit monitoring dashboard started")
        
        # Start background tasks if needed
        if self.enable_auto_analysis:
            asyncio.create_task(self._auto_analysis_loop())
    
    async def stop_monitoring(self):
        """Stop the monitoring dashboard."""
        self.is_running = False
        logger.info("Audit monitoring dashboard stopped")
    
    async def _auto_analysis_loop(self):
        """Background loop for automatic analysis."""
        while self.is_running:
            try:
                await asyncio.sleep(self.update_interval)
                
                # Perform trend analysis
                for period in ["hourly", "daily", "weekly"]:
                    await self.perform_trend_analysis(period)
                
                self.last_update = datetime.utcnow()
                logger.debug(f"Auto-analysis completed at {self.last_update}")
                
            except Exception as e:
                logger.error(f"Auto-analysis loop error: {str(e)}")
                await asyncio.sleep(10)  # Brief pause on error