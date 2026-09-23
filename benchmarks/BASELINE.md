# Jev reference baseline

The workspace can run the same fixture suite against the hosted Jev API as a reference point for latency and decision quality.

```powershell
uv run s1b benchmark-jev --suite benchmarks/smoke.jsonl --output results/jev-baseline.jsonl
```

The provider reads the key from the `JEV_API_KEY` environment variable (or `JEV_API_KEY_FILE` path) at runtime. The secret contents are never copied into the repository, result files, logs, or external stores.

This baseline is reference-only. Do not use Jev responses as training labels, distillation targets, or model-development data. Compare independent alternatives against the same fixture labels instead.

The API contract is TypeSafe's `POST /v1/systemone` with `model`, `state`, and typed `questions`; the model catalog currently exposes `jev-latest` and `jev-preview`.
