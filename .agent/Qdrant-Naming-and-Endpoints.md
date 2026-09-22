# Qdrant Naming & Endpoints

This file is the canonical reference for semantic-memory naming and endpoints in this workspace.

## Precedence

Runtime config is resolved in this order:
1. CLI arguments
2. environment variables
3. `.agent/qdrant.toml`
4. bootstrap defaults

## Workspace Identity

- Stable workspace id: `jev_local_experiments`
- Keep `[workspace].id` stable even if the repo folder is renamed.
- Prefer lowercase snake_case for workspace ids.

## Collection Naming Rule

- Default collection pattern for new workspaces: `project_memory_<workspace_id>`
- Resolved collection for this workspace: `project_memory_jev_local_experiments`
- If a workspace already has a legacy or shared collection, keep it explicit in `.agent/qdrant.toml`.
- Do not silently rename an existing collection just because the workspace id or folder name changed.

## Endpoint Rule

- Qdrant URL: `http://192.168.31.228:6333`
- Embedding URL: `http://192.168.31.13:1234/v1/embeddings`
- Embedding model: `text-embedding-bge-m3`
- Treat `.agent/qdrant.toml` as the workspace source of truth for endpoints.
- If infrastructure moves, update `.agent/qdrant.toml` first.

## Ingest Settings

- Source directory: `docs`
- Chunk max chars: `16000`

## Operational Rule

- Search and ingest helpers should read runtime config, not duplicate endpoint assumptions in ad hoc scripts.
- When documenting Qdrant behavior in this workspace, point to this file and `.agent/qdrant.toml`.
