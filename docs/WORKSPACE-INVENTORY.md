# Workspace inventory and storage map

**Snapshot:** 2026-09-22  
**Workspace root:** `D:/WebDev/VScode-projects/-ML-AI/JEV-local-experiments`

This document is the operator map for the Jev-alternative lab. It separates files tracked by Git from machine-local credentials, runtimes, and network services. Secret contents are intentionally not documented.

## 1. Repository source of truth

| Area | Location | Tracked? | Purpose |
| --- | --- | ---: | --- |
| Operating rules | `AGENTS.md` | Yes | Local workflow, security, and integration boundaries |
| Project overview | `README.md` | Yes | Quick start and layout |
| Workspace parameters | `config/workspace.toml` | Yes | Project mode, paths, hardware, benchmark policy |
| Provider parameters | `config/providers.toml` | Yes | Local endpoints, Jev reference endpoint, model names, key-path reference |
| Python package | `src/jev_local_experiments/` | Yes | Fixture validation, config loading, Jev baseline client, CLI |
| Tests | `tests/` | Yes | Schema, config, and baseline contract tests |
| Dependencies | `pyproject.toml`, `uv.lock`, `.python-version` | Yes | Python/uv environment and locked packages |
| Alternative catalog | `alternatives/manifest.toml` | Yes | Candidate repositories and install directories |
| Alternative installs | `alternatives/<id>/` | No | Local third-party checkouts, virtual environments, and model artifacts |
| Benchmark fixtures | `benchmarks/` | Yes | JSONL cases and baseline instructions |
| Research and decisions | `docs/` | Yes | Plans, research, benchmark summaries, and this inventory |
| Run outputs | `results/` | No | Raw baseline/evaluation JSONL; only `.gitkeep` is tracked |
| User-owned exploration notes | `findings.md`, `progress.md`, `task_plan.md` | No | Existing untracked Jev Lab exploration/planning notes; preserved and not automatically staged or ingested |
| Workspace integrations | `.agent/` | Yes | Identity references, Chrome route, Qdrant config, validation ledger |
| Initializer scaffold | `.agent/WORKSPACE-MODE.md`, `.agent/*GTM*`, `.agent/projects/_templates/` | Yes | Standard `gtm-initialize` conventions; GTM/GA4 files are dormant templates only |
| Hindsight Codex wiring | `.codex/config.toml` | No/absent | Deliberately absent; no project-specific Hindsight bank exists |

The Git repository is on branch `master`. The current working tree was clean when this inventory was generated.

## 2. Secrets and identity boundaries

| Secret or identity | Location | Stored in Git? | Use |
| --- | --- | ---: | --- |
| Jev API key | `C:/Users/cacan/.codex/secrets/jev` | No | Read at runtime by `jevx benchmark-jev`; never copied to results or logs |
| Google account bundle | `C:/Users/cacan/.codex/google-identities/accounts/stellar-insights-analytics/identity.json` | No | Shared identity metadata for `analytics@stellar-insights.com` |
| Google Workspace profile | `C:/Users/cacan/.codex/gws-profiles/stellar-insights-analytics/` | No | Shared GWS OAuth/profile state; not a workspace credential store |
| Chrome profile | `C:/Users/cacan/AppData/Local/Google/Chrome/User Data/Profile 40` | No | Assigned browser profile for `analytics@stellar-insights.com` |
| BrowserSkill state | `C:/Users/cacan/.bsk/stellar-insights/` | No | BrowserSkill home for port `22840` |
| Hermes secrets/auth | `C:/Users/cacan/AppData/Local/hermes/.env`, `auth.json` | No | Hermes runtime credentials; never read into project docs |

Project references to these paths are acceptable; secret contents are not. The Jev provider is marked `reference_only=true` and `training_use=false`.

## 3. Local runtimes and network services

### LM Studio

- Server: `http://192.168.31.13:1234`
- OpenAI-compatible base URL: `http://192.168.31.13:1234/v1`
- Native management API: `http://192.168.31.13:1234/api/v1`
- Embeddings: model `text-embedding-bge-m3`, 1024 dimensions, context 8192
- Current Hermes smoke model: `google/gemma-4-e4b`, loaded at 65536 context for Hermes' minimum context requirement
- Suggested available models: `unsloth/gemma-4-26b-a4b-it` and `kwaipilot_kat-coder-v2.5-dev` (catalogued, not currently loaded)
- LM Studio executable/catalog: `C:/Users/cacan/.cache/lm-studio/bin/lms.exe`
- LM Studio model library is managed outside this repository. Use `lms ls --json` or LM Studio settings for the current model-library root; catalog `path` values are relative to that root.

