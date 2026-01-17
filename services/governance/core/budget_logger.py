"""
Budget Logging and Monitoring System for SponsorScope
Tracks LLM usage, costs, and provides detailed audit trails
"""

import asyncio
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import aiofiles
from services.governance.core.token_manager import token_manager

class BudgetEventType(Enum):
    TOKEN_CONSUMPTION = "token_consumption"
    RATE_LIMIT_HIT = "rate_limit_hit"
    ABUSE_DETECTION = "abuse_detection"
    DEGRADATION_TRIGGERED = "degradation_triggered"
    BUDGET_WARNING = "budget_warning"
    BUDGET_EXCEEDED = "budget_exceeded"
    SERVICE_DEGRADATION = "service_degradation"
    CIRCUIT_BREAKER = "circuit_breaker"

@dataclass
class BudgetEvent:
    timestamp: str
    event_type: str
    ip_address: str
    endpoint: str
    tokens_used: int
    cost_incurred: float
    model_used: str
    request_id: str
    user_agent: str
    degradation_level: str
    additional_data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class BudgetLogger:
    """
    Comprehensive budget logging and monitoring system.
    """
    
    def __init__(self):
        self.log_directory = os.getenv("BUDGET_LOG_DIR", "services/governance/logs")
        self.log_rotation_hours = int(os.getenv("BUDGET_LOG_ROTATION_HOURS", "24"))
        self.retention_days = int(os.getenv("BUDGET_LOG_RETENTION_DAYS", "30"))
        
        # Ensure log directory exists
        os.makedirs(self.log_directory, exist_ok=True)
        
        # Current log file
        self.current_log_file = None
        self.current_log_date = None
        
        # In-memory buffer for recent events
        self.event_buffer = []
        self.buffer_max_size = 1000
        
        # Budget thresholds
        self.warning_threshold = float(os.getenv("BUDGET_WARNING_THRESHOLD", "0.8"))  # 80%
        self.critical_threshold = float(os.getenv("BUDGET_CRITICAL_THRESHOLD", "0.95"))  # 95%
        
        # Statistics
        self.daily_stats = {
            "total_tokens": 0,
            "total_cost": 0.0,
            "total_requests": 0,
            "blocked_requests": 0,
            "degraded_requests": 0,
            "events_by_type": {}
        }
    
    async def _get_current_log_file(self) -> str:
        """Get current log file path, rotating daily."""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        if self.current_log_date != current_date:
            self.current_log_date = current_date
            self.current_log_file = os.path.join(
                self.log_directory, 
                f"budget_audit_{current_date}.jsonl"
            )
            
            # Initialize new log file if it doesn't exist
            if not os.path.exists(self.current_log_file):
                await self._initialize_log_file()
        
        return self.current_log_file
    
    async def _initialize_log_file(self):
        """Initialize a new log file with header."""
        header = {
            "log_version": "1.0",
            "created_at": datetime.now().isoformat(),
            "system_info": {
                "daily_token_limit": int(os.getenv("DAILY_TOKEN_LIMIT", "1000000")),
                "daily_spend_limit": float(os.getenv("DAILY_SPEND_LIMIT", "100.0")),
                "warning_threshold": self.warning_threshold,
                "critical_threshold": self.critical_threshold
            }
        }
        
        try:
            async with aiofiles.open(self.current_log_file, 'w') as f:
                await f.write(json.dumps(header) + "\n")
        except Exception as e:
            print(f"Error initializing log file: {e}")
    
    async def log_event(self, event: BudgetEvent):
        """Log a budget event."""
        try:
            # Add to buffer
            self.event_buffer.append(event)
            if len(self.event_buffer) > self.buffer_max_size:
                self.event_buffer.pop(0)
            
            # Update statistics
            await self._update_statistics(event)
            
            # Write to file
            log_file = await self._get_current_log_file()
            async with aiofiles.open(log_file, 'a') as f:
                await f.write(json.dumps(event.to_dict()) + "\n")
            
            # Check thresholds and trigger alerts
            await self._check_budget_thresholds(event)
            
        except Exception as e:
            print(f"Error logging budget event: {e}")
    
    async def log_token_consumption(self, ip_address: str, tokens: int, model: str, cost: float, 
                                  request_id: str, endpoint: str = "/api/analyze", 
                                  user_agent: str = "", additional_data: Dict[str, Any] = None):
        """Log token consumption event."""
        event = BudgetEvent(
            timestamp=datetime.now().isoformat(),
            event_type=BudgetEventType.TOKEN_CONSUMPTION.value,
            ip_address=ip_address,
            endpoint=endpoint,
            tokens_used=tokens,
            cost_incurred=cost,
            model_used=model,
            request_id=request_id,
            user_agent=user_agent,
            degradation_level="normal",
            additional_data=additional_data or {}
        )
        await self.log_event(event)
    
    async def log_rate_limit_hit(self, ip_address: str, endpoint: str, request_id: str,
                               rate_limit_type: str, remaining_limits: Dict[str, int],
                               user_agent: str = ""):
        """Log rate limit hit event."""
        event = BudgetEvent(
            timestamp=datetime.now().isoformat(),
            event_type=BudgetEventType.RATE_LIMIT_HIT.value,
            ip_address=ip_address,
            endpoint=endpoint,
            tokens_used=0,
            cost_incurred=0.0,
            model_used="",
            request_id=request_id,
            user_agent=user_agent,
            degradation_level="normal",
            additional_data={
                "rate_limit_type": rate_limit_type,
                "remaining_limits": remaining_limits
            }
        )
        await self.log_event(event)
    
    async def log_abuse_detection(self, ip_address: str, endpoint: str, request_id: str,
                                abuse_type: str, reason: str, user_agent: str = ""):
        """Log abuse detection event."""
        event = BudgetEvent(
            timestamp=datetime.now().isoformat(),
            event_type=BudgetEventType.ABUSE_DETECTION.value,
            ip_address=ip_address,
            endpoint=endpoint,
            tokens_used=0,
            cost_incurred=0.0,
            model_used="",
            request_id=request_id,
            user_agent=user_agent,
            degradation_level="normal",
            additional_data={
                "abuse_type": abuse_type,
                "reason": reason
            }
        )
        await self.log_event(event)
    
    async def log_degradation_event(self, degradation_level: str, reason: str,
                                  affected_requests: int, additional_data: Dict[str, Any] = None):
        """Log service degradation event."""
        event = BudgetEvent(
            timestamp=datetime.now().isoformat(),
            event_type=BudgetEventType.DEGRADATION_TRIGGERED.value,
            ip_address="system",
            endpoint="system",
            tokens_used=0,
            cost_incurred=0.0,
            model_used="",
            request_id=f"degradation_{int(time.time())}",
            user_agent="",
            degradation_level=degradation_level,
            additional_data={
                "reason": reason,
                "affected_requests": affected_requests,
                **(additional_data or {})
            }
        )
        await self.log_event(event)
    
    async def _update_statistics(self, event: BudgetEvent):
        """Update daily statistics."""
        self.daily_stats["total_tokens"] += event.tokens_used
        self.daily_stats["total_cost"] += event.cost_incurred
        self.daily_stats["total_requests"] += 1
        
        # Count events by type
        event_type = event.event_type
        if event_type not in self.daily_stats["events_by_type"]:
            self.daily_stats["events_by_type"][event_type] = 0
        self.daily_stats["events_by_type"][event_type] += 1
        
        # Count blocked requests
        if event.event_type in [BudgetEventType.RATE_LIMIT_HIT.value, 
                              BudgetEventType.ABUSE_DETECTION.value]:
            self.daily_stats["blocked_requests"] += 1
        
        # Count degraded requests
        if event.event_type == BudgetEventType.DEGRADATION_TRIGGERED.value:
            self.daily_stats["degraded_requests"] += event.additional_data.get("affected_requests", 0)
    
    async def _check_budget_thresholds(self, event: BudgetEvent):
        """Check if budget thresholds are exceeded and trigger alerts."""
        if event.event_type != BudgetEventType.TOKEN_CONSUMPTION.value:
            return
        
        try:
            # Get current usage stats
            usage_stats = await token_manager.get_usage_stats()
            token_percentage = usage_stats.get("percentage_used", 0) / 100
            spend_percentage = (usage_stats.get("spend_used", 0) / 
                              float(os.getenv("DAILY_SPEND_LIMIT", "100.0")))
            
            # Check token threshold
            if token_percentage >= self.critical_threshold:
                await self._log_budget_warning("CRITICAL", "token", token_percentage)
            elif token_percentage >= self.warning_threshold:
                await self._log_budget_warning("WARNING", "token", token_percentage)
            
            # Check spend threshold
            if spend_percentage >= self.critical_threshold:
                await self._log_budget_warning("CRITICAL", "spend", spend_percentage)
            elif spend_percentage >= self.warning_threshold:
                await self._log_budget_warning("WARNING", "spend", spend_percentage)
                
        except Exception as e:
            print(f"Error checking budget thresholds: {e}")
    
    async def _log_budget_warning(self, severity: str, budget_type: str, percentage: float):
        """Log budget threshold warning."""
        event_type = (BudgetEventType.BUDGET_WARNING.value if severity == "WARNING" 
                     else BudgetEventType.BUDGET_EXCEEDED.value)
        
        event = BudgetEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            ip_address="system",
            endpoint="system",
            tokens_used=0,
            cost_incurred=0.0,
            model_used="",
            request_id=f"budget_warning_{int(time.time())}",
            user_agent="",
            degradation_level="normal",
            additional_data={
                "severity": severity,
                "budget_type": budget_type,
                "percentage_used": percentage * 100,
                "threshold": self.warning_threshold if severity == "WARNING" else self.critical_threshold
            }
        )
        await self.log_event(event)
    
    async def get_daily_summary(self, date: str = None) -> Dict[str, Any]:
        """Get daily budget summary."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            usage_stats = await token_manager.get_usage_stats(date)
            
            return {
                "date": date,
                "usage_stats": usage_stats,
                "daily_stats": self.daily_stats.copy(),
                "thresholds": {
                    "warning_threshold": self.warning_threshold,
                    "critical_threshold": self.critical_threshold
                },
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error getting daily summary: {e}")
            return {
                "date": date,
                "error": str(e),
                "daily_stats": self.daily_stats.copy()
            }
    
    async def get_recent_events(self, limit: int = 100, event_type: str = None) -> List[Dict[str, Any]]:
        """Get recent budget events."""
        events = []
        
        # Get from buffer (most recent)
        for event in reversed(self.event_buffer):
            if event_type is None or event.event_type == event_type:
                events.append(event.to_dict())
                if len(events) >= limit:
                    break
        
        return events
    
    async def get_abuse_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of abuse detection events."""
        recent_events = await self.get_recent_events(limit=1000, event_type=BudgetEventType.ABUSE_DETECTION.value)
        
        abuse_by_ip = {}
        abuse_by_type = {}
        
        for event in recent_events:
            ip = event["ip_address"]
            abuse_type = event["additional_data"].get("abuse_type", "unknown")
            
            if ip not in abuse_by_ip:
                abuse_by_ip[ip] = 0
            abuse_by_ip[ip] += 1
            
            if abuse_type not in abuse_by_type:
                abuse_by_type[abuse_type] = 0
            abuse_by_type[abuse_type] += 1
        
        return {
            "total_abuse_events": len(recent_events),
            "abuse_by_ip": abuse_by_ip,
            "abuse_by_type": abuse_by_type,
            "top_abusive_ips": sorted(abuse_by_ip.items(), key=lambda x: x[1], reverse=True)[:10],
            "most_common_types": sorted(abuse_by_type.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    async def export_audit_log(self, start_date: str, end_date: str, output_file: str):
        """Export audit log for specified date range."""
        try:
            events = []
            
            # This is a simplified implementation
            # In production, you'd read from the actual log files
            async for event in self._read_events_in_range(start_date, end_date):
                events.append(event)
            
            # Export to file
            export_data = {
                "export_info": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "exported_at": datetime.now().isoformat(),
                    "total_events": len(events)
                },
                "events": events
            }
            
            async with aiofiles.open(output_file, 'w') as f:
                await f.write(json.dumps(export_data, indent=2))
            
            return {"success": True, "events_exported": len(events), "output_file": output_file}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _read_events_in_range(self, start_date: str, end_date: str):
        """Read events from log files in date range."""
        # This is a simplified implementation
        # In production, you'd parse the actual log files
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        
        while current_date <= end_date_obj:
            date_str = current_date.strftime("%Y-%m-%d")
            log_file = os.path.join(self.log_directory, f"budget_audit_{date_str}.jsonl")
            
            if os.path.exists(log_file):
                try:
                    async with aiofiles.open(log_file, 'r') as f:
                        async for line in f:
                            if line.strip():
                                event_data = json.loads(line.strip())
                                if "timestamp" in event_data:
                                    yield event_data
                except Exception as e:
                    print(f"Error reading log file {log_file}: {e}")
            
            current_date += timedelta(days=1)
    
    async def cleanup_old_logs(self):
        """Clean up old log files."""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            for filename in os.listdir(self.log_directory):
                if filename.startswith("budget_audit_") and filename.endswith(".jsonl"):
                    try:
                        date_str = filename.replace("budget_audit_", "").replace(".jsonl", "")
                        file_date = datetime.strptime(date_str, "%Y-%m-%d")
                        
                        if file_date < cutoff_date:
                            file_path = os.path.join(self.log_directory, filename)
                            os.remove(file_path)
                            print(f"Removed old log file: {filename}")
                    except Exception as e:
                        print(f"Error processing file {filename}: {e}")
                        
        except Exception as e:
            print(f"Error during log cleanup: {e}")

# Global budget logger instance
budget_logger = BudgetLogger()