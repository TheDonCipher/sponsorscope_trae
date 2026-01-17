import os
import asyncio
from typing import Optional, List, Dict, Any
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class EnhancedKillSwitch:
    """
    Enhanced KillSwitch with Redis support and system notices.
    Provides centralized control for system-wide operations with persistence.
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._redis_connected = False
        self._system_notices: List[str] = []
        
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
            print("✅ Redis killswitch connected")
        except Exception as e:
            print(f"⚠️  Redis connection failed for killswitch: {e}")
            self._redis_connected = False
    
    def _get_redis_key(self, component: str) -> str:
        """Generate Redis key for killswitch state."""
        return f"killswitch:{component}"
    
    def _get_notice_key(self) -> str:
        """Generate Redis key for system notices."""
        return "killswitch:system_notices"
    
    async def is_scan_enabled(self) -> bool:
        """
        If True, new scans are allowed.
        If False, system rejects new scan requests (HTTP 503).
        """
        if self._redis_connected and self.redis_client:
            try:
                redis_state = await self.redis_client.get(self._get_redis_key("scans"))
                if redis_state is not None:
                    return redis_state.lower() == "enabled"
            except Exception as e:
                print(f"Redis killswitch error for scans: {e}")
        
        # Fall back to environment variable
        return os.getenv("KILL_SWITCH_SCANS", "enabled").lower() == "enabled"
    
    async def is_read_enabled(self) -> bool:
        """
        If True, cached reports are readable.
        If False, entire system is down (Maintenance Mode).
        """
        if self._redis_connected and self.redis_client:
            try:
                redis_state = await self.redis_client.get(self._get_redis_key("read"))
                if redis_state is not None:
                    return redis_state.lower() == "enabled"
            except Exception as e:
                print(f"Redis killswitch error for read: {e}")
        
        # Fall back to environment variable
        return os.getenv("KILL_SWITCH_READ", "enabled").lower() == "enabled"
    
    async def set_scan_enabled(self, enabled: bool) -> bool:
        """Set scan killswitch state."""
        state = "enabled" if enabled else "disabled"
        
        if self._redis_connected and self.redis_client:
            try:
                await self.redis_client.set(self._get_redis_key("scans"), state)
                return True
            except Exception as e:
                print(f"Redis killswitch set error for scans: {e}")
        
        return False
    
    async def set_read_enabled(self, enabled: bool) -> bool:
        """Set read killswitch state."""
        state = "enabled" if enabled else "disabled"
        
        if self._redis_connected and self.redis_client:
            try:
                await self.redis_client.set(self._get_redis_key("read"), state)
                return True
            except Exception as e:
                print(f"Redis killswitch set error for read: {e}")
        
        return False
    
    def get_maintenance_message(self) -> str:
        """Get maintenance message."""
        return os.getenv("MAINTENANCE_MESSAGE", "SponsorScope is currently undergoing scheduled maintenance.")
    
    async def add_system_notice(self, notice: str) -> bool:
        """Add a system-wide notice."""
        if self._redis_connected and self.redis_client:
            try:
                await self.redis_client.lpush(self._get_notice_key(), notice)
                # Keep only recent 10 notices
                await self.redis_client.ltrim(self._get_notice_key(), 0, 9)
                return True
            except Exception as e:
                print(f"Redis system notice error: {e}")
        
        # Fall back to memory
        self._system_notices.append(notice)
        # Keep only recent 10 notices
        if len(self._system_notices) > 10:
            self._system_notices = self._system_notices[-10:]
        return True
    
    async def get_system_notices(self) -> List[str]:
        """Get current system notices."""
        if self._redis_connected and self.redis_client:
            try:
                notices = await self.redis_client.lrange(self._get_notice_key(), 0, -1)
                return [notice for notice in notices if notice]
            except Exception as e:
                print(f"Redis system notices error: {e}")
        
        # Fall back to memory
        return self._system_notices.copy()
    
    async def clear_system_notices(self) -> bool:
        """Clear all system notices."""
        if self._redis_connected and self.redis_client:
            try:
                await self.redis_client.delete(self._get_notice_key())
                return True
            except Exception as e:
                print(f"Redis clear notices error: {e}")
        
        # Fall back to memory
        self._system_notices.clear()
        return True
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive killswitch status."""
        scans_enabled = await self.is_scan_enabled()
        read_enabled = await self.is_read_enabled()
        notices = await self.get_system_notices()
        
        return {
            "scans_enabled": scans_enabled,
            "read_enabled": read_enabled,
            "maintenance_message": self.get_maintenance_message(),
            "system_notices": notices,
            "redis_connected": self._redis_connected
        }

# Global enhanced killswitch instance
enhanced_killswitch = EnhancedKillSwitch()