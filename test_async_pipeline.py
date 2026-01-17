#!/usr/bin/env python3
"""
Test script for the async pipeline implementation.
Tests all three endpoints: POST /api/analyze, GET /api/status/{job_id}, GET /api/report/{job_id}
"""

import asyncio
import aiohttp
import json
import time
from typing import Optional

API_BASE_URL = "http://localhost:8000"

async def test_async_pipeline():
    """Test the complete async pipeline flow."""
    print("🚀 Testing Async Pipeline Implementation")
    print("=" * 50)
    
    # Test handle
    test_handle = "test_user_123"
    test_platform = "instagram"
    
    try:
        # Step 1: Submit analysis request
        print(f"📤 Submitting analysis request for @{test_handle}...")
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            # Submit analysis
            async with session.post(
                f"{API_BASE_URL}/api/analyze",
                json={"handle": test_handle, "platform": test_platform}
            ) as response:
                submit_time = time.time() - start_time
                
                if response.status != 202:
                    error_text = await response.text()
                    print(f"❌ Analysis submission failed: {response.status} - {error_text}")
                    return
                
                submit_result = await response.json()
                job_id = submit_result["job_id"]
                
                print(f"✅ Analysis submitted successfully!")
                print(f"   Job ID: {job_id}")
                print(f"   Response time: {submit_time*1000:.1f}ms (target: ≤200ms)")
                
                if submit_time > 0.2:
                    print(f"⚠️  Warning: Response time exceeded 200ms target")
        
        # Step 2: Poll job status
        print(f"\n📊 Polling job status for {job_id}...")
        max_polls = 30  # Max 30 polls (about 30 seconds)
        poll_interval = 1.0  # 1 second between polls
        
        for poll_count in range(max_polls):
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                
                async with session.get(f"{API_BASE_URL}/api/status/{job_id}") as response:
                    status_time = time.time() - start_time
                    
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"❌ Status check failed: {response.status} - {error_text}")
                        return
                    
                    status_result = await response.json()
                    
                    if status_time > 0.1:
                        print(f"⚠️  Warning: Status query exceeded 100ms target")
                    
                    # Print status update
                    percent = status_result.get("percent", "N/A")
                    phase = status_result["phase"]
                    job_status = status_result["status"]
                    
                    print(f"   Poll {poll_count + 1}: {job_status} - {phase} ({percent}%)")
                    print(f"   Status query time: {status_time*1000:.1f}ms")
                    
                    # Check if job is completed or failed
                    if job_status == "completed":
                        print(f"✅ Job completed successfully!")
                        break
                    elif job_status == "failed":
                        error_msg = status_result.get("error_message", "Unknown error")
                        print(f"❌ Job failed: {error_msg}")
                        return
                    
                    # Wait before next poll
                    await asyncio.sleep(poll_interval)
        
        else:
            print(f"⏰ Max polling limit reached, job may still be processing")
            return
        
        # Step 3: Retrieve final report
        print(f"\n📋 Retrieving final report for {job_id}...")
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/report/{job_id}") as response:
                report_time = time.time() - start_time
                
                if response.status != 200:
                    error_text = await response.text()
                    print(f"❌ Report retrieval failed: {response.status} - {error_text}")
                    return
                
                report_result = await response.json()
                
                print(f"✅ Report retrieved successfully!")
                print(f"   Report query time: {report_time*1000:.1f}ms (target: ≤500ms)")
                
                if report_time > 0.5:
                    print(f"⚠️  Warning: Report retrieval exceeded 500ms target")
                
                # Print report summary
                handle = report_result["handle"]
                platform = report_result["platform"]
                generated_at = report_result["generated_at"]
                
                print(f"\n📈 Report Summary:")
                print(f"   Handle: @{handle}")
                print(f"   Platform: {platform}")
                print(f"   Generated at: {generated_at}")
                
                # Print pillar scores
                pillars = ["true_engagement", "audience_authenticity", "brand_safety"]
                for pillar in pillars:
                    if pillar in report_result:
                        score_data = report_result[pillar]
                        signal_strength = score_data.get("signal_strength", "N/A")
                        confidence = score_data.get("confidence", "N/A")
                        print(f"   {pillar.replace('_', ' ').title()}: {signal_strength}/100 (confidence: {confidence})")
        
        # Step 4: Test health check
        print(f"\n🏥 Testing async pipeline health...")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/health/async") as response:
                if response.status == 200:
                    health_result = await response.json()
                    print(f"✅ Async pipeline health: {health_result}")
                else:
                    print(f"❌ Health check failed: {response.status}")
        
        print(f"\n🎉 Async pipeline test completed successfully!")
        
    except aiohttp.ClientError as e:
        print(f"❌ Network error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

async def test_error_handling():
    """Test error handling scenarios."""
    print(f"\n🧪 Testing error handling...")
    
    async with aiohttp.ClientSession() as session:
        # Test invalid platform
        print(f"   Testing invalid platform...")
        async with session.post(
            f"{API_BASE_URL}/api/analyze",
            json={"handle": "test", "platform": "invalid_platform"}
        ) as response:
            if response.status == 400:
                print(f"   ✅ Invalid platform properly rejected")
            else:
                print(f"   ❌ Invalid platform not properly handled")
        
        # Test empty handle
        print(f"   Testing empty handle...")
        async with session.post(
            f"{API_BASE_URL}/api/analyze",
            json={"handle": "", "platform": "instagram"}
        ) as response:
            if response.status == 400:
                print(f"   ✅ Empty handle properly rejected")
            else:
                print(f"   ❌ Empty handle not properly handled")
        
        # Test invalid job ID
        print(f"   Testing invalid job ID...")
        async with session.get(f"{API_BASE_URL}/api/status/invalid-job-id") as response:
            if response.status == 404:
                print(f"   ✅ Invalid job ID properly handled")
            else:
                print(f"   ❌ Invalid job ID not properly handled")

async def main():
    """Main test function."""
    print("Starting async pipeline tests...")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("You can start it with: uvicorn services.api.main:app --reload")
    print()
    
    # Wait a moment for user to read instructions
    await asyncio.sleep(2)
    
    # Run main test
    await test_async_pipeline()
    
    # Run error handling tests
    await test_error_handling()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    asyncio.run(main())