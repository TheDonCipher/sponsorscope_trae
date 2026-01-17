# SponsorScope.ai Comprehensive Testing Suite

A comprehensive testing suite designed to validate SponsorScope.ai's **epistemic integrity, UX discipline, and governance safety**. This suite treats the system as **high-risk for misinterpretation** and verifies that it behaves probabilistically, degrades honestly, and resists misuse.

## 🎯 Testing Philosophy

The testing suite is built on these core principles:

- **Tests must verify what the system does and what it refuses to do**
- **Absence of data must never be masked**
- **Failures must be explicit and user-visible**
- **Time, confidence, and uncertainty must be honest**
- **Any test that passes while increasing implied certainty is invalid**

## 🧪 Test Layers

### 1. UNIT TESTS - Determinism & Bounds
Tests heuristic functions, calibration logic, and confidence computation:
- ✅ Identical input → identical output
- ✅ No heuristic can inflate scores
- ✅ LLM adjustments never exceed ±15
- ✅ Confidence never increases under partial data

### 2. CONTRACT TESTS - API Honesty
Tests POST /analyze, GET /status/{job_id}, GET /report/{job_id}:
- ✅ Correct HTTP codes (202, 200, 410, 503)
- ✅ Schema stability
- ✅ Warning banners always propagate to frontend

### 3. ASYNC PIPELINE TESTS - Time Truth
Tests normal scrape, slow scrape, and scraper failure scenarios:
- ✅ No blocking requests
- ✅ Polling respects backoff
- ✅ Jobs are idempotent
- ✅ TTL cleanup works

### 4. SCRAPER REALITY TESTS - Resistance & Degradation
Tests Instagram and TikTok platforms with various scenarios:
- ✅ Detection over bypass
- ✅ Accurate DataCompleteness states
- ✅ Zero fabricated data

### 5. LLM SAFETY TESTS - Authority Containment
Tests sarcasm, cultural slang, mixed sentiment, provocative language:
- ✅ LLM output is advisory
- ✅ Reasoning is logged
- ✅ Failure falls back safely

### 6. UX TESTS - Interpretive Safety
Tests petition-style search, partial data report, withdrawal mid-analysis:
- ✅ Uncertainty shown before signal
- ✅ No verdict language
- ✅ Warnings are non-dismissible

### 7. MISUSE & ADVERSARIAL TESTS
Tests screenshot cropping, selective sharing, malicious repeated requests:
- ✅ Watermarks persist
- ✅ Methodology visible
- ✅ Abuse throttled

### 8. GOVERNANCE & ETHICS TESTS
Tests rate limits, kill switch, PII protection, audit logs:
- ✅ Rate limits trigger correctly
- ✅ Kill switch works
- ✅ PII never exposed
- ✅ Audit logs are complete

### 9. PERFORMANCE & STRESS TESTS
Tests concurrent analysis requests, LLM token pressure:
- ✅ Graceful degradation
- ✅ Cost caps enforced
- ✅ No cascading failures

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- SponsorScope.ai API server running
- Required Python packages (install via requirements.txt)

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Ensure API server is running
uvicorn services.api.main:app --reload
```

### Run All Tests
```bash
# Run comprehensive test suite
python comprehensive_test_runner.py

