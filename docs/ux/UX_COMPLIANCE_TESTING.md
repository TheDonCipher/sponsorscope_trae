# UX Compliance Testing Framework
## SponsorScope.ai Screenshot Audit Validation

**Document Type:** Technical Implementation Guide  
**Version:** 1.0.0  
**Last Updated:** January 17, 2026  

---

## Overview

This framework validates UX compliance for SponsorScope.ai screenshot generation, ensuring:

- ✅ **Watermark Persistence:** Anti-tampering watermarks remain visible in all screenshots
- ✅ **Methodology Version Visibility:** Version identifiers survive cropping attempts  
- ✅ **Probabilistic Framing:** Uncertainty language persists across different screenshot scenarios
- ✅ **Warning Banner Compliance:** Appropriate warnings display for each failure mode
- ✅ **Metadata Standards:** Consistent naming conventions and timestamp inclusion

---

## Test Scenarios

### 1. Private Account Access (UX-001)
**Scenario:** Private Instagram account with login wall blocking comment access
**Expected Warning:** `ACCESS DENIED` 
**Epistemic State:** `LIMITED`
**Validation Points:**
- Warning banner displays "ACCESS DENIED" prominently
- Copy explains "This account is private. We do not analyze private data."
- Watermark includes current date and methodology version
- Evidence count shows 4 public items (no private data)

### 2. Deleted Account Handling (UX-002)
**Scenario:** Deleted or non-existent social media account
**Expected Warning:** `SYSTEM_WARNING`
**Epistemic State:** `INSUFFICIENT`
**Validation Points:**
- System warning for unavailable data
- Zero evidence count (no data available)
- PII-safe (no user data to sanitize)
- Timestamp and version watermark present

### 3. Rate Limiting Response (UX-003)
**Scenario:** Platform rate limiting blocking comment access
**Expected Warning:** `SIGNAL_BLOCKED`
**Epistemic State:** `LIMITED`
**Validation Points:**
- "SCAN PAUSED" warning with throttling explanation
- Evidence count shows 3 available items
- Probabilistic framing maintained despite limitations
- Watermark persistence verified

### 4. Archival Data Usage (UX-004)
**Scenario:** Fallback to archival data when real-time access fails
**Expected Warning:** `SYSTEM_WARNING`
**Epistemic State:** `ROBUST`
**Validation Points:**
- System warning for archival data usage
- 7 evidence items from archival sources
- Clear indication of data source limitations
- Methodology version prominently displayed

### 5. Sparse Data Handling (UX-005)
**Scenario:** Insufficient sample size for statistical confidence
**Expected Warning:** `LOW_SAMPLE_SIZE`
**Epistemic State:** `LIMITED`
**Validation Points:**
- "LOW SAMPLE SIZE" warning with margin of error
- Statistical confidence clearly stated (±15%)
- Evidence count below confidence threshold
- Uncertainty band visualization present

### 6. Comments Disabled (UX-006)
**Scenario:** Creator disabled comments on majority of posts
**Expected Warning:** `SIGNAL_BLOCKED`
**Epistemic State:** `LIMITED`
**Validation Points:**
- "SIGNAL BLOCKED" warning for disabled comments
- 5 evidence items from available sources
- Clear explanation of analysis limitations
- Probabilistic language maintained

---

## Compliance Validation Criteria

### Watermark Persistence Tests
```python
def validate_watermark_persistence(screenshot_path):
    """Verify anti-tampering watermarks remain visible"""
    required_elements = [
        "SponsorScope.ai",           # Platform identifier
        datetime.now().strftime("%Y-%m-%d"),  # Current date
        "v2.4",                      # Methodology version
        "ESTIMATED",                 # Probabilistic framing
        "CONFIDENCE INTERVAL"        # Uncertainty indication
    ]
    
    # OCR-based validation (simulated)
    for element in required_elements:
        if not ocr_detect_element(screenshot_path, element):
            return f"Missing watermark: {element}"
```

### Probabilistic Framing Validation
```python
def validate_probabilistic_framing(screenshot_path):
    """Ensure uncertainty language survives cropping"""
    probabilistic_terms = [
        "Estimated",
        "Confidence Interval", 
        "Signal Strength",
        "Uncertainty",
        "±",
        "Range"
    ]
    
    # Validate terms appear in screenshot
    for term in probabilistic_terms:
        if not ocr_detect_element(screenshot_path, term):
            return f"Missing probabilistic framing: {term}"
```

### Warning Banner Compliance
```python
def validate_warning_display(test_case):
    """Verify appropriate warnings for each scenario"""
    expected_warnings = {
        "blocked": "SIGNAL BLOCKED",
        "sparse": "LOW SAMPLE SIZE", 
        "rate_limit": "SCAN PAUSED",
        "private": "ACCESS DENIED",
        "system": "SYSTEM WARNING"
    }
    
    return expected_warnings.get(test_case.expected_warning)
```

---

