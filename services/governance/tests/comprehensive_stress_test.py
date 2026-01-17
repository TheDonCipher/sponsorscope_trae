#!/usr/bin/env python3
"""
Comprehensive System Stress Test Runner
Combines all rate limiting, abuse prevention, and graceful degradation tests
"""

import asyncio
import sys
import json
from datetime import datetime
from typing import Dict, Any
import subprocess
import os

class SystemStressTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {}
        
    async def run_rate_limiting_tests(self) -> Dict[str, Any]:
        """Run rate limiting simulation tests."""
        print("🚀 Running Rate Limiting Tests...")
        
        try:
            # Import and run the rate limiting simulation
            from services.governance.tests.rate_limit_simulation import RateLimitSimulator
            
            simulator = RateLimitSimulator(self.base_url)
            
            # Run individual test components
            results = {}
            
            print("  📊 Testing rapid requests...")
            results["rapid_requests"] = await simulator.simulate_rapid_requests(50, 10)
            
            print("  💰 Testing token spikes...")
            results["token_spike"] = await simulator.simulate_token_spike(10)
            
            print("  🚨 Testing abuse patterns...")
            results["abuse_patterns"] = await simulator.simulate_abuse_patterns()
            
            print("  📈 Testing rate limit boundaries...")
            results["boundary_test"] = await simulator.simulate_rate_limit_boundary()
            
            # Generate summary
            summary = {
                "total_tests": sum(len(r) for r in results.values()),
                "blocked_requests": sum(
                    sum(1 for req in r if req.get("status") in [403, 429, 503]) 
                    for r in results.values()
                ),
                "success_rate": 0,
                "degradation_events": 0
            }
            
            total_requests = sum(len(r) for r in results.values())
            if total_requests > 0:
                summary["success_rate"] = (
                    (total_requests - summary["blocked_requests"]) / total_requests * 100
                )
            
            return {
                "status": "completed",
                "summary": summary,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def run_abuse_prevention_tests(self) -> Dict[str, Any]:
        """Run abuse prevention tests."""
        print("🛡️  Running Abuse Prevention Tests...")
        
        try:
            from services.governance.tests.abuse_prevention_test import AbusePreventionTester
            
            tester = AbusePreventionTester(self.base_url)
            
            # Run key abuse tests
            results = {}
            
            print("  🔄 Testing rapid resubmission...")
            results["rapid_resubmission"] = await tester.test_rapid_resubmission()
            
            print("  🎯 Testing handle variations...")
            results["handle_variations"] = await tester.test_multiple_handle_variations()
            
            print("  📧 Testing spam payloads...")
            results["spam_payloads"] = await tester.test_spam_payload_patterns()
            
            print("  🔧 Testing header manipulation...")
            results["header_manipulation"] = await tester.test_header_manipulation()
            
            # Generate summary
            summary = {
                "total_tests": sum(len(r) for r in results.values()),
                "abuse_detected": sum(
                    sum(1 for req in r if req.get("status") == 403) 
                    for r in results.values()
                ),
                "rate_limited": sum(
                    sum(1 for req in r if req.get("status") == 429) 
                    for r in results.values()
                ),
                "detection_rate": 0
            }
            
            total_requests = sum(len(r) for r in results.values())
            if total_requests > 0:
                summary["detection_rate"] = (
                    (summary["abuse_detected"] + summary["rate_limited"]) / total_requests * 100
                )
            
            return {
                "status": "completed",
                "summary": summary,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def run_graceful_degradation_tests(self) -> Dict[str, Any]:
        """Test graceful degradation mechanisms."""
        print("⚡ Running Graceful Degradation Tests...")
        
        try:
            from services.governance.core.graceful_degradation import degradation_manager
            from services.governance.core.budget_logger import budget_logger
            
            results = {}
            
            # Test 1: Check degradation levels
            print("  📊 Testing degradation level detection...")
            health_status = await degradation_manager.check_system_health()
            results["degradation_levels"] = {
                "current_level": health_status["level"],
                "metrics": health_status["metrics"],
                "config": degradation_manager._get_current_config()
            }
            
            # Test 2: Process different request types
            print("  🔄 Testing request processing under load...")
            test_requests = [
                ("analysis", {"handle": "test_user", "platform": "instagram"}),
                ("report", {"handle": "test_user", "report_type": "authenticity"}),
                ("health", {}),
                ("generic", {"action": "test"})
            ]
            
            request_results = []
            for request_type, request_data in test_requests:
                result = await degradation_manager.process_request(request_type, request_data)
                request_results.append({
                    "type": request_type,
                    "result": result
                })
            
            results["request_processing"] = request_results
            
            # Test 3: Budget logging integration
            print("  💰 Testing budget logging integration...")
            
            # Log some test events
            await budget_logger.log_token_consumption(
                ip_address="127.0.0.1",
                tokens=1000,
                model="gpt-3.5-turbo",
                cost=0.001,
                request_id="test_123"
            )
            
            await budget_logger.log_rate_limit_hit(
                ip_address="127.0.0.1",
                endpoint="/api/analyze",
                request_id="test_456",
                rate_limit_type="minute",
                remaining_limits={"minute": 0, "hour": 50, "day": 500}
            )
            
            # Get summary
            daily_summary = await budget_logger.get_daily_summary()
            results["budget_summary"] = daily_summary
            
            # Test 4: Abuse summary
            abuse_summary = await budget_logger.get_abuse_summary(hours=1)
            results["abuse_summary"] = abuse_summary
            
            summary = {
                "degradation_level": results["degradation_levels"]["current_level"],
                "total_requests_processed": len(request_results),
                "degraded_requests": sum(1 for r in request_results if r["result"]["status"] == "degraded"),
                "budget_events_logged": daily_summary["daily_stats"]["total_requests"],
                "abuse_events_detected": abuse_summary["total_abuse_events"]
            }
            
            return {
                "status": "completed",
                "summary": summary,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run comprehensive test suite combining all scenarios."""
        print("🎯 Starting Comprehensive System Stress Test Suite")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Run all test suites
        rate_limiting_results = await self.run_rate_limiting_tests()
        abuse_prevention_results = await self.run_abuse_prevention_tests()
        graceful_degradation_results = await self.run_graceful_degradation_tests()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Compile comprehensive results
        comprehensive_results = {
            "test_suite_info": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "base_url": self.base_url,
                "test_environment": "development"
            },
            "rate_limiting": rate_limiting_results,
            "abuse_prevention": abuse_prevention_results,
            "graceful_degradation": graceful_degradation_results,
            "system_verdict": {}
        }
        
        # Generate system verdict
        comprehensive_results["system_verdict"] = self._generate_system_verdict(comprehensive_results)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"comprehensive_system_test_{timestamp}.json"
        report_file = f"comprehensive_system_test_report_{timestamp}.md"
        
        with open(results_file, "w") as f:
            json.dump(comprehensive_results, f, indent=2, default=str)
        
        # Generate markdown report
        report = self._generate_markdown_report(comprehensive_results)
        with open(report_file, "w") as f:
            f.write(report)
        
        print("\n" + "=" * 60)
        print("COMPREHENSIVE TEST SUITE COMPLETED")
        print("=" * 60)
        print(f"📊 Results saved to: {results_file}")
        print(f"📄 Report saved to: {report_file}")
        print(f"⏱️  Total duration: {duration:.1f} seconds")
        
        return comprehensive_results
    
    def _generate_system_verdict(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall system verdict based on test results."""
        
        # Rate limiting effectiveness
        rate_limiting_summary = results["rate_limiting"].get("summary", {})
        abuse_prevention_summary = results["abuse_prevention"].get("summary", {})
        degradation_summary = results["graceful_degradation"].get("summary", {})
        
        # Calculate scores
        rate_limiting_score = 0
        if rate_limiting_summary.get("total_tests", 0) > 0:
            rate_limiting_score = min(100, rate_limiting_summary.get("blocked_requests", 0) / 
                                      rate_limiting_summary.get("total_tests", 1) * 100)
        
        abuse_prevention_score = 0
        if abuse_prevention_summary.get("total_tests", 0) > 0:
            abuse_prevention_score = min(100, abuse_prevention_summary.get("detection_rate", 0))
        
        graceful_degradation_score = 100
        if degradation_summary.get("degraded_requests", 0) > 0:
            graceful_degradation_score = max(0, 100 - degradation_summary.get("degraded_requests", 0))
        
        overall_score = (rate_limiting_score + abuse_prevention_score + graceful_degradation_score) / 3
        
        # Determine verdict
        if overall_score >= 90:
            verdict = "EXCELLENT"
            status = "All systems functioning optimally"
        elif overall_score >= 80:
            verdict = "GOOD"
            status = "Systems functioning well with minor areas for improvement"
        elif overall_score >= 70:
            verdict = "ADEQUATE"
            status = "Systems functioning adequately but require attention"
        elif overall_score >= 60:
            verdict = "NEEDS_ATTENTION"
            status = "Systems require immediate attention and improvements"
        else:
            verdict = "CRITICAL"
            status = "Systems are critically compromised and need urgent fixes"
        
        return {
            "overall_score": round(overall_score, 1),
            "verdict": verdict,
            "status": status,
            "breakdown": {
                "rate_limiting_score": round(rate_limiting_score, 1),
                "abuse_prevention_score": round(abuse_prevention_score, 1),
                "graceful_degradation_score": round(graceful_degradation_score, 1)
            },
            "recommendations": self._generate_recommendations(results)
        }
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        # Rate limiting recommendations
        rate_limiting_summary = results["rate_limiting"].get("summary", {})
        if rate_limiting_summary.get("blocked_requests", 0) < rate_limiting_summary.get("total_tests", 0) * 0.1:
            recommendations.append("Consider tightening rate limits as only minimal blocking was observed")
        
        # Abuse prevention recommendations
        abuse_prevention_summary = results["abuse_prevention"].get("summary", {})
        if abuse_prevention_summary.get("detection_rate", 0) < 50:
            recommendations.append("Improve abuse detection algorithms - current detection rate is below 50%")
        
        # Graceful degradation recommendations
        degradation_summary = results["graceful_degradation"].get("summary", {})
        if degradation_summary.get("degraded_requests", 0) > 0:
            recommendations.append("Monitor system load - some requests were degraded")
        
        # Budget management recommendations
        if not recommendations:
            recommendations.append("System is performing well - continue monitoring and regular testing")
        
        return recommendations
    
    def _generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive markdown report."""
        
        verdict = results["system_verdict"]
        
        report = f"""# SponsorScope System Stress Test Report

**Generated:** {datetime.now().isoformat()}  
**Test Duration:** {results['test_suite_info']['duration_seconds']:.1f} seconds  
**Base URL:** {results['test_suite_info']['base_url']}  

## System Verdict: {verdict['verdict']}

**Overall Score:** {verdict['overall_score']}/100  
**Status:** {verdict['status']}  

### Component Scores
- **Rate Limiting:** {verdict['breakdown']['rate_limiting_score']}/100
- **Abuse Prevention:** {verdict['breakdown']['abuse_prevention_score']}/100  
- **Graceful Degradation:** {verdict['breakdown']['graceful_degradation_score']}/100

## Rate Limiting Test Results

**Status:** {results['rate_limiting']['status']}  
**Total Tests:** {results['rate_limiting']['summary']['total_tests']}  
**Blocked Requests:** {results['rate_limiting']['summary']['blocked_requests']}  
**Success Rate:** {results['rate_limiting']['summary']['success_rate']:.1f}%  

## Abuse Prevention Test Results

**Status:** {results['abuse_prevention']['status']}  
**Total Tests:** {results['abuse_prevention']['summary']['total_tests']}  
**Abuse Detected:** {results['abuse_prevention']['summary']['abuse_detected']}  
**Rate Limited:** {results['abuse_prevention']['summary']['rate_limited']}  
**Detection Rate:** {results['abuse_prevention']['summary']['detection_rate']:.1f}%  

## Graceful Degradation Test Results

**Status:** {results['graceful_degradation']['status']}  
**Current Level:** {results['graceful_degradation']['summary']['degradation_level']}  
**Requests Processed:** {results['graceful_degradation']['summary']['total_requests_processed']}  
**Degraded Requests:** {results['graceful_degradation']['summary']['degraded_requests']}  

## Recommendations

"""
        
        for i, recommendation in enumerate(verdict['recommendations'], 1):
            report += f"{i}. {recommendation}\n"
        
        report += f"""

## Test Environment Details

- **Test Start:** {results['test_suite_info']['start_time']}
- **Test End:** {results['test_suite_info']['end_time']}
- **Environment:** {results['test_suite_info']['test_environment']}

---

*This report was generated automatically by the SponsorScope System Stress Test Suite*
"""
        
        return report

async def main():
    """Main function to run comprehensive tests."""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    print(f"🎯 Starting Comprehensive System Stress Test against {base_url}")
    print("This will test:")
    print("  ✅ Rate limiting effectiveness")
    print("  ✅ Abuse prevention mechanisms")
    print("  ✅ Graceful degradation under load")
    print("  ✅ Budget logging and monitoring")
    print("  ✅ System response to stress scenarios")
    print("")
    
    tester = SystemStressTester(base_url)
    
    try:
        results = await tester.run_comprehensive_test_suite()
        
        # Print summary
        verdict = results["system_verdict"]
        print(f"\n🏆 FINAL VERDICT: {verdict['verdict']}")
        print(f"📊 Overall Score: {verdict['overall_score']}/100")
        print(f"📝 Status: {verdict['status']}")
        
        if verdict["recommendations"]:
            print("\n💡 Recommendations:")
            for i, rec in enumerate(verdict["recommendations"], 1):
                print(f"  {i}. {rec}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Test suite interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())