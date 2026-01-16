# Deployment Checklist

**Last Updated:** 2026-01-16

## 1. Environment Configuration
*   [ ] **Prod/Staging Separation**: Ensure `STAGING` env vars are distinct from `PROD`.
*   [ ] **Secrets Management**: All API keys (Instagram, OpenAI) must be injected via Secret Manager (e.g., AWS Secrets Manager, GSM), NOT env vars directly.
*   [ ] **Kill Switch Default**: Verify `KILL_SWITCH_SCANS=enabled` and `KILL_SWITCH_READ=enabled` are set in prod.

## 2. Infrastructure Scaling
*   [ ] **Rate Limiting**: Configure Cloud Load Balancer / API Gateway to cap requests at 100/min per IP.
*   [ ] **Budget Alerts**: Set GCP/AWS budget alerts at 50%, 75%, and 90% of monthly cap ($500 for MVP).
*   [ ] **Auto-Scaling**: Configure Cloud Run / Lambda max instances to prevent runaway costs (Cap at 10 concurrent instances).

## 3. Observability
*   [ ] **Logging**: Ensure structured JSON logging is enabled for all services.
*   [ ] **Error Tracking**: Connect Sentry or equivalent.
*   [ ] **Metrics**: Dashboard for "Successful Scans", "Failed Scans", "Cache Hit Rate".

## 4. Legal & Compliance
*   [ ] **Terms of Service**: Link to `docs/legal/terms_of_service.md` must be visible in footer.
*   [ ] **Media Guidelines**: Link to `docs/legal/media_guidelines.md` must be visible.
*   [ ] **GDPR/CCPA**: Ensure "Right to Erasure" workflow is documented internally.

## 5. Final Smoke Test
*   [ ] **Kill Switch Drill**: Toggle `KILL_SWITCH_SCANS=disabled` in staging and verify 503 response.
*   [ ] **Partial Data Drill**: Simulate a blocked profile and verify "Partial Data" banner appears.
*   [ ] **Report Rendering**: Check visual rendering of Confidence Intervals on mobile.

**GO/NO-GO DECISION**: Only proceed if all checks are PASS.
