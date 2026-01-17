"""
Graceful Degradation System for SponsorScope
Handles system overload scenarios with transparent fallback mechanisms
"""

import asyncio
import time
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from services.governance.core.token_manager import token_manager
from services.governance.core.rate_limiter import rate_limiter

class DegradationLevel(Enum):
    NORMAL = "normal"
    CAUTION = "caution"      # 70% capacity
    WARNING = "warning"      # 85% capacity  
    CRITICAL = "critical"    # 95% capacity
    EMERGENCY = "emergency"  # 100% capacity

@dataclass
class DegradationConfig:
    level: DegradationLevel
    token_limit_multiplier: float
    rate_limit_multiplier: float
    cache_ttl_extension: int
    analysis_depth_reduction: float
    evidence_quality_threshold: float
    enable_batch_processing: bool
    enable_circuit_breaker: bool

class GracefulDegradationManager:
    """
    Manages system degradation under load with transparent fallbacks.
    """
    
    def __init__(self):
        self.current_level = DegradationLevel.NORMAL
        self.configs = self._initialize_configs()
        self.circuit_breakers = {}
        self.cache_store = {}
        self.last_degradation_check = time.time()
        self.degradation_check_interval = 30  # seconds
        
        # Performance metrics
        self.request_counts = {
            "total": 0,
            "blocked": 0,
            "degraded": 0,
            "normal": 0
        }
        
        # System health indicators
        self.health_metrics = {
            "avg_response_time": 0.0,
            "error_rate": 0.0,
            "token_usage_percentage": 0.0,
            "rate_limit_usage_percentage": 0.0
        }
    
    def _initialize_configs(self) -> Dict[DegradationLevel, DegradationConfig]:
        """Initialize degradation configurations for each level."""
        return {
            DegradationLevel.NORMAL: DegradationConfig(
                level=DegradationLevel.NORMAL,
                token_limit_multiplier=1.0,
                rate_limit_multiplier=1.0,
                cache_ttl_extension=1,
                analysis_depth_reduction=1.0,
                evidence_quality_threshold=0.7,
                enable_batch_processing=False,
                enable_circuit_breaker=False
            ),
            DegradationLevel.CAUTION: DegradationConfig(
                level=DegradationLevel.CAUTION,
                token_limit_multiplier=0.9,
                rate_limit_multiplier=0.95,
                cache_ttl_extension=2,
                analysis_depth_reduction=0.9,
                evidence_quality_threshold=0.65,
                enable_batch_processing=True,
                enable_circuit_breaker=False
            ),
            DegradationLevel.WARNING: DegradationConfig(
                level=DegradationLevel.WARNING,
                token_limit_multiplier=0.7,
                rate_limit_multiplier=0.8,
                cache_ttl_extension=4,
                analysis_depth_reduction=0.7,
                evidence_quality_threshold=0.6,
                enable_batch_processing=True,
                enable_circuit_breaker=True
            ),
            DegradationLevel.CRITICAL: DegradationConfig(
                level=DegradationLevel.CRITICAL,
                token_limit_multiplier=0.5,
                rate_limit_multiplier=0.6,
                cache_ttl_extension=8,
                analysis_depth_reduction=0.5,
                evidence_quality_threshold=0.5,
                enable_batch_processing=True,
                enable_circuit_breaker=True
            ),
            DegradationLevel.EMERGENCY: DegradationConfig(
                level=DegradationLevel.EMERGENCY,
                token_limit_multiplier=0.3,
                rate_limit_multiplier=0.4,
                cache_ttl_extension=16,
                analysis_depth_reduction=0.3,
                evidence_quality_threshold=0.4,
                enable_batch_processing=True,
                enable_circuit_breaker=True
            )
        }
    
    async def check_system_health(self) -> Dict[str, Any]:
        """Check current system health and update degradation level."""
        current_time = time.time()
        
        # Only check every 30 seconds to avoid overhead
        if current_time - self.last_degradation_check < self.degradation_check_interval:
            return self._get_current_health_status()
        
        self.last_degradation_check = current_time
        
        try:
            # Get token usage
            token_stats = await token_manager.get_usage_stats()
            token_usage_percentage = token_stats.get("percentage_used", 0)
            
            # Get rate limit usage (sample from recent activity)
            # This would need to be implemented based on your rate limiting store
            rate_limit_usage_percentage = await self._estimate_rate_limit_usage()
            
            # Calculate system health metrics
            self.health_metrics.update({
                "token_usage_percentage": token_usage_percentage,
                "rate_limit_usage_percentage": rate_limit_usage_percentage,
                "avg_response_time": await self._calculate_avg_response_time(),
                "error_rate": await self._calculate_error_rate()
            })
            
            # Determine degradation level based on health metrics
            await self._update_degradation_level()
            
        except Exception as e:
            print(f"Health check error: {e}")
            # In case of error, move to caution level
            self.current_level = DegradationLevel.CAUTION
        
        return self._get_current_health_status()
    
    async def _estimate_rate_limit_usage(self) -> float:
        """Estimate current rate limit usage percentage."""
        # This is a simplified estimation
        # In a real implementation, you'd query your rate limiting store
        return min(100.0, (self.request_counts["total"] / 1000) * 10)  # Rough estimate
    
    async def _calculate_avg_response_time(self) -> float:
        """Calculate average response time from recent requests."""
        # This would integrate with your monitoring system
        # For now, return a placeholder
        return self.health_metrics.get("avg_response_time", 0.5)
    
    async def _calculate_error_rate(self) -> float:
        """Calculate error rate from recent requests."""
        total = self.request_counts["total"]
        if total == 0:
            return 0.0
        return (self.request_counts["blocked"] / total) * 100
    
    async def _update_degradation_level(self):
        """Update degradation level based on health metrics."""
        metrics = self.health_metrics
        
        # Determine level based on multiple factors
        if (metrics["token_usage_percentage"] >= 95 or 
            metrics["rate_limit_usage_percentage"] >= 95 or
            metrics["error_rate"] >= 50):
            self.current_level = DegradationLevel.EMERGENCY
        elif (metrics["token_usage_percentage"] >= 85 or 
              metrics["rate_limit_usage_percentage"] >= 85 or
              metrics["error_rate"] >= 25):
            self.current_level = DegradationLevel.CRITICAL
        elif (metrics["token_usage_percentage"] >= 70 or 
              metrics["rate_limit_usage_percentage"] >= 70 or
              metrics["error_rate"] >= 10):
            self.current_level = DegradationLevel.WARNING
        elif (metrics["token_usage_percentage"] >= 50 or 
              metrics["rate_limit_usage_percentage"] >= 50 or
              metrics["error_rate"] >= 5):
            self.current_level = DegradationLevel.CAUTION
        else:
            self.current_level = DegradationLevel.NORMAL
    
    def _get_current_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        return {
            "level": self.current_level.value,
            "metrics": self.health_metrics.copy(),
            "request_counts": self.request_counts.copy(),
            "config": self._get_current_config()
        }
    
    def _get_current_config(self) -> DegradationConfig:
        """Get current degradation configuration."""
        return self.configs[self.current_level]
    
    async def process_request(self, request_type: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request with appropriate degradation level."""
        self.request_counts["total"] += 1
        
        # Check system health first
        health_status = await self.check_system_health()
        current_config = self._get_current_config()
        
        # Apply degradation based on request type
        if request_type == "analysis":
            return await self._process_analysis_request(request_data, current_config)
        elif request_type == "report":
            return await self._process_report_request(request_data, current_config)
        elif request_type == "health":
            return await self._process_health_request(request_data, current_config)
        else:
            return await self._process_generic_request(request_data, current_config)
    
    async def _process_analysis_request(self, request_data: Dict[str, Any], config: DegradationConfig) -> Dict[str, Any]:
        """Process analysis request with degradation."""
        
        # Check circuit breaker
        if config.enable_circuit_breaker and self._is_circuit_open("analysis"):
            self.request_counts["blocked"] += 1
            return {
                "status": "degraded",
                "action": "circuit_breaker",
                "message": "Analysis service temporarily unavailable due to high load",
                "fallback": self._get_analysis_fallback(request_data)
            }
        
        # Check token availability with degradation multiplier
        estimated_tokens = self._estimate_analysis_tokens(request_data)
        adjusted_token_limit = int(estimated_tokens * config.token_limit_multiplier)
        
        is_allowed, reason = await token_manager.check_token_availability(adjusted_token_limit)
        if not is_allowed:
            self.request_counts["degraded"] += 1
            return {
                "status": "degraded",
                "action": "token_limit",
                "message": reason,
                "fallback": self._get_analysis_fallback(request_data),
                "reduced_tokens": adjusted_token_limit
            }
        
        # Apply analysis depth reduction
        if config.analysis_depth_reduction < 1.0:
            request_data["analysis_depth"] = config.analysis_depth_reduction
            request_data["evidence_quality_threshold"] = config.evidence_quality_threshold
        
        self.request_counts["normal"] += 1
        return {
            "status": "normal",
            "action": "processed",
            "message": "Request processed normally",
            "config_applied": {
                "analysis_depth_reduction": config.analysis_depth_reduction,
                "evidence_quality_threshold": config.evidence_quality_threshold
            }
        }
    
    async def _process_report_request(self, request_data: Dict[str, Any], config: DegradationConfig) -> Dict[str, Any]:
        """Process report request with degradation."""
        
        # Check cache first with extended TTL
        cache_key = self._generate_cache_key("report", request_data)
        cached_result = self._get_from_cache(cache_key, config.cache_ttl_extension)
        if cached_result:
            return {
                "status": "cached",
                "action": "cache_hit",
                "message": "Report served from cache",
                "data": cached_result
            }
        
        # Apply degradation if needed
        if config.analysis_depth_reduction < 1.0:
            self.request_counts["degraded"] += 1
            return {
                "status": "degraded",
                "action": "reduced_quality",
                "message": "Report generated with reduced analysis depth",
                "reduction_factor": config.analysis_depth_reduction
            }
        
        self.request_counts["normal"] += 1
        return {
            "status": "normal",
            "action": "processed",
            "message": "Report processed normally"
        }
    
    async def _process_health_request(self, request_data: Dict[str, Any], config: DegradationConfig) -> Dict[str, Any]:
        """Process health check request."""
        # Health checks should always work, even in emergency mode
        health_status = await self.check_system_health()
        return {
            "status": "normal",
            "action": "health_check",
            "message": "System health status",
            "health": health_status
        }
    
    async def _process_generic_request(self, request_data: Dict[str, Any], config: DegradationConfig) -> Dict[str, Any]:
        """Process generic request with basic degradation."""
        if config.rate_limit_multiplier < 1.0:
            # Apply rate limiting degradation
            self.request_counts["degraded"] += 1
            return {
                "status": "degraded",
                "action": "rate_limited",
                "message": "Request processed with reduced rate limits",
                "rate_limit_multiplier": config.rate_limit_multiplier
            }
        
        self.request_counts["normal"] += 1
        return {
            "status": "normal",
            "action": "processed",
            "message": "Request processed normally"
        }
    
    def _is_circuit_open(self, service: str) -> bool:
        """Check if circuit breaker is open for a service."""
        if service not in self.circuit_breakers:
            return False
        
        circuit = self.circuit_breakers[service]
        if circuit["state"] == "open":
            # Check if we should attempt to close it
            if time.time() - circuit["last_failure"] > 60:  # 1 minute timeout
                circuit["state"] = "half_open"
                return False
            return True
        
        return False
    
    def _open_circuit(self, service: str):
        """Open circuit breaker for a service."""
        self.circuit_breakers[service] = {
            "state": "open",
            "last_failure": time.time(),
            "failure_count": 0
        }
    
    def _get_analysis_fallback(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get fallback response for analysis requests."""
        return {
            "status": "fallback",
            "confidence": 0.5,
            "authenticity_score": 0.5,
            "message": "Analysis unavailable - system under high load",
            "recommendation": "Please try again later",
            "evidence": [],
            "degraded": True
        }
    
    def _estimate_analysis_tokens(self, request_data: Dict[str, Any]) -> int:
        """Estimate token usage for analysis request."""
        base_tokens = 1000
        if request_data.get("deep_analysis"):
            base_tokens *= 3
        if request_data.get("include_evidence"):
            base_tokens *= 2
        return base_tokens
    
    def _generate_cache_key(self, request_type: str, request_data: Dict[str, Any]) -> str:
        """Generate cache key for request."""
        key_data = f"{request_type}:{json.dumps(request_data, sort_keys=True)}"
        return f"degradation_cache:{hash(key_data)}"
    
    def _get_from_cache(self, cache_key: str, ttl_extension: int) -> Optional[Dict[str, Any]]:
        """Get data from cache with TTL extension."""
        if cache_key not in self.cache_store:
            return None
        
        cached_data = self.cache_store[cache_key]
        if time.time() - cached_data["timestamp"] > (300 * ttl_extension):  # 5 min base * extension
            del self.cache_store[cache_key]
            return None
        
        return cached_data["data"]
    
    def _store_in_cache(self, cache_key: str, data: Dict[str, Any]):
        """Store data in cache."""
        self.cache_store[cache_key] = {
            "data": data,
            "timestamp": time.time()
        }
    
    def get_degradation_summary(self) -> Dict[str, Any]:
        """Get summary of current degradation status."""
        return {
            "current_level": self.current_level.value,
            "health_metrics": self.health_metrics.copy(),
            "request_counts": self.request_counts.copy(),
            "circuit_breakers": self.circuit_breakers.copy(),
            "cache_size": len(self.cache_store),
            "timestamp": datetime.now().isoformat()
        }

# Global degradation manager instance
degradation_manager = GracefulDegradationManager()