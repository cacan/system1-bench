# GTM Tracking & Implementation Workspace

This workspace (`JEV-local-experiments`) is organized for GTM implementation, vendor coordination, documentation, and semantic memory.

Last updated: 2026-09-22

## Terminology

- **Workspace**: the local repo or top-level folder that contains the shared `.agent/` operating model.
- **GTM project**: one implementation stream inside the workspace, usually one vendor, platform, rollout, or tracking workstream.
- **Thread**: one communication or decision track inside a GTM project.
- **Container source of truth**: the authoritative GTM export JSON or related reference document.
- **GTM workspace export**: a GTM-side export artifact. Do not confuse this with the local documentation workspace.

## Key Files (start here)

### GTM skill suite map
- Local suite index: `.agent/GTM-Skill-Suite.md`
- Use this file to choose the right `gtm-*` skill before onboarding, project updates, communication handling, live GTM access, or runtime audits.

### Latest GTM exports (JSON)
- Primary vendor-tag / third-party-pixels container: `TBD`
- Loader / secondary / market-specific container: `TBD`

### Container ID reference
- GTM container IDs list: `TBD`

### Memory configuration
- Workspace Qdrant config: `.agent/qdrant.toml`
- Qdrant naming and endpoint rules: `.agent/Qdrant-Naming-and-Endpoints.md`

### GTM API OAuth / MCP identity
- Workspace GTM API identity decision: `.agent/GTM-API-OAuth-and-MCP.md`
- Workspace Google account bundle decision: `.agent/Google-Workspace-Identity.md`
- Workspaces may share the same `identity_ref`; shared workspaces reuse the same token/profile bundle instead of minting duplicate workspace-local credentials.
- Do not run GTM API operations until the selected MCP server and Google account are documented and validated.

### Chrome control readiness
- Workspace browser-control readiness: `.agent/Chrome-Control-Readiness.md`
- Required ChatGPT Chrome extension ID: `hehggadaopoacecdllhhajmbjkdcmajg`
- Use this before tasks that depend on existing Chrome tabs, profile login state, or extension-backed control.

### Chrome/CDP runtime audit setup
- Workspace SOP: `.agent/Chrome-CDP-GTM-Audit-SOP.md`
- Chrome audit profile registry: `.agent/Chrome-Audit-Profiles.md`
- Evidence folders: `.agent/projects/<Project>/evidence/YYYY-MM-DD-scenario/`
- Use `scenario.json`, DataLayer Evidence Recorder JSON, raw pushes, Recorder `network.analytics` records, HAR, CDP comparison reports, and scenario notes for runtime audits.

### Notes about searching
- Prefer PowerShell file search if `rg` is unavailable.

## Role & Objectives
- GTM tracking implementation
- vendor and stakeholder communications
- privacy and PII handling
- dashboard and source-of-truth maintenance

## Documentation Standards
Project documentation in `.agent/projects/` should follow this structure:
1. Overview
2. Tags / Variables
3. Country / Locale Enablement
4. Communications Hub
5. PII and Security Handling
6. Work-in-Progress
7. ChangeLog

> [!TIP]
> Use the global GTM Skill Suite and keep `AGENTS.md` updated with authoritative container pointers.
