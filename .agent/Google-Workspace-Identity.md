# Google Workspace identity reference

**Workspace:** `jev-local-experiments`

This project is a local Jev-alternative lab, not a GTM/GA4 workspace. It references the existing account bundle only so browser research can be routed to the correct signed-in Chrome profile.

## Assigned identity

- Account: `analytics@stellar-insights.com`
- Identity reference: `stellar-insights-analytics`
- Shared bundle: `C:/Users/cacan/.codex/google-identities/accounts/stellar-insights-analytics/identity.json`
- GWS profile metadata: `stellar-insights-analytics`
- Workspace APIs: disabled in this project
- Gmail: disabled in this project

## Browser binding

- Chrome profile: `Profile 40`
- Profile path: `C:/Users/cacan/AppData/Local/Google/Chrome/User Data/Profile 40`
- BrowserSkill port: `22840`
- `BSK_HOME`: `C:/Users/cacan/.bsk/stellar-insights`
- ChatGPT extension id: `hehggadaopoacecdllhhajmbjkdcmajg`

The exact profile assignment is preserved from the shared account bundle. The 2026-09-22 preflight reached the dedicated BrowserSkill daemon, but its single connected browser exposed no identity label, so browser control remains blocked until Profile 40 is explicitly connected on port 22840. Do not fall back to another Chrome profile.

No OAuth tokens, client secrets, cookies, or ADC contents are stored in this workspace.
