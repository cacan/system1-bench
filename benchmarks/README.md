# Benchmark fixtures

Fixtures are JSON Lines (`.jsonl`). Each line represents one test case with:

- `id`: stable case identifier (e.g. `support-001`, `scope-S1`);
- `state`: text, object, or array presented to the decision provider;
- `questions`: one or more typed decisions;
- `labels`: ground-truth expected answers used for evaluation.

## Available Benchmark Suites

| Suite File | Cases | Experiments | Description |
|------------|-------|-------------|-------------|
| [`diverse_300.jsonl`](diverse_300.jsonl) | 300 | 5 | Multi-domain evaluation suite (Banking77, CLINC150, Moderation, E-Commerce, AG News) |
| [`jev_complete.jsonl`](jev_complete.jsonl) | 164 | 27 | Full canonical suite spanning all 27 typed-decision experiments |
| [`jev_core.jsonl`](jev_core.jsonl) | 36 | 4 | Core interactive playground presets (Support triage, Semantic ranking, Citation verification, Feedback signals) |
| [`jev_agentic.jsonl`](jev_agentic.jsonl) | 36 | 9 | Agent reasoning, plan scope, behavioral contracts, boundaries, stopping signals |
| [`jev_governance.jsonl`](jev_governance.jsonl) | 60 | 10 | Safety, hallucination severity, terminology, instruction creep, freshness, policy |
| [`jev_patterns.jsonl`](jev_patterns.jsonl) | 32 | 4 | Architectural patterns: speculative fan-out, confidence gating, composite scoring, intent handlers |
| [`smoke.jsonl`](smoke.jsonl) | 2 | 2 | Minimal synthetic smoke suite for baseline format checks |

For full taxonomy, descriptions of all 27 experiments, and the 50 use-cases catalog, see [`JEV_LAB_EXPLORATION.md`](JEV_LAB_EXPLORATION.md).

## Question Types

- `noul`: binary decision; label is a JSON boolean (`true` or `false`).
- `choice`: finite named options; `criteria` is an object mapping option names to descriptions; label is an option name string.
- `score`: ordered levels; `criteria` is a list of at least two levels; label is a zero-based integer index.

## Policy

Keep public benchmark data and private/customer data in separate files, and do not ingest private data into Qdrant without an explicit source policy. Reference Jev API outputs must remain evaluation-only baselines and must not be used for model distillation or training.
