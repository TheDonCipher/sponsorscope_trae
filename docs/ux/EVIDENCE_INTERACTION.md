# Evidence-First Interaction Design

**Role:** Autonomous Interaction Designer
**Objective:** Prove the claim before explaining the claim. Users should never have to trust the algorithm blindly.

## 1. Interaction Flows

### Flow A: The "Why?" Click
1.  **Trigger:** User clicks on a metric flagged as "Low Confidence" or "Anomaly Detected" (e.g., in the `UncertaintyBand` label).
2.  **Action:** The row expands (accordion style) or a side-drawer slides out.
3.  **Content Priority:**
    *   **Level 1 (Immediate):** The raw artifact. "Here are the 50 comments that triggered this flag."
    *   **Level 2 (Context):** The pattern. "Notice they all arrived within 3 seconds."
    *   **Level 3 (Explanation):** The algorithm. "This exceeds the standard deviation for human typing speed."

### Flow B: The Evidence Trail
1.  **Trigger:** User scrolls to the "Evidence Trail" feed at the bottom of the report.
2.  **Action:** Infinite scroll of raw data points.
3.  **Interaction:** Hovering over an item highlights the corresponding spike on the main engagement chart (Cross-linking).

## 2. Evidence Card Design

A reusable `<EvidenceCard />` component that acts as a "digital exhibit."

*   **Header:**
    *   Type Icon (e.g., `comment`, `timestamp`, `network`).
    *   Severity Indicator (Neutral/Warning/Critical - using neutral colors).
    *   Timestamp (Absolute + Relative).
*   **Body (The Raw Data):**
    *   **Text:** Monospace font for exact raw text.
    *   **Visual:** Mini-histogram for timestamp clusters.
    *   **Network:** Mini-graph for circular referencing.
*   **Footer:**
    *   **Source Link:** "View on Instagram" (External icon).
    *   **Verify Action:** "Flag as False Positive" (Correction loop).

## 3. States

### 3.1 Loading State
*   Skeleton loader that mimics the shape of a social media post (avatar, lines of text).
*   Copy: "Retrieving raw artifacts..."

### 3.2 Empty / Missing Evidence
*   **Scenario:** A score is low, but the specific evidence is private or deleted.
*   **Design:**
    *   Greyed out card.
    *   Icon: `visibility_off`.
    *   Copy: "Primary evidence is no longer publicly accessible. Score based on cached metadata."
    *   Action: "Learn about metadata analysis."

## 4. Accessibility & Safety

*   **External Links:** Must always use `rel="noopener noreferrer"` and include a visual "External" icon.
*   **Content Warnings:** If the evidence contains hate speech or toxicity, blur it by default with a "Show Content" toggle.

---
**Next Steps:** Implement `<EvidenceCard />` and the expandable logic in `ReportView`.
