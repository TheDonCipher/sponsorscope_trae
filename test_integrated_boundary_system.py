#!/usr/bin/env python3
"""
Integrated AI Refinement Boundary System Test Suite

This script demonstrates the complete integrated system including:
- Enhanced AuthenticityRefiner with boundary auditing
- Real-time monitoring dashboard
- Automated alerting system
- Statistical analysis and trend detection
- Comprehensive reporting capabilities
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Import all the integrated components
from services.analyzer.llm.enhanced_refiner import EnhancedAuthenticityRefiner
from services.analyzer.llm.audit_dashboard import AuditMonitoringDashboard, DashboardAlert, AlertLevel
from services.analyzer.llm.boundary_auditor import AIRefinementBoundaryAuditor, BoundaryViolationType
from services.analyzer.heuristics.types import HeuristicResult
from shared.schemas.domain import DataCompleteness
from services.analyzer.llm.types import LLMRefinementResult

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MockHeuristicResult:
    """Mock heuristic result for testing."""
    def __init__(self, score: float, confidence: float, data_completeness: DataCompleteness, signals: Optional[Dict[str, Any]] = None):
        self.score = score
        self.confidence = confidence
        self.data_completeness = data_completeness
        self.signals = signals or {
            "bot_probability": 0.2,
            "entropy": 0.75,
            "uniqueness": 0.68,
            "variance": 0.82
        }


class IntegratedBoundarySystemDemo:
    """Comprehensive demo of the integrated boundary auditing system."""
    
    def __init__(self):
        # Initialize components
        self.boundary_auditor = AIRefinementBoundaryAuditor(adjustment_boundary=15.0)
        
        # Alert callback for real-time monitoring
        self.alert_callback = self._handle_alert
        
        # Initialize dashboard with alert callback
        self.dashboard = AuditMonitoringDashboard(
            update_interval=30,  # 30 second updates
            alert_callback=self.alert_callback,
            max_alerts=500,
            enable_auto_analysis=True
        )
        
        # Initialize enhanced refiner with dashboard integration
        self.enhanced_refiner = EnhancedAuthenticityRefiner(
            boundary_auditor=self.boundary_auditor,
            audit_callback=self._audit_callback,
            enable_monitoring=True
        )
        
        # Track demo statistics
        self.demo_stats = {
            "total_tests": 0,
            "violations_detected": 0,
            "alerts_generated": 0,
            "compliant_refinements": 0
        }
        
        logger.info("🚀 Integrated Boundary System Demo Initialized")
    
    def _handle_alert(self, alert: DashboardAlert):
        """Handle dashboard alerts in real-time."""
        self.demo_stats["alerts_generated"] += 1
        
        logger.warning(
            f"🚨 ALERT [{alert.level.value.upper()}]: {alert.title}\n"
            f"   Platform: {alert.platform} | Handle: {alert.handle}\n"
            f"   Message: {alert.message}\n"
            f"   Audit Score: {alert.audit_score:.1f}/100"
        )
        
        # Additional processing based on alert level
        if alert.level == AlertLevel.CRITICAL or alert.level == AlertLevel.EMERGENCY:
            logger.critical(f"🔥 CRITICAL ALERT REQUIRES IMMEDIATE ATTENTION")
            # Here you could trigger external notifications (email, Slack, etc.)
    
    async def _audit_callback(self, audit_record):
        """Process audit records and feed them to the dashboard."""
        await self.dashboard.add_audit_record(audit_record)
        logger.debug(f"📊 Audit record added to dashboard for {audit_record.handle}")
    
    async def run_comprehensive_demo(self):
        """Run comprehensive demonstration with real-time monitoring."""
        
        print("\n" + "="*80)
        print("🎯 INTEGRATED AI REFINEMENT BOUNDARY SYSTEM DEMO")
        print("="*80)
        print("Testing: Sarcastic Comments, Cultural Slang, Mixed Sentiment")
        print("Monitoring: Real-time alerts, Statistical analysis, Trend detection")
        print("="*80)
        
        # Start the monitoring dashboard
        await self.dashboard.start_monitoring()
        
        # Test scenarios representing different challenging content types
        test_scenarios = [
            {
                "name": "Sarcastic Influencer Content",
                "handle": "@sarcastic_beauty_guru",
                "platform": "Instagram",
                "heuristic_score": 78.0,
                "heuristic_confidence": 0.82,
                "data_completeness": DataCompleteness.PARTIAL_NO_COMMENTS,
                "expected_adjustment": 12,
                "expected_confidence": 0.75,
                "reasoning_quality": "poor",
                "comments": [
                    "Oh wow, another foundation review. My life is complete now.",
                    "Amazing! This is exactly what I needed to see today.",
                    "Brilliant content! I've never seen anything like this before.",
                    "Fantastic! Just what I wanted to spend my time watching."
                ]
            },
            {
                "name": "British Cultural Content",
                "handle": "@uk_lifestyle_creator",
                "platform": "TikTok",
                "heuristic_score": 85.0,
                "heuristic_confidence": 0.88,
                "data_completeness": DataCompleteness.FULL,
                "expected_adjustment": -8,
                "expected_confidence": 0.85,
                "reasoning_quality": "good",
                "comments": [
                    "Bloody brilliant content mate! Absolutely chuffed with this.",
                    "I'm proper knackered after watching all these videos, but well worth it.",
                    "This is absolutely mint! You smashed it, queen!",
                    "Brilliant stuff! I'm well impressed with your authentic content."
                ]
            },
            {
                "name": "Mixed Sentiment Reviews",
                "handle": "@honest_reviewer_uk",
                "platform": "Instagram",
                "heuristic_score": 65.0,
                "heuristic_confidence": 0.70,
                "data_completeness": DataCompleteness.PARTIAL_NO_COMMENTS,
                "expected_adjustment": 18,  # Will exceed boundary
                "expected_confidence": 0.90,  # Will increase under partial data
                "reasoning_quality": "minimal",
                "comments": [
                    "I love this product but the price is quite high, however quality is good.",
                    "Great video however I'm not sure about the recommendation. Still helpful.",
                    "Amazing review although I disagree with some points, yet it's informative.",
                    "I appreciate the honesty but I'm not convinced, though it's well presented."
                ]
            },
            {
                "name": "Gen Z Authentic Engagement",
                "handle": "@gen_z_creator vibes",
                "platform": "TikTok",
                "heuristic_score": 92.0,
                "heuristic_confidence": 0.90,
                "data_completeness": DataCompleteness.FULL,
                "expected_adjustment": -5,
                "expected_confidence": 0.88,
                "reasoning_quality": "excellent",
                "comments": [
                    "No cap this slaps! You're the queen of authentic content fr fr.",
                    "Bet! This is fire content. You're killing it, king! No cap.",
                    "This is bussin! Slay all day, period. You ate and left no crumbs.",
                    "ONG this is lit! Your content is so real and authentic, fr."
                ]
            },
            {
                "name": "Extreme Boundary Violation",
                "handle": "@controversial_opinions",
                "platform": "Instagram",
                "heuristic_score": 45.0,
                "heuristic_confidence": 0.60,
                "data_completeness": DataCompleteness.PARTIAL_NO_COMMENTS,
                "expected_adjustment": 25,  # Exceeds ±15 boundary
                "expected_confidence": 0.95,  # Increases under partial data
                "reasoning_quality": "none",
                "comments": [
                    "This is the worst content I've ever seen. Absolutely terrible.",
                    "I can't believe anyone would post something this bad. Disgusting.",
                    "Complete waste of time. Who approves this garbage content?",
                    "Unfollowed immediately. This account is pure trash and misleading."
                ]
            }
        ]
        
        print(f"\n🧪 Running {len(test_scenarios)} Test Scenarios with Real-time Monitoring")
        print("-" * 80)
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n📊 Test {i}: {scenario['name']}")
            print(f"   Handle: {scenario['handle']} | Platform: {scenario['platform']}")
            print(f"   Expected: Adjustment ±{scenario['expected_adjustment']}, Confidence {scenario['expected_confidence']}")
            
            await self._test_scenario(scenario)
            
            # Brief pause to allow dashboard processing
            await asyncio.sleep(2)
        
        # Allow time for final dashboard processing
        await asyncio.sleep(5)
        
        # Generate comprehensive reports
        await self._generate_comprehensive_reports()
        
        # Stop monitoring
        await self.dashboard.stop_monitoring()
        
        print(f"\n✅ Demo Completed Successfully")
        print("="*80)
    
    async def _test_scenario(self, scenario: Dict[str, Any]):
        """Test individual scenario with enhanced refiner."""
        
        self.demo_stats["total_tests"] += 1
        
        # Create mock heuristic result
        heuristic_result = MockHeuristicResult(
            score=scenario['heuristic_score'],
            confidence=scenario['heuristic_confidence'],
            data_completeness=scenario['data_completeness']
        )
        
        try:
            # Perform enhanced refinement with boundary auditing
            refinement_result = await self.enhanced_refiner.refine(
                heuristic_result=heuristic_result,
                comments=scenario['comments'],
                context="English",
                handle=scenario['handle'],
                platform=scenario['platform']
            )
            
            # Extract audit score from flags
            audit_score = 100.0
            for flag in refinement_result.flags:
                if flag.startswith("audit_score:"):
                    audit_score = float(flag.split(":")[1])
                    break
            
            # Check compliance
            is_compliant = audit_score >= 80
            if is_compliant:
                self.demo_stats["compliant_refinements"] += 1
            
            # Display results
            print(f"   ✅ Refinement Complete:")
            print(f"      Score: {scenario['heuristic_score']:.1f} → {refinement_result.refined_score:.1f} (Δ{refinement_result.adjustment:+.1f})")
            print(f"      Confidence: {scenario['heuristic_confidence']:.2f} → {refinement_result.confidence:.2f} (Δ{refinement_result.confidence - scenario['heuristic_confidence']:+.2f})")
            print(f"      Audit Score: {audit_score:.1f}/100 {'✅ COMPLIANT' if is_compliant else '❌ NON-COMPLIANT'}")
            print(f"      Reasoning: {refinement_result.explanation[:100]}...")
            
            # Check for violations
            if hasattr(refinement_result, '_audit_record') and refinement_result._audit_record.boundary_violations:
                self.demo_stats["violations_detected"] += len(refinement_result._audit_record.boundary_violations)
                print(f"      ⚠️  Violations: {len(refinement_result._audit_record.boundary_violations)}")
                for violation in refinement_result._audit_record.boundary_violations:
                    print(f"         - {violation.value}")
            
        except Exception as e:
            print(f"   ❌ Error in refinement: {str(e)}")
            logger.error(f"Test scenario failed for {scenario['handle']}: {str(e)}")
    
    async def _generate_comprehensive_reports(self):
        """Generate comprehensive analysis reports."""
        
        print(f"\n📈 Generating Comprehensive Reports")
        print("-" * 80)
        
        # Get refiner statistics
        refiner_stats = self.enhanced_refiner.get_refinement_statistics()
        
        print(f"\n🔍 Refiner Statistics:")
        print(f"   Total Refinements: {refiner_stats['total_refinements']}")
        print(f"   Boundary Violations: {refiner_stats['boundary_violations']}")
        print(f"   Violation Rate: {refiner_stats['violation_rate']:.1%}")
        print(f"   Average Adjustment: {refiner_stats['average_adjustment']:+.2f}")
        print(f"   Average Confidence Delta: {refiner_stats['average_confidence_delta']:+.3f}")
        
        # Get dashboard summary
        dashboard_summary = self.dashboard.get_dashboard_summary()
        
        print(f"\n📊 Dashboard Summary:")
        print(f"   Total Audits: {dashboard_summary['summary']['total_audits']}")
        print(f"   Total Violations: {dashboard_summary['summary']['total_violations']}")
        print(f"   Overall Violation Rate: {dashboard_summary['summary']['violation_rate']:.1%}")
        print(f"   Active Alerts: {dashboard_summary['summary']['active_alerts']}")
        
        # Trend analysis
        print(f"\n📈 Trend Analysis:")
        for period, data in dashboard_summary['trend_analysis'].items():
            print(f"   {period.title()}:")
            print(f"      Violation Rate: {data['violation_rate']:.1%}")
            print(f"      Trend: {data['trend_direction'].title()}")
            print(f"      Anomaly Score: {data['anomaly_score']:.1f}/100")
            print(f"      Risk: {data['risk_assessment'].title()}")
        
        # Platform reliability
        if dashboard_summary['platform_reliability']:
            print(f"\n🌍 Platform Reliability:")
            for platform, stats in dashboard_summary['platform_reliability'].items():
                print(f"   {platform}:")
                print(f"      Total Audits: {stats['total_audits']}")
                print(f"      Violation Rate: {stats['violation_rate']:.1%}")
                print(f"      Reliability Score: {stats['reliability_score']:.1f}/100")
        
        # Content complexity analysis
        complexity = dashboard_summary['content_complexity']
        print(f"\n📝 Content Complexity Analysis:")
        print(f"   Sarcasm Detection Rate: {complexity['sarcasm_detection_rate']:.1%}")
        print(f"   Cultural Slang Detection Rate: {complexity['cultural_slang_detection_rate']:.1%}")
        print(f"   Mixed Sentiment Detection Rate: {complexity['mixed_sentiment_detection_rate']:.1%}")
        print(f"   Overall Complexity Score: {complexity['complexity_score']:.1f}/100")
        print(f"   Handling Accuracy: {complexity['handling_accuracy']:.1f}%")
        
        if complexity['problematic_patterns']:
            print(f"   Problematic Patterns:")
            for pattern in complexity['problematic_patterns']:
                print(f"      - {pattern}")
        
        # Recent alerts
        if dashboard_summary['recent_alerts']:
            print(f"\n🚨 Recent Alerts:")
            for alert in dashboard_summary['recent_alerts'][-5:]:  # Last 5
                print(f"   [{alert['level'].upper()}] {alert['title']}")
                print(f"      {alert['handle']} on {alert['platform']} (Score: {alert['audit_score']:.1f})")
        
        # Export detailed data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export dashboard data
        dashboard_export = self.dashboard.export_dashboard_data()
        dashboard_file = f"dashboard_export_{timestamp}.json"
        
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            json.dump(dashboard_export, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Dashboard data exported to: {dashboard_file}")
        
        # Export boundary auditor data
        auditor_export = self.boundary_auditor.export_audit_report()
        auditor_file = f"auditor_export_{timestamp}.json"
        
        with open(auditor_file, 'w', encoding='utf-8') as f:
            json.dump(auditor_export, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Auditor data exported to: {auditor_file}")
        
        # Demo statistics summary
        print(f"\n📋 Demo Statistics Summary:")
        print(f"   Total Tests Run: {self.demo_stats['total_tests']}")
        print(f"   Violations Detected: {self.demo_stats['violations_detected']}")
        print(f"   Alerts Generated: {self.demo_stats['alerts_generated']}")
        print(f"   Compliant Refinements: {self.demo_stats['compliant_refinements']}")
        print(f"   Compliance Rate: {self.demo_stats['compliant_refinements']/self.demo_stats['total_tests']:.1%}")
        
        # Save demo summary
        demo_summary = {
            "timestamp": timestamp,
            "demo_stats": self.demo_stats,
            "refiner_stats": refiner_stats,
            "dashboard_summary": dashboard_summary,
            "files_generated": [dashboard_file, auditor_file]
        }
        
        summary_file = f"demo_summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(demo_summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Complete demo summary saved to: {summary_file}")


async def main():
    """Main demo function."""
    demo = IntegratedBoundarySystemDemo()
    await demo.run_comprehensive_demo()


if __name__ == "__main__":
    asyncio.run(main())