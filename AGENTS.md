# System1-Alternatives-Benchmark - Agent Guidelines

## Purpose

This repository is a local evaluation harness for benchmarking open-source and free alternatives for System 1 typed decisions.

The benchmarks evaluate models on three typed-decision primitives:
1. **Noul (binary)**: Continuous probability decisions [0.0, 1.0].
2. **Choice (categorical)**: Multi-option categorical distributions.
3. **Score (rubric)**: Ordered discrete/continuous ratings against evaluation rubrics.

## Operating Rules

- Keep all documentation, code comments, test suites, and commit messages in English.
- **Zero-Secret Policy**: Never commit API keys, authentication tokens, credentials, private IPs, or personal filesystem paths to this repository.
- Use environment variables (`JEV_API_KEY`, `JEV_API_KEY_FILE`) for external provider credentials.
- `alternatives/` is a local installation boundary. Third-party source trees and model weights remain untracked; record each candidate in `alternatives/manifest.toml`.
- Results published under `results/runs/` must be sanitized and reproducible.
- Any new features, metrics, or CLI tools must be covered by automated unit tests in `tests/`.

## Key Commands

```powershell
# Environment setup
uv sync --extra dev

# Run unit tests
uv run pytest

# Validate benchmark fixtures
uv run jevx validate-suite benchmarks/smoke.jsonl

# Inspect configuration
uv run jevx show-config

# Explain test cases and metrics
uv run jevx explain-case support-001 --suite benchmarks/smoke.jsonl
uv run jevx explain-metrics

# View leaderboard
uv run jevx leaderboard
```
