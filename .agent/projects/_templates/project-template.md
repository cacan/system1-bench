# <Project Name> Implementation

## Overview

Describe the implementation scope, business purpose, and deployment status.

## GTM API OAuth / MCP Identity

- GTM MCP server: `<GTM MCP Server>`
- Google account: `<Google Account>`
- OAuth status: `<OAuth Status>`
- Workspace identity source: `.agent/GTM-API-OAuth-and-MCP.md`
- Identity mode: `<Identity Mode>`
- Identity ref: `<Identity Ref>`
- Account bundle: `<Account Bundle>`
- Workspace identity source: `.agent/Google-Workspace-Identity.md`
- API operator access: inherit workspace `api_operator_access` unless this project records an explicit override.
- GWS profile: `<GWS Profile>`
- Mutation policy: `.agent/Google-Workspace-Mutation-Policy.md`
- Broader Google Workspace identity source: `.agent/Google-Workspace-Identity.md`
- Before API writes, confirm the selected MCP server maps to the intended Google account and has GTM access.

## Runtime Evidence / Audit Readiness

- Chrome/CDP SOP: `.agent/Chrome-CDP-GTM-Audit-SOP.md`
- Chrome control readiness: `.agent/Chrome-Control-Readiness.md`
- Chrome audit profile registry: `.agent/Chrome-Audit-Profiles.md`
- GTM live-check evidence: `.agent/gtm-live-checks/`
- Evidence folder pattern: `.agent/projects/<Project>/evidence/YYYY-MM-DD-scenario/`
- Required baseline artifacts: `scenario.json`, Recorder JSON, raw pushes when useful, Recorder `network.analytics` records when available, HAR, CDP comparison report, and scenario notes.
- Use `gtm-datalayer-evidence-audit` before concluding whether runtime dataLayer behavior matches implementation expectations.

## Tags

- Add implemented GTM tags and their triggers.

## Variables

- Add key lookup variables, custom JavaScript variables, and feature flags.

## Country / Locale Enablement

| Locale | Status |
| :--- | :--- |

## Communications Hub

- None yet.

## PII and Security Handling

- Document any privacy, consent, or user-data handling notes here.

## Work-in-Progress

- [ ] Add current operator tasks here.

## ChangeLog

### 2026-09-22

- **[Initialized]** Project document created from workspace template.
