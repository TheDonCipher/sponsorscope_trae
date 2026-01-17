#!/usr/bin/env python3
"""
Test script for AI Refinement Boundary Auditor

This script demonstrates the comprehensive auditing capabilities for:
- Sarcastic comments detection and handling
- Cultural slang interpretation
- Mixed sentiment content analysis
- LLM adjustment boundary verification (±15 limit)
- Confidence validation under partial data conditions
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any

# Import the boundary auditor
from services.analyzer.llm.boundary_auditor import (
    AIRefinementBoundaryAuditor, 
    BoundaryViolationType,
    DataCompleteness
)
from services.analyzer.llm.types import LLMRefinementResult


class MockHeuristicResult:
    """Mock heuristic result for testing."""
    def __init__(self, score: float, confidence: float, data_completeness: DataCompleteness):
        self.score = score
        self.confidence = confidence
        self.data_completeness = data_completeness


class BoundaryAuditorDemo:
    """Demo class showcasing the AI refinement boundary auditor capabilities."""
    
    def __init__(self):
        self.auditor = AIRefinementBoundaryAuditor(adjustment_boundary=15.0)
        
        # Test content samples representing different challenging content types
        self.test_scenarios = [
            {
                "name": "Sarcastic Comments Scenario",
                "handle": "@sarcastic_influencer",
                "platform": "Instagram",
                "heuristic_score": 75.0,
                "heuristic_confidence": 0.80,
                "data_completeness": DataCompleteness.PARTIAL_NO_COMMENTS,
                "llm_adjustment": 8,
                "llm_confidence": 0.75,
                "reasoning": "High engagement detected with positive sentiment indicators",
                "sample_content": [
                    "Oh great, another influencer promoting detox tea. My life is complete now.",
                    "Wow, such authentic content. I've never seen anything like this before.",
                    "Amazing! This is exactly what I needed in my life. So grateful.",
                    "Brilliant marketing strategy. Really captured my attention with this one."
                ]
            },
            {
                "name": "Cultural Slang Scenario",
                "handle": "@uk_creator_london",
                "platform": "TikTok",
                "heuristic_score": 82.0,
                "heuristic_confidence": 0.85,
                "data_completeness": DataCompleteness.FULL,
                "llm_adjustment": -12,
                "llm_confidence": 0.90,
                "reasoning": "Authentic British audience engagement with proper cultural context",
                "sample_content": [
                    "Bloody brilliant content mate! Absolutely chuffed with this post.",
                    "I'm absolutely knackered after watching all these videos. Proper gutted.",
                    "This is proper mint! Can't wait for the next one, you're smashing it.",
                    "Brilliant stuff! I'm well impressed with your content, keep it up!"
                ]
            },
            {
                "name": "Mixed Sentiment Scenario",
                "handle": "@controversial_commenter",
                "platform": "Instagram",
                "heuristic_score": 65.0,
                "heuristic_confidence": 0.70,
                "data_completeness": DataCompleteness.PARTIAL_NO_COMMENTS,
                "llm_adjustment": 15,
                "llm_confidence": 0.85,
                "reasoning": "Strong positive engagement and audience resonance",
                "sample_content": [
                    "I love this content but sometimes it feels a bit forced, you know?",
                    "Great video however I'm not sure about the messaging. Still enjoyable though.",
                    "Amazing production quality although the content could be more authentic.",
                    "I appreciate the effort but I'm not convinced about the approach, yet it's interesting."
                ]
            },
            {
                "name": "Boundary Violation Scenario",
                "handle": "@extreme_adjuster",
                "platform": "TikTok",
                "heuristic_score": 45.0,
                "heuristic_confidence": 0.60,
                "data_completeness": DataCompleteness.PARTIAL_NO_COMMENTS,
                "llm_adjustment": 25,  # Exceeds ±15 boundary
                "llm_confidence": 0.95,  # Increases under partial data
                "reasoning": "Poor",
                "sample_content": [
                    "This is the worst content I've ever seen. Absolutely terrible.",
                    "I can't believe anyone would post something this bad. Disgusting.",
                    "Complete waste of time. Who approves this garbage?",
                    "Unfollowed immediately. This account is pure trash."
                ]
            },
            {
                "name": "Gen Z Slang Scenario",
                "handle": "@gen_z_creator",
                "platform": "TikTok",
                "heuristic_score": 88.0,
                "heuristic_confidence": 0.82,
                "data_completeness": DataCompleteness.FULL,
                "llm_adjustment": -3,
                "llm_confidence": 0.80,
                "reasoning": "Authentic Gen Z engagement patterns with proper slang interpretation",
                "sample_content": [
                    "No cap this slaps! You're the queen of content creation fr fr.",
                    "Bet! This is fire content. You're killing it, king!",
                    "This is bussin! Slay all day, no cap on this one.",
                    "ONG this is lit! You ate and left no crumbs, period."
                ]
            }
        ]
    
    async def run_comprehensive_audit_demo(self):
        """Run comprehensive demonstration of the boundary auditor."""
        
        print("🚀 AI Refinement Boundary Auditor Demo")
        print("=" * 60)
        print(f"Testing sarcastic comments, cultural slang, and mixed sentiment handling")
        print(f"Adjustment Boundary: ±{self.auditor.adjustment_boundary}")
        print("=" * 60)
        
        for i, scenario in enumerate(self.test_scenarios, 1):
            print(f"\n📊 Test Scenario {i}: {scenario['name']}")
            print("-" * 50)
            
            # Create mock results
            heuristic_result = MockHeuristicResult(
                score=scenario['heuristic_score'],
                confidence=scenario['heuristic_confidence'],
                data_completeness=scenario['data_completeness']
            )
            
            refinement_result = LLMRefinementResult(
                refined_score=scenario['heuristic_score'] + scenario['llm_adjustment'],
                adjustment=scenario['llm_adjustment'],
                explanation=scenario['reasoning'],
                confidence=scenario['llm_confidence'],
                flags=[]
            )
            
            # Perform audit
            audit_record = self.auditor.audit_refinement(
                heuristic_result=heuristic_result,
                refinement_result=refinement_result,
                handle=scenario['handle'],
                platform=scenario['platform'],
                sample_content=scenario['sample_content']
            )
            
            # Display results
            self._display_audit_results(scenario, audit_record)
        
        # Generate summary report
        print(f"\n📈 Overall Audit Summary")
        print("=" * 60)
        self._display_summary_report()
    
    def _display_audit_results(self, scenario: Dict[str, Any], audit_record):
        """Display detailed audit results for a scenario."""
        
        print(f"Handle: {scenario['handle']}")
        print(f"Platform: {scenario['platform']}")
        print(f"Data Completeness: {scenario['data_completeness'].value}")
        print()
        
        # Score Analysis
        print(f"📊 Score Analysis:")
        print(f"  Raw Heuristic Score: {scenario['heuristic_score']:.1f}")
        print(f"  LLM Adjusted Score: {scenario['heuristic_score'] + scenario['llm_adjustment']:.1f}")
        print(f"  Adjustment Delta: {scenario['llm_adjustment']:+.1f}")
        print(f"  Boundary Check: {'✅ PASS' if abs(scenario['llm_adjustment']) <= 15 else '❌ FAIL'}")
        print()
        
        # Confidence Analysis
        print(f"🔍 Confidence Analysis:")
        print(f"  Original Confidence: {scenario['heuristic_confidence']:.2f}")
        print(f"  Final Confidence: {scenario['llm_confidence']:.2f}")
        confidence_delta = scenario['llm_confidence'] - scenario['heuristic_confidence']
        print(f"  Confidence Delta: {confidence_delta:+.2f}")
        
        if scenario['data_completeness'] != DataCompleteness.FULL and confidence_delta > 0:
            print(f"  Partial Data Check: ❌ FAIL (confidence increased under partial data)")
        else:
            print(f"  Partial Data Check: ✅ PASS")
        print()
        
        # Content Analysis
        print(f"📝 Content Analysis:")
        print(f"  Sarcasm Detected: {'✅' if audit_record.sarcastic_content_detected else '❌'}")
        print(f"  Cultural Slang Detected: {'✅' if audit_record.cultural_slang_detected else '❌'}")
        print(f"  Mixed Sentiment Detected: {'✅' if audit_record.mixed_sentiment_detected else '❌'}")
        print()
        
        # Reasoning Quality
        print(f"🧠 Reasoning Analysis:")
        print(f"  Reasoning String: '{scenario['reasoning']}'")
        print(f"  Reasoning Quality: {'✅ Adequate' if len(scenario['reasoning']) >= 10 else '❌ Insufficient'}")
        print()
        
        # Violations and Justification
        if audit_record.boundary_violations:
            print(f"⚠️  Boundary Violations Detected:")
            for violation in audit_record.boundary_violations:
                print(f"  - {violation.value}")
            print()
        
        print(f"🔍 Audit Justification:")
        print(f"  {audit_record.justification}")
        print()
        
        print(f"📊 Audit Score: {audit_record.audit_score:.1f}/100")
        print(f"  Compliance: {'✅ COMPLIANT' if audit_record.audit_score >= 80 else '❌ NON-COMPLIANT'}")
        print()
        
        # Sample content preview
        if scenario['sample_content']:
            print(f"💬 Sample Content Analysis:")
            for i, content in enumerate(scenario['sample_content'][:2], 1):
                print(f"  {i}. \"{content}\"")
            if len(scenario['sample_content']) > 2:
                print(f"  ... and {len(scenario['sample_content']) - 2} more")
        print()
    
    def _display_summary_report(self):
        """Display comprehensive audit summary."""
        
        summary = self.auditor.generate_audit_summary()
        
        print(f"Total Audits Performed: {summary.total_audits}")
        print(f"Compliant Audits: {summary.compliant_audits}")
        print(f"Overall Compliance Rate: {summary.compliance_rate:.1%}")
        print(f"Risk Score: {summary.risk_score:.1f}/100 (lower is better)")
        print()
        
        if summary.violation_types:
            print(f"Violation Breakdown:")
            for violation_type, count in summary.violation_types.items():
                percentage = (count / summary.total_audits) * 100
                print(f"  {violation_type.value}: {count} ({percentage:.1f}%)")
            print()
        
        print(f"Statistical Summary:")
        print(f"  Average Adjustment Delta: {summary.average_adjustment_delta:+.2f}")
        print(f"  Average Confidence Delta: {summary.average_confidence_delta:+.2f}")
        print()
        
        # Export detailed report
        detailed_report = self.auditor.export_audit_report()
        
        print(f"📋 Detailed audit report exported with {len(detailed_report['detailed_audits'])} records")
        print(f"🎯 Boundary Statistics:")
        print(f"  Max Adjustment Observed: ±{detailed_report['boundary_statistics']['max_adjustment_observed']:.1f}")
        print(f"  Boundary Limit: ±{detailed_report['boundary_statistics']['adjustment_boundary']:.1f}")
        
        # Save report to file
        report_filename = f"ai_refinement_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(detailed_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Full audit report saved to: {report_filename}")


async def main():
    """Main demo function."""
    demo = BoundaryAuditorDemo()
    await demo.run_comprehensive_audit_demo()


if __name__ == "__main__":
    asyncio.run(main())