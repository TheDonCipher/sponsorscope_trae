#!/usr/bin/env python3
"""
Platform Resistance Debug Utility

Comprehensive debugging and error trace generation for platform resistance system.
"""

import json
import os
import sys
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add project root to path
sys.path.insert(0, '.')

from services.governance.core.platform_resistance import platform_resistance
from services.governance.core.resistance_logger import resistance_logger
from services.governance.core.rate_limiter import rate_limiter

def get_log_files(log_dir: str = "services/governance/logs") -> Dict[str, str]:
    """Get all platform resistance log files."""
    log_files = {
        "resistance_events": f"{log_dir}/platform_resistance.jsonl",
        "error_traces": f"{log_dir}/resistance_errors.jsonl",
        "failure_reasons": f"{log_dir}/resistance_failures.jsonl",
        "scraper_detections": f"{log_dir}/scraper_detections.jsonl",
        "rate_limit_violations": f"{log_dir}/rate_limit_violations.jsonl",
        "evaluation_errors": f"{log_dir}/evaluation_errors.jsonl",
        "legitimate_access": f"{log_dir}/legitimate_access.jsonl",
        "internal_errors": f"{log_dir}/internal_errors.jsonl"
    }
    
    return log_files

def read_log_file(file_path: str, limit: int = 1000) -> List[Dict[str, Any]]:
    """Read and parse a log file."""
    entries = []
    
    if not os.path.exists(file_path):
        return entries
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Read last 'limit' lines
        for line in lines[-limit:]:
            try:
                entry = json.loads(line.strip())
                entries.append(entry)
            except json.JSONDecodeError:
                continue
                
    except Exception as e:
        print(f"Error reading log file {file_path}: {e}")
    
    return entries

