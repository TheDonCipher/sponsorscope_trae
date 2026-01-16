# Feedback Loop Design

**Method:** In-App Feedback Widget & Weekly Surveys

## 1. The "Dispute" Widget (In-App)
*   **Trigger**: User clicks "Report Issue" on a report.
*   **Data Captured**: Handle, Issue Type, User Comment.
*   **Routing**: Sent immediately to `dev-team` Slack channel (during pilot).

## 2. The "Interpretation" Survey (Weekly)
Sent to Group B (Agencies) to test if they understand the signals.

**Question 1**: "You see a signal of 45 ± 15. What does this mean?"
*   A) The influencer is a fraud. (FAIL)
*   B) The influencer has low engagement. (FAIL)
*   C) The system has insufficient data to be sure. (PASS)

**Question 2**: "The 'Authenticity' signal is low. Why?"
*   A) They bought bots. (FAIL)
*   B) Observed patterns match automated behavior, but intent is unknown. (PASS)

*Action*: If > 20% fail this quiz, we must rewrite the `ScoreExplanation` component.

## 3. The "Journalist" Hotline
*   Direct WhatsApp line to the Lead Engineer for fact-checking before publication.
*   Mandatory pre-publish review of technical claims (not editorial control, just fact-checking).
