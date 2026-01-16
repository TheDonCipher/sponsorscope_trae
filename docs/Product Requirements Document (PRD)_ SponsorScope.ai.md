# Product Requirements Document (PRD): SponsorScope.ai

**Version:** 1.1  
**Status:** Final - Incorporating Structural Improvements  
**Project Goal:** Build a public, open-access influencer intelligence dashboard that provides verifiable, evidence-backed analysis of influencer credibility, audience quality, and brand safety.

---

## 1. Executive Summary
SponsorScope.ai is a public utility for the influencer economy, transforming raw social media data into transparent, sponsor-ready research reports. It operates as an independent analytics bureau, providing a fixed, globally transparent scoring model to enable due diligence without barriers.

## 2. Problem Statement
*   **Vanity Metric Deception:** Follower counts are easily manipulated, creating information asymmetry.
*   **Credibility Gap:** Lack of tools to differentiate authentic influence from fabricated popularity.
*   **Opacity in Reporting:** Existing solutions are "black boxes" or hidden behind paywalls.
*   **Market Information Failure:** No public, standards-based repository for influence quality exists.

## 3. Target Users
*   **Brand Managers:** Vet influencer partners and demonstrate due diligence.
*   **Agency Leads:** Compare influencer options for client pitches with data-backed justifications.
*   **Public Researchers:** Journalists and academics studying influencer economy trends.

## 4. Core User Flows
### 4.1. Influencer Search & Instant Report
1. User enters an influencer handle (e.g., `@creator_bw`).
2. System returns a cached report (within 7 days) or triggers an on-demand scan.
3. Report displays a 4-pillar summary, raw metrics, and an evidence trail.

### 4.2. Comparison Mode
1. User selects "Compare" and enters up to 3 handles.
2. System renders a side-by-side table of scores, metrics, and risk flags.

### 4.3. Evidence Deep Dive
1. User clicks "View Evidence" on any specific score or risk flag.
2. Modal displays sample comments, post snippets, and statistical summaries.

## 5. MVP Feature Set
### 5.1. Analysis Engine (Hybrid Model)
*   **On-Demand Scraping:** Instagram and TikTok public profile scraping (last 30 posts + top comments).
*   **4-Pillar Scoring (Empirically Justified):**
    *   **True Engagement Score (40%):** Weighted ratio (Comments × 3 vs Likes × 1). Justified by higher intent signaling in comments.
    *   **Audience Authenticity (30%):** Bot detection via statistical heuristics (entropy, velocity) + Gemini refinement.
    *   **Brand Safety Grade (20%):** Toxicity analysis (A-F). Includes "Research Context" banner to mitigate reputational risk.
    *   **Niche Credibility (10%):** Alignment between content and stated category via cosine similarity.
*   **Evidence Linking:** Direct links to source data for every score.

### 5.2. Transparency & Governance
*   **Methodology Appendix:** Publicly documented rationale for all weights and thresholds.
*   **Confidence Intervals:** Display uncertainty bands on scores to reflect data completeness.
*   **Correction Mechanism:** Public log for correction requests to maintain epistemic integrity.
*   **Graceful Degradation:** Explicitly flag reports as "Partial" or "Archival" if scraping is restricted.

## 6. Out of Scope
*   User registration, private dashboards, or monetization.
*   Influencer discovery/recommendation engine.
*   Automated continuous monitoring (MVP is on-demand only).

## 7. Success Metrics (KPIs)
| KPI | Target |
| :--- | :--- |
| **Cached Report Latency** | < 1.5 seconds |
| **Fresh Scan Latency** | < 2 minutes |
| **Bot Detection Accuracy** | > 90% precision |
| **Scraping Success Rate** | > 95% |

## 8. Constraints & Risks
*   **Google Native:** Must operate within GCP (Cloud Run, Firestore, Vertex AI).
*   **Legal Exposure:** Mitigated via "Research Context" banners, confidence intervals, and public methodology.
*   **Scraping Resilience:** System must degrade gracefully (e.g., "Text-only analysis") when platforms block media.

## 9. Standards Governance
SponsorScope.ai aims to be the reference schema for influencer due diligence.
*   **Methodology Versioning:** All reports are tagged with a version (e.g., v1.0).
*   **Regional Calibration:** Botswana serves as the primary validation environment and ground-truth audit pool before global expansion.
