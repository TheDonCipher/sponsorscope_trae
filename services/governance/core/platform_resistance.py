"""
Platform Resistance Layer for SponsorScope.ai

This module implements platform resistance mechanisms to prevent scraping abuse
while ensuring legitimate users can access the service.
"""

import asyncio
import time
import traceback
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from services.governance.core.rate_limiter import rate_limiter
from services.governance.core.enhanced_killswitch import enhanced_killswitch
import json
import os

class PlatformResistanceError(Exception):
    """Base exception for platform resistance errors."""
    
    def __init__(self, message: str, error_type: str, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message  # Add message attribute
        self.error_type = error_type
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()

class ScraperHaltError(PlatformResistanceError):
    """Exception thrown when scraper is halted due to platform resistance."""
    pass

class PlatformResistance:
    """
    Enhanced platform resistance layer that implements scraper-safe halting
    with comprehensive logging and user communication.
    """
    
    def __init__(self):
        self.resistance_log_file = "services/governance/logs/platform_resistance.jsonl"
        self.scraper_detection_threshold = int(os.getenv("SCRAPER_DETECTION_THRESHOLD", "5"))
        self.resistance_mode = os.getenv("PLATFORM_RESISTANCE_MODE", "moderate")
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(self.resistance_log_file), exist_ok=True)
    
    async def evaluate_request(self, request_data: Dict[str, Any]) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Evaluate if a request should be resisted.
        
        Returns:
            Tuple of (should_halt, reason, metadata)
        """
        try:
            client_ip = request_data.get("client_ip", "unknown")
            user_agent = request_data.get("user_agent", "")
            endpoint = request_data.get("endpoint", "")
            handle = request_data.get("handle", "")
            
            # Scraper detection heuristics
            scraper_score = await self._calculate_scraper_score(user_agent, request_data)
            
            # Check if request matches scraping patterns
            if scraper_score >= self.scraper_detection_threshold:
                reason = f"Automated access detected (score: {scraper_score})"
                metadata = {
                    "scraper_score": scraper_score,
                    "detection_method": "heuristic_analysis",
                    "user_agent": user_agent,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await self._log_resistance_event(client_ip, endpoint, reason, metadata)
                return True, reason, metadata
            
            # Check rate limiting with enhanced scraper detection
            rate_limit_info = await rate_limiter.check_rate_limit(client_ip)
            if not rate_limit_info[0]:
                # Additional scraper check for rate-limited requests
                if await self._is_likely_scraper(client_ip, user_agent):
                    reason = "Rate limit exceeded with scraper characteristics"
                    metadata = {
                        "rate_limit_remaining": rate_limit_info[1],
                        "detection_method": "rate_limit_scraper",
                        "user_agent": user_agent,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    await self._log_resistance_event(client_ip, endpoint, reason, metadata)
                    return True, reason, metadata
            
            return False, None, {}
            
        except Exception as e:
            error_trace = traceback.format_exc()
            await self._log_resistance_event(
                request_data.get("client_ip", "unknown"),
                request_data.get("endpoint", ""),
                "Evaluation error",
                {"error": str(e), "trace": error_trace}
            )
            # Fail open - don't block on evaluation errors
            return False, None, {}
    
    async def _calculate_scraper_score(self, user_agent: str, request_data: Dict[str, Any]) -> int:
        """
        Calculate scraper detection score based on various heuristics.
        
        Returns:
            Integer score (higher = more likely scraper)
        """
        score = 0
        
        # Legitimate browser indicators (negative scoring)
        legitimate_indicators = [
            "mozilla", "chrome", "safari", "firefox", "edge", "opera"
        ]
        
        # User agent analysis - higher scores for obvious scrapers
        scraper_patterns = [
            ("curl", 5), ("wget", 5), ("python-requests", 5), ("scrapy", 5),
            ("selenium", 4), ("phantomjs", 4), ("headless", 4),
            ("bot", 3), ("spider", 3), ("crawler", 3)
        ]
        
        user_agent_lower = user_agent.lower()
        
        # Check for legitimate browser indicators first
        has_legitimate_indicator = any(indicator in user_agent_lower for indicator in legitimate_indicators)
        if has_legitimate_indicator:
            score -= 2  # Reduce score for legitimate browsers
        
        # Check for scraper patterns
        for pattern, points in scraper_patterns:
            if pattern in user_agent_lower:
                score += points
        
        # Missing or suspicious user agents
        if not user_agent:
            score += 5  # Empty user agent is very suspicious
        elif len(user_agent) < 10:
            score += 3  # Very short user agent is suspicious
        
        # Request pattern analysis
        headers = request_data.get("headers", {})
        
        # Check for missing browser headers
        browser_headers = ["Accept-Language", "Accept-Encoding", "DNT", "Upgrade-Insecure-Requests"]
        missing_browser_headers = sum(1 for header in browser_headers if header not in headers)
        score += missing_browser_headers * 2
        
        # Check for scraping-related headers
        if "X-Forwarded-For" in headers or "X-Real-IP" in headers:
            score += 2
        
        # Check for missing Accept header (common in scrapers)
        if "Accept" not in headers:
            score += 3
        
        # Request timing patterns (if available)
        request_history = request_data.get("request_history", [])
        if len(request_history) > 1:
            # Check for too-regular timing patterns
            intervals = []
            for i in range(1, len(request_history)):
                if "timestamp" in request_history[i] and "timestamp" in request_history[i-1]:
                    interval = request_history[i]["timestamp"] - request_history[i-1]["timestamp"]
                    intervals.append(interval)
            
            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                # Suspicious if intervals are too regular (within 10% variance)
                if all(abs(interval - avg_interval) / avg_interval < 0.1 for interval in intervals):
                    score += 3
        
        return max(0, score)  # Ensure score doesn't go negative
    
    async def _is_likely_scraper(self, client_ip: str, user_agent: str) -> bool:
        """
        Quick scraper likelihood check for rate-limited requests.
        """
        # Simple heuristics for quick decisions
        user_agent_lower = user_agent.lower()
        scraper_indicators = ["curl", "wget", "python", "scrapy", "selenium", "headless"]
        
        return any(indicator in user_agent_lower for indicator in scraper_indicators)
    
    async def _log_resistance_event(self, client_ip: str, endpoint: str, reason: str, metadata: Dict[str, Any]):
        """Log platform resistance events for monitoring and analysis."""
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "client_ip": client_ip,
                "endpoint": endpoint,
                "reason": reason,
                "metadata": metadata,
                "resistance_mode": self.resistance_mode
            }
            
            with open(self.resistance_log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
                
        except Exception as e:
            print(f"Failed to log resistance event: {e}")
    
    def get_resistance_info(self) -> Dict[str, Any]:
        """Get current platform resistance status and statistics."""
        try:
            # Read recent resistance events
            recent_events = []
            if os.path.exists(self.resistance_log_file):
                with open(self.resistance_log_file, "r") as f:
                    lines = f.readlines()
                    # Get last 100 events
                    for line in lines[-100:]:
                        try:
                            event = json.loads(line.strip())
                            recent_events.append(event)
                        except:
                            continue
            
            # Calculate statistics
            total_resisted = len(recent_events)
            scraper_blocks = sum(1 for event in recent_events if "scraper" in event.get("reason", "").lower())
            rate_limit_blocks = sum(1 for event in recent_events if "rate limit" in event.get("reason", "").lower())
            
            return {
                "resistance_mode": self.resistance_mode,
                "total_requests_resisted": total_resisted,
                "scraper_blocks": scraper_blocks,
                "rate_limit_blocks": rate_limit_blocks,
                "recent_events": recent_events[-10:],  # Last 10 events
                "scraper_detection_threshold": self.scraper_detection_threshold,
                "log_file": self.resistance_log_file
            }
            
        except Exception as e:
            return {
                "error": f"Failed to get resistance info: {str(e)}",
                "resistance_mode": self.resistance_mode
            }
    
    def halt_scraper(self, reason: str, metadata: Dict[str, Any]) -> ScraperHaltError:
        """
        Create a scraper halt error with comprehensive information.
        
        This method ensures scrapers halt safely without fabricated data.
        """
        error_message = self._get_user_facing_message(reason, metadata)
        
        return ScraperHaltError(
            message=error_message,
            error_type="platform_resistance",
            details={
                "halt_reason": reason,
                "halt_timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata,
                "user_facing_message": error_message,
                "scraper_guidance": "Halt scraping operations. No fabricated data will be provided.",
                "contact_info": "Contact support@sponsorscope.ai for legitimate access"
            }
        )
    
    def _get_user_facing_message(self, reason: str, metadata: Dict[str, Any]) -> str:
        """Generate appropriate user-facing messages based on resistance reason."""
        
        if "scraper" in reason.lower():
            return (
                "Access temporarily restricted due to automated activity detection. "
                "Please contact support@sponsorscope.ai for legitimate research access."
            )
        elif "rate limit" in reason.lower():
            return (
                "Rate limit exceeded. Please reduce request frequency or "
                "contact support@sponsorscope.ai for higher limits."
            )
        else:
            return (
                "Access restricted for security reasons. "
                "Contact support@sponsorscope.ai for assistance."
            )

# Global platform resistance instance
platform_resistance = PlatformResistance()