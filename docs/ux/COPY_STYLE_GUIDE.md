# Language & Copy Governance: SponsorScope.ai

**Role:** Autonomous UX Writer & Risk Editor
**Objective:** Eliminate accusatory language. Enforce epistemic humility.

## 1. The Core Philosophy: "The Thermometer Principle"
SponsorScope is a thermometer, not a judge. A thermometer tells you the temperature is 102°F; it does not accuse you of having a fever to get out of work.
*   **We report data (Facts).**
*   **We highlight patterns (Observations).**
*   **We do NOT assign intent (Judgments).**

## 2. Banned vs. Approved Lexicon

| Banned Word ❌ | Why? | Approved Replacement ✅ |
| :--- | :--- | :--- |
| **"Fake"** | Implies intent to deceive. A creator might have "fake" followers they didn't buy (bot spam). | "Anomalous", "Non-Organic", "Inauthentic Pattern" |
| **"Fraud"** | A legal term. We are not a court. | "Signal Discrepancy", "Policy Violation" |
| **"Bot"** | Dehumanizing and overused. | "Automated Activity", "High-Velocity Account", "Scripted Pattern" |
| **"Manipulated"** | Accusatory. | "Statistically Atypical", "Deviates from Baseline" |
| **"Real"** | Vague. | "Organic", "Human-Consistent" |
| **"Verdict"** | Implies a final judgment. | "Assessment", "Analysis Summary" |
| **"Clean"** | Implies moral purity. | "Baseline Consistent", "Within Expected Range" |

## 3. Approved Glossary

*   **Epistemic Uncertainty:** The state of not knowing. We always explicitly state when we don't know something.
*   **Signal Consistency:** The degree to which engagement metrics (likes, comments) match the expected distribution for the follower count.
*   **Audience Patterns:** The behavioral clusters observed in the follower base (e.g., "Day-trading timestamps").
*   **Confidence Interval:** The statistical probability that our sample represents the whole.
*   **Artifact:** A specific piece of evidence (e.g., a single comment string).

## 4. Error Message Templates

### Scenario: Low Confidence Data
*   *Bad:* "This report is inaccurate because the account is too small."
*   *Good:* "Confidence is limited by sample size. Findings should be treated as directional estimates."

### Scenario: Private Account
*   *Bad:* "You can't scan this account."
*   *Good:* "Public signal analysis is unavailable. This account has privacy settings enabled."

### Scenario: System Error
*   *Bad:* "We failed to analyze the account."
*   *Good:* "The analysis could not be completed. The external data source is currently unresponsive."

## 5. Tone Guidelines

1.  **Passive Observation:** Prefer "Patterns were observed" over "The user did X".
2.  **Conditional Truth:** Use "appears to," "suggests," and "indicates" rather than "is."
    *   *Example:* "This *suggests* automated activity" (Correct) vs "This *is* a bot farm" (Incorrect).
3.  **No Alarmism:** Avoid exclamation marks (!). Use neutral colors.

---
**Implementation Checklist:**
- [ ] Run grep scan for "fake", "bot", "fraud" in frontend codebase.
- [ ] Update tooltip copy to match glossary.
