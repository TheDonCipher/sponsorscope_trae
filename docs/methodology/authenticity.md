# Audience Authenticity Methodology

**Metric Type:** Probability Floor
**Range:** 0 - 100

## Definition
Estimates the probability that the *active* audience (commenters/likers) consists of independent, organic human users.

## How It's Calculated

We use a "penalty-only" approach. We assume 100% authenticity and deduct points for observed anomalies.

### Key Factors

1.  **Lexical Entropy (Variety)**
    *   **Concept**: Humans rarely repeat the exact same phrase 50 times.
    *   **Detection**: We measure the "entropy" (randomness) of comment text.
    *   *Correction*: Common phrases like "Congrats!" are whitelisted if they match the post context (e.g., a wedding photo).

2.  **Timing Concentration**
    *   **Concept**: Humans do not coordinate to comment at the exact same second.
    *   **Detection**: We flag "bursts" where a statistically improbable number of interactions occur instantly.

3.  **Engagement Reuse (Graph Signal)**
    *   **Concept**: Organic audiences churn. If the exact same 50 users comment on every single post for months, it suggests a "Pod".
    *   **Detection**: We analyze the overlap of commenters across a 30-day window.

## Example Scenarios

### Scenario A: The Viral Hit
*   **Observation**: 10,000 comments in 1 hour.
*   **Analysis**: Timestamps are concentrated, BUT lexical entropy is high (everyone saying different things).
*   **Result**: **High Signal**. (Organic Virality)

### Scenario B: The Engagement Pod
*   **Observation**: 50 comments in 5 minutes.
*   **Analysis**: Timestamps concentrated. Lexical entropy high (unique comments).
*   **Graph Check**: These same 50 users commented on the last 10 posts together.
*   **Result**: **Low Signal**. (Coordinated Behavior)

## What We Do NOT Flag
*   **International Audiences**: Multiple languages are treated as a positive diversity signal.
*   **Short Comments**: Emojis are fine, provided they are not the *only* engagement type.
