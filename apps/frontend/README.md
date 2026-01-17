# SponsorScope Frontend

Next.js 14 app for rendering influencer reports, methodology, corrections, and docs.

## Features
- Report dashboard at /report/[handle] with pillar visualizations and uncertainty cues
- Deterministic polling for report readiness (supports 200/202/404/410/503)
- Pages: methodology, correction, docs, help, pricing, settings

## Scripts
```bash
npm run dev     # start dev server
npm run build   # production build
npm run start   # start production server
npm run lint    # lint checks
```

## Getting Started
```bash
cd apps/frontend
npm install
npm run dev
```
Open http://localhost:3000 and visit /report/exampleuser.

## Data Flow
- Hook fetches reports from /api/report/{handle} and handles 202 polling:
  - [useReport.ts](file:///c:/Users/Japan/OneDrive/Documents/GitHub/sponsorscope_trae/apps/frontend/hooks/useReport.ts)
- Report types mirrored locally:
  - [schema.ts](file:///c:/Users/Japan/OneDrive/Documents/GitHub/sponsorscope_trae/apps/frontend/types/schema.ts)

## Routes
- /report/[handle]
- /methodology
- /correction
- /docs
- /help
- /pricing
- /settings

## UI Components
- Report view: [ReportView.tsx](file:///c:/Users/Japan/OneDrive/Documents/GitHub/sponsorscope_trae/apps/frontend/components/ReportView/ReportView.tsx)
- Visualization primitives: [Viz](file:///c:/Users/Japan/OneDrive/Documents/GitHub/sponsorscope_trae/apps/frontend/components/Viz)
- Layout: [layout.tsx](file:///c:/Users/Japan/OneDrive/Documents/GitHub/sponsorscope_trae/apps/frontend/app/layout.tsx)

## Notes
- Requires API server at http://localhost:8000 mounting /api routes.
- Tailwind 4 PostCSS pipeline configured; global styles in [globals.css](file:///c:/Users/Japan/OneDrive/Documents/GitHub/sponsorscope_trae/apps/frontend/app/globals.css)