### Qdrant and embeddings

- Qdrant server: `http://192.168.31.228:6333`
- Collection: `project_memory_jev_local_experiments`
- Collection distance/vector size: cosine / 1024
- Current collection point count: 5 documentation chunks
- Embedding endpoint: `http://192.168.31.13:1234/v1/embeddings`
- Embedding model: `text-embedding-bge-m3`
- Workspace config: `.agent/qdrant.toml`
- Ingest source: `docs/`

Ingest command:

```powershell
python C:/Users/cacan/.codex/skills/qdrant-ingest/scripts/ingest.py --config .agent/qdrant.toml
```

### Jev reference API

- Base URL: `https://api.typesafe.ai`
- Endpoint: `POST /v1/systemone`
- Requested model: `jev-latest`
- Returned model in the latest smoke run: `jev-1.13.0`
- Runner: `src/jev_local_experiments/baseline.py`
- Command: `uv run jevx benchmark-jev --suite benchmarks/smoke.jsonl`
- Raw output: `results/jev-baseline.jsonl` (ignored)
- Durable summary: `docs/benchmarks/2026-09-22-jev-reference-baseline.md`

### BrowserSkill / Chrome

- BrowserSkill port: `22840`
- BrowserSkill home: `C:/Users/cacan/.bsk/stellar-insights`
- Assigned Chrome profile: `Profile 40`
- Assigned account: `analytics@stellar-insights.com`
- Workspace readiness: blocked until the connected browser exposes an exact Profile 40 identity; do not fall back to another profile.
- Source-of-truth docs: `.agent/Chrome-Control-Readiness.md` and `.agent/google-workspace-identity.json`

## 4. Hermes and Hindsight storage

### Hermes

- Executable: `C:/Users/cacan/AppData/Local/hermes/bin/hermes.exe`
- Hermes home: `C:/Users/cacan/AppData/Local/hermes/`
- Main config: `C:/Users/cacan/AppData/Local/hermes/config.yaml`
- Auth/secrets: `auth.json` and `.env` under Hermes home; not copied here
- Installed Hermes skills: `C:/Users/cacan/AppData/Local/hermes/skills/`
- Hermes Hindsight deployment notes: `C:/Users/cacan/AppData/Local/hermes/workspace/hindsight-deployment/findings.md`
- Current Hermes default provider is separate from this workspace's per-process LM Studio smoke override. The workspace does not edit Hermes global configuration.

### Hindsight

This workspace does not have a Hindsight bank or `.codex/config.toml`. Existing Hindsight banks must not be reused for this project.

The known shared Hindsight service, documented by Hermes, is:

- API: `http://192.168.31.229:8888`
- Control plane: `http://192.168.31.229:9999`
- Service container: Proxmox CT120 (`hindsight`)
- Persistent data inside CT120: `/var/lib/hindsight/pg0`
- Service environment inside CT120: `/opt/hindsight/hindsight.env`
- Systemd unit inside CT120: `/etc/systemd/system/hindsight.service`
- Existing profile banks include `hermes-default-hal` and `hermes-sysadmin`; this workspace has no `codex-jev-local-experiments` bank.

These are external infrastructure locations, not files owned by this repository. Do not create, rename, or repoint a Hindsight bank from this workspace without an explicit decision and a project-specific bank.

## 5. Common commands

```powershell
# Workspace tests and fixture validation
uv sync --extra dev
uv run pytest
uv run jevx validate-suite benchmarks/smoke.jsonl

# Jev reference baseline (reads the external key path at runtime)
uv run jevx benchmark-jev --suite benchmarks/smoke.jsonl --output results/jev-baseline.jsonl

# Inspect resolved non-secret provider/workspace parameters
uv run jevx show-config

# LM Studio catalog
C:/Users/cacan/.cache/lm-studio/bin/lms.exe ls --json

# BrowserSkill preflight
$env:BSK_HOME='C:\Users\cacan\.bsk\stellar-insights'
$env:BSK_AUTO_START='0'
& 'C:\Users\cacan\.local\bin\bsk.exe' status --json
```

## 6. What is intentionally not stored here

- OAuth tokens, client secrets, browser cookies, or API key contents.
- LM Studio model weights and third-party alternative source trees.
- Hindsight database files or another project's bank configuration.
- Gmail, GTM, GA4, Search Console, Ads, Merchant, BigQuery, or other Google API data.
- Raw customer data or private benchmark sets.
