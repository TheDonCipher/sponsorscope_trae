# UX Philosophy: SponsorScope.ai

**Role:** High-Stakes Interpretation System
**Objective:** Prevent Authority Bias & Enforce Cognitive Guardrails

## Core Principles

### 1. Evidence Before Conclusions
*   **Philosophy:** Users must process the raw data *before* being handed a judgment.
*   **Implementation:** Never show a "Score" or "Verdict" on the initial load. Show the *signal distribution* (e.g., "70% of comments match organic linguistic patterns") first. The summary score should require a scroll or a click, or be visually secondary.

### 2. Confidence Before Magnitude
*   **Philosophy:** A strong claim with weak data is misinformation.
*   **Implementation:** Always couple metrics with their confidence interval or sample size reliability.
    *   *Bad:* "Fake Follower Count: 50,000"
    *   *Good:* "Anomaly Detected: ~50k accounts (Confidence: Low, based on limited sample)"

### 3. Uncertainty Over Precision
*   **Philosophy:** False precision creates false trust.
*   **Implementation:** Use ranges and probabilities instead of absolutes.
    *   *Avoid:* "12.5% Bot Rate"
    *   *Prefer:* "Estimated Anomaly Range: 10-15%"

### 4. Neutral Language Everywhere
*   **Philosophy:** Our tool is a thermometer, not a judge.
*   **Implementation:**
    *   Replace "Fake" with "Anomalous"
    *   Replace "Bot" with "Non-Organic Pattern"
    *   Replace "Fraud" with "Signal Discrepancy"

---

## Design Rules (Do/Do-Not)

| Feature | DO ✅ | DO NOT ❌ |
| :--- | :--- | :--- |
| **Score Display** | Show score as a composite of signals. | Show a giant green/red "Pass/Fail" stamp. |
| **Color Palette** | Use neutral blues, purples, and slate grays. | Use alarmist reds or "safe" greens for subjective metrics. |
| **Loading States** | Explain *what* is being analyzed ("Parsing timestamps..."). | Show a generic spinner that implies a black box. |
| **Empty States** | "Insufficient data to form a conclusion." | "Score: 0" or "No Risks Found." |
| **Tooltips** | Explain the *methodology* (e.g., "Calculated via Benford's Law"). | Explain the *meaning* (e.g., "This means they are cheating"). |

---

## Visual Hierarchy Rules

1.  **Primary Layer (The Data):**
    *   Raw histograms (Comment length distribution).
    *   Time-series graphs (Engagement velocity).
    *   These must be the most prominent visual elements.

2.  **Secondary Layer (The Context):**
    *   Benchmarks ("Average for this niche is X").
    *   Sample size warnings ("Based on last 50 posts").

3.  **Tertiary Layer (The Synthesis):**
    *   The "SponsorScope Score".
    *   The "Verdict" or "Summary".
    *   *Constraint:* This layer must never appear 'above the fold' without data context.

---

## Cognitive Guardrails

*   **Friction on Judgment:** Before a user can export a "Risk Report," they must acknowledge the confidence level.
*   **The "Why" Toggle:** Every metric must have an expandable "Why?" section that reveals the raw signal source (e.g., "Why is this flagged? -> 90% of comments share identical timestamps").
