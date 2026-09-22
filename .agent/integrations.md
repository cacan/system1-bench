# Workspace integrations

| Integration | Status | Configuration | Notes |
| --- | --- | --- | --- |
| Qdrant | Ready for ingest | `.agent/qdrant.toml` | Dedicated collection `project_memory_jev_local_experiments`; read-only endpoint probe returned HTTP 200 |
| LM Studio embeddings | Ready | `.agent/qdrant.toml` | `text-embedding-bge-m3` was listed by the configured endpoint |
| Chrome/BrowserSkill | Blocked | `.agent/Chrome-Control-Readiness.md` | Daemon is reachable on port 22840, but the connected browser identity is empty; no tab was borrowed |
| Google Workspace APIs | Disabled | `.agent/google-workspace-identity.json` | Identity is metadata-only for this project |
| Gmail | Disabled | `.agent/google-workspace-identity.json` | No mailbox reads are permitted here |
| GTM/GA4 | Disabled | `.agent/google-workspace-identity.json` | This is intentionally not a GTM/GA4 workspace |
| Hindsight | Deferred | No `.codex/config.toml` yet | No dedicated bank exists; do not reuse another project's bank or create one implicitly |

Durable Markdown under `docs/` is the Qdrant ingest source. Keep credentials and transient run output out of that tree.
