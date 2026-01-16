# Incident Runbook: SponsorScope.ai

**Severity Levels:**
*   **SEV-1 (Critical)**: Data leak, legal threat, massive cost spike.
*   **SEV-2 (Major)**: Core scraping blocked, LLM outage.
*   **SEV-3 (Minor)**: UI glitch, slow performance.

## Scenario A: Massive Traffic Spike (Media Event)
**Trigger**: Viral tweet or news article links to a report.
**Symptoms**: Latency > 2s, 5xx errors, cost alert triggered.
**Action**:
1.  **Enable Cache-Only Mode**: Set `KILL_SWITCH_SCANS=disabled`.
    *   *Effect*: Users can see existing reports but cannot generate new ones. Saves DB/Scraper costs.
2.  **Scale Read Replicas**: If DB is bottleneck, increase read replicas.
3.  **CDN Caching**: Ensure static assets and report JSONs are cached at Cloudflare/Edge.

## Scenario B: Platform Block (Instagram/TikTok)
**Trigger**: "Scraper blocked" errors spike > 10%.
**Action**:
1.  **Pause Scraper**: Set `KILL_SWITCH_SCANS=disabled` immediately to prevent IP burning.
2.  **Rotate Proxies**: Trigger proxy rotation in scraper infrastructure.
3.  **Slow Down**: Reduce concurrency limit in `services/orchestrator`.
4.  **Resume**: Re-enable scans in "Staging" first to verify fix.

## Scenario C: LLM Hallucination / Failure
**Trigger**: Users report "nonsense" scores or scores > 100.
**Action**:
1.  **Disable LLM Refinement**: Set env var `ENABLE_LLM_REFINEMENT=false`.
    *   *Effect*: System falls back to Heuristic-only scores (Safe mode).
2.  **Investigate**: Check OpenAI/Gemini logs for prompt injection or model drift.

## Scenario D: Legal Takedown Request
**Trigger**: Cease & Desist letter received.
**Action**:
1.  **Manual Takedown**: Use admin tool to delete report `DELETE /admin/report/{handle}`.
2.  **Blacklist**: Add handle to `BLACKLISTED_HANDLES` env var.
    *   *Effect*: Future attempts to scan this handle return 404 or "Unavailable".
3.  **Reply**: "We have removed the public report as a courtesy." (Standard legal template).

## Emergency Contacts
*   **Lead Engineer**: [Phone Number]
*   **Legal Counsel**: [Email]
