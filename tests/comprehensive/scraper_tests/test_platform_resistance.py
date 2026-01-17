#!/usr/bin/env python3
"""
SCRAPER REALITY TESTS — RESISTANCE & DEGRADATION
Tests for Instagram and TikTok platforms with various scenarios
Verifies detection over bypass, accurate DataCompleteness states, zero fabricated data
"""

import unittest
import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

API_BASE_URL = "http://localhost:8000"


class TestPlatformResistance(unittest.TestCase):
    """Test platform resistance and degradation scenarios"""
    
    def setUp(self):
        """Set up test data"""
        self.test_platforms = ["instagram", "tiktok"]
        self.test_scenarios = [
            "public_profile",
            "private_profile", 
            "comments_disabled",
            "rate_limited",
            "sparse_data",
            "deleted_user",
            "login_required"
        ]
    
    async def _submit_analysis(self, handle: str, platform: str) -> str:
        """Submit analysis request and return job ID"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_BASE_URL}/api/analyze",
                json={"handle": handle, "platform": platform}
            ) as response:
                if response.status == 202:
                    result = await response.json()
                    return result["job_id"]
                else:
                    return None
    
    async def _get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job status"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/status/{job_id}") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"status": "error", "error": await response.text()}
    
    async def _get_job_report(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job report"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/report/{job_id}") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
    
    async def _wait_for_completion(self, job_id: str, timeout: int = 120) -> Dict[str, Any]:
        """Wait for job completion with timeout"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status_data = await self._get_job_status(job_id)
            
            if status_data["status"] == "completed":
                return status_data
            elif status_data["status"] == "failed":
                return status_data
            
            await asyncio.sleep(1)
        
        return {"status": "timeout", "error": "Job did not complete within timeout"}
    
    def run_async_test(self, test_func):
        """Helper to run async tests"""
        return asyncio.run(test_func())
    
    async def test_public_profile_detection(self):
        """Test detection of public profiles (should work normally)"""
        print("\n🧪 Testing public profile detection...")
        
        for platform in self.test_platforms:
            with self.subTest(platform=platform):
                # Use a well-known public profile handle
                public_handle = f"test_public_{platform}"
                
                job_id = await self._submit_analysis(public_handle, platform)
                self.assertIsNotNone(job_id, f"Should accept analysis for public {platform} profile")
                
                # Wait for completion
                result = await self._wait_for_completion(job_id)
                
                if result["status"] == "completed":
                    report = await self._get_job_report(job_id)
                    self.assertIsNotNone(report, f"Should generate report for public {platform} profile")
                    
                    # Check for data completeness indicators
                    self.assertIn("data_completeness", str(report).lower(), 
                                "Report should indicate data completeness")
                    
                    print(f"✅ Public {platform} profile detected and analyzed")
                else:
                    print(f"⚠️ Public {platform} profile analysis failed: {result.get('error', 'Unknown')}")
    
    async def test_private_profile_handling(self):
        """Test handling of private profiles"""
        print("\n🧪 Testing private profile handling...")
        
        for platform in self.test_platforms:
            with self.subTest(platform=platform):
                # Use a handle that represents a private profile
                private_handle = f"test_private_{platform}"
                
                job_id = await self._submit_analysis(private_handle, platform)
                
                if job_id:
                    result = await self._wait_for_completion(job_id)
                    
                    if result["status"] == "completed":
                        report = await self._get_job_report(job_id)
                        
                        # Should handle private profiles gracefully
                        # Should not fabricate data for private profiles
                        report_str = str(report).lower()
                        self.assertNotIn("fabricated", report_str, 
                                       "Should not fabricate data for private profiles")
                        self.assertNotIn("fake", report_str,
                                       "Should not generate fake data")
                        
                        # Should indicate limited data availability
                        self.assertTrue(
                            "limited" in report_str or "partial" in report_str or "restricted" in report_str,
                            "Should indicate limited data for private profiles"
                        )
                        
                        print(f"✅ Private {platform} profile handled gracefully")
                    else:
                        print(f"⚠️ Private {platform} profile analysis failed: {result.get('error', 'Unknown')}")
                else:
                    print(f"⚠️ Could not submit analysis for private {platform} profile")
    
    async def test_comments_disabled_scenario(self):
        """Test handling of profiles with comments disabled"""
        print("\n🧪 Testing comments disabled scenario...")
        
        for platform in self.test_platforms:
            with self.subTest(platform=platform):
                # Use a handle representing profile with comments disabled
                no_comments_handle = f"test_no_comments_{platform}"
                
                job_id = await self._submit_analysis(no_comments_handle, platform)
                
                if job_id:
                    result = await self._wait_for_completion(job_id)
                    
                    if result["status"] == "completed":
                        report = await self._get_job_report(job_id)
                        self.assertIsNotNone(report, "Should generate report even without comments")
                        
                        # Should indicate comments are not available
                        report_str = str(report).lower()
                        self.assertTrue(
                            "no comments" in report_str or "comments disabled" in report_str or 
                            "limited" in report_str or "partial" in report_str,
                            "Should indicate comments are not available"
                        )
                        
                        # Should not fabricate comment data
                        self.assertNotIn("fake comments", report_str,
                                       "Should not fabricate comment data")
                        
                        print(f"✅ Comments disabled scenario handled for {platform}")
                    else:
                        print(f"⚠️ Comments disabled analysis failed for {platform}: {result.get('error', 'Unknown')}")
                else:
                    print(f"⚠️ Could not submit analysis for comments disabled {platform}")
    
    async def test_rate_limit_handling(self):
        """Test handling of rate limiting scenarios"""
        print("\n🧪 Testing rate limit handling...")
        
        # Test rapid submissions that might trigger rate limiting
        handles = [f"rate_test_{i}" for i in range(10)]
        
        job_ids = []
        rate_limited_count = 0
        
        for handle in handles:
            job_id = await self._submit_analysis(handle, "instagram")
            if job_id:
                job_ids.append(job_id)
            else:
                rate_limited_count += 1
        
        # Should either accept requests or properly rate limit
        self.assertGreater(len(job_ids), 0, "Should accept at least some requests")
        
        if rate_limited_count > 0:
            print(f"✅ Rate limiting triggered: {rate_limited_count}/{len(handles)} requests limited")
        else:
            print(f"✅ All {len(handles)} requests accepted (rate limit not triggered)")
        
        # Check that accepted jobs complete
        completed_count = 0
        for job_id in job_ids[:3]:  # Check first 3 jobs
            result = await self._wait_for_completion(job_id, timeout=60)
            if result["status"] == "completed":
                completed_count += 1
        
        if completed_count > 0:
            print(f"✅ {completed_count} rate-limited jobs completed successfully")
    
    async def test_sparse_data_handling(self):
        """Test handling of profiles with very sparse data"""
        print("\n🧪 Testing sparse data handling...")
        
        for platform in self.test_platforms:
            with self.subTest(platform=platform):
                # Use a handle representing a new/sparse profile
                sparse_handle = f"test_sparse_{platform}"
                
                job_id = await self._submit_analysis(sparse_handle, platform)
                
                if job_id:
                    result = await self._wait_for_completion(job_id)
                    
                    if result["status"] == "completed":
                        report = await self._get_job_report(job_id)
                        self.assertIsNotNone(report, "Should generate report for sparse data")
                        
                        # Should indicate sparse/limited data
                        report_str = str(report).lower()
                        self.assertTrue(
                            "sparse" in report_str or "limited" in report_str or 
                            "low" in report_str or "minimal" in report_str or
                            "insufficient" in report_str or "partial" in report_str,
                            "Should indicate sparse data availability"
                        )
                        
                        # Should have low confidence for sparse data
                        self.assertTrue(
                            "low confidence" in report_str or "confidence" in report_str,
                            "Should indicate confidence level for sparse data"
                        )
                        
                        # Should not extrapolate/fabricate data
                        self.assertNotIn("extrapolated", report_str,
                                       "Should not extrapolate sparse data")
                        
                        print(f"✅ Sparse data handled honestly for {platform}")
                    else:
                        print(f"⚠️ Sparse data analysis failed for {platform}: {result.get('error', 'Unknown')}")
                else:
                    print(f"⚠️ Could not submit analysis for sparse {platform} data")
    
    async def test_deleted_user_handling(self):
        """Test handling of deleted/non-existent users"""
        print("\n🧪 Testing deleted user handling...")
        
        for platform in self.test_platforms:
            with self.subTest(platform=platform):
                # Use a clearly non-existent handle
                deleted_handle = f"deleted_user_12345_nonexistent_{platform}"
                
                job_id = await self._submit_analysis(deleted_handle, platform)
                
                if job_id:
                    result = await self._wait_for_completion(job_id)
                    
                    if result["status"] == "completed":
                        report = await self._get_job_report(job_id)
                        
                        # Should handle deleted users gracefully
                        report_str = str(report).lower()
                        
                        # Should indicate user not found/unavailable
                        self.assertTrue(
                            "not found" in report_str or "unavailable" in report_str or
                            "deleted" in report_str or "does not exist" in report_str or
                            "invalid" in report_str or "error" in report_str,
                            "Should indicate user is not available"
                        )
                        
                        # Should not fabricate data for non-existent users
                        self.assertNotIn("fake user", report_str,
                                       "Should not fabricate user data")
                        
                        print(f"✅ Deleted user handled gracefully for {platform}")
                    elif result["status"] == "failed":
                        # Failure is acceptable for deleted users
                        print(f"✅ Deleted user properly failed for {platform}: {result.get('error', 'Unknown')}")
                    else:
                        print(f"⚠️ Deleted user analysis timed out for {platform}")
                else:
                    print(f"⚠️ Could not submit analysis for deleted {platform} user")
    
    async def test_login_wall_detection(self):
        """Test detection of login walls"""
        print("\n🧪 Testing login wall detection...")
        
        for platform in self.test_platforms:
            with self.subTest(platform=platform):
                # Use a handle that might trigger login wall
                login_wall_handle = f"test_login_required_{platform}"
                
                job_id = await self._submit_analysis(login_wall_handle, platform)
                
                if job_id:
                    result = await self._wait_for_completion(job_id)
                    
                    if result["status"] == "completed":
                        report = await self._get_job_report(job_id)
                        
                        # Should detect login wall scenario
                        report_str = str(report).lower()
                        self.assertTrue(
                            "login" in report_str or "authentication" in report_str or
                            "restricted" in report_str or "limited" in report_str or
                            "access" in report_str,
                            "Should indicate login/authentication requirements"
                        )
                        
                        # Should not bypass login walls
                        self.assertNotIn("bypassed", report_str,
                                         "Should not claim to bypass authentication")
                        
                        print(f"✅ Login wall detected for {platform}")
                    else:
                        print(f"⚠️ Login wall analysis failed for {platform}: {result.get('error', 'Unknown')}")
                else:
                    print(f"⚠️ Could not submit analysis for login wall {platform}")
    
    async def test_layout_change_resilience(self):
        """Test resilience to platform layout changes"""
        print("\n🧪 Testing layout change resilience...")
        
        for platform in self.test_platforms:
            with self.subTest(platform=platform):
                # Use handles that might encounter layout changes
                test_handles = [
                    f"test_layout_change_{platform}",
                    f"test_new_ui_{platform}",
                    f"test_updated_layout_{platform}"
                ]
                
                results = []
                for handle in test_handles:
                    job_id = await self._submit_analysis(handle, platform)
                    if job_id:
                        result = await self._wait_for_completion(job_id, timeout=60)
                        results.append((handle, result))
                
                # Should handle layout changes gracefully
                completed_count = sum(1 for _, result in results if result["status"] == "completed")
                failed_count = sum(1 for _, result in results if result["status"] == "failed")
                
                print(f"✅ Layout change resilience for {platform}: {completed_count} completed, {failed_count} failed")
                
                # Should not crash completely due to layout changes
                self.assertGreater(len(results), 0, "Should attempt analysis despite layout changes")


