# Information Architecture: SponsorScope.ai

**Role:** Autonomous Information Architect
**Objective:** Define page structure, navigation logic, and URL conventions to ensure transparency and prevent dead ends.

## 1. Site Map

```mermaid
graph TD
    A[Home / Search] -->|Enter Handle| B[Report Overview]
    A --> C[Methodology]
    A --> D[Pricing]
    A --> E[Docs / Research Context]
    
    B -->|Click Metric| F[Evidence Deep Dive]
    B -->|Click 'Why?'| G[Metric Explanation (Methodology)]
    B -->|Export| H[PDF Report]
    B -->|Dispute| I[Correction Request]
    
    F -->|Back| B
    F -->|View Source| J[External Platform (IG/TikTok)]
    
    C --> K[Limitations]
    C --> L[Algorithmic Audits]
    
    I --> M[Support / Help]
```

### Core Pages

1.  **Landing / Search** (`/`)
    *   **Goal:** Establish trust, explain value proposition, and capture search intent.
    *   **Key Elements:** Search Bar, Value Prop, Platform Support Indicators.

2.  **Report Overview** (`/report/[handle]`)
    *   **Goal:** Provide a high-level summary of the analysis without overwhelming the user.
    *   **Key Elements:** 4-Pillar Scores, Engagement Chart, Top-Level Heuristics.
    *   **Navigation Logic:** No score is a dead end. Every score links to evidence.

3.  **Evidence Deep Dive** (`/report/[handle]/evidence/[signal_id]`)
    *   **Goal:** Show the raw data backing up a claim.
    *   **Key Elements:** Raw comment logs, timestamp histograms, "View Source" links.

4.  **Methodology** (`/methodology`)
    *   **Goal:** Explain *how* we calculate scores.
    *   **Key Elements:** Mathematical formulas, "Limitations" section, Ethics statement.

5.  **Correction Request** (`/correction`)
    *   **Goal:** Allow users to dispute data (Right to Reply).
    *   **Key Elements:** Form to submit evidence of error.

---

## 2. URL Conventions

We use clean, semantic URLs to build trust and shareability.

| Page Type | URL Pattern | Example |
| :--- | :--- | :--- |
| **Home** | `/` | `sponsorscope.ai/` |
| **Report** | `/report/[handle]` | `sponsorscope.ai/report/mkbhd` |
| **Evidence** | `/report/[handle]/evidence` | `sponsorscope.ai/report/mkbhd/evidence` |
| **Specific Signal** | `/report/[handle]/evidence?focus=[signal]` | `sponsorscope.ai/report/mkbhd/evidence?focus=bot_comments` |
| **Methodology** | `/methodology` | `sponsorscope.ai/methodology` |
| **Metric Definition** | `/methodology#[metric_slug]` | `sponsorscope.ai/methodology#linguistic_entropy` |
| **Corrections** | `/correction` | `sponsorscope.ai/correction` |
| **Docs** | `/docs` | `sponsorscope.ai/docs` |
| **Help** | `/help` | `sponsorscope.ai/help` |
| **Pricing** | `/pricing` | `sponsorscope.ai/pricing` |
| **Settings** | `/settings` | `sponsorscope.ai/settings` |

---

## 3. Navigation Logic & Rules

### Rule #1: No Dead Ends
*   **Bad:** A red "FAIL" badge with no click action.
*   **Good:** A red "Anomaly Detected" badge that clicks to -> Evidence Deep Dive showing the specific timestamps that triggered the flag.

### Rule #2: Contextual Methodology
*   **Requirement:** Users shouldn't have to leave the report to understand a metric.
*   **Implementation:** "Methodology" is not just a separate page; it is injected via tooltips and slide-overs directly next to the score.
*   **Link:** "How is this calculated?" links -> `/methodology#[metric_slug]`.

### Rule #3: The "Why?" Toggle
*   Every high-level score must have an expandable "Why?" section or a link to the Evidence Deep Dive.

### Rule #4: Correction Accessibility
*   The "Dispute this Report" link must be visible in the footer of every report page, ensuring fairness.

---

## 4. Current Implementation Status vs. Architecture

| Component | Status | Action Required |
| :--- | :--- | :--- |
| **Landing / Search** | ✅ Implemented | None. |
| **Report Overview** | ✅ Implemented | Exists at `/report/[handle]`. |
| **Evidence Deep Dive** | ❌ Missing | Needs to be built as a sub-view or modal. |
| **Methodology** | ✅ Implemented | Exists at `/methodology`. |
| **Correction Request** | ✅ Implemented | Exists at `/correction`. |

## 5. Next Steps (Migration Plan)

1.  **Refactor Report Routing:** Move `ReportView` from a conditional render in `page.tsx` to a dedicated dynamic route `/report/[handle]/page.tsx`.
2.  **Build Evidence View:** Create the evidence drill-down page.
3.  **Implement Correction Flow:** Add the correction form.
