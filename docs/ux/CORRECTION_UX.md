# Correction & Rescan UX Design

**Role:** Autonomous Form & Workflow Specialist
**Objective:** Ensure that if our data is wrong, the user feels heard, respected, and empowered to correct it without being treated like a criminal appealing a sentence.

## 1. Principles of the "Right to Reply"

1.  **Assume Technical Error:** The default assumption is that *our algorithm missed something*, not that the user is lying.
2.  **Low Friction:** No "contact support and wait 24 hours." The form should be accessible directly from the report.
3.  **Transparent Queue:** Users should know exactly where their request is.

## 2. Interaction Flow

1.  **Entry Point:** Footer of the Report View -> "Report a Data Discrepancy" (Not "Appeal this Score").
2.  **Selection:** User selects the specific metric (e.g., "Audience Patterns").
3.  **Evidence Submission:** User uploads context (e.g., "I went viral on this date, explaining the spike").
4.  **Confirmation:** "Feedback received. Recalibration scheduled."

## 3. Form Design Specification

### Modal Title: "Improve Data Accuracy"
*   *Bad:* "Appeal Violation"
*   *Good:* "Help us improve this report."

### Fields
1.  **Discrepancy Type:** Dropdown [Missing Data, Timestamp Error, Context Missing, Other].
2.  **Context (Optional):** "Did a specific event trigger this pattern?" (TextArea).
3.  **Verification:** "I certify I am authorized to speak for this account." (Checkbox).

## 4. Status States

| State | Label | Visual | Copy |
| :--- | :--- | :--- | :--- |
| **Pending** | `REVIEWING` | Blue Pulse | "Our team is analyzing your submission against the raw logs." |
| **Accepted** | `RECALIBRATING` | Green Check | "Context accepted. Adjusting baseline for next scan." |
| **Rejected** | `UNCHANGED` | Slate Circle | "The submitted evidence did not statistically alter the finding." |

## 5. Copy & Tone

*   **Confirmation:** "Thank you for the context. We have flagged this report for a priority re-scan. You will be notified if the Epistemic State changes."
*   **Boundaries:** "Note: We cannot manually alter scores. We can only input new parameters into the model."

---
**Next Steps:** Create `CorrectionModal.tsx` and the `CorrectionRequest` page.
