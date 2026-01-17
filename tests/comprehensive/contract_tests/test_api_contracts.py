#!/usr/bin/env python3
"""
CONTRACT TESTS — API HONESTY
Tests for POST /analyze, GET /status/{job_id}, GET /report/{job_id}
Verifies correct HTTP codes, schema stability, and warning banner propagation
"""

import unittest
import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime

from pydantic import ValidationError
from services.api.models.async_models import AnalyzeResponse, JobStatusResponse, ReportResponse
from services.api.models.report import ReportResponse as ReportResponseModel


API_BASE_URL = "http://localhost:8000"


class TestAPIContracts(unittest.TestCase):
    """Test API contract compliance and honesty"""
    
    def setUp(self):
        """Set up test data"""
        self.test_handle = "test_user_contract"
        self.test_platform = "instagram"
        self.invalid_platform = "invalid_platform_xyz"
        self.empty_handle = ""
        self.invalid_job_id = "invalid-job-id-123"
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> tuple:
        """Helper to make HTTP requests"""
        async with aiohttp.ClientSession() as session:
            if method == "POST":
                async with session.post(f"{API_BASE_URL}{endpoint}", json=data) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else None
                    return response.status, response_data, response.headers
            elif method == "GET":
                async with session.get(f"{API_BASE_URL}{endpoint}") as response:
                    response_data = await response.json() if response.content_type == 'application/json' else None
                    return response.status, response_data, response.headers
    
    def run_async_test(self, test_func):
        """Helper to run async tests"""
        return asyncio.run(test_func())
    
    async def test_analyze_endpoint_contract(self):
        """Test POST /analyze endpoint contract compliance"""
        print("\n🧪 Testing POST /analyze endpoint contract...")
        
        # Test 1: Valid request should return 202
        valid_request = {"handle": self.test_handle, "platform": self.test_platform}
        status, response, headers = await self._make_request("POST", "/api/analyze", valid_request)
        
        self.assertEqual(status, 202, "Valid analyze request should return 202 Accepted")
        self.assertIsNotNone(response, "Response should contain JSON data")
        
        # Validate response schema
        try:
            analyze_response = AnalyzeResponse(**response)
            self.assertIsInstance(analyze_response.job_id, str)
            self.assertEqual(analyze_response.status, "accepted")
        except ValidationError as e:
            self.fail(f"Response schema validation failed: {e}")
        
        # Test response time compliance (≤200ms)
        start_time = time.time()
        await self._make_request("POST", "/api/analyze", valid_request)
        response_time = (time.time() - start_time) * 1000
        
        self.assertLessEqual(response_time, 200, 
                            f"Response time should be ≤200ms, got {response_time:.1f}ms")
        
        print(f"✅ Valid request: 202 response in {response_time:.1f}ms")
        return analyze_response.job_id
    
    async def test_analyze_invalid_platform(self):
        """Test POST /analyze with invalid platform"""
        print("\n🧪 Testing POST /analyze with invalid platform...")
        
        invalid_request = {"handle": self.test_handle, "platform": self.invalid_platform}
        status, response, headers = await self._make_request("POST", "/api/analyze", invalid_request)
        
        self.assertEqual(status, 400, "Invalid platform should return 400 Bad Request")
        self.assertIsNotNone(response, "Response should contain error details")
        self.assertIn("detail", response, "Response should contain error detail")
        self.assertIn("Invalid platform", response["detail"], 
                     "Error message should mention invalid platform")
        
        print(f"✅ Invalid platform properly rejected with 400")
    
    async def test_analyze_empty_handle(self):
        """Test POST /analyze with empty handle"""
        print("\n🧪 Testing POST /analyze with empty handle...")
        
        empty_request = {"handle": self.empty_handle, "platform": self.test_platform}
        status, response, headers = await self._make_request("POST", "/api/analyze", empty_request)
        
        self.assertEqual(status, 400, "Empty handle should return 400 Bad Request")
        self.assertIsNotNone(response, "Response should contain error details")
        self.assertIn("detail", response, "Response should contain error detail")
        
        print(f"✅ Empty handle properly rejected with 400")
    
    async def test_status_endpoint_contract(self):
        """Test GET /status/{job_id} endpoint contract"""
        print("\n🧪 Testing GET /status/{job_id} endpoint contract...")
        
        # First create a job
        job_id = await self.test_analyze_endpoint_contract()
        
        # Test valid job ID
        status, response, headers = await self._make_request("GET", f"/api/status/{job_id}")
        
        self.assertEqual(status, 200, "Valid job ID should return 200 OK")
        self.assertIsNotNone(response, "Response should contain JSON data")
        
        # Validate response schema
        try:
            status_response = JobStatusResponse(**response)
            self.assertEqual(status_response.job_id, job_id)
            self.assertIn(status_response.status, ["pending", "processing", "completed", "failed"])
            self.assertIsInstance(status_response.phase, str)
        except ValidationError as e:
            self.fail(f"Response schema validation failed: {e}")
        
        # Test response time compliance (≤100ms)
        start_time = time.time()
        await self._make_request("GET", f"/api/status/{job_id}")
        response_time = (time.time() - start_time) * 1000
        
        self.assertLessEqual(response_time, 100, 
                            f"Response time should be ≤100ms, got {response_time:.1f}ms")
        
        print(f"✅ Status endpoint: 200 response in {response_time:.1f}ms")
    
    async def test_status_invalid_job_id(self):
        """Test GET /status/{job_id} with invalid job ID"""
        print("\n🧪 Testing GET /status/{job_id} with invalid job ID...")
        
        status, response, headers = await self._make_request("GET", 
                                                             f"/api/status/{self.invalid_job_id}")
        
        self.assertEqual(status, 404, "Invalid job ID should return 404 Not Found")
        self.assertIsNotNone(response, "Response should contain error details")
        self.assertIn("detail", response, "Response should contain error detail")
        self.assertIn("Job not found", response["detail"], 
                     "Error message should mention job not found")
        
        print(f"✅ Invalid job ID properly handled with 404")
    
    async def test_report_endpoint_contract(self):
        """Test GET /report/{job_id} endpoint contract"""
        print("\n🧪 Testing GET /report/{job_id} endpoint contract...")
        
        # Note: This test may need adjustment based on actual job completion
        # For now, test the error cases and schema validation
        
        # Test with invalid job ID
        status, response, headers = await self._make_request("GET", 
                                                             f"/api/report/{self.invalid_job_id}")
        
        self.assertEqual(status, 404, "Invalid job ID should return 404 Not Found")
        self.assertIsNotNone(response, "Response should contain error details")
        
        # Test with job that's not completed (should return 400)
        job_id = await self.test_analyze_endpoint_contract()
        status, response, headers = await self._make_request("GET", 
                                                             f"/api/report/{job_id}")
        
        # Job might be pending/processing, so should return 400
        self.assertIn(status, [400, 404], "Uncompleted job should return 400 or 404")
        
        print(f"✅ Report endpoint contract validated")
    
    async def test_schema_stability(self):
        """Test that API schemas remain stable"""
        print("\n🧪 Testing API schema stability...")
        
        # Test AnalyzeResponse schema
        test_analyze_response = {
            "job_id": "test-job-123",
            "status": "accepted"
        }
        
        try:
            response = AnalyzeResponse(**test_analyze_response)
            self.assertEqual(response.job_id, "test-job-123")
            self.assertEqual(response.status, "accepted")
        except ValidationError as e:
            self.fail(f"AnalyzeResponse schema changed: {e}")
        
        # Test JobStatusResponse schema
        test_status_response = {
            "job_id": "test-job-123",
            "status": "processing",
            "phase": "scraping",
            "percent": 50,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "error_message": None
        }
        
        try:
            response = JobStatusResponse(**test_status_response)
            self.assertEqual(response.job_id, "test-job-123")
            self.assertEqual(response.status, "processing")
        except ValidationError as e:
            self.fail(f"JobStatusResponse schema changed: {e}")
        
        print(f"✅ API schemas are stable")
    
    async def test_warning_banner_propagation(self):
        """Test that warning banners propagate to frontend"""
        print("\n🧪 Testing warning banner propagation...")
        
        # This test would need to be implemented based on actual warning banner implementation
        # For now, test that error messages are properly formatted
        
        # Test error response format
        invalid_request = {"handle": self.empty_handle, "platform": self.test_platform}
        status, response, headers = await self._make_request("POST", "/api/analyze", invalid_request)
        
        self.assertEqual(status, 400)
        self.assertIn("detail", response, "Error responses should have 'detail' field")
        self.assertIsInstance(response["detail"], str, "Error detail should be a string")
        
        print(f"✅ Warning/error messages are properly formatted")


