# Jev and local alternatives

**Research date:** 2026-09-22

## What Jev is

Jev is a hosted System One decision model/API. The official local-run page says that Jev has no public weights, offline binary, or supported self-hosting path. The useful local target is therefore a compatible decision interface or an independent model that returns probabilities over typed options.

Sources:

- [TypeSafe AI: Running Jev locally](https://www.jevtypesafeai.com/jev/local)
- [Community-maintained awesome-jev catalog](https://github.com/heyjunpenn/awesome-jev)
- [System One Models: open alternatives](https://systemonemodels.org/examples/alternatives/)

## Candidate shortlist

| Candidate | Approach | First local test | Caveat |
| --- | --- | --- | --- |
| [Kev](https://github.com/jaredpalmer/kev) | Small local System One-compatible family on Qwen3.5; Choice/Noul/Score | 0.8B, then 4B | Upstream metrics are self-reported and hardware/dtype dependent |
| [OpenJev Verdict 2.0](https://github.com/heman10x-ngu/openJev-verdict-2.0) | 151M non-autoregressive decision model | Released checkpoint | Verify calibration and license locally |
| [NanoJev](https://github.com/TianyuCodings/NanoJev) | 0.6B Jev-style probability model with training pipeline | Released checkpoint | Independent reproduction; not Jev weights |
| [open-jev](https://github.com/daseinlabs/open-jev) | Batched option/logit scoring over an open model | 3B–4B quantized base | Quality depends strongly on the chosen base model and prompting |
| ModernBERT/SetFit | Fixed-label encoder classifiers | CPU/GPU baseline | Not a drop-in System One API; useful control group |

The RTX 4060 Ti has 16 GiB VRAM. Small checkpoints and a quantized 3B–4B model are the sensible starting range; a 9B model may require careful quantization and memory checks. No candidate is installed automatically by workspace initialization.

## Shared evaluation contract

For every candidate, use the same fixture and record:

1. exact repository/model revision and license;
2. runtime, dtype, quantization, and device;
3. accuracy per question type;
4. Brier score and calibration error where probabilities are available;
5. selective risk at explicit confidence thresholds;
6. p50/p95 latency and throughput;
7. option-order sensitivity; and
8. raw request/response references without credentials.

The checked-in smoke suite is only a wiring test. A real comparison needs a held-out labeled set and a documented split before any accuracy claim is made.

## Integration posture

The workspace maintains strict credential isolation: no proprietary keys, personal accounts, or browser session tokens are stored in the repository.

## Jev reference baseline

The workspace has a reference-only provider for the hosted Jev API. It reads the API key from the environment variable `JEV_API_KEY` (or `JEV_API_KEY_FILE`) and runs only on approved benchmark fixtures. Jev outputs must not be used as training or distillation labels for the alternatives. See [`benchmarks/BASELINE.md`](../../benchmarks/BASELINE.md).
