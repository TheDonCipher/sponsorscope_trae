"""
Enhanced Governance Middleware with Platform Resistance

Integrates platform resistance layer with existing governance middleware.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import time
import traceback
from services.governance.core.enhanced_killswitch import enhanced_killswitch
from services.governance.core.rate_limiter import rate_limiter
from services.governance.core.token_manager import token_manager
from services.governance.core.platform_resistance import platform_resistance, ScraperHaltError
from services.governance.core.resistance_logger import resistance_logger, ResistanceEventType
from services.api.models.report import ReportResponse

class EnhancedGovernanceMiddleware:
    """
    Enhanced FastAPI middleware that integrates platform resistance
    with existing governance layer.
    """
    
    def __init__(self):
        self.enabled = True
        self.platform_resistance_enabled = True
    
    async def __call__(self, request: Request, call_next):
        """Process request through enhanced governance layer with platform resistance."""
        if not self.enabled:
            return await call_next(request)
        
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        path = request.url.path
        method = request.method
        
        # Collect request data for platform resistance evaluation
        request_data = await self._collect_request_data(request, client_ip)
        
        try:
            # 1. Platform Resistance Evaluation (NEW)
            if self.platform_resistance_enabled:
                should_halt, resistance_reason, resistance_metadata = await platform_resistance.evaluate_request(request_data)
                
                if should_halt:
                    # Log the resistance event
                    resistance_logger.log_resistance_event(
                        ResistanceEventType.RESISTANCE_TRIGGERED,
                        client_ip,
                        path,
                        resistance_reason,
                        resistance_metadata,
                        request_data
                    )
                    
                    # Create scraper halt error
                    halt_error = platform_resistance.halt_scraper(resistance_reason, resistance_metadata)
                    
                    return self._create_resistance_response(halt_error, client_ip)
            
            # 2. Kill Switch Check (existing)
            killswitch_result = await self._check_killswitch(request, path)
            if killswitch_result["blocked"]:
                return self._create_killswitch_response(killswitch_result["reason"])
            
            # 3. Rate Limiting for API endpoints (existing)
            if path.startswith("/api/"):
                rate_limit_result = await self._check_rate_limit(client_ip, path)
                if rate_limit_result["blocked"]:
                    # Enhanced logging for rate limit violations
                    resistance_logger.log_resistance_event(
                        ResistanceEventType.RATE_LIMIT_EXCEEDED,
                        client_ip,
                        path,
                        "Rate limit exceeded",
                        rate_limit_result.get("metadata", {}),
                        request_data
                    )
                    return self._create_rate_limit_response(rate_limit_result)
            
            # 4. Abuse Detection (existing)
            abuse_result = await self._check_abuse(client_ip, request)
            if abuse_result["blocked"]:
                resistance_logger.log_resistance_event(
                    ResistanceEventType.ABUSE_DETECTED,
                    client_ip,
                    path,
                    abuse_result["reason"],
                    abuse_result.get("metadata", {}),
                    request_data
                )
                return self._create_abuse_response(abuse_result["reason"])
            
            # 5. Token Management for analysis endpoints (existing)
            if path == "/api/analyze":
                token_result = await self._check_token_availability()
                if token_result["blocked"]:
                    return self._create_token_limit_response(token_result["reason"])
            
            # Log legitimate access for tuning
            resistance_logger.log_legitimate_access(
                client_ip,
                path,
                "Request passed all resistance checks",
                {
                    "user_agent": request_data.get("user_agent"),
                    "scraper_score": request_data.get("scraper_score", 0),
                    "resistance_mode": "moderate"
                }
            )
            
            # Process request
            response = await call_next(request)
            
            # Add governance headers
            response = self._add_governance_headers(response, client_ip, start_time)
            
            return response
            
        except ScraperHaltError as e:
            # Handle scraper halt errors specifically
            resistance_logger.log_error_trace(client_ip, path, e, {"error_type": "scraper_halt"})
            return self._create_resistance_response(e, client_ip)
            
        except Exception as e:
            # Log unexpected errors
            error_trace = traceback.format_exc()
            resistance_logger.log_error_trace(client_ip, path, e, {
                "error_type": "unexpected",
                "traceback": error_trace
            })
            
            # Log evaluation error for resistance system
            resistance_logger.log_resistance_event(
                ResistanceEventType.EVALUATION_ERROR,
                client_ip,
                path,
                f"Middleware error: {str(e)}",
                {"error": str(e), "traceback": error_trace},
                request_data
            )
            
            # Fail open - allow request to proceed on middleware errors
            print(f"Governance middleware error: {e}")
            return await call_next(request)
    
    async def _collect_request_data(self, request: Request, client_ip: str) -> Dict[str, Any]:
        """Collect comprehensive request data for platform resistance evaluation."""
        request_data = {
            "client_ip": client_ip,
            "user_agent": request.headers.get("user-agent", ""),
            "endpoint": request.url.path,
            "method": request.method,
            "headers": dict(request.headers),
            "timestamp": time.time()
        }
        
        # Extract handle if available
        if request.url.path == "/api/analyze":
            try:
                body = await request.json()
                request_data["handle"] = body.get("handle", "")
            except:
                request_data["handle"] = ""
        elif request.url.path.startswith("/api/report/"):
            request_data["handle"] = request.url.path.split("/")[-1]
        
        return request_data
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        if request.client:
            return request.client.host
        
        return "unknown"
    
    async def _check_killswitch(self, request: Request, path: str) -> Dict[str, Any]:
        """Check killswitch status."""
        if not await enhanced_killswitch.is_read_enabled():
            return {"blocked": True, "reason": enhanced_killswitch.get_maintenance_message()}
        
        if path in ["/api/analyze", "/api/report"] and not await enhanced_killswitch.is_scan_enabled():
            return {"blocked": True, "reason": enhanced_killswitch.get_maintenance_message()}
        
        return {"blocked": False, "reason": ""}
    
    async def _check_rate_limit(self, ip: str, path: str) -> Dict[str, Any]:
        """Check rate limits."""
        is_allowed, remaining = await rate_limiter.check_rate_limit(ip)
        
        if not is_allowed:
            return {
                "blocked": True,
                "reason": "Rate limit exceeded",
                "metadata": {"remaining_counts": remaining}
            }
        
        return {"blocked": False, "remaining": remaining}
    
    async def _check_abuse(self, ip: str, request: Request) -> Dict[str, Any]:
        """Check for abusive behavior."""
        path = request.url.path
        
        handle = None
        if path == "/api/analyze":
            try:
                body = await request.json()
                handle = body.get("handle")
            except:
                pass
        elif path.startswith("/api/report/"):
            handle = path.split("/")[-1]
        
        is_abusive, reason = await rate_limiter.detect_abuse(ip, path, handle)
        
        if is_abusive:
            return {"blocked": True, "reason": reason, "metadata": {"abuse_type": "detected"}}
        
        return {"blocked": False, "reason": ""}
    
    async def _check_token_availability(self) -> Dict[str, Any]:
        """Check token availability for analysis."""
        estimated_tokens = 5000
        is_allowed, reason = await token_manager.check_token_availability(estimated_tokens)
        
        if not is_allowed:
            return {"blocked": True, "reason": reason}
        
        return {"blocked": False, "reason": ""}
    
    def _create_resistance_response(self, halt_error: ScraperHaltError, client_ip: str) -> JSONResponse:
        """Create response for platform resistance halt."""
        return JSONResponse(
            status_code=403,
            content={
                "error": "Access restricted",
                "message": halt_error.message,
                "type": "platform_resistance",
                "details": {
                    "halt_reason": halt_error.details.get("halt_reason"),
                    "halt_timestamp": halt_error.details.get("halt_timestamp"),
                    "scraper_guidance": halt_error.details.get("scraper_guidance"),
                    "contact_info": halt_error.details.get("contact_info"),
                    "client_ip": client_ip
                },
                "user_facing_message": halt_error.message,
                "data_integrity_verdict": "No fabricated data provided - scraper halted safely"
            },
            headers={
                "X-Resistance-Action": "platform_block",
                "X-Resistance-Reason": halt_error.details.get("halt_reason", "unknown"),
                "Retry-After": "3600"  # 1 hour
            }
        )
    
    def _create_killswitch_response(self, reason: str) -> JSONResponse:
        """Create response for killswitch block."""
        return JSONResponse(
            status_code=503,
            content={
                "error": "Service temporarily unavailable",
                "message": reason,
                "type": "maintenance"
            },
            headers={
                "Retry-After": "3600",
                "X-Governance-Action": "killswitch"
            }
        )
    
    def _create_rate_limit_response(self, rate_info: Dict[str, Any]) -> JSONResponse:
        """Create response for rate limit."""
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
                "remaining": rate_info.get("remaining", {}),
                "type": "rate_limit",
                "user_facing_message": "Rate limit exceeded. Please reduce request frequency."
            },
            headers={
                "Retry-After": "60",
                "X-Governance-Action": "rate_limit"
            }
        )
    
    def _create_abuse_response(self, reason: str) -> JSONResponse:
        """Create response for abuse detection."""
        return JSONResponse(
            status_code=403,
            content={
                "error": "Request blocked",
                "message": reason,
                "type": "abuse_detection",
                "user_facing_message": "Request blocked due to suspicious activity."
            },
            headers={
                "X-Governance-Action": "abuse_block"
            }
        )
    
    def _create_token_limit_response(self, reason: str) -> JSONResponse:
        """Create response for token limit."""
        return JSONResponse(
            status_code=503,
            content={
                "error": "Service temporarily unavailable",
                "message": reason,
                "type": "token_limit",
                "user_facing_message": "Service temporarily unavailable due to resource constraints."
            },
            headers={
                "Retry-After": "3600",
                "X-Governance-Action": "token_limit"
            }
        )
    
    def _add_governance_headers(self, response, client_ip: str, start_time: float) -> any:
        """Add governance information headers."""
        processing_time = time.time() - start_time
        
        response.headers["X-Governance-IP"] = client_ip
        response.headers["X-Governance-Time"] = f"{processing_time:.3f}s"
        response.headers["X-Governance-Status"] = "active"
        response.headers["X-Platform-Resistance"] = "enabled"
        
        return response

# Create enhanced middleware instance
enhanced_governance_middleware = EnhancedGovernanceMiddleware()