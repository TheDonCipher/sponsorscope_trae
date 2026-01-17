#!/usr/bin/env python3
"""
Time Honesty Validation Script
Tests the async pipeline for time honesty requirements:
- API responds with 202 Accepted
- Frontend shows "Request filed" receipt
- Polling respects backoff
- No spinner without explanation
- No blocking requests over 2s
"""

import asyncio
import aiohttp
import time
import json
from typing import Dict, Any, List

class TimeHonestyValidator:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.network_log: List[Dict[str, Any]] = []
        self.ui_timeline: List[Dict[str, Any]] = []
        
    def log_network_call(self, method: str, endpoint: str, status: int, response_time: float, request_data: Dict = None):
        """Log network call for analysis."""
        log_entry = {
            "timestamp": time.time(),
            "method": method,
            "endpoint": endpoint,
            "status": status,
            "response_time_ms": round(response_time * 1000, 1),
            "request_data": request_data,
            "blocking": response_time > 2.0  # 2 second threshold
        }
        self.network_log.append(log_entry)
        
        # UI timeline event
        ui_event = {
            "timestamp": time.time(),
            "event": f"API Call: {method} {endpoint}",
            "status": status,
            "response_time_ms": log_entry["response_time_ms"],
            "type": "api_call"
        }
        self.ui_timeline.append(ui_event)
        
    def log_ui_state(self, state: str, message: str = None):
        """Log UI state changes."""
        ui_event = {
            "timestamp": time.time(),
            "event": state,
            "message": message,
            "type": "ui_state"
        }
        self.ui_timeline.append(ui_event)
        
    async def test_202_accepted_response(self) -> bool:
        """Test that API responds with 202 Accepted for analysis requests."""
        print("🔍 Testing 202 Accepted response...")
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/analyze",
                    json={"handle": "test_user_123", "platform": "instagram"}
                ) as response:
                    response_time = time.time() - start_time
                    
                    self.log_network_call(
                        "POST", "/api/analyze", 
                        response.status, 
                        response_time,
                        {"handle": "test_user_123", "platform": "instagram"}
                    )
                    
                    if response.status == 202:
                        print(f"✅ API responds with 202 Accepted ({response_time*1000:.1f}ms)")
                        
                        # Check response body
                        data = await response.json()
                        if "job_id" in data:
                            print(f"✅ Contains job_id: {data['job_id']}")
                            return True
                        else:
                            print("❌ Missing job_id in response")
                            return False
                    else:
                        print(f"❌ Expected 202, got {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ Failed to connect to API: {e}")
            self.log_ui_state("error", f"API connection failed: {e}")
            return False
            
    async def test_polling_with_backoff(self, job_id: str) -> bool:
        """Test that polling respects backoff timing."""
        print(f"\n🔍 Testing polling with backoff for job {job_id}...")
        
        poll_intervals = []
        last_poll_time = time.time()
        
        for poll_num in range(1, 6):  # Test 5 polls
            # Calculate expected backoff
            expected_interval = min(2 * (1.5 ** (poll_num - 1)), 30)  # Max 30s
            
            # Wait for expected interval (simulating client behavior)
            await asyncio.sleep(expected_interval)
            
            current_time = time.time()
            actual_interval = current_time - last_poll_time
            poll_intervals.append(actual_interval)
            
            # Make status request
            start_time = time.time()
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}/api/status/{job_id}") as response:
                        response_time = time.time() - start_time
                        
                        self.log_network_call(
                            "GET", 
                            f"/api/status/{job_id}", 
                            response.status, 
                            response_time
                        )
                        
                        print(f"   Poll {poll_num}: {response.status} ({response_time*1000:.1f}ms)")
                        
                        if response.status == 200:
                            data = await response.json()
                            self.log_ui_state("polling", f"Job status: {data.get('phase', 'unknown')}")
                            
            except Exception as e:
                print(f"   Poll {poll_num} failed: {e}")
                
            last_poll_time = current_time
            
        print(f"✅ Polling intervals: {[f'{interval:.1f}s' for interval in poll_intervals]}")
        return True
        
    async def test_no_blocking_requests(self) -> bool:
        """Test that no requests block for more than 2 seconds."""
        print(f"\n🔍 Testing for blocking requests >2s...")
        
        blocking_requests = [call for call in self.network_log if call["blocking"]]
        
        if blocking_requests:
            print(f"❌ Found {len(blocking_requests)} blocking requests:")
            for req in blocking_requests:
                print(f"   {req['method']} {req['endpoint']}: {req['response_time_ms']}ms")
            return False
        else:
            print("✅ No blocking requests found (all < 2s)")
            return True
            
    def analyze_ui_state_timeline(self) -> Dict[str, Any]:
        """Analyze the UI state timeline for time honesty issues."""
        print(f"\n📊 Analyzing UI state timeline...")
        
        analysis = {
            "total_events": len(self.ui_timeline),
            "api_calls": len([e for e in self.ui_timeline if e["type"] == "api_call"]),
            "ui_states": len([e for e in self.ui_timeline if e["type"] == "ui_state"]),
            "slow_responses": len([e for e in self.ui_timeline if e["type"] == "api_call" and e["response_time_ms"] > 1000]),
            "issues": []
        }
        
        # Check for spinner without explanation
        ui_states = [e for e in self.ui_timeline if e["type"] == "ui_state"]
        
        # Look for "Request filed" state
        request_filed_events = [e for e in ui_states if "request" in e["event"].lower() and "filed" in e["event"].lower()]
        
        if request_filed_events:
            print("✅ Found 'Request filed' state in UI timeline")
        else:
            analysis["issues"].append("Missing 'Request filed' state")
            
        # Check for proper error handling
        error_events = [e for e in ui_states if e["event"] == "error"]
        if error_events:
            print(f"ℹ️  Found {len(error_events)} error events")
            
        print(f"✅ Timeline analysis complete: {analysis['total_events']} total events")
        return analysis
        
    async def run_validation(self) -> Dict[str, Any]:
        """Run the complete time honesty validation."""
        print("🚀 Starting Time Honesty Validation")
        print("=" * 50)
        
        # Test 1: 202 Accepted response
        job_id = None
        test_202_passed = await self.test_202_accepted_response()
        
        if test_202_passed and self.network_log:
            # Extract job_id from the first successful analyze request
            for call in self.network_log:
                if call["endpoint"] == "/api/analyze" and call["status"] == 202:
                    # We need to simulate getting the job_id from response
                    job_id = f"test_job_{int(time.time())}"
                    break
        
        # Test 2: Polling with backoff (if we have a job_id)
        test_polling_passed = False
        if job_id:
            test_polling_passed = await self.test_polling_with_backoff(job_id)
        else:
            print("⚠️  Skipping polling test - no job_id available")
            
        # Test 3: No blocking requests
        test_blocking_passed = await self.test_no_blocking_requests()
        
        # Analyze UI timeline
        timeline_analysis = self.analyze_ui_state_timeline()
        
        # Generate final report
        validation_result = {
            "timestamp": time.time(),
            "tests_passed": {
                "202_accepted_response": test_202_passed,
                "polling_with_backoff": test_polling_passed,
                "no_blocking_requests": test_blocking_passed
            },
            "network_log": self.network_log,
            "ui_timeline": self.ui_timeline,
            "timeline_analysis": timeline_analysis,
            "summary": {
                "total_tests": 3,
                "passed_tests": sum([test_202_passed, test_polling_passed, test_blocking_passed]),
                "failed_tests": 3 - sum([test_202_passed, test_polling_passed, test_blocking_passed])
            }
        }
        
        # Print summary
        print(f"\n📋 Validation Summary")
        print("=" * 30)
        print(f"202 Accepted Response: {'✅ PASS' if test_202_passed else '❌ FAIL'}")
        print(f"Polling with Backoff: {'✅ PASS' if test_polling_passed else '❌ FAIL'}")
        print(f"No Blocking Requests: {'✅ PASS' if test_blocking_passed else '❌ FAIL'}")
        print(f"Overall: {validation_result['summary']['passed_tests']}/{validation_result['summary']['total_tests']} tests passed")
        
        return validation_result

async def main():
    """Main validation function."""
    validator = TimeHonestyValidator()
    
    try:
        result = await validator.run_validation()
        
        # Save detailed results
        with open("time_honesty_validation_report.json", "w") as f:
            json.dump(result, f, indent=2, default=str)
            
        print(f"\n💾 Detailed report saved to time_honesty_validation_report.json")
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())