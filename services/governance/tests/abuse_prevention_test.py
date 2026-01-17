#!/usr/bin/env python3
"""
Abuse Prevention System Test Suite
Tests all abuse detection mechanisms and prevention strategies
"""

import asyncio
import aiohttp
import time
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import statistics

class AbusePreventionTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        
    async def make_request(self, session: aiohttp.ClientSession, endpoint: str, 
                          payload: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Make a single request and return response data."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if payload:
                async with session.post(url, json=payload, headers=headers or {}) as response:
                    response_data = await response.json()
                    return {
                        "status": response.status,
                        "headers": dict(response.headers),
                        "data": response_data,
                        "timestamp": datetime.now().isoformat(),
                        "success": response.status < 400
                    }
            else:
                async with session.get(url, headers=headers or {}) as response:
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
    
    async def test_rapid_resubmission(self) -> List[Dict[str, Any]]:
        """Test rapid resubmission of the same handle."""
        print("🔄 Testing rapid resubmission abuse...")
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            # Rapidly submit the same handle multiple times
            for i in range(15):
                payload = {
                    "handle": "rapid_resubmission_test",
                    "platform": "instagram",
                    "analysis_type": "authenticity"
                }
                
                result = await self.make_request(session, "/api/analyze", payload)
                result["request_id"] = i
                result["test_type"] = "rapid_resubmission"
                result["attempt_number"] = i + 1
                results.append(result)
                
                # Very rapid submission (100ms delay)
                await asyncio.sleep(0.1)
                
                if i % 5 == 0:
                    print(f"  Progress: {i+1}/15 rapid submissions")
        
        return results
    
    async def test_multiple_handle_variations(self) -> List[Dict[str, Any]]:
        """Test multiple handle variations from same IP."""
        print("🎯 Testing multiple handle variations...")
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            # Test many different handles in quick succession
            for i in range(25):
                payload = {
                    "handle": f"test_variation_{i:03d}",
                    "platform": "instagram",
                    "analysis_type": "authenticity"
                }
                
                result = await self.make_request(session, "/api/analyze", payload)
                result["request_id"] = i
                result["test_type"] = "handle_variations"
                results.append(result)
                
                # Rapid requests (200ms delay)
                await asyncio.sleep(0.2)
                
                if i % 5 == 0:
                    print(f"  Progress: {i+1}/25 handle variations")
        
        return results
    
    async def test_spam_payload_patterns(self) -> List[Dict[str, Any]]:
        """Test spam payload patterns."""
        print("📧 Testing spam payload patterns...")
        
        results = []
        spam_patterns = [
            {"handle": "a" * 1000, "platform": "instagram"},  # Very long handle
            {"handle": "../../../etc/passwd", "platform": "instagram"},  # Path traversal
            {"handle": "<script>alert('xss')</script>", "platform": "instagram"},  # XSS attempt
            {"handle": "test', 'other', 'values", "platform": "instagram"},  # SQL injection
            {"handle": "test\x00null", "platform": "instagram"},  # Null byte
            {"handle": "", "platform": "instagram"},  # Empty handle
            {"handle": "normal", "platform": "a" * 1000},  # Very long platform
            {"handle": "normal", "platform": "../../../etc/passwd"},  # Platform injection
        ]
        
        async with aiohttp.ClientSession() as session:
            for i, spam_payload in enumerate(spam_patterns):
                result = await self.make_request(session, "/api/analyze", spam_payload)
                result["request_id"] = i
                result["test_type"] = "spam_payload"
                result["payload_type"] = list(spam_payload.values())[0][:50] + "..." if len(str(list(spam_payload.values())[0])) > 50 else list(spam_payload.values())[0]
                results.append(result)
                
                await asyncio.sleep(0.5)
                
                print(f"  Tested spam pattern {i+1}/{len(spam_patterns)}")
        
        return results
    
    async def test_header_manipulation(self) -> List[Dict[str, Any]]:
        """Test header manipulation attempts."""
        print("🔧 Testing header manipulation...")
        
        results = []
        malicious_headers = [
            {"X-Forwarded-For": "192.168.1.1, 10.0.0.1, 172.16.0.1"},  # Multiple IPs
            {"X-Real-IP": "256.256.256.256"},  # Invalid IP
            {"User-Agent": "a" * 1000},  # Very long user agent
            {"User-Agent": "<script>alert('xss')</script>"},  # XSS in user agent
            {"X-Custom-Header": "../../../etc/passwd"},  # Path in header
            {"Authorization": "Bearer ' OR '1'='1"},  # SQL injection in auth
            {"Content-Type": "application/json; charset='; DROP TABLE users; --"},  # SQL injection
        ]
        
        async with aiohttp.ClientSession() as session:
            for i, headers in enumerate(malicious_headers):
                payload = {"handle": "header_test", "platform": "instagram"}
                result = await self.make_request(session, "/api/analyze", payload, headers)
                result["request_id"] = i
                result["test_type"] = "header_manipulation"
                result["header_type"] = list(headers.keys())[0]
                results.append(result)
                
                await asyncio.sleep(0.3)
                
                print(f"  Tested header manipulation {i+1}/{len(malicious_headers)}")
        
        return results
    
    async def test_rate_limit_boundary(self) -> List[Dict[str, Any]]:
        """Test rate limit boundary conditions."""
        print("📊 Testing rate limit boundaries...")
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            # Make requests right up to the limit
            for i in range(70):  # Assuming 60/minute limit
                result = await self.make_request(session, "/api/health")
                result["request_id"] = i
                result["test_type"] = "rate_limit_boundary"
                results.append(result)
                
                # Fast requests (50ms delay)
                await asyncio.sleep(0.05)
                
                if i == 59:
                    print(f"  Reached expected limit at request {i+1}")
        
        return results
    
    async def test_distributed_abuse_simulation(self) -> List[Dict[str, Any]]:
        """Test distributed abuse simulation with different IPs."""
        print("🌐 Testing distributed abuse simulation...")
        
        results = []
        
        # Simulate requests from different IPs using X-Forwarded-For
        fake_ips = [
            f"192.168.1.{i}" for i in range(1, 21)
        ] + [
            f"10.0.0.{i}" for i in range(1, 21)
        ] + [
            f"172.16.0.{i}" for i in range(1, 21)
        ]
        
        async with aiohttp.ClientSession() as session:
            for i, fake_ip in enumerate(fake_ips[:30]):  # Test 30 different IPs
                headers = {"X-Forwarded-For": fake_ip}
                payload = {
                    "handle": f"distributed_test_{i}",
                    "platform": "instagram",
                    "analysis_type": "authenticity"
                }
                
                result = await self.make_request(session, "/api/analyze", payload, headers)
                result["request_id"] = i
                result["test_type"] = "distributed_abuse"
                result["fake_ip"] = fake_ip
                results.append(result)
                
                # Moderate delay (300ms)
                await asyncio.sleep(0.3)
                
                if i % 10 == 0:
                    print(f"  Progress: {i+1}/{min(30, len(fake_ips))} distributed requests")
        
        return results
    
    async def test_token_exhaustion_attack(self) -> List[Dict[str, Any]]:
        """Test token exhaustion attack simulation."""
        print("💰 Testing token exhaustion attack...")
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            # Make requests that would consume large amounts of tokens
            for i in range(20):
                payload = {
                    "handle": f"token_exhaustion_{i}",
                    "platform": "instagram",
                    "analysis_type": "authenticity",
                    "deep_analysis": True,
                    "include_evidence": True,
                    "confidence_threshold": 0.95,
                    "comprehensive_report": True
                }
                
                result = await self.make_request(session, "/api/analyze", payload)
                result["request_id"] = i
                result["test_type"] = "token_exhaustion"
                results.append(result)
                
                # Wait between large requests to see budget impact
                await asyncio.sleep(1)
                
                if i % 5 == 0:
                    print(f"  Progress: {i+1}/20 token exhaustion attempts")
        
        return results
    
    def analyze_abuse_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze abuse prevention results."""
        if not results:
            return {"error": "No results to analyze"}
        
        total_requests = len(results)
        blocked_requests = sum(1 for r in results if r.get("status") in [403, 429, 503])
        abuse_blocked = sum(1 for r in results if r.get("status") == 403)
        rate_limited = sum(1 for r in results if r.get("status") == 429)
        service_unavailable = sum(1 for r in results if r.get("status") == 503)
        
        # Check for abuse detection headers
        abuse_indicators = []
        for r in results:
            headers = r.get("headers", {})
            if "X-Governance-Action" in headers:
                abuse_indicators.append({
                    "action": headers["X-Governance-Action"],
                    "status": r.get("status"),
                    "test_type": r.get("test_type"),
                    "reason": r.get("data", {}).get("message", "Unknown")
                })
        
        # Response time analysis
        response_times = []
        for r in results:
            if "X-Governance-Time" in r.get("headers", {}):
                try:
                    response_times.append(float(r["headers"]["X-Governance-Time"].rstrip("s")))
                except:
                    pass
        
        # Pattern analysis
        patterns = {}
        for r in results:
            test_type = r.get("test_type", "unknown")
            if test_type not in patterns:
                patterns[test_type] = {"total": 0, "blocked": 0}
            patterns[test_type]["total"] += 1
            if r.get("status") in [403, 429, 503]:
                patterns[test_type]["blocked"] += 1
        
        return {
            "summary": {
                "total_requests": total_requests,
                "blocked_requests": blocked_requests,
                "abuse_blocked": abuse_blocked,
                "rate_limited": rate_limited,
                "service_unavailable": service_unavailable,
                "block_rate": (blocked_requests / total_requests * 100) if total_requests > 0 else 0
            },
            "abuse_indicators": {
                "total_indicators": len(abuse_indicators),
                "unique_actions": list(set(d["action"] for d in abuse_indicators)),
                "indicators": abuse_indicators[:10]  # First 10 for brevity
            },
            "performance": {
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0
            },
            "patterns": patterns
        }
    
    def generate_abuse_report(self, all_results: Dict[str, List[Dict[str, Any]]]) -> str:
        """Generate comprehensive abuse prevention report."""
        report = []
        report.append("# Abuse Prevention System Test Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        
        for test_name, results in all_results.items():
            if not results:
                continue
                
            analysis = self.analyze_abuse_results(results)
            report.append(f"## {test_name.replace('_', ' ').title()}")
            report.append("")
            
            # Summary
            summary = analysis.get("summary", {})
            report.append(f"- Total Requests: {summary.get('total_requests', 0)}")
            report.append(f"- Block Rate: {summary.get('block_rate', 0):.1f}%")
            report.append(f"- Abuse Blocked: {summary.get('abuse_blocked', 0)}")
            report.append(f"- Rate Limited: {summary.get('rate_limited', 0)}")
            report.append(f"- Service Unavailable: {summary.get('service_unavailable', 0)}")
            report.append("")
            
            # Abuse indicators
            indicators = analysis.get("abuse_indicators", {})
            report.append(f"- Abuse Indicators Triggered: {indicators.get('total_indicators', 0)}")
            report.append(f"- Unique Actions: {', '.join(indicators.get('unique_actions', []))}")
            report.append("")
            
            # Performance
            perf = analysis.get("performance", {})
            report.append(f"- Avg Response Time: {perf.get('avg_response_time', 0):.3f}s")
            report.append("")
            
            # Sample blocked requests
            if indicators.get("indicators"):
                report.append("**Sample Abuse Detections:**")
                for indicator in indicators["indicators"][:3]:
                    report.append(f"- {indicator['action']}: {indicator['status']} - {indicator['reason']}")
                report.append("")
        
        return "\n".join(report)
    
    async def run_all_abuse_tests(self) -> str:
        """Run all abuse prevention tests."""
        print("🛡️  Starting comprehensive abuse prevention testing...")
        start_time = time.time()
        
        all_results = {}
        
        # Test 1: Rapid resubmission
        print("\n" + "="*50)
        all_results["rapid_resubmission"] = await self.test_rapid_resubmission()
        
        # Test 2: Multiple handle variations
        print("\n" + "="*50)
        all_results["handle_variations"] = await self.test_multiple_handle_variations()
        
        # Test 3: Spam payload patterns
        print("\n" + "="*50)
        all_results["spam_payloads"] = await self.test_spam_payload_patterns()
        
        # Test 4: Header manipulation
        print("\n" + "="*50)
        all_results["header_manipulation"] = await self.test_header_manipulation()
        
        # Test 5: Rate limit boundaries
        print("\n" + "="*50)
        all_results["rate_limit_boundary"] = await self.test_rate_limit_boundary()
        
        # Test 6: Distributed abuse
        print("\n" + "="*50)
        all_results["distributed_abuse"] = await self.test_distributed_abuse_simulation()
        
        # Test 7: Token exhaustion
        print("\n" + "="*50)
        all_results["token_exhaustion"] = await self.test_token_exhaustion_attack()
        
        # Generate report
        print("\n" + "="*50)
        print("📊 Generating abuse prevention report...")
        report = self.generate_abuse_report(all_results)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"abuse_prevention_test_results_{timestamp}.json"
        report_file = f"abuse_prevention_test_report_{timestamp}.md"
        
        with open(results_file, "w") as f:
            json.dump(all_results, f, indent=2, default=str)
        
        with open(report_file, "w") as f:
            f.write(report)
        
        total_time = time.time() - start_time
        print(f"\n✅ Abuse prevention testing complete in {total_time:.1f}s")
        print(f"📁 Results saved to: {results_file}")
        print(f"📄 Report saved to: {report_file}")
        
        return report

async def main():
    """Main abuse testing function."""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    print(f"🛡️  Starting abuse prevention testing against {base_url}")
    print("This will test:")
    print("  - Rapid resubmission detection")
    print("  - Multiple handle variation patterns")
    print("  - Spam payload detection")
    print("  - Header manipulation attempts")
    print("  - Rate limit boundary conditions")
    print("  - Distributed abuse simulation")
    print("  - Token exhaustion attack prevention")
    print("")
    
    tester = AbusePreventionTester(base_url)
    
    try:
        report = await tester.run_all_abuse_tests()
        print("\n" + "="*60)
        print("FINAL ABUSE PREVENTION REPORT")
        print("="*60)
        print(report)
        
    except KeyboardInterrupt:
        print("\n⚠️  Abuse testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Abuse testing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())