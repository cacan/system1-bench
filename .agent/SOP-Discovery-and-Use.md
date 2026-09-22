# SOP Discovery and Use

Last updated: 2026-09-22

## Purpose

This SOP makes SOP usage operational. The agent must discover, read, and apply the right local and global instructions before acting, especially before live Google, Google Workspace, GTM, GA4, BigQuery, Search Console, Ads, Merchant, Cloud Storage, browser-control, browser-audit, Hindsight, Qdrant, or other memory operations.

## Required Workflow

1. Anchor the workspace.
   - Confirm the current workspace path.
   - Read `AGENTS.md` first when it exists.
   - Treat `AGENTS.md` as the index of authoritative local docs, live IDs, identity references, Chrome profile readiness, and local constraints.

2. Recall project memory when configured.
   - If `AGENTS.md` declares Hindsight or another memory system, run a targeted recall before non-trivial work.
   - Use memory as context, not as proof of current external state.

3. Classify the task before using tools.
   - Identify whether the request touches GTM, sGTM, Google Workspace, OAuth, GCP, GA4, BigQuery, Looker Studio, browser control, browser runtime audits, Qdrant, project docs, vendor email, or another domain.
   - If a task crosses domains, collect the SOP set for each domain.

4. Build the SOP set.
   - Start from `AGENTS.md`.
   - Add relevant `.agent/*.md` workspace docs.
   - Add relevant `C:/Users/cacan/.codex/skills/*/SKILL.md` files.
   - Add referenced skill `references/` docs when the skill points to them.

5. Verify before mutation.
   - Prefer read/list/get/inspect/dry-run first.
   - Confirm the account, project, profile, OAuth scope state, mutation policy, and Chrome-control readiness before write operations or browser-session-dependent work.
   - If verification fails, stop at a clear blocker with exact evidence and safe next commands.

6. Execute and record evidence.
   - Save durable artifacts for non-trivial checks, audits, generated reports, and live-system changes.
   - Do not leave important status only in terminal output.

7. Repair discoverability gaps.
   - If a needed SOP exists but was not discoverable from `AGENTS.md` or the global skills README, update the relevant pointer after the task.
   - If no SOP exists for a recurring workflow, create or propose one.

## Task-to-SOP Map

| Task area | Read first | Gate |
| --- | --- | --- |
| GTM API or sGTM live work | `.agent/GTM-API-OAuth-and-MCP.md`, `.agent/Google-Workspace-Identity.md`, `.agent/Google-Workspace-Mutation-Policy.md`, `.agent/identity-validation/validation-ledger.ndjson`, `C:/Users/cacan/.codex/skills/gtm-api/SKILL.md` | Confirm account/profile/project, OAuth scope state, target GTM account/container/workspace, and mutation policy. |
| Google Workspace / GWS | `.agent/Google-Workspace-Identity.md`, `.agent/google-workspace-identity.json`, `.agent/Google-Workspace-Mutation-Policy.md`, `C:/Users/cacan/.codex/skills/gws-profile-manager/SKILL.md` | Confirm the shared account bundle and data boundary before reading or mutating Workspace data. |
| Shared Google authentication | `C:/Users/cacan/.codex/skills/gtm-shared-ops/references/shared-google-auth-discovery.md`, `.agent/google-workspace-identity.json`, referenced account bundle | Shared GWS OAuth profile before gcloud. Resolve the installed `gws` runtime beyond PATH, validate exact user/scopes, and use exports only in memory. |
| Browser control with existing Chrome state | `.agent/Chrome-Control-Readiness.md`, `.agent/google-workspace-identity.json`, `C:/Users/cacan/.codex/plugins/cache/openai-bundled/chrome/*/skills/control-chrome/SKILL.md` | If the exact profile and extension status are not already documented and user-confirmed, report browser control as blocked and ask the user for the exact Chrome profile name and whether the ChatGPT extension is installed there. |
| Browser runtime audit | `.agent/Chrome-CDP-GTM-Audit-SOP.md`, `.agent/Chrome-Audit-Profiles.md`, relevant `gtm-audit-recorder-*` skills | Verify the active audit profile, scenario, consent state, recorder artifacts, and generated reports. |
| Qdrant / project memory | `.agent/qdrant.toml`, `.agent/Qdrant-Naming-and-Endpoints.md`, `C:/Users/cacan/.codex/skills/qdrant-search/SKILL.md`, `C:/Users/cacan/.codex/skills/qdrant-ingest/SKILL.md` | Search before relying on prior project docs; ingest after meaningful `.agent/projects` changes. |
| GTM project/thread docs | `C:/Users/cacan/.codex/skills/gtm-shared-ops/SKILL.md`, `.agent/projects/<Project>.md`, `.agent/PROJECTS_OVERVIEW.md` | Keep project, thread, changelog, and dashboard status aligned. |

## Required Pre-Action Statement

Before a live mutation, provide this compact status:

```text
SOPs read: <files>
Identity: <account/profile/project confirmed or blocker>
Browser control: <user-confirmed Chrome profile / ChatGPT extension status / not required / blocked pending user answer>
Target: <resource IDs>
Action gate: <read-only / guarded mutation / explicit approval needed / blocked>
Evidence: <artifact path or command result summary>
```

## Non-Negotiables

- Do not rely on ambient `gcloud`, ADC, `gws`, Codex connector, MCP, or browser identity without checking the workspace identity docs.
- Shared GWS OAuth profile before gcloud: for `account-bundle-ref`, follow `C:/Users/cacan/.codex/skills/gtm-shared-ops/references/shared-google-auth-discovery.md`. A PATH-only `gws` failure or stale gcloud token is not proof that shared authentication is unavailable.
- Do not treat `Selected GTM MCP server: TBD` as proof that no native GTM access exists; check the documented `gws_profile`, OAuth scopes, and live-check evidence.
- Do not rely on Chrome browser state unless `.agent/Chrome-Control-Readiness.md` confirms a profile with `ChatGPT` extension `hehggadaopoacecdllhhajmbjkdcmajg`.
- If the exact Chrome profile and ChatGPT-extension installation status are missing, report the missing assignment and ask the user for the exact Chrome profile name (and directory, if known) and whether the ChatGPT extension is installed there.
- Preserve a user-confirmed assigned profile as `Configured`. Require exactly one tool connection whose metadata identifies it. Reject extension-ID-only, unidentified, zero-match, multiple-match, or mismatched connections before navigation; do not mark the configured profile itself blocked.
- A reachable page or existing authenticated session does not cure a failed profile gate. Continue only through an independently validated API/OAuth identity when possible.
- Do not enumerate or discover candidate Chrome profiles, inspect unrelated profiles, choose a default or recent profile, or fall back to Playwright or another browser.
- Do not print OAuth client secrets, refresh tokens, raw ADC files, raw token responses, private keys, or API keys.
- Do not mutate live systems when the documented account, project, scope, browser profile, or mutation policy is missing or contradictory.
