import time
import asyncio
from typing import Dict, Optional, Tuple
from collections import defaultdict, deque
import os
from datetime import datetime, timedelta
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class RateLimiter:
    """
    Rate limiting with sliding window and Redis support.
    Tracks requests per IP with configurable limits.
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.memory_store: Dict[str, deque] = defaultdict(deque)
        self._redis_connected = False
        
        # Configuration from environment
        self.requests_per_minute = int(os.getenv("RATE_LIMIT_RPM", "60"))
        self.requests_per_hour = int(os.getenv("RATE_LIMIT_RPH", "1000"))
        self.requests_per_day = int(os.getenv("RATE_LIMIT_RPD", "10000"))
        
        # Abuse detection thresholds
        self.rapid_resubmission_threshold = int(os.getenv("RAPID_RESUBMISSION_THRESHOLD", "5"))
        self.rapid_resubmission_window = int(os.getenv("RAPID_RESUBMISSION_WINDOW", "60"))  # seconds
        
        # Initialize Redis if available
        if REDIS_AVAILABLE:
            asyncio.create_task(self._init_redis())
    
    async def _init_redis(self):
        """Initialize Redis connection."""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            await self.redis_client.ping()
            self._redis_connected = True
            print("✅ Redis rate limiter connected")
        except Exception as e:
            print(f"⚠️  Redis connection failed, falling back to memory: {e}")
            self._redis_connected = False
    
    def _get_redis_key(self, ip: str, window: str) -> str:
        """Generate Redis key for rate limiting."""
        return f"rate_limit:{ip}:{window}"
    
    def _get_abuse_key(self, ip: str) -> str:
        """Generate Redis key for abuse detection."""
        return f"abuse_detection:{ip}"
    
    async def _check_memory_limit(self, ip: str, limit: int, window_seconds: int) -> Tuple[bool, int]:
        """Check rate limit using in-memory storage."""
        now = time.time()
        window_start = now - window_seconds
        
        # Clean old entries
        while self.memory_store[ip] and self.memory_store[ip][0] < window_start:
            self.memory_store[ip].popleft()
        
        # Check if limit exceeded
        current_requests = len(self.memory_store[ip])
        if current_requests >= limit:
            return False, limit - current_requests
        
        # Add current request
        self.memory_store[ip].append(now)
        return True, limit - current_requests - 1
    
    async def _check_redis_limit(self, ip: str, limit: int, window_seconds: int) -> Tuple[bool, int]:
        """Check rate limit using Redis."""
        if not self._redis_connected or not self.redis_client:
            return await self._check_memory_limit(ip, limit, window_seconds)
        
        try:
            key = self._get_redis_key(ip, f"{window_seconds}s")
            now = time.time()
            window_start = now - window_seconds
            
            # Remove old entries
            await self.redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count current entries
            current_requests = await self.redis_client.zcard(key)
            
            if current_requests >= limit:
                return False, limit - current_requests
            
            # Add current request
            await self.redis_client.zadd(key, {str(now): now})
            await self.redis_client.expire(key, window_seconds)
            
            return True, limit - current_requests - 1
            
        except Exception as e:
            print(f"Redis error, falling back to memory: {e}")
            return await self._check_memory_limit(ip, limit, window_seconds)
    
    async def check_rate_limit(self, ip: str) -> Tuple[bool, Dict[str, int]]:
        """
        Check all rate limits for an IP.
        Returns (is_allowed, remaining_counts)
        """
        # Check minute limit
        allowed_minute, remaining_minute = await self._check_redis_limit(
            ip, self.requests_per_minute, 60
        )
        
        # Check hour limit
        allowed_hour, remaining_hour = await self._check_redis_limit(
            ip, self.requests_per_hour, 3600
        )
        
        # Check day limit
        allowed_day, remaining_day = await self._check_redis_limit(
            ip, self.requests_per_day, 86400
        )
        
        is_allowed = allowed_minute and allowed_hour and allowed_day
        
        remaining_counts = {
            "minute": remaining_minute,
            "hour": remaining_hour,
            "day": remaining_day
        }
        
        return is_allowed, remaining_counts
    
    async def detect_abuse(self, ip: str, endpoint: str, handle: str = None) -> Tuple[bool, str]:
        """
        Detect abusive behavior patterns.
        Returns (is_abusive, reason)
        """
        if not self._redis_connected or not self.redis_client:
            return False, ""
        
        try:
            abuse_key = self._get_abuse_key(ip)
            now = time.time()
            
            # Check rapid resubmissions
            if handle:
                handle_key = f"{abuse_key}:handle:{handle}"
                recent_submissions = await self.redis_client.zcount(
                    handle_key, now - self.rapid_resubmission_window, now
                )
                
                if recent_submissions >= self.rapid_resubmission_threshold:
                    return True, f"Rapid resubmission detected ({recent_submissions} attempts)"
                
                # Record this submission
                await self.redis_client.zadd(handle_key, {str(now): now})
                await self.redis_client.expire(handle_key, self.rapid_resubmission_window)
            
            # Check for suspicious proxy patterns (simple heuristics)
            # This could be expanded with more sophisticated detection
            
            return False, ""
            
        except Exception as e:
            print(f"Abuse detection error: {e}")
            return False, ""
    
    async def get_rate_limit_info(self, ip: str) -> Dict[str, any]:
        """Get current rate limit status for an IP."""
        is_allowed, remaining = await self.check_rate_limit(ip)
        
        return {
            "allowed": is_allowed,
            "remaining": remaining,
            "limits": {
                "minute": self.requests_per_minute,
                "hour": self.requests_per_hour,
                "day": self.requests_per_day
            }
        }

# Global rate limiter instance
rate_limiter = RateLimiter()