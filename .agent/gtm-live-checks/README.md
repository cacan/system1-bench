# GTM Live Checks

Store low-risk live GTM API, identity, quota, and access validation notes here.

Use this folder for evidence that proves the current workspace can read the intended GTM resources through the documented access path.

## Required Fields For Each Check

- Date/time
- Workspace id
- Google account
- Identity ref / GWS profile
- Access path: `gtm-mcp`, `gws-oauth-rest`, `adc-gcloud`, or other documented path
- GTM account/container/workspace IDs checked
- Low-risk API call used, such as accounts list or containers list
- Result and blocker, if any
- Whether writes/mutations remain blocked pending explicit approval

Do not store OAuth secrets, refresh tokens, ADC contents, raw bearer tokens, or private keys in this folder.
