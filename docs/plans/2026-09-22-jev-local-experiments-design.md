# JEV Local Experiments Workspace Design

**Status:** Approved for initialization on 2026-09-22

## Goal

Create a local, reproducible workspace for evaluating open-source and free alternatives to Jev's typed-decision interface without treating the project as a GTM/GA4 workspace.

## Research decision

Jev itself is a hosted, closed model with no public weights or supported local build. The workspace therefore evaluates Jev-style implementations and adjacent local classifiers rather than attempting to install Jev. The first benchmark is workload-neutral and supports the three useful decision shapes: binary/Noul, Choice, and ordered Score.

Initial candidate families are:

- Kev: a small local System One-compatible family with 0.8B, 4B, and 9B variants.
- OpenJev Verdict: a small non-autoregressive calibrated decision model.
- NanoJev: a small Jev-style model with an end-to-end training pipeline.
- Open-jev/logit-scoring adapters: local option scoring over an existing open model.
- Classical encoder baselines such as ModernBERT/SetFit for fixed-label classification.

Published numbers are treated as claims until this workspace reruns them on shared fixtures.

## Workspace architecture

```text
config/       Non-secret experiment and provider parameters
benchmarks/   Versioned JSONL fixtures and benchmark documentation
alternatives/ Local third-party checkouts/installations (ignored by default)
src/          Small reusable schema/config/validation package
tests/        Offline tests for schemas and configuration
docs/         Research, decisions, and durable experiment notes
.agent/       Workspace-scoped identity, browser, Qdrant, and integration metadata
results/      Local run outputs (ignored)
```

The main harness stays provider-neutral. Each alternative is installed under `alternatives/<id>/` and is called through an adapter or HTTP endpoint recorded in `config/providers.toml`. No model weights, OAuth tokens, or third-party source trees are committed to the main repository.

## Integrations

- Provider boundaries: each alternative is called through an adapter or HTTP endpoint configured in `config/providers.toml`.
- API keys: loaded strictly from environment variables; never committed to the repository.
- Research memory: optional local vector storage or documentation sync.

## Evaluation contract

Every provider should eventually be measured on the same cases for:

1. task accuracy against explicit labels,
2. probability quality (Brier score and calibration error where probabilities exist),
3. selective risk/coverage for confidence thresholds,
4. p50/p95 latency and throughput,
5. option-order sensitivity, and
6. reproducibility (provider revision, model revision, runtime, device, and config snapshot).

The initial smoke fixture is intentionally tiny and synthetic. It is a wiring check, not a quality claim.

## Non-goals

- No GTM, GA4, Search Console, Ads, Merchant, or BigQuery project structure.
- No automatic download of model weights or third-party repositories during initialization.
- No production decision service, external publishing, or Gmail access.
- No implicit Hindsight bank creation or cross-project memory reuse.
