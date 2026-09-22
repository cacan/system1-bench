# Hindsight workspace memory

**Status:** Blocked during project-bank provisioning  
**Intended bank:** `codex-jev-local-experiments`  
**Service:** `http://192.168.31.229:8888`  
**Codex MCP binding:** intentionally not written until the bank exists

## Intended runtime parameters

- Hindsight LLM provider: `lmstudio`
- Hindsight LLM base URL: `http://192.168.31.13:1234/v1`
- Preferred Hindsight LLM: `qwen3.6-35b-a3b-mtp`
- Fallback Hindsight LLM: `qwen3.5-4b`
- Embeddings provider: OpenAI-compatible endpoint
- Embeddings base URL: `http://192.168.31.13:1234/v1`
- Embeddings model: `text-embedding-bge-m3`
- Embedding dimensions: `1024`

## Provisioning attempt

On 2026-09-22, a dedicated bank creation request was sent for `codex-jev-local-experiments`. The Hindsight API returned HTTP 500:

```text
could not resize shared memory segment "/PostgreSQL.429023496" to 533795008 bytes: No space left on device
```

The bank list was rechecked afterward and the target bank was absent. No existing bank was reused, and no `.codex/config.toml` was created with a broken target.

## Required recovery

An operator with access to Hindsight CT120 must inspect container disk and `/dev/shm` capacity, then restart the service after correcting the PostgreSQL shared-memory/storage limit. After that, retry creation of the same bank id and verify it through the bank list before adding the Codex MCP binding.

Never retain API keys, OAuth data, browser state, raw credentials, or transient benchmark output in this bank.
