# GTM Skill Suite

This workspace uses the global flat `gtm-*` skill suite installed in Codex. Use this file as the local suite map; use the actual skill files for the full procedure.

## Core Operating Model

- Project truth: `.agent/projects/<Project>.md`
- Thread truth: `.agent/projects/<Project>/threads/<date-topic>/`
- Dashboard truth: `.agent/PROJECTS_OVERVIEW.md`
- GTM API identity truth: `.agent/GTM-API-OAuth-and-MCP.md`
- Google account identity truth: `.agent/Google-Workspace-Identity.md` and account bundle referenced by `.agent/google-workspace-identity.json`
- SOP discovery gate: `.agent/SOP-Discovery-and-Use.md`
- Chrome control readiness: `.agent/Chrome-Control-Readiness.md`
- GTM live-check evidence: `.agent/gtm-live-checks/`
- Runtime audit SOP: `.agent/Chrome-CDP-GTM-Audit-SOP.md`
- Chrome profile registry: `.agent/Chrome-Audit-Profiles.md`
- Evidence package: `.agent/projects/<Project>/evidence/YYYY-MM-DD-scenario/` with `scenario.json`

## Skill Index

- `gtm-initialize`: bootstrap the workspace operating structure.
- `gtm-new-project`: create a project document and standard folders.
- `gtm-shared-ops`: follow shared workspace rules and project/thread conventions.
- `gtm-project-status`: read current project state from docs and threads.
- `gtm-project-update`: update project docs after decisions, publishes, or audit findings.
- `gtm-thread-manager`: create or update communication thread folders.
- `gtm-email-workflow`: draft and preserve GTM stakeholder or vendor email work.
- `gtm-memory-sync`: ingest meaningful project and thread changes into semantic memory.
- `gtm-api`: prepare GTM API calls and container validation work.
- `gtm-api-chrome-mcp-onboarding`: set up or validate GTM MCP/API identity, OAuth, ADC, and Chrome profile access.
- `gtm-container-source-of-truth`: document live containers, saved/exported JSON, and authoritative references.
- `gtm-container-runtime-diff`: compare runtime evidence against live GTM MCP reads, saved/exported JSON, specs, or project notes.
- `gtm-browser-cdp-audit`: launch and validate real Chrome/CDP audit sessions.
- `gtm-datalayer-evidence-audit`: audit DataLayer Evidence Recorder exports, raw pushes, analytics hits, HARs, and data contracts.
- `gtm-consent-mode-runtime-audit`: audit consent defaults, consent updates, and consent-attached hits.
- `gtm-ecommerce-journey-audit`: audit ecommerce journeys, event order, object keys, values, and continuity.

## Onboarding Flow

1. Run `gtm-initialize` for a new or incomplete workspace.
2. Review `.agent/GTM-Skill-Suite.md`, `.agent/Gemini.md`, `.agent/GTM-Standards-and-Containers.md`, and `AGENTS.md`.
3. Use `gtm-api-chrome-mcp-onboarding` before live GTM MCP/API work.
4. Use `.agent/Chrome-Control-Readiness.md` before work that depends on existing Chrome profile state or ChatGPT extension-backed browser control.
5. Use `google-workspace-identity-onboarding` and `google-workspace-access-audit` before live Gmail, Drive, Calendar, Docs, Sheets, or broader Workspace MCP work.
6. Use `gtm-container-source-of-truth` to document live containers and saved/exported JSON.
7. Use `gtm-new-project` for each vendor, rollout, platform, or audit workstream.

## Project Workflow

1. Use `gtm-project-status` before editing project state.
2. Use `gtm-thread-manager` and `gtm-email-workflow` for communication-backed work.
3. Use `gtm-project-update` after confirmed decisions, launches, audit findings, or implementation changes.
4. Use `gtm-memory-sync` after meaningful project or thread updates.

## Runtime Audit Flow

1. Use `gtm-browser-cdp-audit` to prepare an isolated Chrome/CDP session.
2. Capture evidence with DataLayer Evidence Recorder, HAR, and scenario notes under the evidence package path.
3. Use `gtm-datalayer-evidence-audit` for expected-vs-observed event, object key, value, type, null-state, and analytics-hit checks.
4. Use `gtm-consent-mode-runtime-audit` when consent is in scope.
5. Use `gtm-ecommerce-journey-audit` when ecommerce journeys are in scope.
6. Use `gtm-container-runtime-diff` to compare runtime behavior with live GTM MCP reads, saved/exported JSON, specs, or project notes.

## Data Audit Contract

- Check expected events, missing events, unexpected events, duplicate events, and event order.
- Check object paths, object keys, value formats, value correctness, data types, empty strings, nulls, undefined values, and stale values.
- Check ecommerce item identity, list attribution, currency, price, quantity, discounts, cart continuity, checkout state, and purchase totals when applicable.
- Check consent state attached to dataLayer events and network hits when consent is in scope.
- Mark custom events and project-specific standards as expected only when the project notes or audit request defines them.

## Guardrails

- Do not run GTM API operations before OAuth/MCP identity is documented and validated.
- Do not claim full audit coverage unless relevant consent paths and journey scenarios were tested or explicitly marked blocked/not available.
- Treat Recorder `network.analytics` records as debugging evidence, not a HAR replacement.
- Do not update stable project docs from speculative evidence.
- Keep using the flat `gtm-*` namespace; do not reintroduce nested `gtm-pm-suite` skill paths.
