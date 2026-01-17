# Contributing to SponsorScope.ai

Thanks for your interest in contributing. This project aims to provide transparent, audit-friendly influencer intelligence.

## How to Contribute
- Open an issue describing the problem or proposal.
- Fork the repo and create a branch for your change.
- Keep documentation up to date with code changes.
- Add tests for analysis logic when feasible.
- Submit a PR with a clear summary and references to affected files.

## Development Setup
- Frontend: Next.js 14 in `apps/frontend`
- API: FastAPI in `services/api`
- Shared models and contracts in `shared/`

## Code Style
- TypeScript/React: idiomatic Next.js components and hooks
- Python: Pydantic models, clear separation of heuristics/LLM/scraper
- Avoid committing secrets; respect environment-based configuration

## Commit & PR Guidelines
- Prefer conventional commits: `feat:`, `fix:`, `docs:`, `chore:`
- Link to relevant code files using repository-absolute references
- Include screenshots or JSON examples for UI/API changes when helpful

## Documentation
- Update root and app/service READMEs when changing routes or features
- Reflect API changes in `services/api/README.md`
- Keep UX docs in `docs/ux/` aligned with implemented pages

## Governance & Safety
- Respect the kill switch behavior and epistemic signaling
- Security-conscious contribution; no scraping of private data

## Contact
Open a GitHub issue for questions or proposals.
