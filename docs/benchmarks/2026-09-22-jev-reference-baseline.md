# Jev reference baseline — 2026-09-22

This is a wiring baseline for the checked-in synthetic smoke suite, not a general capability claim.

## Run metadata

- Provider: `jev_reference`
- Requested model: `jev-latest`
- Returned model: `jev-1.13.0`
- Endpoint: `https://api.typesafe.ai/v1/systemone`
- Fixture: `benchmarks/smoke.jsonl`
- Cases: 2
- Questions: 5
- HTTP results: 2/2 successful (`200`)
- Raw result file: `results/jev-baseline.jsonl` (ignored by Git)
- API key: read at runtime from the machine-local path in `config/providers.toml`; not copied into this document or the result file

## Observed smoke metrics

- Latencies: 759.724 ms and 731.540 ms
- Mean latency: 745.632 ms
- Label agreement: 5/5 on the two synthetic cases using the fixture labels, binary threshold, and argmax Choice/Score checks

The sample is too small for a quality conclusion. The result only establishes that the reference provider, request conversion, response capture, and timing path work.

## Policy

Jev responses are reference-only. They must not be used as training labels, distillation targets, or model-development data for the alternatives. Compare local candidates against the fixture labels and keep their output separate from this reference artifact.
