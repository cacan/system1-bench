# Research Review: hearim (헤아림) — Multi-Backend System One Gateway

**Date:** 2026-09-22  
**Candidate ID:** `hearim`  
**Repository:** [https://github.com/ziozzang/hearim](https://github.com/ziozzang/hearim)  
**Author:** `ziozzang`  
**Community Source:** [r/LocalLLaMA: "hearim(헤아림): Maybe you don't need a special model for Jev — ordinary local LLMs already have the capability"](https://www.reddit.com/r/LocalLLaMA/comments/1wm6eri/hearim%ED%97%A4%EC%95%84%EB%A6%BC_maybe_you_dont_need_a_special_model_for/)  
**Implementation Language:** Go  
**Target Installation Path:** `alternatives/hearim/`  

---

## 1. Executive Summary & Core Hypothesis

**hearim** (헤아림, from the Korean verb *헤아리다*, meaning both "to count one by one" and "to comprehend by thinking through") is an open-source gateway that exposes TypeSafe AI's Jev `POST /v1/systemone` interface over ordinary local or remote autoregressive LLMs.

The central hypothesis presented by the project is:
> **You do not need a specialized or fine-tuned model for Jev-style typed decisions.** Standard pretrained and instruction-tuned LLMs already possess rich world knowledge and calibrated decision capabilities. Rather than asking an LLM to generate unstructured text or parse fragile JSON schemas, one can frame decisions as single-token multiple-choice selections and read the model's output logprobs directly.

By restricting inference to **prompt prefill (with prefix caching) + 1-token decode**, hearim avoids multi-token decode latency, eliminates JSON parsing failures, and computes true conditional probabilities with normalized entropy confidence.

---

## 2. Gateway Architecture & Request Flow

```
Client (POST /v1/systemone)
  │
  ▼
[SystemOne Schema Validator]       ── Validates choice / score / noul schemas
  │
  ▼
[RFC 8785 Canonicalizer]           ── Deterministic JSON canonicalization
  │
  ▼
[Model Router]                     ── Maps aliases to provider/engine/model
  │
  ▼
[EvaluationPlan Compiler]          ── Compiles prompt layout (state-major / rubric-major)
  │
  ▼
[Prefix-Aware Scheduler]           ── Groups requests by shared prefix for KV cache reuse
  │
  ▼
[Provider Adapter]                 ── Dispatches to Ollama / llama.cpp / vLLM / SGLang / OpenAI
  │
  ▼
[Logprob Reducer]                  ── Conditional softmax + normalized entropy confidence
  │
  ▼
Jev-Compatible Response            ── Returns choice/score/noul, probabilities, and confidence
```

---

## 3. Mathematical & Scoring Foundation

### 3.1 Probability Restoration
For a decision with candidates $C = \{c_1, \dots, c_K\}$ (e.g. A, B, C, D) and corresponding unnormalized next-token log probabilities $l_1, \dots, l_K$:

$$p(c_i) = \frac{\exp(l_i)}{\sum_{j=1}^K \exp(l_j)}$$

### 3.2 Normalized Entropy Confidence
Confidence is computed directly from the distribution's Shannon entropy $H(p)$, normalized by the maximum possible entropy $\ln(K)$:

$$\text{confidence} = 1 - \frac{H(p)}{\ln K} = 1 - \frac{-\sum_{i=1}^K p(c_i) \ln p(c_i)}{\ln K}$$

- When all probability is concentrated on one option ($p_k = 1$), $H(p) = 0 \implies \text{confidence} = 1.0$.
- When probability is uniformly distributed ($p_i = 1/K$), $H(p) = \ln K \implies \text{confidence} = 0.0$.

### 3.3 Scoring Strategy Fallback Chain
Hearim implements a multi-tier fallback ladder per question:
1. **selected-token-ids**: Direct candidate token-ID logprob request (supported in vLLM and SGLang).
2. **top-k**: Request top-$N$ logprobs (`top_logprobs`) and match by token string or bytes.
3. **teacher-forced-label**: Evaluate input-token logprob of the label token.
4. **constrained-vocab**: Grammar or logit bias masking (`allowed_token_ids`).
5. **choice-text continuation**: Score full text strings under normalized likelihood.

---

## 4. Hardware & Local Runtime Fit

- **Gateway Overhead**: Written in Go; compiles to a single native binary (`hearim.exe`). Consumes <50 MB RAM and negligible CPU during routing.
- **Inference Engine**:
  - Local GPU: NVIDIA GeForce RTX 4060 Ti 16 GB VRAM.
  - Active LM Studio: `http://127.0.0.1:1234/v1` running `google/gemma-4-e4b`.
  - Logprob Verification: Verified via probe that `google/gemma-4-e4b` on LM Studio returns `logprobs` and `top_logprobs` accurately.
- **Offline / Mock Mode**: Hearim includes built-in mock inference capabilities (`cmd/hearim-mock`), enabling offline testing and verification without requiring live GPU compute.

---

## 5. Workspace Integration & Policy Alignment

- **Installation Directory**: Installed strictly in `alternatives/hearim/`, complying with `docs/SOP-POLICIES.md` and `AGENTS.md`.
- **Git Exclusions**: Ignored by `.gitignore` (`/alternatives/*`). No Go build artifacts or dependencies pollute the root repository.
- **Cataloging**: Registered in `alternatives/manifest.toml`.
- **Provider Registration**: Declared in `config/providers.toml` under `[providers.hearim]` on port `8013`.
- **Evaluation**: Validated against `benchmarks/smoke.jsonl` and full benchmark suites.
