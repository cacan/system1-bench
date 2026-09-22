# Chrome control readiness

**Status:** Blocked pending exact Profile 40 identity match

| Field | Value |
| --- | --- |
| Account | `analytics@stellar-insights.com` |
| Profile | `Profile 40` |
| Profile path | `C:/Users/cacan/AppData/Local/Google/Chrome/User Data/Profile 40` |
| BrowserSkill port | `22840` |
| `BSK_HOME` | `C:/Users/cacan/.bsk/stellar-insights` |
| Extension | ChatGPT (`hehggadaopoacecdllhhajmbjkdcmajg`) |
| Last preflight | 2026-09-22 |
| Result | Daemon reached with one connected browser, but identity label was empty; no navigation or tab borrowing attempted |

Read-only preflight command:

```powershell
$env:BSK_HOME = 'C:\Users\cacan\.bsk\stellar-insights'
$env:BSK_AUTO_START = '0'
& 'C:\Users\cacan\.local\bin\bsk.exe' status --json
```

Only after the connection is identified as the assigned Profile 40 should a browser session be started. Never use a default/recent profile or a connection identified as another account.
