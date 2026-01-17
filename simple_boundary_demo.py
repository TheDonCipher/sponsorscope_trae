#!/usr/bin/env python3
"""
Simple Demo of AI Refinement Boundary Auditing System

Demonstrates the core functionality without complex export features.
"""

import asyncio
from datetime import datetime
from services.analyzer.llm.boundary_auditor import AIRefinementBoundaryAuditor, BoundaryViolationType
from services.analyzer.llm.enhanced_refiner import EnhancedAuthenticityRefiner
from shared.schemas.domain import DataCompleteness


class MockHeuristicResult:
    """Mock heuristic result for testing."""
    def __init__(self, score: float, confidence: float, data_completeness: DataCompleteness):
        self.score = score
        self.confidence = confidence
        self.data_completeness = data_completeness


async def simple_demo():
    """Run simple demonstration of the boundary auditing system."""
    
    print("🎯 AI REFINEMENT BOUNDARY AUDITING SYSTEM")
    print("=" * 60)
    print("Testing: Sarcastic Comments, Cultural Slang, Mixed Sentiment")
    print("=" * 60)
    
    # Initialize components
    auditor = AIRefinementBoundaryAuditor(adjustment_boundary=15.0)
    refiner = EnhancedAuthenticityRefiner(boundary_auditor=auditor)
    
    # Test scenarios
    test_cases = [
        {
            "name": "Sarcastic Content Detection",
            "handle": "@sarcastic_influencer",
            "platform": "Instagram",
            "heuristic_score": 75.0,
            "heuristic_confidence": 0.80,
            "data_completeness": DataCompleteness.PARTIAL_NO_COMMENTS,
            "llm_adjustment": 8,
            "llm_confidence": 0.75,
            "reasoning": "High engagement detected with positive sentiment",
            "comments": [
                "Oh great, another influencer promoting detox tea. My life is complete now.",
                "Amazing! This is exactly what I needed to see today.",
                "Brilliant content! I've never seen anything like this before."
            ]
        },
        {
            "name": "British Cultural Slang",
            "handle": "@uk_creator_london",
            "platform": "TikTok",
            "heuristic_score": 82.0,
            "heuristic_confidence": 0.85,
            "data_completeness": DataCompleteness.FULL,
            "llm_adjustment": -12,
            "llm_confidence": 0.90,
            "reasoning": "Authentic British audience engagement with proper cultural context",
            "comments": [
                "Bloody brilliant content mate! Absolutely chuffed with this post.",
                "I'm absolutely knackered after watching all these videos. Proper gutted.",
                "This is proper mint! Can't wait for the next one, you're smashing it."
            ]
        },
        {
            "name": "Boundary Violation Test",
            "handle": "@extreme_adjuster",
            "platform": "Instagram",
            "heuristic_score": 45.0,
            "heuristic_confidence": 0.60,
            "data_completeness": DataCompleteness.PARTIAL_NO_COMMENTS,
            "llm_adjustment": 25,  # Exceeds ±15 boundary
            "llm_confidence": 0.95,  # Increases under partial data
            "reasoning": "Poor",
            "comments": [
                "This is the worst content I've ever seen. Absolutely terrible.",
                "I can't believe anyone would post something this bad. Disgusting."
            ]
        }
    ]
    
    print(f"\n🧪 Running {len(test_cases)} Test Cases")
    print("-" * 60)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📊 Test {i}: {case['name']}")
        print(f"   Handle: {case['handle']} | Platform: {case['platform']}")
        
        # Create mock results
        heuristic_result = MockHeuristicResult(
            score=case['heuristic_score'],
            confidence=case['heuristic_confidence'],
            data_completeness=case['data_completeness']
        )
        
        # Create mock refinement result
        from services.analyzer.llm.types import LLMRefinementResult
        refinement_result = LLMRefinementResult(
            refined_score=case['heuristic_score'] + case['llm_adjustment'],
            adjustment=case['llm_adjustment'],
            explanation=case['reasoning'],
            confidence=case['llm_confidence'],
            flags=[]
        )
        
        # Perform audit
        audit_record = auditor.audit_refinement(
            heuristic_result=heuristic_result,
            refinement_result=refinement_result,
            handle=case['handle'],
            platform=case['platform'],
            sample_content=case['comments']
        )
        
        # Display results
        print(f"   Score Analysis:")
        print(f"      Raw: {case['heuristic_score']:.1f} → Adjusted: {refinement_result.refined_score:.1f} (Δ{case['llm_adjustment']:+.1f})")
        print(f"      Boundary Check: {'✅ PASS' if abs(case['llm_adjustment']) <= 15 else '❌ FAIL'}")
        
        print(f"   Confidence Analysis:")
        conf_delta = case['llm_confidence'] - case['heuristic_confidence']
        print(f"      Original: {case['heuristic_confidence']:.2f} → Final: {case['llm_confidence']:.2f} (Δ{conf_delta:+.2f})")
        if case['data_completeness'] != DataCompleteness.FULL and conf_delta > 0:
            print(f"      Partial Data Check: ❌ FAIL")
        
        print(f"   Content Analysis:")
        print(f"      Sarcasm Detected: {'✅' if audit_record.sarcastic_content_detected else '❌'}")
        print(f"      Cultural Slang: {'✅' if audit_record.cultural_slang_detected else '❌'}")
        print(f"      Mixed Sentiment: {'✅' if audit_record.mixed_sentiment_detected else '❌'}")
        
        if audit_record.boundary_violations:
            print(f"   ⚠️  Violations Detected:")
            for violation in audit_record.boundary_violations:
                print(f"      - {violation.value}")
        
        print(f"   Audit Score: {audit_record.audit_score:.1f}/100")
        print(f"   Compliance: {'✅ COMPLIANT' if audit_record.audit_score >= 80 else '❌ NON-COMPLIANT'}")
    
    # Generate summary
    print(f"\n📈 System Summary")
    print("-" * 60)
    
    summary = auditor.generate_audit_summary()
    print(f"Total Audits: {summary.total_audits}")
    print(f"Compliant Audits: {summary.compliant_audits}")
    print(f"Overall Compliance Rate: {summary.compliance_rate:.1%}")
    print(f"Risk Score: {summary.risk_score:.1f}/100")
    print(f"Average Adjustment: {summary.average_adjustment_delta:+.2f}")
    print(f"Average Confidence Delta: {summary.average_confidence_delta:+.3f}")
    
    if summary.violation_types:
        print(f"\nViolation Breakdown:")
        for violation_type, count in summary.violation_types.items():
            percentage = (count / summary.total_audits) * 100
            print(f"   {violation_type.value}: {count} ({percentage:.1f}%)")
    
    print(f"\n✅ Demo Completed Successfully")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(simple_demo())