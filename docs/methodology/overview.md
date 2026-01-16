# SponsorScope Signal Overview

**Version:** 2.3
**Last Updated:** 2026-01-16

## What is the SponsorScope Signal?

The **SponsorScope Signal** (formerly "Score") is a **probabilistic credibility index** ranging from 0 to 100. It estimates the likelihood that an influencer's audience engagement is organic, safe, and valuable for sponsors.

### It IS:
*   ✅ A statistical estimate based on public data.
*   ✅ A measure of consistency with organic growth patterns.
*   ✅ A tool for risk management.

### It is NOT:
*   ❌ A judgment of an influencer's character.
*   ❌ A detection of "fake followers" (we do not use that term).
*   ❌ A guarantee of campaign performance.

---

## How It Works

Our system analyzes public interactions using three independent layers:

1.  **Heuristics (The Math)**:
    *   Measures raw engagement rates, comment entropy (variety), and timing variance.
    *   *Example:* If 500 comments arrive in the same minute, entropy drops, lowering the signal.

2.  **Graph Intelligence (The Network)**:
    *   Analyzes anonymous coordination patterns.
    *   *Example:* If a group of users consistently interacts with the same cluster of creators, it may indicate a "pod" (coordinated support group).

3.  **LLM Refinement (The Context)**:
    *   Uses advanced AI to understand slang, sarcasm, and cultural nuance.
    *   *Example:* "I hate you (affectionate)" is recognized as positive engagement, not toxicity.

---

## Interpreting the Signal

| Signal Strength | Interpretation | Action |
| :--- | :--- | :--- |
| **80 - 100** | **High Confidence** | Consistent with organic, high-value engagement. |
| **60 - 79** | **Moderate Confidence** | Generally organic, with some statistical anomalies. |
| **40 - 59** | **Low Confidence** | Significant atypical patterns detected. Manual review recommended. |
| **0 - 39** | **Very Low Confidence** | Highly coordinated or atypical behavior observed. |

### Understanding Uncertainty
You will always see a range (e.g., **74 ± 9**).
*   A **wide range** (±15) means we have partial data or conflicting signals.
*   A **narrow range** (±3) means all signals corroborate each other.

---

## Limitations

*   **AI-Generated Content**: Advanced LLM-generated comments may mimic organic speech patterns well enough to evade detection.
*   **Private Data**: We do not access private DMs or stories, which may contain authentic engagement.
*   **Platform Blocks**: If a platform restricts our access, we report "Partial Data" rather than guessing.