# Run with custom API URL
python comprehensive_test_runner.py --base-url http://your-api-url:8000
```

### Run Individual Test Suites
```bash
# Run specific test suite
python -m unittest unit_tests.test_heuristic_determinism -v
python -m unittest contract_tests.test_api_contracts -v
python -m unittest async_tests.test_async_pipeline -v
python -m unittest scraper_tests.test_platform_resistance -v
python -m unittest llm_tests.test_llm_safety -v
```

## 📊 Test Results

The test suite generates:
- **JSON Report**: Detailed test results with all pass/fail information
- **Markdown Report**: Human-readable summary with recommendations
- **Failure Matrix**: Comprehensive list of all test scenarios and expected outcomes
- **Final Declaration**: Signed statement of system readiness

## 🛑 Hard Stop Conditions

The following conditions automatically fail the entire system:

1. **Any test increases implied certainty**
2. **Any failure is silent**
3. **Any report renders without uncertainty context**
4. **Fabrication of any data**
5. **Privacy breach (PII exposure)**
6. **Ethical violation**
7. **Safety bypass**

## 📋 Certification Requirements

For system certification, the following must be met:

- ✅ **No CRITICAL severity failures**
- ✅ **No Hard Stop condition violations**
- ✅ **Overall score ≥ 80/100**
- ✅ **All HIGH severity issues documented with mitigation plan**
- ✅ **Test coverage ≥ 90% of critical paths**

## 📁 File Structure

```
tests/comprehensive/
├── __init__.py
├── comprehensive_test_runner.py      # Main test orchestrator
├── failure_matrix.md                 # Test scenarios and failure conditions
├── README.md                         # This file
├── unit_tests/                       # Unit test implementations
│   ├── __init__.py
│   └── test_heuristic_determinism.py
├── contract_tests/                   # API contract tests
│   ├── __init__.py
│   └── test_api_contracts.py
├── async_tests/                      # Async pipeline tests
│   ├── __init__.py
│   └── test_async_pipeline.py
├── scraper_tests/                    # Platform resistance tests
│   ├── __init__.py
│   └── test_platform_resistance.py
└── llm_tests/                        # LLM safety tests
    ├── __init__.py
    └── test_llm_safety.py
```

## 🔧 Configuration

### API Configuration
Set the API base URL via command line:
```bash
python comprehensive_test_runner.py --base-url http://your-api:8000
```

### Test Timeouts
Adjust timeouts in individual test files:
```python
self.max_poll_time = 60  # Maximum seconds for job completion
self.poll_interval = 1.0  # Seconds between status polls
```

### Test Data
Modify test handles and scenarios in test files to match your test environment.

## 📈 Interpreting Results

### Test Output
```
🚀 Starting Comprehensive SponsorScope.ai Testing Suite
================================================================================
🧪 Running UNIT TESTS - Determinism & Bounds
================================================================================
test_entropy_calculation_determinism (__main__.TestHeuristicDeterminism) ... ok
test_uniqueness_ratio_determinism (__main__.TestHeuristicDeterminism) ... ok
...
✅ UNIT TESTS - Determinism & Bounds completed with status: passed
```

### Final Declaration
The test suite issues a final declaration based on results:

- ✅ **EXCELLENT**: System demonstrates excellent epistemic integrity
- ✅ **GOOD**: System shows good performance with minor improvements needed
- ⚠️ **ADEQUATE**: System is adequate but requires attention
- ⚠️ **NEEDS_ATTENTION**: System has significant issues
- ❌ **CRITICAL**: System is critically compromised

### Certification Statement
```
✅ SYSTEM CERTIFICATION STATEMENT

"This system behaves probabilistically, degrades honestly, and resists misuse under tested conditions."
```

## 🔍 Troubleshooting

### API Connection Issues
```bash
# Check if API server is running
curl http://localhost:8000/health

# Expected response: {"status": "ok"}
```

### Test Failures
1. **Check API server logs** for error details
2. **Verify test data** matches your environment
3. **Review failure matrix** for expected behavior
4. **Check hard stop conditions** for critical issues

### Performance Issues
- Increase timeouts for slow environments
- Reduce concurrent test load
- Check system resources

## 🤝 Contributing

When adding new tests:
1. Follow the existing test structure
2. Include appropriate severity levels
3. Update the failure matrix
4. Test both success and failure paths
5. Ensure tests are deterministic

## 📞 Support

For issues with the testing suite:
1. Check existing test outputs and logs
2. Review the failure matrix for guidance
3. Verify API server configuration
4. Consult the comprehensive test report

---

**Remember**: This testing suite is designed to prove that SponsorScope.ai maintains **epistemic integrity** - it must be honest about what it knows, what it doesn't know, and how certain it is about its conclusions.**