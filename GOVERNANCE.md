# SponsorScope Governance Layer

This document describes the operational resilience and governance features implemented in SponsorScope.

## Overview

The governance layer provides:
- **Kill Switch**: Emergency system controls for maintenance and incidents
- **Rate Limiting**: Per-IP request throttling with sliding windows
- **Abuse Detection**: Rapid resubmission and suspicious activity detection
- **Token Management**: LLM usage tracking and spend caps
- **System Notices**: Administrative messaging to users

## Architecture

### Components

1. **GovernanceMiddleware**: FastAPI middleware that processes all requests
2. **EnhancedKillSwitch**: Redis-backed emergency controls
3. **RateLimiter**: Sliding window rate limiting with Redis fallback
4. **TokenManager**: LLM token usage and cost tracking
5. **Governance Routes**: Administrative endpoints for monitoring and control

### Request Flow

```
Request → GovernanceMiddleware → [Kill Switch] → [Rate Limit] → [Abuse Detection] → [Token Check] → Route Handler
```

## Configuration

### Environment Variables

See `.env.example` for all configuration options. Key settings:

#### Kill Switch
- `KILL_SWITCH_SCANS`: Enable/disable new analysis requests
- `KILL_SWITCH_READ`: Enable/disable all system access
- `MAINTENANCE_MESSAGE`: Message shown during maintenance

#### Rate Limiting
- `RATE_LIMIT_RPM`: Requests per minute (default: 60)
- `RATE_LIMIT_RPH`: Requests per hour (default: 1000)
- `RATE_LIMIT_RPD`: Requests per day (default: 10000)
- `RAPID_RESUBMISSION_THRESHOLD`: Max handle resubmissions (default: 5)
- `RAPID_RESUBMISSION_WINDOW`: Resubmission window in seconds (default: 60)

#### Token Management
- `DAILY_TOKEN_LIMIT`: Maximum tokens per day (default: 1M)
- `DAILY_SPEND_LIMIT`: Maximum daily spend in USD (default: $100)
- `TOKEN_COST_PER_1K`: Base cost per 1000 tokens (default: $0.01)

#### Redis (Optional)
- `REDIS_URL`: Redis connection URL (falls back to memory if unavailable)

## API Endpoints

### Governance Status
- `GET /api/governance/status` - Current governance status
- `GET /api/governance/killswitch` - Kill switch status
- `GET /api/governance/token-usage` - Token usage statistics
- `GET /api/governance/rate-limit/{ip}` - Rate limit status for IP

### Administrative (Require Auth in Production)
- `POST /api/governance/killswitch/{component}/{action}` - Toggle kill switch
- `POST /api/governance/reset-rate-limit/{ip}` - Reset rate limits
- `POST /api/governance/reset-token-usage` - Reset token counters

## Response Headers

All responses include governance headers:
- `X-Governance-IP`: Client IP address
- `X-Governance-Time`: Request processing time
- `X-Governance-Status`: Governance system status
- `X-Governance-Action`: Action taken (if blocked)

## Error Responses

### Rate Limit Exceeded
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later.",
  "remaining": {"minute": 0, "hour": 0, "day": 0},
  "type": "rate_limit"
}
```

### Kill Switch Active
```json
{
  "error": "Service temporarily unavailable",
  "message": "SponsorScope is currently undergoing scheduled maintenance.",
  "type": "maintenance"
}
```

### Abuse Detection
```json
{
  "error": "Request blocked",
  "message": "Rapid resubmission detected (5 attempts)",
  "type": "abuse_detection"
}
```

### Token Limit Exceeded
```json
{
  "error": "Service temporarily unavailable",
  "message": "Daily token limit exceeded (1000000 tokens)",
  "type": "token_limit"
}
```

## System Notices

Administrators can add system-wide notices that appear in report `warning_banners`:

```python
await enhanced_killswitch.add_system_notice("System maintenance scheduled for 2 AM EST")
```

## Redis Integration

The governance layer automatically uses Redis when available for:
- Rate limiting counters (persistent across restarts)
- Kill switch state (immediate propagation)
- Token usage tracking (accurate daily totals)
- Abuse detection data (cross-instance coordination)

Falls back to in-memory storage if Redis is unavailable.

## Monitoring

Monitor governance operations through:
- API logs with `GOVERNANCE_LOG_LEVEL`
- Response headers showing processing time
- Governance status endpoints
- Redis monitoring for distributed systems

## Security Considerations

- Administrative endpoints should require authentication
- Rate limits should be conservative for public endpoints
- Token limits prevent cost overruns
- Abuse detection protects against malicious usage
- Kill switches provide emergency shutdown capability

## Testing

Test governance features:
```bash
# Check governance status
curl http://localhost:8000/api/governance/status

# Test rate limiting (make many requests)
for i in {1..70}; do curl -s http://localhost:8000/api/analyze; done

# Test kill switch
curl -X POST http://localhost:8000/api/governance/killswitch/scans/disable
```

## Troubleshooting

### High Rate Limit Blocks
- Check `RAPID_RESUBMISSION_THRESHOLD` and `RAPID_RESUBMISSION_WINDOW`
- Monitor Redis connection for distributed rate limiting

### Token Limit Issues
- Verify `DAILY_TOKEN_LIMIT` and `DAILY_SPEND_LIMIT` settings
- Check token consumption in logs

### Kill Switch Not Working
- Verify Redis connection for distributed kill switches
- Check environment variable precedence

### Performance Issues
- Monitor `X-Governance-Time` headers
- Consider Redis for better performance with high traffic