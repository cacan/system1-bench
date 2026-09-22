# JEV Local Experiments Workspace Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Initialize a provider-neutral local evaluation workspace for Jev-style open-source decision models.

**Architecture:** A small Python package validates typed-decision JSONL fixtures and configuration. Provider-specific projects live under `alternatives/` and are referenced through non-secret TOML manifests. Workspace integrations are isolated under `.agent/`, with Qdrant enabled and Google/Chrome metadata referenced without copying credentials.

**Tech Stack:** Python 3.12+, `uv`, standard-library TOML/JSON tooling, `pytest`, Markdown, TOML, JSONL, Qdrant, and an OpenAI-compatible LM Studio endpoint when available.

---

### Task 1: Initialize repository and workspace boundaries

**Files:**
- Create: `AGENTS.md`
- Create: `.gitignore`
- Create: `.editorconfig`
- Create: `.python-version`
- Create: `README.md`
- Create: `pyproject.toml`
- Create: `config/workspace.toml`
- Create: `config/providers.toml`
- Create: `alternatives/README.md`
- Create: `alternatives/manifest.toml`
- Create: `results/.gitkeep`

**Steps:**

1. Add the local-experiment operating rules, explicitly excluding GTM/GA4 structures.
2. Add non-secret runtime/provider parameters and the ignored alternative-install boundary.
3. Add the Python project metadata and developer commands.
4. Initialize Git and commit the design plus repository boundary files.

### Task 2: Add the typed-decision fixture contract

**Files:**
- Create: `benchmarks/README.md`
- Create: `benchmarks/smoke.jsonl`
- Create: `src/jev_local_experiments/__init__.py`
- Create: `src/jev_local_experiments/schema.py`
- Create: `src/jev_local_experiments/config.py`
- Create: `src/jev_local_experiments/cli.py`
- Create: `tests/test_schema.py`
- Create: `tests/test_config.py`

**Steps:**

1. Write tests for valid binary, Choice, and Score questions and for invalid criteria/labels.
2. Implement standard-library validation and config loading.
3. Add `jevx validate-suite` and `jevx show-config` commands.
4. Run the offline tests and smoke-suite validation.

### Task 3: Record research and alternative candidates

**Files:**
- Create: `docs/research/jev-and-alternatives.md`

**Steps:**

1. Record the sourced distinction between hosted Jev and local alternatives.
2. Record candidate repositories, install directories, hardware notes for the RTX 4060 Ti 16 GB machine, and verification status.
3. Keep all performance claims labeled as self-reported until rerun locally.

### Task 4: Configure identity, Chrome, Qdrant, and optional memory

**Files:**
- Create: `.agent/google-workspace-identity.json`
- Create: `.agent/Google-Workspace-Identity.md`
- Create: `.agent/Chrome-Control-Readiness.md`
- Create: `.agent/qdrant.toml`
- Create: `.agent/integrations.md`
- Create: `.agent/identity-validation/validation-ledger.ndjson`
- Create: `.agent/projects/README.md`

**Steps:**

1. Reference the existing Stellar Insights account bundle and exact Profile 40 route without copying secrets.
2. Mark Chrome control blocked until the BrowserSkill daemon on port 22840 is connected to Profile 40.
3. Configure the dedicated Qdrant collection and reachable embedding endpoint.
4. Record Hindsight as deferred because no project-specific bank exists and cross-project reuse is unsafe.
5. Run the offline Google identity audit and identity manifest summary.

### Task 5: Validate and ingest durable documentation

**Files:**
- Modify: `.agent/identity-validation/validation-ledger.ndjson`
- Modify: `.agent/qdrant.toml` only if validation identifies a configuration issue

**Steps:**

1. Run `uv run pytest` and `uv run jevx validate-suite benchmarks/smoke.jsonl`.
2. Probe Qdrant and LM Studio read-only endpoints.
3. Ingest `docs/` into the dedicated Qdrant collection once the docs exist.
4. Record sanitized counts and final blockers in the completion summary.
