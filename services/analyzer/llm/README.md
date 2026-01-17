# Vertex AI Gemini Integration for Bounded Refinement

This module integrates Vertex AI Gemini as a bounded refinement engine for audience authenticity scoring.

## Overview

The `AuthenticityRefiner` class uses Vertex AI Gemini to refine heuristic-based authenticity scores with:

- **Bounded Adjustments**: Score adjustments limited to ±15 points
- **Monotonic Safety Rules**: Score increases only allowed with full data completeness
- **Bot Floor Respect**: Score increases suppressed when bot probability > 0.8
- **Confidence Calibration**: Adjusts confidence based on LLM agreement and data quality
- **Robust Error Handling**: Graceful degradation on timeouts and API errors

## Architecture

### Core Components

1. **AuthenticityRefiner** (`refiner.py`): Main refinement engine
2. **VertexAIGeminiClient** (`vertex_client.py`): Vertex AI client with timeout/retry logic
3. **Calibration Engine** (`calibration.py`): Confidence calibration with safety rules
4. **Configuration** (`config.py`): Environment-based configuration management

### Integration Flow

```
HeuristicResult → AuthenticityRefiner → Vertex AI Gemini → Bounded Refinement → LLMRefinementResult
```

## Usage

### Basic Usage

```python
from services.analyzer.llm.refiner import AuthenticityRefiner
from services.analyzer.llm.config import VertexAIConfig
from services.analyzer.heuristics.types import HeuristicResult
from shared.schemas.domain import DataCompleteness

# Configure Vertex AI
vertex_config = VertexAIConfig.get_config()
refiner = AuthenticityRefiner(vertex_config=vertex_config)

# Create heuristic result
heuristic_result = HeuristicResult(
    score=75.0,
    confidence=0.8,
    data_completeness=DataCompleteness.FULL,
    signals={"bot_probability": 0.2, "entropy": 0.85}
)

# Refine with Gemini
result = await refiner.refine(
    heuristic_result=heuristic_result,
    comments=["Great content!", "Love this post!"],
    context="English"
)

print(f"Refined score: {result.refined_score}")
print(f"Adjustment: {result.adjustment}")
print(f"Confidence: {result.confidence}")
```

### Environment Configuration

Set these environment variables:

```bash
export VERTEX_AI_PROJECT_ID="your-project-id"
export VERTEX_AI_LOCATION="us-central1"  # Optional, defaults to us-central1
export VERTEX_AI_MODEL_NAME="gemini-1.5-pro"  # Optional, defaults to gemini-1.5-pro
export VERTEX_AI_TIMEOUT="30"  # Optional, defaults to 30 seconds
export VERTEX_AI_MAX_RETRIES="2"  # Optional, defaults to 2 retries
```

### Fallback Mode

When Vertex AI is not configured or encounters errors, the system falls back to:
- Deterministic simulation based on prompt content
- Lowered confidence scores
- Error flags in the result

## Safety Rules

### Monotonic Safety
- Score increases (+adjustment) only allowed with `DataCompleteness.FULL`
- Prevents over-optimistic scoring with incomplete data
- Flags: `monotonic_safety_applied`

### Bot Floor Respect
- Score increases suppressed when `bot_probability > 0.8`
- Prevents inflating scores for likely bot accounts
- Flags: `bot_floor_respected`

### Bounded Adjustments
- All adjustments limited to ±15 points
- Prevents extreme score changes
- Maintains score stability

## Error Handling

### Timeout Handling
- 30-second timeout per request (configurable)
- Exponential backoff retry logic
- Graceful fallback with lowered confidence

### Error Types
- `llm_timeout`: Request exceeded timeout
- `llm_error`: General API errors
- `llm_json_parse_error`: Invalid response format

### Confidence Impact
- LLM errors reduce confidence by 50%
- Monotonic safety application reduces confidence by 10%
- Partial data reduces confidence based on completeness level

## Testing

Run the comprehensive test suite:

```bash
python -m pytest services/analyzer/llm/test_vertex_integration.py -v
```

### Test Coverage
- ✅ Successful refinement with Gemini
- ✅ Monotonic safety with partial data
- ✅ Bot floor respect with high bot probability
- ✅ Timeout error handling
- ✅ General error handling
- ✅ Bounded adjustment limits
- ✅ JSON parsing errors
- ✅ Configuration management

## Performance Considerations

### Latency
- Typical response time: 2-5 seconds
- Timeout threshold: 30 seconds (configurable)
- Retry attempts: 2 with exponential backoff

### Rate Limiting
- Vertex AI has built-in rate limiting
- Consider implementing client-side rate limiting for high-volume usage
- Monitor quota usage through Google Cloud Console

### Resource Usage
- Async/await pattern for non-blocking operations
- Thread pool executor for synchronous Vertex AI calls
- Memory-efficient comment sampling (max 50 comments)

## Monitoring

### Logging
- Structured logging with correlation IDs
- Error categorization for alerting
- Performance metrics (latency, success rate)

### Health Checks
```python
# Check Vertex AI connectivity
client = VertexAIGeminiClient(project_id="your-project")
is_healthy = await client.health_check()
```

### Key Metrics
- Refinement success rate
- Average adjustment magnitude
- Confidence distribution
- Error rates by type
- Response latency percentiles

## Security

### Authentication
- Uses Google Cloud Application Default Credentials
- Service account key rotation recommended
- IAM roles: `roles/aiplatform.user`

### Data Privacy
- Comments are processed for linguistic analysis only
- No persistent storage of user data
- Complies with data retention policies

## Troubleshooting

### Common Issues

1. **Permission Denied**
   - Ensure service account has Vertex AI permissions
   - Check project IAM roles

2. **Model Not Found**
   - Verify model name is available in your region
   - Check Vertex AI model deployment status

3. **Timeout Errors**
   - Increase timeout configuration
   - Check network connectivity
   - Monitor API quota usage

4. **Invalid JSON Response**
   - Verify prompt format matches expected structure
   - Check for model hallucination issues

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger('services.analyzer.llm').setLevel(logging.DEBUG)
```

## Future Enhancements

- Multi-model support (Gemini Pro, Flash, Ultra)
- Caching layer for repeated analyses
- Batch processing for high-volume scenarios
- Advanced prompt engineering for better accuracy
- Custom model fine-tuning for domain-specific use cases