def analyze_error_patterns(log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze error patterns in log entries."""
    analysis = {
        "total_entries": len(log_entries),
        "error_types": {},
        "time_distribution": {},
        "client_ip_patterns": {},
        "endpoint_patterns": {},
        "recent_errors": []
    }
    
    for entry in log_entries:
        # Count error types
        error_type = entry.get("error_type", entry.get("event_type", "unknown"))
        analysis["error_types"][error_type] = analysis["error_types"].get(error_type, 0) + 1
        
        # Time distribution (by hour)
        timestamp = entry.get("timestamp", "")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                hour_key = dt.strftime("%Y-%m-%d %H:00")
                analysis["time_distribution"][hour_key] = analysis["time_distribution"].get(hour_key, 0) + 1
            except ValueError:
                pass
        
        # Client IP patterns
        client_ip = entry.get("client_ip", "unknown")
        analysis["client_ip_patterns"][client_ip] = analysis["client_ip_patterns"].get(client_ip, 0) + 1
        
        # Endpoint patterns
        endpoint = entry.get("endpoint", entry.get("path", "unknown"))
        analysis["endpoint_patterns"][endpoint] = analysis["endpoint_patterns"].get(endpoint, 0) + 1
    
    # Get recent errors (last 10)
    analysis["recent_errors"] = log_entries[-10:] if log_entries else []
    
    return analysis

def generate_error_trace_report(client_ip: Optional[str] = None, hours: int = 24) -> Dict[str, Any]:
    """Generate comprehensive error trace report."""
    print(f"🔍 Generating error trace report for {hours} hours...")
    
    log_files = get_log_files()
    
    # Read all relevant log files
    resistance_logs = read_log_file(log_files["resistance_events"])
    error_traces = read_log_file(log_files["error_traces"])
    failure_reasons = read_log_file(log_files["failure_reasons"])
    
    # Filter by client IP if specified
    if client_ip:
        resistance_logs = [log for log in resistance_logs if log.get("client_ip") == client_ip]
        error_traces = [log for log in error_traces if log.get("client_ip") == client_ip]
        failure_reasons = [log for log in failure_reasons if log.get("client_ip") == client_ip]
    
    # Filter by time period
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    def filter_by_time(logs):
        filtered = []
        for log in logs:
            timestamp = log.get("timestamp", "")
            if timestamp:
                try:
                    log_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    if log_time >= cutoff_time:
                        filtered.append(log)
                except ValueError:
                    continue
        return filtered
    
    resistance_logs = filter_by_time(resistance_logs)
    error_traces = filter_by_time(error_traces)
    failure_reasons = filter_by_time(failure_reasons)
    
    # Analyze patterns
    resistance_analysis = analyze_error_patterns(resistance_logs)
    error_trace_analysis = analyze_error_patterns(error_traces)
    failure_analysis = analyze_error_patterns(failure_reasons)
    
    # Get current platform resistance status
    resistance_info = platform_resistance.get_resistance_info()
    
    # Generate comprehensive report
    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "filter_parameters": {
            "client_ip": client_ip,
            "hours": hours,
            "cutoff_time": cutoff_time.isoformat()
        },
        "summary": {
            "total_resistance_events": len(resistance_logs),
            "total_error_traces": len(error_traces),
            "total_failure_reasons": len(failure_reasons),
            "most_common_errors": dict(sorted(resistance_analysis["error_types"].items(), key=lambda x: x[1], reverse=True)[:5]),
            "most_active_ips": dict(sorted(resistance_analysis["client_ip_patterns"].items(), key=lambda x: x[1], reverse=True)[:5]),
            "most_affected_endpoints": dict(sorted(resistance_analysis["endpoint_patterns"].items(), key=lambda x: x[1], reverse=True)[:5])
        },
        "platform_resistance_status": resistance_info,
        "detailed_analysis": {
            "resistance_events": resistance_analysis,
            "error_traces": error_trace_analysis,
            "failure_reasons": failure_analysis
        },
        "recent_errors": {
            "resistance_events": resistance_logs[-10:] if resistance_logs else [],
            "error_traces": error_traces[-10:] if error_traces else [],
            "failure_reasons": failure_reasons[-10:] if failure_reasons else []
        },
        "recommendations": generate_recommendations(resistance_analysis, error_trace_analysis)
    }
    
    return report

def generate_recommendations(resistance_analysis: Dict[str, Any], error_analysis: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on error patterns."""
    recommendations = []
    
    # Analyze error frequency
    total_resistance = resistance_analysis.get("total_entries", 0)
    total_errors = error_analysis.get("total_entries", 0)
    
    if total_resistance > 100:
        recommendations.append("High resistance activity detected. Consider adjusting detection thresholds.")
    
    if total_errors > 50:
        recommendations.append("High error rate detected. Review system stability and error handling.")
    
    # Analyze error types
    error_types = resistance_analysis.get("error_types", {})
    if "scraper_detected" in error_types and error_types["scraper_detected"] > total_resistance * 0.7:
        recommendations.append("High scraper detection rate. Verify detection accuracy to avoid false positives.")
    
    if "evaluation_error" in error_types and error_types["evaluation_error"] > total_resistance * 0.1:
        recommendations.append("High evaluation error rate. Review error handling and system resources.")
    
    # Analyze IP patterns
    ip_patterns = resistance_analysis.get("client_ip_patterns", {})
    if len(ip_patterns) < 5 and total_resistance > 20:
        recommendations.append("Low IP diversity in resistance events. Check for concentrated attacks.")
    
    # Analyze time patterns
    time_dist = resistance_analysis.get("time_distribution", {})
    if time_dist:
        recent_hours = list(time_dist.keys())[-3:]  # Last 3 hours
        recent_activity = sum(time_dist.get(hour, 0) for hour in recent_hours)
        if recent_activity > total_resistance * 0.5:
            recommendations.append("High recent activity. Monitor for ongoing attacks or system issues.")
    
    if not recommendations:
        recommendations.append("No significant issues detected. System appears to be operating normally.")
    
    return recommendations

def generate_debug_trace(error_entry: Dict[str, Any]) -> str:
    """Generate detailed debug trace for a specific error."""
    trace_lines = [
        "=" * 60,
        f"PLATFORM RESISTANCE ERROR TRACE",
        "=" * 60,
        f"Timestamp: {error_entry.get('timestamp', 'Unknown')}",
        f"Client IP: {error_entry.get('client_ip', 'Unknown')}",
        f"Endpoint: {error_entry.get('endpoint', 'Unknown')}",
        f"Error Type: {error_entry.get('error_type', 'Unknown')}",
        f"Error Message: {error_entry.get('error_message', 'Unknown')}",
        "",
        "CONTEXT:",
        "-" * 30
    ]
    
    context = error_entry.get("context", {})
    for key, value in context.items():
        trace_lines.append(f"{key}: {value}")
    
    trace_lines.extend([
        "",
        "TRACEBACK:",
        "-" * 30,
        error_entry.get("traceback", "No traceback available"),
        "",
        "STACK TRACE:",
        "-" * 30,
        "\n".join(error_entry.get("stack_trace", ["No stack trace available"])),
        "=" * 60
    ])
    
    return "\n".join(trace_lines)

def check_system_health() -> Dict[str, Any]:
    """Check overall system health for platform resistance."""
    print("🏥 Checking Platform Resistance System Health...")
    
    health_status = {
        "timestamp": datetime.utcnow().isoformat(),
        "overall_status": "healthy",
        "components": {},
        "issues": [],
        "recommendations": []
    }
    
    # Check log files
    log_files = get_log_files()
    for name, path in log_files.items():
        if os.path.exists(path):
            file_size = os.path.getsize(path)
            health_status["components"][f"{name}_log"] = {
                "status": "exists",
                "size_bytes": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2)
            }
            
            if file_size > 50 * 1024 * 1024:  # 50MB
                health_status["issues"].append(f"{name} log file is large ({file_size / (1024*1024):.1f}MB)")
        else:
            health_status["components"][f"{name}_log"] = {
                "status": "missing",
                "size_bytes": 0
            }
    
    # Check platform resistance instance
    try:
        resistance_info = platform_resistance.get_resistance_info()
        health_status["components"]["platform_resistance"] = {
            "status": "operational",
            "mode": resistance_info.get("resistance_mode", "unknown"),
            "threshold": resistance_info.get("scraper_detection_threshold", "unknown")
        }
        
        if resistance_info.get("error"):
            health_status["issues"].append(f"Platform resistance error: {resistance_info['error']}")
            health_status["overall_status"] = "degraded"
            
    except Exception as e:
        health_status["components"]["platform_resistance"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["issues"].append(f"Platform resistance system error: {str(e)}")
        health_status["overall_status"] = "unhealthy"
    
    # Check rate limiter
    try:
        # Test basic functionality
        health_status["components"]["rate_limiter"] = {
            "status": "operational"
        }
    except Exception as e:
        health_status["components"]["rate_limiter"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["issues"].append(f"Rate limiter error: {str(e)}")
    
    # Generate recommendations
    if health_status["issues"]:
        health_status["recommendations"].append("Address identified issues to improve system health.")
    else:
        health_status["recommendations"].append("System appears healthy. Continue monitoring.")
    
    return health_status

def main():
    """Main debug utility function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Platform Resistance Debug Utility")
    parser.add_argument("--client-ip", help="Filter by specific client IP")
    parser.add_argument("--hours", type=int, default=24, help="Hours to analyze (default: 24)")
    parser.add_argument("--health-check", action="store_true", help="Run system health check")
    parser.add_argument("--trace", help="Generate detailed trace for specific error ID or timestamp")
    parser.add_argument("--output", help="Output file for the report")
    
    args = parser.parse_args()
    
    try:
        if args.health_check:
            # Run health check
            health_report = check_system_health()
            print("\n" + "=" * 60)
            print("SYSTEM HEALTH REPORT")
            print("=" * 60)
            print(f"Overall Status: {health_report['overall_status'].upper()}")
            print(f"Timestamp: {health_report['timestamp']}")
            
            if health_report['issues']:
                print("\nISSUES FOUND:")
                for issue in health_report['issues']:
                    print(f"  - {issue}")
            
            if health_report['recommendations']:
                print("\nRECOMMENDATIONS:")
                for rec in health_report['recommendations']:
                    print(f"  - {rec}")
            
            print("\nCOMPONENT STATUS:")
            for component, status in health_report['components'].items():
                print(f"  {component}: {status['status']}")
                if 'error' in status:
                    print(f"    Error: {status['error']}")
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(health_report, f, indent=2, default=str)
                print(f"\nHealth report saved to: {args.output}")
                
        else:
            # Generate error trace report
            report = generate_error_trace_report(args.client_ip, args.hours)
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                print(f"Error trace report saved to: {args.output}")
            else:
                print("\n" + "=" * 60)
                print("PLATFORM RESISTANCE ERROR TRACE REPORT")
                print("=" * 60)
                print(f"Generated: {report['generated_at']}")
                print(f"Analysis Period: {args.hours} hours")
                if args.client_ip:
                    print(f"Client IP Filter: {args.client_ip}")
                
                print(f"\nSUMMARY:")
                print(f"  Total Resistance Events: {report['summary']['total_resistance_events']}")
                print(f"  Total Error Traces: {report['summary']['total_error_traces']}")
                print(f"  Total Failure Reasons: {report['summary']['total_failure_reasons']}")
                
                if report['summary']['most_common_errors']:
                    print(f"\nMOST COMMON ERRORS:")
                    for error_type, count in report['summary']['most_common_errors'].items():
                        print(f"  {error_type}: {count}")
                
                if report['recommendations']:
                    print(f"\nRECOMMENDATIONS:")
                    for rec in report['recommendations']:
                        print(f"  - {rec}")
                
                if report['recent_errors']['resistance_events']:
                    print(f"\nRECENT RESISTANCE EVENTS:")
                    for event in report['recent_errors']['resistance_events'][-3:]:
                        print(f"  {event.get('timestamp', 'Unknown')}: {event.get('reason', 'Unknown reason')}")
                
                print(f"\nFor detailed analysis, use --output flag to save full report.")
    
    except KeyboardInterrupt:
        print("\n🛑 Debug utility interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Fatal error in debug utility: {str(e)}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)