## Screenshot Metadata Standards

### Naming Convention
Format: `{timestamp}_{handle}_{platform}_{completeness}_{epistemic}.png`

**Example:** `20260117_103931_test_private_123_instagram_partial_no_comments_limited.png`

**Components:**
- **Timestamp:** `YYYYMMDD_HHMMSS` (ISO 8601 basic format)
- **Handle:** `@username` without @ symbol
- **Platform:** `instagram` or `tiktok`
- **Completeness:** `full`, `partial_no_comments`, `unavailable`, `archival`, `sparse`
- **Epistemic:** `robust`, `limited`, `insufficient`

### Required Metadata Validation
```python
def validate_screenshot_metadata(filename):
    """Validate screenshot naming convention"""
    pattern = r"^(\d{8}_\d{6})_(.+)_(instagram|tiktok)_(\w+)_(\w+)$"
    
    match = re.match(pattern, filename)
    if not match:
        return False, "Invalid filename format"
    
    timestamp, handle, platform, completeness, epistemic = match.groups()
    
    # Validate timestamp format
    datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
    
    return True, "Valid metadata"
```

---

## Risk Assessment Matrix

| Risk Category | Severity | Likelihood | Mitigation Strategy |
|---------------|----------|------------|---------------------|
| **Watermark Removal** | High | Medium | Multi-layer watermarking with OCR-resistant techniques |
| **Context Stripping** | High | High | Mandatory timestamp + version in all screenshots |
| **Misinterpretation** | Medium | High | Persistent probabilistic language in all views |
| **Warning Suppression** | Medium | Low | Non-dismissible warning banners |
| **Metadata Tampering** | Low | Low | Cryptographic validation of screenshot integrity |

---

## Implementation Guidelines

### Frontend Integration
```typescript
// WarningBanner component integration
interface WarningBannerProps {
  type: 'blocked' | 'sparse' | 'rate_limit' | 'private' | 'system';
  platform: 'instagram' | 'tiktok';
  evidenceCount: number;
  timestamp: string;
  version: string;
}

const WarningBanner: React.FC<WarningBannerProps> = ({
  type, platform, evidenceCount, timestamp, version
}) => {
  return (
    <div className={`warning-banner warning-${type}`}>
      <div className="watermark" data-timestamp={timestamp} data-version={version}>
        SponsorScope.ai v{version} • {timestamp}
      </div>
      {/* Warning content */}
    </div>
  );
};
```

### Screenshot Generation Pipeline
```python
async def generate_compliance_screenshot(analysis_result, test_scenario):
    """Generate UX-compliant screenshot with all validations"""
    
    # 1. Apply warning banners based on scenario
    warning_config = get_warning_config(test_scenario)
    
    # 2. Add watermark with timestamp and version
    watermark_data = {
        "platform": "SponsorScope.ai",
        "version": "v2.4",
        "timestamp": datetime.now().isoformat(),
        "epistemic_state": analysis_result.epistemic_state
    }
    
    # 3. Ensure probabilistic framing
    framing_elements = add_probabilistic_framing(analysis_result)
    
    # 4. Validate naming convention
    filename = generate_compliance_filename(analysis_result, test_scenario)
    
    return {
        "screenshot_path": f"docs/audits/{filename}",
        "compliance_validations": run_compliance_checks(filename),
        "metadata": watermark_data
    }
```

---

## Testing Execution

### Automated Compliance Testing
```bash
# Run full UX compliance test suite
python services/governance/ux_compliance_tester.py

# Generate compliance report
python -m services.governance.ux_compliance_tester --generate-report

# Validate specific screenshot
python -m services.governance.ux_compliance_tester --validate-screenshot path/to/screenshot.png
```

### Manual Validation Checklist
- [ ] Watermark contains platform name and current date
- [ ] Methodology version (v2.4) clearly visible
- [ ] Probabilistic language ("Estimated", "Confidence Interval") present
- [ ] Appropriate warning banner for scenario type
- [ ] Epistemic state clearly indicated
- [ ] Evidence count accurate for scenario
- [ ] PII-safe content (no private user data)
- [ ] Timestamp in ISO format within screenshot
- [ ] Platform identification clear
- [ ] Naming convention follows metadata standards

---

## Success Metrics

### Compliance KPIs
- **Watermark Persistence Rate:** 100% of screenshots
- **Warning Display Accuracy:** 100% correct warning type
- **Probabilistic Framing Survival:** 95%+ after cropping
- **Metadata Standards Compliance:** 100% valid naming
- **Version Visibility:** 100% methodology version shown

### Quality Gates
- ✅ All test scenarios pass compliance validation
- ✅ No PII exposure in any screenshot
- ✅ Consistent warning banner implementation
- ✅ Watermark anti-tampering verified
- ✅ Probabilistic framing language persistent

---

**Framework Status:** ✅ **ACTIVE**  
**Last Validation:** January 17, 2026  
**Next Review:** February 17, 2026