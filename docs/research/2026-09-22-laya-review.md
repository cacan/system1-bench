# Candidate Review: Laya (ConvAI Innovations)

**Date:** 2026-09-22  
**Candidate ID:** `laya`  
**License:** Apache 2.0  
**Upstream Repository:** `https://github.com/NandhaKishorM/laya`  
**Model Weights:** `https://huggingface.co/convaiinnovations/laya`  
**Release Date:** September 18, 2026  
**Status:** Installed / Live Benchmark  

---

## 1. Executive Summary

Laya is an open-source, non-autoregressive "System 1" decision engine developed by Nandakishor Mukkunnoth (ConvAI Innovations). Launched three days after TypeSafe AI's commercial Jev service, Laya provides a locally deployable, Apache 2.0-licensed alternative that produces structured, typed decisions and calibrated probabilities in a single forward pass without autoregressive token generation.

Unlike Hearim (which is a Go gateway mapping prompts to autoregressive LLMs via single-token logprob scoring), Laya uses a dedicated encoder backbone topped with an RLCD-trained (Reinforcement Learning for Calibrated Decisions) multi-task decision head.

---

## 2. Technical Architecture

### Backbone Models
- **English / Typed Decisions:** Built on ModernBERT-large (421M parameters).
- **Multilingual:** Built on mmBERT-base (322M parameters) covering 100+ languages and scripts.

### Decision Head & Forward Pass
- State inputs (plain text or JSON) and questions are concatenated into an encoder sequence.
- Option marker tokens indicate each choice or rubric level.
- A single forward pass through the transformer backbone and scorer head yields logits across all options simultaneously.
- No autoregressive generation, no token streaming, no text parsing, and zero risk of prose hallucination.
- Typical inference latency on modern GPUs is 30–40 ms (7–15 ms batched).

### Calibration & RLCD Training
Laya is trained against strictly proper scoring rules (Brier score and log score) via Reinforcement Learning from Calibrated Decisions (RLCD). This forces reported probabilities to reflect empirical ground-truth likelihoods, enabling reliable automated confidence gating.

---

## 3. Decision Primitives Compatibility

Laya's internal API natively implements the exact three Jev System One primitives:

| Primitive | Output Structure | Jev Parity |
| :--- | :--- | :--- |
| **`choice`** | Categorical decision, confidence, full option probability distribution | 100% byte-for-byte compatible |
| **`score`** | Continuous expected rubric value, discrete level probabilities, legend | 100% byte-for-byte compatible |
| **`noul`** | Binary calibrated probability `P(true)` and confidence | 100% byte-for-byte compatible |

The output schema matches TypeSafe's `/v1/systemone` format down to field names (`answers`, `type`, `choice`, `score`, `noul`, `confidence`, `probabilities`, `legend`, `usage`).

---

## 4. Hardware Fit & Deployment Boundary

- **Local Machine:** NVIDIA GeForce RTX 4060 Ti 16 GB VRAM.
- **VRAM Requirement:** ~842 MB model weights + ~300 MB KV/activations = < 1.5 GB VRAM.
- **Installation Policy:** All dependencies and code are strictly isolated within `alternatives/laya/` (`alternatives/laya/.venv`). Model weights are fetched into Hugging Face local cache or local alternative boundary, keeping the main repository clean.
- **Serving Architecture:** A lightweight local HTTP adapter (`alternatives/laya/serve.py`) listens on `http://127.0.0.1:8014/v1/systemone`, enabling seamless integration with the `s1b benchmark-provider` harness.

---

## 5. Architectural Comparison

| Dimension | TypeSafe Jev | Hearim (Gemma 4 Local) | Laya (convaiinnovations) |
| :--- | :--- | :--- | :--- |
| **Type** | Hosted Proprietary API | Open-source Go Gateway | Dedicated Open Weights Encoder |
| **Backbone** | Undisclosed | Gemma 4 (26B-A4B-IT quantized) | ModernBERT-large (421M) / mmBERT |
| **Inference Mode** | Non-autoregressive head | Autoregressive logprob extraction | Non-autoregressive forward pass |
| **Latency (p50)** | ~750 ms (cloud roundtrip) | ~890 ms (LAN LM Studio) | ~30–40 ms (local GPU) |
| **Token Cost** | Commercial SaaS pricing | $0 (Self-hosted) | $0 (Self-hosted) |
| **Licensing** | Closed commercial | MIT | Apache 2.0 |
