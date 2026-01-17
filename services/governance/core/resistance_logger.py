"""
Platform Resistance Logging System

Comprehensive logging for platform resistance events, failures, and debugging.
"""

import json
import os
import time
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

class ResistanceEventType(Enum):
    """Types of platform resistance events."""
    SCRAPER_DETECTED = "scraper_detected"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    ABUSE_DETECTED = "abuse_detected"
    EVALUATION_ERROR = "evaluation_error"
    RESISTANCE_TRIGGERED = "resistance_triggered"
    LEGITIMATE_ACCESS = "legitimate_access"

class ResistanceLogger:
    """
    Comprehensive logging system for platform resistance events.
    """
    
    def __init__(self):
        self.log_dir = "services/governance/logs"
        self.resistance_log = f"{self.log_dir}/platform_resistance.jsonl"
        self.error_trace_log = f"{self.log_dir}/resistance_errors.jsonl"
        self.failure_reasons_log = f"{self.log_dir}/resistance_failures.jsonl"
        self.legitimate_access_log = f"{self.log_dir}/legitimate_access.jsonl"
        
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Log rotation settings
        self.max_log_size = 10 * 1024 * 1024  # 10MB
        self.retention_days = 30
    
    def log_resistance_event(
        self, 
        event_type: ResistanceEventType,
        client_ip: str,
        endpoint: str,
        reason: str,
        metadata: Dict[str, Any],
        request_data: Optional[Dict[str, Any]] = None
    ):
        """
        Log a platform resistance event with comprehensive details.
        """
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type.value,
                "client_ip": client_ip,
                "endpoint": endpoint,
                "reason": reason,
                "metadata": metadata,
                "request_data": request_data,
                "session_id": metadata.get("session_id"),
                "user_agent": metadata.get("user_agent"),
                "scraper_score": metadata.get("scraper_score"),
                "resistance_mode": metadata.get("resistance_mode", "moderate")
            }
            
            self._write_log(self.resistance_log, log_entry)
            
            # Log to appropriate specialized log
            if event_type == ResistanceEventType.SCRAPER_DETECTED:
                self._log_scraper_detection(client_ip, endpoint, reason, metadata)
            elif event_type == ResistanceEventType.RATE_LIMIT_EXCEEDED:
                self._log_rate_limit_violation(client_ip, endpoint, reason, metadata)
            elif event_type == ResistanceEventType.EVALUATION_ERROR:
                self._log_evaluation_error(client_ip, endpoint, reason, metadata)
                
        except Exception as e:
            self._log_internal_error(f"Failed to log resistance event: {e}", traceback.format_exc())
    
    def log_failure_reason(
        self,
        client_ip: str,
        endpoint: str,
        failure_type: str,
        reason: str,
        error_details: Dict[str, Any],
        resolution_suggestion: str = ""
    ):
        """
        Log detailed failure reasons for debugging and analysis.
        """
        try:
            failure_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "client_ip": client_ip,
                "endpoint": endpoint,
                "failure_type": failure_type,
                "reason": reason,
                "error_details": error_details,
                "resolution_suggestion": resolution_suggestion,
                "traceback": error_details.get("traceback", ""),
                "environment": {
                    "resistance_mode": error_details.get("resistance_mode"),
                    "scraper_threshold": error_details.get("scraper_detection_threshold"),
                    "rate_limit_config": error_details.get("rate_limit_config")
                }
            }
            
            self._write_log(self.failure_reasons_log, failure_entry)
            
        except Exception as e:
            self._log_internal_error(f"Failed to log failure reason: {e}", traceback.format_exc())
    
    def log_error_trace(
        self,
        client_ip: str,
        endpoint: str,
        error: Exception,
        context: Dict[str, Any] = None
    ):
        """
        Log detailed error traces for debugging platform resistance issues.
        """
        try:
            error_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "client_ip": client_ip,
                "endpoint": endpoint,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "traceback": traceback.format_exc(),
                "context": context or {},
                "stack_trace": traceback.format_stack()[:-1]  # Exclude this function
            }
            
            self._write_log(self.error_trace_log, error_entry)
            
        except Exception as e:
            self._log_internal_error(f"Failed to log error trace: {e}", traceback.format_exc())
    
    def log_legitimate_access(
        self,
        client_ip: str,
        endpoint: str,
        access_reason: str,
        verification_data: Dict[str, Any]
    ):
        """
        Log legitimate access attempts to help tune resistance parameters.
        """
        try:
            access_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "client_ip": client_ip,
                "endpoint": endpoint,
                "access_reason": access_reason,
                "verification_data": verification_data,
                "user_agent": verification_data.get("user_agent"),
                "scraper_score": verification_data.get("scraper_score"),
                "resistance_mode": verification_data.get("resistance_mode")
            }
            
            self._write_log(self.legitimate_access_log, access_entry)
            
        except Exception as e:
            self._log_internal_error(f"Failed to log legitimate access: {e}", traceback.format_exc())
    
    def _log_scraper_detection(self, client_ip: str, endpoint: str, reason: str, metadata: Dict[str, Any]):
        """Specialized logging for scraper detection events."""
        scraper_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "client_ip": client_ip,
            "endpoint": endpoint,
            "detection_reason": reason,
            "scraper_score": metadata.get("scraper_score"),
            "detection_method": metadata.get("detection_method"),
            "user_agent": metadata.get("user_agent"),
            "request_patterns": metadata.get("request_patterns", {}),
            "resistance_action": "blocked"
        }
        
        self._write_log(f"{self.log_dir}/scraper_detections.jsonl", scraper_entry)
    
    def _log_rate_limit_violation(self, client_ip: str, endpoint: str, reason: str, metadata: Dict[str, Any]):
        """Specialized logging for rate limit violations."""
        rate_limit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "client_ip": client_ip,
            "endpoint": endpoint,
            "violation_reason": reason,
            "rate_limit_remaining": metadata.get("remaining_counts", {}),
            "request_rate": metadata.get("request_rate"),
            "resistance_action": "rate_limited"
        }
        
        self._write_log(f"{self.log_dir}/rate_limit_violations.jsonl", rate_limit_entry)
    
    def _log_evaluation_error(self, client_ip: str, endpoint: str, reason: str, metadata: Dict[str, Any]):
        """Specialized logging for evaluation errors."""
        error_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "client_ip": client_ip,
            "endpoint": endpoint,
            "error_reason": reason,
            "error_details": metadata.get("error_details", {}),
            "traceback": metadata.get("traceback", ""),
            "resistance_action": "error_fallback"
        }
        
        self._write_log(f"{self.log_dir}/evaluation_errors.jsonl", error_entry)
    
    def _write_log(self, log_file: str, entry: Dict[str, Any]):
        """Write a log entry to file."""
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"Failed to write to log file {log_file}: {e}")
    
    def _log_internal_error(self, message: str, traceback_str: str):
        """Log internal errors in the logging system itself."""
        try:
            internal_error_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "error_type": "internal_logging_error",
                "message": message,
                "traceback": traceback_str
            }
            
            with open(f"{self.log_dir}/internal_errors.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(internal_error_entry, ensure_ascii=False) + "\n")
                
        except:
            # Last resort - print to console
            print(f"CRITICAL: Logging system failure: {message}")
            print(traceback_str)
    
    def get_resistance_stats(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get platform resistance statistics for the specified time period.
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            stats = {
                "period_hours": hours,
                "total_events": 0,
                "scraper_detections": 0,
                "rate_limit_violations": 0,
                "evaluation_errors": 0,
                "legitimate_access": 0,
                "top_blocked_ips": {},
                "top_blocked_endpoints": {},
                "hourly_breakdown": {}
            }
            
            # Read and analyze resistance events
            if os.path.exists(self.resistance_log):
                with open(self.resistance_log, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            event = json.loads(line.strip())
                            event_time = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
                            
                            if event_time >= cutoff_time:
                                stats["total_events"] += 1
                                
                                event_type = event.get("event_type", "")
                                if event_type == "scraper_detected":
                                    stats["scraper_detections"] += 1
                                elif event_type == "rate_limit_exceeded":
                                    stats["rate_limit_violations"] += 1
                                elif event_type == "evaluation_error":
                                    stats["evaluation_errors"] += 1
                                elif event_type == "legitimate_access":
                                    stats["legitimate_access"] += 1
                                
                                # Track top IPs and endpoints
                                client_ip = event.get("client_ip", "unknown")
                                endpoint = event.get("endpoint", "unknown")
                                
                                stats["top_blocked_ips"][client_ip] = stats["top_blocked_ips"].get(client_ip, 0) + 1
                                stats["top_blocked_endpoints"][endpoint] = stats["top_blocked_endpoints"].get(endpoint, 0) + 1
                                
                                # Hourly breakdown
                                hour_key = event_time.strftime("%Y-%m-%d %H:00")
                                stats["hourly_breakdown"][hour_key] = stats["hourly_breakdown"].get(hour_key, 0) + 1
                                
                        except (json.JSONDecodeError, ValueError):
                            continue
            
            return stats
            
        except Exception as e:
            return {
                "error": f"Failed to generate statistics: {str(e)}",
                "period_hours": hours
            }
    
    def get_error_traces(self, client_ip: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent error traces for debugging.
        """
        try:
            error_traces = []
            
            if os.path.exists(self.error_trace_log):
                with open(self.error_trace_log, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    
                # Process in reverse order (most recent first)
                for line in reversed(lines):
                    try:
                        error_entry = json.loads(line.strip())
                        
                        if client_ip is None or error_entry.get("client_ip") == client_ip:
                            error_traces.append(error_entry)
                            
                            if len(error_traces) >= limit:
                                break
                                
                    except json.JSONDecodeError:
                        continue
            
            return error_traces
            
        except Exception as e:
            return [{
                "error": f"Failed to retrieve error traces: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }]

# Global resistance logger instance
resistance_logger = ResistanceLogger()