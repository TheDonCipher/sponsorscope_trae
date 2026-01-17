# Failure Modes & Warning States: SponsorScope.ai

**Role:** Autonomous UX Designer
**Objective:** Handle data gaps transparently. Never penalize a creator for missing data; simply state the limitation.

## 1. Principles

1.  **Non-Dismissible:** If data is missing, the user *must* see the warning. They cannot close it and pretend the analysis is complete.
2.  **No Hidden Penalties:** A score of "0" is different from "Null". If comments are disabled, the "Engagement" score should be `N/A`, not `0%`.
3.  **Plain Language:** Avoid "API Error 403". Use "Access Restricted by User."

## 2. Failure Scenarios & Copy

| Scenario | Warning Title | Plain Language Copy | Visual Treatment |
| :--- | :--- | :--- | :--- |
| **Comments Disabled** | `SIGNAL BLOCKED` | "The creator has disabled comments on >50% of recent posts. Linguistic analysis is unavailable." | Yellow Stripe Banner |
| **Sparse Data** | `LOW SAMPLE SIZE` | "Only 12 posts found. Statistical confidence is low (±15% margin of error)." | Dashed Border Container |
| **API Rate Limit** | `SCAN PAUSED` | "System is throttling requests to respect platform limits. Analysis will resume in 60s." | Blue/Slate Pulse |
| **Private Account** | `ACCESS DENIED` | "This account is private. We do not analyze private data." | Locked State (Grey) |

## 3. Visual Treatment (CSS Classes)

We will use a dedicated `WarningBanner` component.

*   **Yellow (Warning):** `bg-yellow-500/10 border-yellow-500/50 text-yellow-200`
*   **Grey (Info):** `bg-slate-700/50 border-slate-500 text-slate-300`
*   **Purple (System):** `bg-purple-900/20 border-purple-500/50 text-purple-200`

## 4. Example States

### A. Comments Disabled
```jsx
<div className="w-full p-4 border-l-4 border-yellow-500 bg-yellow-900/10 mb-6">
  <div className="flex items-start gap-3">
    <span className="material-symbols-outlined text-yellow-500">comments_disabled</span>
    <div>
      <h4 className="font-bold text-yellow-500 text-sm uppercase tracking-wider">Signal Blocked</h4>
      <p className="text-sm text-yellow-200/80 mt-1">
        This account has limited public comments. Engagement quality cannot be fully verified.
      </p>
    </div>
  </div>
</div>
```

### B. Sparse Data
```jsx
<div className="border-2 border-dashed border-slate-600 rounded-xl p-8 text-center opacity-70">
   <h3 className="text-lg font-bold text-slate-400">Insufficient Data</h3>
   <p className="text-sm text-slate-500 mt-2">Need at least 50 comments to form a baseline.</p>
</div>
```

---
**Next Steps:** Create `WarningBanner.tsx` and integrate it into `ReportView`.
