# Chrome CDP GTM Audit SOP

Use this file as the workspace operating procedure for runtime GTM, dataLayer, consent, and ecommerce audits.

## Required Skills

- `gtm-browser-cdp-audit` for Chrome profile and CDP setup.
- `gtm-datalayer-evidence-audit` for DataLayer Evidence Recorder exports, HAR files, and evidence packaging.
- `gtm-consent-mode-runtime-audit` for consent default/update and hit behavior checks.
- `gtm-ecommerce-journey-audit` for home, PLP, search, PDP, cart, checkout, and success scenarios.
- `gtm-container-runtime-diff` for comparing GTM export expectations with runtime evidence.

## Evidence Location

Store each scenario under:

```text
.agent/projects/<Project>/evidence/YYYY-MM-DD-scenario/
```

Each folder should contain:

- `scenario.json` with scenario metadata, artifact filenames, consent path, profile, extension version, and expected-data source.
- DataLayer Evidence Recorder JSON export.
- DataLayer Evidence Recorder raw `dataLayer.push(...)` export when useful.
- Recorder `network.analytics` records when available; use them as debugging signals, not a HAR replacement.
- HAR file from the same browser session.
- CDP comparison JSON/MD report when available.
- Scenario notes copied from `_templates/evidence-scenario-template.md`.

## Audit Execution Rule

- When an operator requests a GTM audit, run the evidence capture and analysis instead of only describing the workflow.
- Run accept and reject consent scenarios separately when the site exposes both paths.
- Use custom-preference and SPA-after-update consent scenarios when the CMP or site supports them.
- Stop before irreversible production checkout/order submission unless the user explicitly approves a staging or test-order path.

## Chrome Profile Rule

- Record profile purpose, path, installed extensions, and last validation in `.agent/Chrome-Audit-Profiles.md`.
- Use an isolated Chrome profile for audit automation when normal Chrome must stay open.
- Install DataLayer Evidence Recorder in the audit profile.
- Install Adswerve or other comparison extensions only in comparison profiles.
- Do not use direct URL navigation for click-event validation; use real clicks.
- Do not submit real orders unless the user confirms a staging/test checkout path.

## CDP TCP Workflow

From the DataLayer Evidence Recorder extension repository:

```powershell
.\tools\chrome-debug\launch-debug-chrome.ps1 `
  -ProfileDir ".chrome-profile-recorder-adswerve" `
  -AllowOtherExtensions `
  -StartUrl "about:blank"
```

Verify CDP:

```powershell
node .\tools\chrome-debug\cdp-check.js --port 9222
```

## CDP Pipe Fallback

Use this when TCP CDP does not become available:

```powershell
node .\tools\chrome-debug\cdp-pipe-smoke.js --keep-open --allow-other-extensions
```

## Scenario Matrix

- reject cookies
- accept cookies
- home page load
- PLP/category listing
- search results
- real PLP product click
- PDP load
- PDP related/upsell product click
- add to cart
- cart page
- checkout entry
- checkout success only on staging/test order approval

## Reporting Rule

After the audit, include a consent timeline, data audit findings, runtime-to-container mapping when applicable, and unresolved questions. Update the project `Work-in-Progress`, `ChangeLog`, and any relevant thread or evidence notes, then run `gtm-memory-sync`.
