# JEV Local Experiments

This repository is a local lab for testing open-source and free alternatives to Jev's typed-decision interface. Jev itself is hosted and closed; this workspace compares independent local implementations and simpler classifier/logit-scoring baselines under one reproducible fixture and measurement contract.

## Quick start

```powershell
uv sync --extra dev
uv run pytest
uv run jevx validate-suite benchmarks/smoke.jsonl
uv run jevx show-config
uv run jevx benchmark-jev --suite benchmarks/smoke.jsonl
```

The smoke suite validates the fixture contract only. It does not claim model quality until a provider is installed and a run is recorded under `results/`.

The Jev reference baseline reads the API key from the machine-local path configured in `config/providers.toml`; the key is never committed or printed. Reference outputs are evaluation-only and must not be used as training or distillation labels.

## Layout

- `alternatives/` — local third-party checkouts/installations; ignored by default.
- `benchmarks/` — versioned JSONL fixtures and benchmark notes.
- `config/` — non-secret workspace and provider parameters.
- `docs/` — research, plans, and durable experiment notes.
- `.agent/` — identity, Chrome, Qdrant, and integration metadata.
- `src/jev_local_experiments/` — provider-neutral schema/config/validation code.
- `results/` — local reports and raw run outputs; ignored by default.

## First candidates

The initial shortlist is recorded in [`alternatives/manifest.toml`](alternatives/manifest.toml): Kev, OpenJev Verdict, NanoJev, open-jev/logit scoring, and ModernBERT/SetFit baselines. Install one candidate at a time under its declared directory and capture its exact revision in the run metadata.

## Integrations

Qdrant and the configured LM Studio embedding endpoint are available on the local network. The workspace references the existing `analytics@stellar-insights.com` account bundle and Profile 40 for future browser research, but does not enable Google APIs or Gmail access. Hindsight remains optional until a dedicated project bank exists.
