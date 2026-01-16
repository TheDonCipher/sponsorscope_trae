# Go / Pause / Iterate Criteria

**Decision Date:** Day 30

## 🟢 GO (Expand to South Africa)
*   Zero legal threats.
*   Correction rate < 5%.
*   Agencies successfully use "Signal Strength" in campaigns without confusion.
*   Infrastructure costs < $500.

## 🟡 PAUSE (Extend Pilot 30 Days)
*   High dispute rate (> 10%) due to "Partial Data". -> **Fix**: Improve scraper resilience.
*   Journalists use "Fake Follower" terminology. -> **Fix**: Harder watermarks, stricter media guidelines.
*   LLM misses local slang. -> **Fix**: Fine-tune model on local dataset.

## 🔴 STOP (Kill Switch)
*   **Safety Incident**: An influencer is harassed/doxxed based on our report.
*   **Legal Injunction**: Received C&D.
*   **Cost Explosion**: Scraper loop burns > $1000 in a week.

**Action on STOP**:
1.  Enable `KILL_SWITCH_READ`.
2.  Email all participants: "Pilot Concluded".
3.  Delete all non-anonymized data.
