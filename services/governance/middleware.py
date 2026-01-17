from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import time
from services.governance.core.enhanced_killswitch import enhanced_killswitch
from services.governance.core.rate_limiter import rate_limiter
from services.governance.core.token_manager import token_manager
from services.api.models.report import ReportResponse

class GovernanceMiddleware:
    """
    FastAPI middleware for governance layer.
    Handles rate limiting, abuse detection, killswitch, and token management.
    """
    
    def __init__(self):
        self.enabled = True
    
    async def __call__(self, request: Request, call_next):
        """Process request through governance layer."""
        if not self.enabled:
            return await call_next(request)
        
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        path = request.url.path
        method = request.method
        
        try:
            # 1. Kill Switch Check
            killswitch_result = await self._check_killswitch(request, path)
            if killswitch_result["blocked"]:
                return self._create_killswitch_response(killswitch_result["reason"])
            
            # 2. Rate Limiting for API endpoints
            if path.startswith("/api/"):
                rate_limit_result = await self._check_rate_limit(client_ip, path)
                if rate_limit_result["blocked"]:
                    return self._create_rate_limit_response(rate_limit_result)
            
            # 3. Abuse Detection
            abuse_result = await self._check_abuse(client_ip, request)
            if abuse_result["blocked"]:
                return self._create_abuse_response(abuse_result["reason"])
            
            # 4. Token Management for analysis endpoints
            if path == "/api/analyze":
                token_result = await self._check_token_availability()
                if token_result["blocked"]:
                    return self._create_token_limit_response(token_result["reason"])
            
            # Process request
            response = await call_next(request)
            
            # Add governance headers
            response = self._add_governance_headers(response, client_ip, start_time)
            
            return response
            
        except Exception as e:
            print(f"Governance middleware error: {e}")
            return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Check for forwarded headers first
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection
        if request.client:
            return request.client.host
        
        return "unknown"
    
    async def _check_killswitch(self, request: Request, path: str) -> Dict[str, Any]:
        """Check killswitch status."""
        # Check read killswitch (affects all endpoints)
        if not await enhanced_killswitch.is_read_enabled():
            return {"blocked": True, "reason": enhanced_killswitch.get_maintenance_message()}
        
        # Check scan killswitch (affects analysis endpoints)
        if path in ["/api/analyze", "/api/report"] and not await enhanced_killswitch.is_scan_enabled():
            return {"blocked": True, "reason": enhanced_killswitch.get_maintenance_message()}
        
        return {"blocked": False, "reason": ""}
    
    async def _check_rate_limit(self, ip: str, path: str) -> Dict[str, Any]:
        """Check rate limits."""
        is_allowed, remaining = await rate_limiter.check_rate_limit(ip)
        
        if not is_allowed:
            return {
                "blocked": True,
                "remaining": remaining,
                "reason": "Rate limit exceeded"
            }
        
        return {"blocked": False, "remaining": remaining}
    
    async def _check_abuse(self, ip: str, request: Request) -> Dict[str, Any]:
        """Check for abusive behavior."""
        path = request.url.path
        
        # Extract handle from request if available
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
            return {"blocked": True, "reason": reason}
        
        return {"blocked": False, "reason": ""}
    
    async def _check_token_availability(self) -> Dict[str, Any]:
        """Check token availability for analysis."""
        # Estimate tokens needed for analysis (rough estimate)
        estimated_tokens = 5000  # Conservative estimate
        
        is_allowed, reason = await token_manager.check_token_availability(estimated_tokens)
        
        if not is_allowed:
            return {"blocked": True, "reason": reason}
        
        return {"blocked": False, "reason": ""}
    
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
                "Retry-After": "3600",  # 1 hour
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
                "remaining": rate_info["remaining"],
                "type": "rate_limit"
            },
            headers={
                "Retry-After": "60",  # 1 minute
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
                "type": "abuse_detection"
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
                "type": "token_limit"
            },
            headers={
                "Retry-After": "3600",  # 1 hour
                "X-Governance-Action": "token_limit"
            }
        )
    
    def _add_governance_headers(self, response, client_ip: str, start_time: float) -> any:
        """Add governance information headers."""
        processing_time = time.time() - start_time
        
        response.headers["X-Governance-IP"] = client_ip
        response.headers["X-Governance-Time"] = f"{processing_time:.3f}s"
        response.headers["X-Governance-Status"] = "active"
        
        return response

# Create middleware instance
governance_middleware = GovernanceMiddleware()