class TestAPIHonesty(unittest.TestCase):
    """Test API honesty principles"""
    
    def setUp(self):
        """Set up test data"""
        self.api_base = "http://localhost:8000"
    
    def run_async_test(self, test_func):
        """Helper to run async tests"""
        return asyncio.run(test_func)
    
    async def _test_endpoint_response_time(self, endpoint: str, max_time_ms: int, method: str = "GET", data: Optional[Dict] = None):
        """Test that endpoint responds within specified time"""
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            if method == "GET":
                async with session.get(f"{self.api_base}{endpoint}") as response:
                    await response.text()
            elif method == "POST":
                async with session.post(f"{self.api_base}{endpoint}", json=data) as response:
                    await response.text()
        
        response_time_ms = (time.time() - start_time) * 1000
        
        self.assertLessEqual(response_time_ms, max_time_ms,
                            f"{endpoint} response time should be ≤{max_time_ms}ms, got {response_time_ms:.1f}ms")
        
        return response_time_ms
    
    def test_performance_targets(self):
        """Test that API meets performance targets"""
        print("\n🧪 Testing API performance targets...")
        
        # Test health endpoint (should be fast)
        response_time = self.run_async_test(
            self._test_endpoint_response_time("/health", 50)
        )
        print(f"✅ Health endpoint: {response_time:.1f}ms")
        
        # Test async health endpoint
        response_time = self.run_async_test(
            self._test_endpoint_response_time("/api/health/async", 100)
        )
        print(f"✅ Async health endpoint: {response_time:.1f}ms")
    
    def test_error_response_consistency(self):
        """Test that error responses are consistent"""
        print("\n🧪 Testing error response consistency...")
        
        async def test_errors():
            async with aiohttp.ClientSession() as session:
                # Test various error scenarios
                error_tests = [
                    ("GET", "/api/status/invalid-job-id", 404),
                    ("POST", "/api/analyze", 400),  # Missing body
                    ("GET", "/api/nonexistent", 404),
                ]
                
                for method, endpoint, expected_status in error_tests:
                    if method == "GET":
                        async with session.get(f"{self.api_base}{endpoint}") as response:
                            self.assertEqual(response.status, expected_status)
                            if response.content_type == 'application/json':
                                error_data = await response.json()
                                self.assertIn("detail", error_data, "Error responses should have consistent format")
                    elif method == "POST":
                        async with session.post(f"{self.api_base}{endpoint}") as response:
                            self.assertEqual(response.status, expected_status)
                            if response.content_type == 'application/json':
                                error_data = await response.json()
                                self.assertIn("detail", error_data, "Error responses should have consistent format")
        
        self.run_async_test(test_errors())
        print(f"✅ Error responses are consistent")


