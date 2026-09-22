# JEV Local Experiments Workspace

## Purpose

This is a local/open-source/free alternative evaluation workspace for Jev-style typed decisions. It is not a GTM or GA4 workspace.

The initial benchmark is generic and covers:

- binary/Noul decisions,
- multi-option Choice decisions, and
- ordered Score decisions.

## Operating rules

- Keep reusable artifacts, code comments, tests, and documentation in English.
- Do not add GTM, GA4, Search Console, Ads, Merchant, BigQuery, or Dataform project structure here.
- Do not copy OAuth tokens, refresh tokens, client secrets, browser cookies, or model credentials into this repository.
- The Google identity reference is metadata only. Reuse the shared Stellar Insights account bundle; never create workspace-local credentials.
- Browser work must use the assigned `analytics@stellar-insights.com` Chrome Profile 40 route on BrowserSkill port `22840`. Do not fall back to another profile.
- `alternatives/` is a local installation boundary. Third-party source trees and weights remain untracked; record each candidate in `alternatives/manifest.toml`.
- Treat upstream benchmark numbers as claims until this workspace reruns them on shared fixtures.
- Record provider/model/runtime/device revisions with every durable result.
- Ingest durable research and decisions into the dedicated Qdrant collection only. Do not ingest secrets, temporary logs, or raw credentials.
- Hindsight is optional and currently deferred because no project-specific bank exists. Do not reuse another project’s bank or create one implicitly.

## Commands

```powershell
uv sync --extra dev
uv run pytest
uv run jevx validate-suite benchmarks/smoke.jsonl
uv run jevx show-config
```

## Integration source of truth

- Workspace identity: `.agent/google-workspace-identity.json`
- Human identity notes: `.agent/Google-Workspace-Identity.md`
- Chrome readiness: `.agent/Chrome-Control-Readiness.md`
- Qdrant configuration: `.agent/qdrant.toml`
- Integration status: `.agent/integrations.md`
