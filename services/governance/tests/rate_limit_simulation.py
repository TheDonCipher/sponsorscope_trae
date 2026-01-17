#!/usr/bin/env python3
"""
Rate Limiting and Abuse Simulation Script
Tests system response to rapid repeated requests, token spikes, and rate limit breaches
"""

import asyncio
import aiohttp
import time
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import statistics

class RateLimitSimulator:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        self.start_time = None
        
    async def make_request(self, session: aiohttp.ClientSession, endpoint: str, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a single request and return response data."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if payload:
                async with session.post(url, json=payload) as response:
                    response_data = await response.json()
                    return {
                        "status": response.status,
                        "headers": dict(response.headers),
                        "data": response_data,
                        "timestamp": datetime.now().isoformat(),
                        "success": response.status < 400
                    }
            else:
                async with session.get(url) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    return {
                        "status": response.status,
                        "headers": dict(response.headers),
                        "data": response_data,
                        "timestamp": datetime.now().isoformat(),
                        "success": response.status < 400
                    }
        except Exception as e:
            return {
                "status": 0,
                "headers": {},
                "data": {"error": str(e)},
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "exception": str(e)
            }
    
    async def simulate_rapid_requests(self, num_requests: int = 100, delay_ms: int = 10) -> List[Dict[str, Any]]:
        """Simulate rapid repeated requests to test rate limiting."""
        print(f"🚀 Simulating {num_requests} rapid requests with {delay_ms}ms delay...")
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            for i in range(num_requests):
                # Test different endpoints to see varied responses
                if i % 3 == 0:
                    endpoint = "/api/health"
                    payload = None
                elif i % 3 == 1:
                    endpoint = "/api/analyze"
                    payload = {"handle": f"test_handle_{i % 10}", "platform": "instagram"}
                else:
                    endpoint = "/api/report/test_handle"
                    payload = None
                
                result = await self.make_request(session, endpoint, payload)
                result["request_id"] = i
                result["test_type"] = "rapid_requests"
                results.append(result)
                
                # Small delay between requests
                if delay_ms > 0:
                    await asyncio.sleep(delay_ms / 1000)
                
                if i % 10 == 0:
                    print(f"  Progress: {i}/{num_requests} requests")
        
        return results
    
    async def simulate_token_spike(self, num_large_requests: int = 20) -> List[Dict[str, Any]]:
        """Simulate requests that consume large amounts of tokens."""
        print(f"💰 Simulating {num_large_requests} token-heavy requests...")
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            for i in range(num_large_requests):
                # Simulate analysis requests that would consume tokens
                payload = {
                    "handle": f"large_analysis_{i}",
                    "platform": "instagram",
                    "deep_analysis": True,  # This would trigger more token usage
                    "include_evidence": True,
                    "confidence_threshold": 0.8
                }
                
                result = await self.make_request(session, "/api/analyze", payload)
                result["request_id"] = i
                result["test_type"] = "token_spike"
                results.append(result)
                
                # Wait between large requests
                await asyncio.sleep(2)
                
                if i % 5 == 0:
                    print(f"  Progress: {i}/{num_large_requests} large requests")
        
        return results
    
    async def simulate_abuse_patterns(self) -> List[Dict[str, Any]]:
        """Simulate abusive behavior patterns."""
        print("🚨 Simulating abuse patterns...")
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            # Pattern 1: Rapid resubmission of same handle
            print("  Pattern 1: Rapid resubmission")
            for i in range(10):
                payload = {
                    "handle": "same_handle_abuse",
                    "platform": "instagram"
                }
                result = await self.make_request(session, "/api/analyze", payload)
                result["request_id"] = i
                result["test_type"] = "abuse_rapid_resubmission"
                results.append(result)
                await asyncio.sleep(0.1)  # Very rapid submissions
            
            # Pattern 2: Multiple requests from same IP with different handles
            print("  Pattern 2: Multiple handle variations")
            for i in range(20):
                payload = {
                    "handle": f"variation_test_{i}",
                    "platform": "instagram"
                }
                result = await self.make_request(session, "/api/analyze", payload)
                result["request_id"] = i + 10
                result["test_type"] = "abuse_multiple_handles"
                results.append(result)
                await asyncio.sleep(0.2)
        
        return results
    
    async def simulate_rate_limit_boundary(self) -> List[Dict[str, Any]]:
        """Test behavior at rate limit boundaries."""
        print("📊 Testing rate limit boundaries...")
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            # Make requests right up to the limit
            for i in range(65):  # Assuming 60/minute limit
                result = await self.make_request(session, "/api/health")
                result["request_id"] = i
                result["test_type"] = "boundary_test"
                results.append(result)
                
                # Fast requests to hit the limit
                await asyncio.sleep(0.05)
                
                if i == 59:
                    print(f"  Reached expected limit at request {i}")
        
        return results
    
    def analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze simulation results and generate report."""
        if not results:
            return {"error": "No results to analyze"}
        
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r.get("success", False))
        rate_limited_requests = sum(1 for r in results if r.get("status") == 429)
        abuse_blocked_requests = sum(1 for r in results if r.get("status") == 403)
        token_limited_requests = sum(1 for r in results if r.get("status") == 503 and "token" in str(r.get("data", {})))
        
        response_times = []
        for r in results:
            if "X-Governance-Time" in r.get("headers", {}):
                try:
                    response_times.append(float(r["headers"]["X-Governance-Time"].rstrip("s")))
                except:
                    pass
        
        # Check for graceful degradation
        degradation_indicators = []
        for r in results:
            if r.get("status") in [429, 403, 503]:
                headers = r.get("headers", {})
                if "X-Governance-Action" in headers:
                    degradation_indicators.append({
                        "action": headers["X-Governance-Action"],
                        "status": r.get("status"),
                        "reason": r.get("data", {}).get("message", "Unknown")
                    })
        
        # Budget analysis
        budget_info = []
        for r in results:
            headers = r.get("headers", {})
            if "X-Governance-Action" in headers and headers["X-Governance-Action"] == "token_limit":
                budget_info.append(r.get("data", {}))
        
        return {
            "summary": {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
                "rate_limited": rate_limited_requests,
                "abuse_blocked": abuse_blocked_requests,
                "token_limited": token_limited_requests
            },
            "performance": {
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0
            },
            "graceful_degradation": {
                "total_blocks": len(degradation_indicators),
                "block_types": list(set(d["action"] for d in degradation_indicators)),
                "block_details": degradation_indicators[:10]  # First 10 for brevity
            },
            "budget_impact": {
                "token_limit_hits": len(budget_info),
                "budget_messages": budget_info[:5]  # First 5 for brevity
            }
        }
    
    def generate_report(self, all_results: Dict[str, List[Dict[str, Any]]]) -> str:
        """Generate comprehensive test report."""
        report = []
        report.append("# Rate Limiting & Abuse Prevention Test Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        
        for test_name, results in all_results.items():
            if not results:
                continue
                
            analysis = self.analyze_results(results)
            report.append(f"## {test_name.replace('_', ' ').title()}")
            report.append("")
            
            # Summary
            summary = analysis.get("summary", {})
            report.append(f"- Total Requests: {summary.get('total_requests', 0)}")
            report.append(f"- Success Rate: {summary.get('success_rate', 0):.1f}%")
            report.append(f"- Rate Limited: {summary.get('rate_limited', 0)}")
            report.append(f"- Abuse Blocked: {summary.get('abuse_blocked', 0)}")
            report.append(f"- Token Limited: {summary.get('token_limited', 0)}")
            report.append("")
            
            # Performance
            perf = analysis.get("performance", {})
            report.append(f"- Avg Response Time: {perf.get('avg_response_time', 0):.3f}s")
            report.append(f"- Max Response Time: {perf.get('max_response_time', 0):.3f}s")
            report.append("")
            
            # Graceful Degradation
            degradation = analysis.get("graceful_degradation", {})
            report.append(f"- Total Blocks: {degradation.get('total_blocks', 0)}")
            report.append(f"- Block Types: {', '.join(degradation.get('block_types', []))}")
            report.append("")
            
            # Sample blocked requests
            if degradation.get("block_details"):
                report.append("**Sample Blocked Requests:**")
                for block in degradation["block_details"][:3]:
                    report.append(f"- {block['action']}: {block['status']} - {block['reason']}")
                report.append("")
        
        return "\n".join(report)
    
    async def run_all_tests(self) -> str:
        """Run all simulation tests and generate report."""
        print("🎯 Starting comprehensive rate limiting simulation...")
        self.start_time = time.time()
        
        all_results = {}
        
        # Test 1: Rapid requests
        print("\n" + "="*50)
        all_results["rapid_requests"] = await self.simulate_rapid_requests(100, 10)
        
        # Test 2: Token spikes
        print("\n" + "="*50)
        all_results["token_spike"] = await self.simulate_token_spike(15)
        
        # Test 3: Abuse patterns
        print("\n" + "="*50)
        all_results["abuse_patterns"] = await self.simulate_abuse_patterns()
        
        # Test 4: Rate limit boundaries
        print("\n" + "="*50)
        all_results["boundary_test"] = await self.simulate_rate_limit_boundary()
        
        # Generate report
        print("\n" + "="*50)
        print("📊 Generating comprehensive report...")
        report = self.generate_report(all_results)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"rate_limit_test_results_{timestamp}.json"
        report_file = f"rate_limit_test_report_{timestamp}.md"
        
        with open(results_file, "w") as f:
            json.dump(all_results, f, indent=2, default=str)
        
        with open(report_file, "w") as f:
            f.write(report)
        
        total_time = time.time() - self.start_time
        print(f"\n✅ Simulation complete in {total_time:.1f}s")
        print(f"📁 Results saved to: {results_file}")
        print(f"📄 Report saved to: {report_file}")
        
        return report

async def main():
    """Main simulation function."""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    print(f"🚀 Starting rate limiting simulation against {base_url}")
    print("This will test:")
    print("  - Rapid repeated requests")
    print("  - LLM token spike scenarios") 
    print("  - Rate limit boundary conditions")
    print("  - Abuse pattern detection")
    print("")
    
    simulator = RateLimitSimulator(base_url)
    
    try:
        report = await simulator.run_all_tests()
        print("\n" + "="*60)
        print("FINAL REPORT")
        print("="*60)
        print(report)
        
    except KeyboardInterrupt:
        print("\n⚠️  Simulation interrupted by user")
    except Exception as e:
        print(f"\n❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())