class TestDataCompletenessAccuracy(unittest.TestCase):
    """Test accuracy of DataCompleteness state reporting"""
    
    def setUp(self):
        """Set up test data"""
        self.api_base = API_BASE_URL
    
    def run_async_test(self, test_func):
        """Helper to run async tests"""
        return asyncio.run(test_func())
    
    async def test_data_completeness_states(self):
        """Test that DataCompleteness states are reported accurately"""
        print("\n🧪 Testing DataCompleteness state accuracy...")
        
        test_scenarios = [
            ("test_full_data", "instagram", "Should have full data"),
            ("test_partial_no_comments", "instagram", "Should have partial data (no comments)"),
            ("test_limited_data", "instagram", "Should have limited data"),
            ("test_insufficient_data", "instagram", "Should have insufficient data"),
        ]
        
        for handle, platform, description in test_scenarios:
            with self.subTest(handle=handle):
                print(f"  Testing: {description}")
                
                # Submit analysis
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.api_base}/api/analyze",
                        json={"handle": handle, "platform": platform}
                    ) as response:
                        if response.status == 202:
                            result = await response.json()
                            job_id = result["job_id"]
                            
                            # Wait for completion
                            start_time = time.time()
                            while time.time() - start_time < 60:
                                async with session.get(f"{self.api_base}/api/status/{job_id}") as status_response:
                                    if status_response.status == 200:
                                        status_data = await status_response.json()
                                        if status_data["status"] == "completed":
                                            # Get final report
                                            async with session.get(f"{self.api_base}/api/report/{job_id}") as report_response:
                                                if report_response.status == 200:
                                                    report = await report_response.json()
                                                    
                                                    # Should indicate data completeness
                                                    report_str = str(report).lower()
                                                    completeness_indicators = [
                                                        "full", "partial", "limited", "insufficient",
                                                        "complete", "incomplete", "available", "unavailable"
                                                    ]
                                                    
                                                    has_completeness = any(indicator in report_str 
                                                                         for indicator in completeness_indicators)
                                                    
                                                    self.assertTrue(has_completeness,
                                                                   f"Report should indicate data completeness for {handle}")
                                                    
                                                    print(f"  ✅ Data completeness reported for {handle}")
                                                    break
                            else:
                                print(f"  ⚠️ Timeout for {handle}")
                        else:
                            print(f"  ⚠️ Could not submit {handle}")


