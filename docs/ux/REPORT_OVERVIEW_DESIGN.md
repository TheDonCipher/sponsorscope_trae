# Report Overview Design: SponsorScope.ai

**Role:** Autonomous Product Designer
**Objective:** Design a research-grade dashboard that prioritizes epistemic uncertainty over simplified verdicts.

## 1. Hierarchy & Layout (Wireframe)

```
+-----------------------------------------------------------------------+
|  [Navbar: Search | Methodology | Settings]                            |
+-----------------------------------------------------------------------+
|                                                                       |
|  [EPISTEMIC STATE BANNER: ROBUST DATA (Confidence: High)]             |
|  "Based on 5,000+ data points across 6 months. Margin of error ±2%."  |
|                                                                       |
+-----------------------------------------------------------------------+
|  [Profile Header: @handle | Platform | Last Scanned]                  |
+-----------------------------------------------------------------------+
|                                                                       |
|  [Main Signal Panel]                                                  |
|                                                                       |
|  +---------------------------+  +----------------------------------+  |
|  | Signal Strength           |  | Uncertainty Band                 |  |
|  | [||||||||||......] 72%    |  | [       |-----|       ]          |  |
|  | (Secondary visual)        |  | Range: 68% - 76% (Primary)       |  |
|  +---------------------------+  +----------------------------------+  |
|                                                                       |
+-----------------------------------------------------------------------+
|  [Pillar Breakdown]                                                   |
|                                                                       |
|  +---------------------+  +---------------------+  +----------------+ |
|  | True Engagement     |  | Audience Patterns   |  | Brand Safety   | |
|  | [Graph]             |  | [Graph]             |  | [Graph]        | |
|  | Conf: High          |  | Conf: Medium        |  | Conf: High     | |
|  +---------------------+  +---------------------+  +----------------+ |
|                                                                       |
+-----------------------------------------------------------------------+
|  [Evidence Trail]                                                     |
|  - [Link] Timestamp Cluster detected at 03:00 UTC (View Raw)          |
|  - [Link] Linguistic Repetition > 4.5 sigma (View Raw)                |
+-----------------------------------------------------------------------+
```

## 2. Component List

1.  **Epistemic State Banner**
    *   **Purpose:** Immediate context on data quality.
    *   **States:**
        *   `ROBUST` (High sample size, consistent history) -> Color: Slate/Blue.
        *   `PARTIAL` (Limited history, API restrictions) -> Color: Slate/Yellow-tint.
        *   `FRAGILE` (Low sample size, high variance) -> Color: Slate/Orange-tint.
    *   **Copy:** "Data Integrity: [State]. Confidence Level: [High/Med/Low]."

2.  **Uncertainty Gauge**
    *   **Purpose:** Replace single numbers with ranges.
    *   **Visual:** A box-and-whisker plot style or a progress bar with a blurred edge indicating the margin of error.

3.  **Signal Cards (The Pillars)**
    *   **Constraint:** No large standalone numbers.
    *   **Content:** Small Tufte-style sparklines + Confidence label.

4.  **Evidence List**
    *   **Style:** Terminal/Log style.
    *   **Action:** Click to expand details.

## 3. Copy & Labels (Neutral Language)

| Concept | Old Label ❌ | New Label ✅ |
| :--- | :--- | :--- |
| **Main Metric** | "Trust Score" | "Signal Consistency" |
| **High Score** | "Verified / Real" | "High Organic Probability" |
| **Low Score** | "Fake / Bot" | "Anomalous Pattern Detected" |
| **Verdict** | "Pass / Fail" | "Within/Outside Expected Variance" |
| **Confidence** | (Hidden) | "Confidence Interval: ±X%" |

## 4. Color Palette (Cognitive Guardrails)

*   **Primary Action:** `#3b82f6` (Royal Blue) - Neutral, professional.
*   **Data/Neutral:** `#94a3b8` (Slate 400).
*   **Anomaly:** `#8b5cf6` (Violet) - Distinct from "Error" (Red).
*   **Background:** `#0f172a` (Slate 900) - Dark mode default.

---
**Next Steps:** Implement this design in `ReportView.tsx`.
