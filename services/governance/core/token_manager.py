import os
import time
import asyncio
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class TokenManager:
    """
    Manages LLM token usage and daily spend caps.
    Tracks usage across different time windows and enforces limits.
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._redis_connected = False
        
        # Configuration from environment
        self.daily_token_limit = int(os.getenv("DAILY_TOKEN_LIMIT", "1000000"))  # 1M tokens default
        self.daily_spend_limit = float(os.getenv("DAILY_SPEND_LIMIT", "100.0"))  # $100 default
        self.token_cost_per_1k = float(os.getenv("TOKEN_COST_PER_1K", "0.01"))  # $0.01 per 1K tokens
        
        # Cost tracking for different models (approximate)
        self.model_costs = {
            "gpt-4": 0.03,  # $0.03 per 1K tokens
            "gpt-3.5-turbo": 0.001,  # $0.001 per 1K tokens
            "claude": 0.008,  # $0.008 per 1K tokens
        }
        
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
            print("✅ Redis token manager connected")
        except Exception as e:
            print(f"⚠️  Redis connection failed for token manager: {e}")
            self._redis_connected = False
    
    def _get_daily_key(self, date: str = None) -> str:
        """Generate Redis key for daily usage."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        return f"token_usage:{date}"
    
    def _get_spend_key(self, date: str = None) -> str:
        """Generate Redis key for daily spend."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        return f"spend_usage:{date}"
    
    async def check_token_availability(self, requested_tokens: int, model: str = "gpt-3.5-turbo") -> Tuple[bool, str]:
        """
        Check if token usage is within limits.
        Returns (is_allowed, reason)
        """
        if not self._redis_connected or not self.redis_client:
            return True, ""
        
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            daily_key = self._get_daily_key(today)
            spend_key = self._get_spend_key(today)
            
            # Get current usage
            current_tokens = int(await self.redis_client.get(daily_key) or 0)
            current_spend = float(await self.redis_client.get(spend_key) or 0.0)
            
            # Calculate cost for requested tokens
            model_cost_per_1k = self.model_costs.get(model, self.token_cost_per_1k)
            requested_cost = (requested_tokens / 1000) * model_cost_per_1k
            
            # Check token limit
            if current_tokens + requested_tokens > self.daily_token_limit:
                return False, f"Daily token limit exceeded ({self.daily_token_limit:,} tokens)"
            
            # Check spend limit
            if current_spend + requested_cost > self.daily_spend_limit:
                return False, f"Daily spend limit exceeded (${self.daily_spend_limit:.2f})"
            
            return True, ""
            
        except Exception as e:
            print(f"Token availability check error: {e}")
            return True, ""
    
    async def consume_tokens(self, tokens: int, model: str = "gpt-3.5-turbo") -> bool:
        """
        Consume tokens and update usage tracking.
        Returns success status.
        """
        if not self._redis_connected or not self.redis_client:
            return True
        
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            daily_key = self._get_daily_key(today)
            spend_key = self._get_spend_key(today)
            
            # Calculate cost
            model_cost_per_1k = self.model_costs.get(model, self.token_cost_per_1k)
            cost = (tokens / 1000) * model_cost_per_1k
            
            # Update usage atomically
            pipe = self.redis_client.pipeline()
            pipe.incrby(daily_key, tokens)
            pipe.incrbyfloat(spend_key, cost)
            pipe.expire(daily_key, 86400)  # 24 hours
            pipe.expire(spend_key, 86400)
            
            results = await pipe.execute()
            
            new_token_total = results[0]
            new_spend_total = results[1]
            
            # Log usage
            print(f"Token usage: {tokens:,} tokens (${cost:.4f}) | "
                  f"Daily total: {new_token_total:,} tokens (${new_spend_total:.2f})")
            
            return True
            
        except Exception as e:
            print(f"Token consumption error: {e}")
            return False
    
    async def get_usage_stats(self, date: str = None) -> Dict[str, any]:
        """Get current usage statistics."""
        if not self._redis_connected or not self.redis_client:
            return {
                "tokens_used": 0,
                "spend_used": 0.0,
                "tokens_remaining": self.daily_token_limit,
                "spend_remaining": self.daily_spend_limit,
                "percentage_used": 0.0
            }
        
        try:
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")
            
            daily_key = self._get_daily_key(date)
            spend_key = self._get_spend_key(date)
            
            tokens_used = int(await self.redis_client.get(daily_key) or 0)
            spend_used = float(await self.redis_client.get(spend_key) or 0.0)
            
            return {
                "tokens_used": tokens_used,
                "spend_used": spend_used,
                "tokens_remaining": max(0, self.daily_token_limit - tokens_used),
                "spend_remaining": max(0.0, self.daily_spend_limit - spend_used),
                "percentage_used": (tokens_used / self.daily_token_limit) * 100 if self.daily_token_limit > 0 else 0
            }
            
        except Exception as e:
            print(f"Usage stats error: {e}")
            return {
                "tokens_used": 0,
                "spend_used": 0.0,
                "tokens_remaining": self.daily_token_limit,
                "spend_remaining": self.daily_spend_limit,
                "percentage_used": 0.0
            }
    
    async def reset_daily_usage(self, date: str = None) -> bool:
        """Reset daily usage counters."""
        if not self._redis_connected or not self.redis_client:
            return False
        
        try:
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")
            
            daily_key = self._get_daily_key(date)
            spend_key = self._get_spend_key(date)
            
            await self.redis_client.delete(daily_key, spend_key)
            return True
            
        except Exception as e:
            print(f"Daily reset error: {e}")
            return False

# Global token manager instance
token_manager = TokenManager()