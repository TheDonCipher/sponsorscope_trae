from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
from services.governance.core.enhanced_killswitch import enhanced_killswitch
from services.governance.core.rate_limiter import rate_limiter
from services.governance.core.token_manager import token_manager
from services.api.models.report import ReportResponse

router = APIRouter()

@router.get("/governance/status")
async def get_governance_status(request: Request) -> Dict[str, Any]:
    """
    Get current governance status including killswitch, rate limits, and token usage.
    """
    client_ip = request.client.host if request.client else "unknown"
    
    # Get rate limit status
    rate_limit_info = await rate_limiter.get_rate_limit_info(client_ip)
    
    # Get token usage stats
    token_stats = await token_manager.get_usage_stats()
    
    # Get killswitch status
    killswitch_status = await enhanced_killswitch.get_status()
    
    return {
        "status": "active",
        "killswitch": killswitch_status,
        "rate_limiting": rate_limit_info,
        "token_usage": token_stats,
        "client_ip": client_ip
    }

@router.get("/governance/rate-limit/{ip}")
async def get_rate_limit_for_ip(ip: str) -> Dict[str, Any]:
    """
    Get rate limit status for a specific IP (admin endpoint).
    """
    rate_limit_info = await rate_limiter.get_rate_limit_info(ip)
    
    return {
        "ip": ip,
        "rate_limiting": rate_limit_info
    }

@router.post("/governance/reset-rate-limit/{ip}")
async def reset_rate_limit_for_ip(ip: str) -> Dict[str, Any]:
    """
    Reset rate limit for a specific IP (admin endpoint).
    """
    # This would require admin authentication in production
    # For now, just return success (implementation would clear Redis keys)
    
    return {
        "ip": ip,
        "action": "rate_limit_reset",
        "status": "success"
    }

@router.get("/governance/token-usage")
async def get_token_usage() -> Dict[str, Any]:
    """
    Get detailed token usage statistics.
    """
    token_stats = await token_manager.get_usage_stats()
    
    return {
        "token_usage": token_stats,
        "limits": {
            "daily_token_limit": token_manager.daily_token_limit,
            "daily_spend_limit": token_manager.daily_spend_limit,
            "token_cost_per_1k": token_manager.token_cost_per_1k
        }
    }

@router.post("/governance/reset-token-usage")
async def reset_token_usage() -> Dict[str, Any]:
    """
    Reset daily token usage counters (admin endpoint).
    """
    # This would require admin authentication in production
    success = await token_manager.reset_daily_usage()
    
    return {
        "action": "token_usage_reset",
        "status": "success" if success else "failed"
    }

@router.get("/governance/killswitch")
async def get_killswitch_status() -> Dict[str, Any]:
    """
    Get killswitch status and configuration.
    """
    return await enhanced_killswitch.get_status()

@router.post("/governance/killswitch/{component}/{action}")
async def toggle_killswitch(component: str, action: str) -> Dict[str, Any]:
    """
    Toggle killswitch for specific component (admin endpoint).
    
    component: 'scans' or 'read'
    action: 'enable' or 'disable'
    """
    # This would require admin authentication in production
    # Would also need to update environment variables or Redis state
    
    if component not in ["scans", "read"]:
        raise HTTPException(status_code=400, detail="Invalid component. Must be 'scans' or 'read'")
    
    if action not in ["enable", "disable"]:
        raise HTTPException(status_code=400, detail="Invalid action. Must be 'enable' or 'disable'")
    
    # In a real implementation, this would update the killswitch state
    # For now, just return the current status
    
    # In a real implementation, this would update the killswitch state
    if action == "enable":
        if component == "scans":
            await enhanced_killswitch.set_scan_enabled(True)
        else:
            await enhanced_killswitch.set_read_enabled(True)
    else:  # disable
        if component == "scans":
            await enhanced_killswitch.set_scan_enabled(False)
        else:
            await enhanced_killswitch.set_read_enabled(False)
    
    return {
        "component": component,
        "action": action,
        "status": "success",
        "current_state": await enhanced_killswitch.get_status()
    }