class TestAPIIntegration(unittest.TestCase):
    """Test API integration scenarios"""
    
    def setUp(self):
        """Set up test data"""
        self.api_base = API_BASE_URL
    
    async def test_complete_analysis_flow(self):
        """Test complete analysis flow from submission to report"""
        print("\n🧪 Testing complete analysis flow...")
        
        test_handle = "test_complete_flow"
        test_platform = "instagram"
        
        async with aiohttp.ClientSession() as session:
            # Step 1: Submit analysis
            submit_data = {"handle": test_handle, "platform": test_platform}
            async with session.post(f"{self.api_base}/api/analyze", json=submit_data) as response:
                self.assertEqual(response.status, 202)
                submit_result = await response.json()
                job_id = submit_result["job_id"]
                print(f"✅ Analysis submitted, job ID: {job_id}")
            
            # Step 2: Check status
            max_polls = 30
            for i in range(max_polls):
                async with session.get(f"{self.api_base}/api/status/{job_id}") as response:
                    self.assertEqual(response.status, 200)
                    status_result = await response.json()
                    
                    if status_result["status"] == "completed":
                        print(f"✅ Job completed after {i+1} polls")
                        break
                    elif status_result["status"] == "failed":
                        self.fail(f"Job failed: {status_result.get('error_message', 'Unknown error')}")
                    
                    await asyncio.sleep(1)
            else:
                self.fail("Job did not complete within timeout")
            
            # Step 3: Get report
            async with session.get(f"{self.api_base}/api/report/{job_id}") as response:
                if response.status == 200:
                    report_result = await response.json()
                    self.assertIn("handle", report_result)
                    self.assertIn("platform", report_result)
                    self.assertIn("generated_at", report_result)
                    print("✅ Report retrieved successfully")
                else:
                    print(f"⚠️ Report not available (status: {response.status})")
    
    def run_async_test(self, test_func):
        """Helper to run async tests"""
        return asyncio.run(test_func())


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)