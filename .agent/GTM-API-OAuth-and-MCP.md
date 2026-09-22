# GTM API OAuth & MCP Identity

This file records which account-scoped GTM API OAuth identity this workspace is allowed to use.
Do not store OAuth client secrets, refresh tokens, or full ADC files here.

Broader Google Workspace identity source: `.agent/Google-Workspace-Identity.md`
Machine-readable manifest: `.agent/google-workspace-identity.json`
Mutation policy: `.agent/Google-Workspace-Mutation-Policy.md`

## Selected Identity

- Identity model: `account-bundle-ref`
- Identity ref: `TBD`
- Account bundle: `TBD`
- Selected GTM MCP server: `TBD`
- Google account: `TBD`
- OAuth client JSON: `TBD`
- ADC credential file: `TBD`
- Chrome profile: `TBD`
- OAuth status: `Needs onboarding`
- Last validated: `TBD`

## Native Access Rule

- A configured GTM MCP server is preferred when available, but `TBD` MCP is not proof that native GTM API access is unavailable.
- If the workspace identity manifest records a validated `gws_profile`, OAuth scopes, and `api_operator_access`, Codex may use that documented GWS OAuth / REST path for read-only GTM checks.
- Local `gcloud` or ADC can be a separate access path; a stale `gcloud` login is not automatically a blocker for a validated GWS OAuth path.
- Before mutations, validate a low-risk GTM API call through the intended access path and record the evidence under `.agent/gtm-live-checks/` or `.agent/identity-validation/`.

## Default Google API Operator Access

- Policy: `full OAuth scopes, guarded actions`
- Manifest field: `api_operator_access`
- Reference: `C:/Users/cacan/.codex/skills/google-workspace-identity-onboarding/references/default-google-api-operator-access.md`
- If an API is disabled, confirm the active gcloud account/project and enable it, or report the exact `gcloud services enable ... --project <INTENDED_GCP_PROJECT_ID>` command.
- Broad OAuth scopes do not approve publish, delete, share, send, manage users/accounts, IAM changes, Ads/Merchant mutations, destructive BigQuery/Cloud Storage actions, or other destructive or externally visible mutations.

## Selection Rule

- Choose the account identity before running GTM API operations.
- Use one named account bundle per Google account/client identity.
- Multiple workspaces may share the same account bundle when they intentionally use the same Google account, OAuth app, GTM permissions, ADC credential, MCP server, and Chrome profile.
- If this workspace needs isolation, create a unique `identity_ref` such as `client-prod` or `client-stage`.
- Do not mint a new workspace-local OAuth token when the correct account bundle already exists.

## Onboarding Command

Run `gtm-api-chrome-mcp-onboarding` to create or validate the identity bundle.

```powershell
gtm-api-chrome-mcp-onboarding `
  -ClientLabel "<client-label>" `
  -GoogleAccount "<exact-google-email>" `
  -OAuthClientFile "<workspace>\.secrets\<oauth-client-json>.json" `
  -ChromeProfileDirectory "<Profile N>" `
  -ApplyCodexConfig
```

Add `-RunOAuth` only when the user is present to complete browser consent.

## Validation Rule

Before marking API access ready, validate all of the following:

- At least one intended native access path is documented: GTM MCP, ADC/gcloud, or GWS OAuth REST through a validated `gws_profile`.
- OpenID userinfo or equivalent account check returns the documented Google account.
- A low-risk GTM API call, such as account listing, succeeds.
- Required Google APIs are enabled or reported as blockers with exact enable commands.
- Codex has been restarted after adding or changing MCP server config.