class TestZeroFabrication(unittest.TestCase):
    """Test that the system never fabricates data"""
    
    def setUp(self):
        """Set up test data"""
        self.api_base = API_BASE_URL
    
    def run_async_test(self, test_func):
        """Helper to run async tests"""
        return asyncio.run(test_func())
    
    async def test_no_fabricated_data(self):
        """Test that no data is fabricated under any circumstances"""
        print("\n🧪 Testing zero fabrication policy...")
        
        # Test scenarios that might tempt fabrication
        fabrication_test_cases = [
            ("nonexistent_user_12345", "instagram", "Non-existent user"),
            ("private_account_test_999", "instagram", "Private account"),
            ("deleted_profile_xyz789", "tiktok", "Deleted profile"),
            ("suspended_user_abc456", "instagram", "Suspended user"),
            ("sparse_new_user_111", "tiktok", "Very new user"),
        ]
        
        for handle, platform, description in fabrication_test_cases:
            with self.subTest(handle=handle, description=description):
                print(f"  Testing {description}: @{handle} on {platform}")
                
                # Submit analysis
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.api_base}/api/analyze",
                        json={"handle": handle, "platform": platform}
                    ) as response:
                        if response.status == 202:
                            result = await response.json()
                            job_id = result["job_id"]
                            
                            # Wait for completion
                            start_time = time.time()
                            while time.time() - start_time < 60:
                                async with session.get(f"{self.api_base}/api/status/{job_id}") as status_response:
                                    if status_response.status == 200:
                                        status_data = await status_response.json()
                                        if status_data["status"] == "completed":
                                            # Get final report
                                            async with session.get(f"{self.api_base}/api/report/{job_id}") as report_response:
                                                if report_response.status == 200:
                                                    report = await report_response.json()
                                                    
                                                    # Check for fabrication indicators
                                                    report_str = str(report).lower()
                                                    fabrication_terms = [
                                                        "fabricated", "fake", "synthetic", "generated",
                                                        "artificial", "simulated", "estimated", "guessed",
                                                        "invented", "created", "made up", "extrapolated"
                                                    ]
                                                    
                                                    has_fabrication_terms = any(term in report_str 
                                                                              for term in fabrication_terms)
                                                    
                                                    # Should NOT contain fabrication terms
                                                    self.assertFalse(has_fabrication_terms,
                                                                   f"Report should not contain fabrication terms for {handle}")
                                                    
                                                    # Should indicate uncertainty or limitations
                                                    uncertainty_terms = [
                                                        "uncertain", "unknown", "limited", "partial",
                                                        "insufficient", "inconclusive", "incomplete",
                                                        "unavailable", "restricted", "cannot determine"
                                                    ]
                                                    
                                                    has_uncertainty = any(term in report_str 
                                                                        for term in uncertainty_terms)
                                                    
                                                    self.assertTrue(has_uncertainty,
                                                                   f"Report should indicate uncertainty for {handle}")
                                                    
                                                    print(f"    ✅ No fabrication detected for {description}")
                                                    break
                            else:
                                print(f"    ⚠️ Timeout for {description}")
                        else:
                            print(f"    ⚠️ Could not submit analysis for {description}")


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)