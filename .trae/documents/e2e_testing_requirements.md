# E2E Live-Data Testing Requirements

## 1. Test Overview

This document outlines the comprehensive end-to-end testing requirements for SponsorScope.ai's live-data pipeline, covering real social data ingestion, LLM calibration verification, and report generation with safety constraints.

## 2. Test Scope

### 2.1 Real Social Data Ingestion
- **Playwright Adapter Testing**: Verify Instagram and TikTok scrapers handle live platform data
- **Data Completeness Validation**: Test partial data scenarios and warning rendering
- **Failure Recovery**: Validate graceful degradation when platforms block access

### 2.2 Frontend Report Rendering
- **Warning Banner Display**: Verify partial data warnings render correctly in ReportView.tsx
- **Epistemic State Visualization**: Test confidence meters and uncertainty bands
- **Data Sharing Safety**: Ensure no PII exposure beyond public links and excerpts

### 2.3 LLM Calibration Verification
- **Adjustment Bounds**: Verify LLM adjustments are bounded at ±15% as per calibration engine
- **Confidence Recalibration**: Test confidence score adjustments based on signal strength
- **Multi-Signal Corroboration**: Validate requirement for ≥2 signals >0.7 threshold

## 3. Test Scenarios

### 3.1 Successful Full Data Ingestion
```
Input: Public Instagram handle with full access
Expected: 
- DataCompleteness.FULL status
- No warning banners in ReportView
- All four pillar scores displayed
- Complete evidence trail
```

### 3.2 Partial Data Scenarios
```
Input: Handle with comments blocked
Expected:
- DataCompleteness.PARTIAL_NO_COMMENTS status
- WarningBanner type="blocked" displayed
- Adjusted confidence scores
- Limited evidence trail
```

### 3.3 Platform Blocking
```
Input: Handle triggering rate limiting
Expected:
- DataCompleteness.UNAVAILABLE status
- System warning banner displayed
- Graceful fallback to archival data if available
- Clear error messaging to user
```

## 4. Verification Checkpoints

### 4.1 Playwright Adapter Verification
- [ ] Browser initialization with stealth settings
- [ ] Blocking mechanism detection (login walls, rate limits, captchas)
- [ ] Profile data extraction across multiple strategies
- [ ] Post and comment extraction with error handling
- [ ] Session metadata logging for audit trail

### 4.2 ReportView.tsx Rendering
- [ ] Warning banner conditional rendering based on data_completeness
- [ ] Confidence meter accuracy (±15% bounds verification)
- [ ] Uncertainty band calculation and display
- [ ] Evidence card rendering with proper PII filtering
- [ ] Share functionality with watermarking and timestamping

### 4.3 LLM Calibration Engine
- [ ] Score adjustment bounds enforcement (max 15% reduction)
- [ ] Confidence penalty application before score adjustment
- [ ] Multi-signal corroboration requirement (≥2 signals >0.7)
- [ ] Uncertainty band width calculation based on confidence
- [ ] Suppressed signals tracking for audit trail

## 5. Output Requirements

### 5.1 Screenshot Audit Documentation
**Location**: `docs/audits/`
**Naming Convention**: `{timestamp}_{handle}_{platform}_{completeness_status}.png`
**Required Elements**:
- Full viewport capture of ReportView
- Visible warning banners (if applicable)
- Confidence meters and uncertainty bands
- Epistemic state banner with data points count
- Ghost watermark overlay for anti-tampering

### 5.2 Failure Log Structure
**Location**: `services/governance/logs/sessions.jsonl`
**Format**: JSONL with structured error data
**Required Fields**:
```json
{
  "handle": "test_handle",
  "platform": "instagram",
  "scraped_at": "2026-01-17T10:30:00Z",
  "ip_session": "session_id",
  "failure_reason": "Rate limiting detected",
  "data_completeness": "partial_no_comments",
  "browser_version": "Chrome/120.0.0.0",
  "session_metadata": {}
}
```

### 5.3 Launch Readiness Statement
**Template Structure**:
```
LAUNCH READINESS ASSESSMENT
Date: {timestamp}
Tested Handles: {count} across {platforms}

Epistemic State Summary:
- ROBUST: {count} handles with >80% confidence
- LIMITED: {count} handles with 50-80% confidence
- INSUFFICIENT: {count} handles with <50% confidence

Data Completeness Distribution:
- FULL: {percentage}% of tested handles
- PARTIAL_NO_COMMENTS: {percentage}%
- PARTIAL_NO_IMAGES: {percentage}%
- UNAVAILABLE: {percentage}%

LLM Calibration Verification:
- Adjustments within ±15% bounds: {verified}/{total}
- Confidence recalibration applied: {count}
- Multi-signal corroboration passed: {count}

Recommendation: {GO/NO-GO} for production deployment
```

## 6. Test Data Requirements

### 6.1 Handle Selection Criteria
- **Public profiles** with varying engagement levels
- **Mixed platform coverage** (Instagram, TikTok)
- **Varied account types** (personal, business, creator)
- **Known edge cases** (private accounts, deleted accounts, rate-limited)

### 6.2 Success Metrics
- **Data ingestion success rate**: ≥90% for public profiles
- **Report generation time**: ≤2 minutes per handle
- **Warning accuracy**: 100% correlation between data_completeness and banner display
- **LLM adjustment compliance**: 100% within ±15% bounds
- **PII exposure**: Zero incidents of private data leakage

## 7. Continuous Monitoring

### 7.1 Post-Launch Verification
- Daily automated E2E tests on rotating handle set
- Weekly manual audit of screenshot documentation
- Monthly review of failure logs for pattern analysis
- Quarterly recalibration of LLM bounds based on performance data

### 7.2 Alert Conditions
- Data ingestion success rate drops below 85%
- Average report generation time exceeds 3 minutes
- LLM adjustments exceed ±15% bounds in >5% of cases
- PII exposure incident detected
- Platform API changes affecting scraper functionality