# Standard Operating Procedures & Workspace Policies (SOP.policies)

**Workspace:** System1-Bench (`d:/WebDev/VScode-projects/-ML-AI/JEV-local-experiments`)  
**Effective Date:** 2026-09-22  
**Status:** Active  

This document serves as the canonical standard operating procedure (SOP) and policy reference for the System1-Bench workspace, specifically defining component boundaries, where code and artifacts must be installed, and candidate evaluation procedures.

---

## 1. Installation Boundaries (Where Things Must Be Installed)

To prevent repository bloat, credential leaks, and accidental commits of large models or third-party code trees, the workspace enforces strict installation boundaries:

| Component Type | Target Installation Path | Tracked in Git? | Policy & Constraints |
| :--- | :--- | :---: | :--- |
| **Third-Party Alternative Implementations** | `alternatives/<id>/`<br>*(e.g., `alternatives/hearim/`, `alternatives/kev/`)* | **No** (Ignored by `.gitignore`) | External checkouts, git sub-repositories, Go/Rust/C++ builds, and Python virtual environments MUST reside here. Never vendor third-party source files into the workspace root. |
| **Alternative Catalog & Manifest** | `alternatives/manifest.toml` | **Yes** | Every candidate evaluated or installed must have a registered entry declaring its `id`, `repo`, `install_dir`, `status`, and hardware notes. |
| **Alternative Guidelines** | `alternatives/README.md` | **Yes** | Defines candidate isolation conventions and step-by-step onboarding guidelines. |
| **Runtime & Provider Configurations** | `config/providers.toml` | **Yes** | Declares endpoints, ports, model aliases, and `install_dir = "alternatives/<id>"`. Never commit secrets/API keys here. |
| **Workspace Global Parameters** | `config/workspace.toml` | **Yes** | Non-secret system parameters, hardware specs (RTX 4060 Ti 16 GB), and benchmark modes. |
| **Benchmark Fixtures & Test Cases** | `benchmarks/*.jsonl` | **Yes** | Versioned benchmark suites (e.g., `smoke.jsonl`, `jev_complete.jsonl`). Must contain only public/synthetic benchmark cases. |
| **Evaluation Run Results** | `results/*.jsonl` | **No** (Only `.gitkeep` tracked) | Raw benchmark outputs, response logs, and evaluation traces. |
| **Durable Research & Decisions** | `docs/research/`, `docs/plans/`, `docs/benchmarks/` | **Yes** | Markdown documentation, analysis reports, comparison findings, and plans. Also acts as the ingest source for Qdrant. |
| **Local LLM Weights & Runtimes** | External (`LM Studio` / `vLLM` / `Ollama`) | **No** | Heavy model weights (GGUF, Safetensors) are served externally via local/network services (e.g. LM Studio on `http://127.0.0.1:1234/v1`) or placed in local machine model caches. Weights must NEVER be committed to this repository. |
| **Secrets, Tokens & Credentials** | `~/.codex/secrets/` or Environment Variables | **No** | API keys (such as Jev API keys, provider tokens) are read at runtime from machine-local paths or environment variables (e.g. `${HEARIM_API_KEY}`). Never commit secrets or print them in logs. |
| **Python Package & Harness** | `src/jev_local_experiments/`, `tests/` | **Yes** | Neutral schema validator, CLI (`s1b`), configuration loader, and evaluation utilities. |

---

## 2. Candidate Onboarding SOP (Standard Operating Procedure)

When adding or evaluating any new Jev-style alternative model or gateway:

1. **Verify Candidate Alignment**:
   - Check that the tool or model addresses Jev-style typed decisions (`noul`, `choice`, `score`) or classification logprob recovery.
   - Confirm hardware requirements fit local hardware (NVIDIA RTX 4060 Ti 16 GB VRAM, 128 GB RAM) or LAN inference backends (LM Studio).

2. **Register in Manifest**:
   - Add an entry to `alternatives/manifest.toml` with `status = "candidate"` or `"installed"`.

3. **Install into Designated Boundary**:
   - Clone or initialize the candidate into `alternatives/<id>/`.
   - Build or install its isolated environment (e.g., Go binary, Python venv, or Docker container) entirely within `alternatives/<id>/`.
   - Verify that `git status` in the workspace root remains clean and ignores the new directory contents.

4. **Configure Provider Endpoint**:
   - Add `[providers.<id>]` in `config/providers.toml` setting `install_dir = "alternatives/<id>"`, unique port (e.g. `8013`), and local endpoint.
   - Configure the candidate's own config (e.g. `hearim.yaml`) using environment variables for authentication and pointing to local/LAN LLM backends.

5. **Execute Verification & Benchmarking**:
   - Run offline test suite: `uv run pytest`.
   - Validate workspace configuration: `uv run s1b show-config`.
   - Test connectivity with smoke suite: `uv run s1b validate-suite benchmarks/smoke.jsonl`.
   - Record candidate performance claims as unverified until reproduced locally.

6. **Document Research Findings**:
   - Save a structured review and evaluation report in `docs/research/<date>-<id>-review.md`.
