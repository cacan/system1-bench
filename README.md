# System1-Bench: Open-Source System 1 Decision Benchmarks

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![Zero Secrets](https://img.shields.io/badge/security-audited-success.svg)]()

> **Benchmarking open-source System 1 decision alternatives.**

A reproducible evaluation harness and benchmark lab comparing open-source and free alternatives for **System 1** typed decisions (fast constrained decision heads, evaluated against hosted reference baselines).

---

## ⚡ What are Typed Decisions?

Traditional LLM workflows force language models to output free-form text or JSON strings via auto-regressive decoding. This approach suffers from non-deterministic latency, high token costs, JSON syntax errors, and hallucinations.

**Typed Decisions** constrain the model directly at inference time, outputting mathematically rigorous structured predictions:

- **Noul (Binary)**: Continuous probability \(p \in [0.0, 1.0]\) evaluated via Brier score calibration and decision thresholds.
- **Choice (Categorical)**: Exact probability distribution over mutually exclusive criteria.
- **Score (Ordered Rubric)**: Class probabilities and continuous expected score evaluated against rubrics via Mean Absolute Error (MAE).

---

## 🏆 Benchmark Highlights (`jev_core`)

Evaluation of top open-source models versus the proprietary Jev 1.13 reference baseline across 37 customer support triage cases:

| Model | Provider | Categorical Accuracy | Score MAE | Latency p50 | Throughput | Notes |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **`jev-1.13.0`** | `jev_reference` | **100.0%** | **0.000** | 744 ms | 1.4 RPS | Closed / Hosted API Baseline |
| **`ornith-35b`** | `hearim` | **100.0%** | 0.167 | 5,813 ms | 0.2 RPS | Full accuracy parity |
| **`kwei`** | `hearim` | **98.2%** | 0.061 | 5,212 ms | 0.2 RPS | High calibration |
| **`gemma-26b`** | `hearim` | **96.4%** | **0.000** | 1,212 ms | 0.8 RPS | Exact rubric match |
| **`laya-typed`** | `laya` | **96.4%** | 0.671 | **54 ms** | **16.9 RPS** | **14x faster** than hosted baseline |
| **`qwen35-9b`** | `hearim` | **94.6%** | 0.146 | 646 ms | 1.6 RPS | Balanced open model |
| **`qwen35-4b`** | `hearim` | **89.3%** | 0.100 | 686 ms | 1.5 RPS | Lightweight edge candidate |

*Full results, metrics, and raw runs are available in [`results/leaderboard.md`](results/leaderboard.md) and [`results/runs/`](results/runs/).*

---

## 📊 Interactive Comparison Dashboard

This repository includes a standalone, zero-dependency interactive HTML comparison dashboard in [`results/dashboard.html`](results/dashboard.html).

It features:
- **Leaderboard & KPIs**: Speed, accuracy, and MAE across all tested providers.
- **Model Race Simulation**: Side-by-side visual race showing single forward-pass logit scoring vs standard autoregressive LLMs.
- **Decision Disagreements Table**: Filterable win/loss matrix comparing any candidate against the baseline.
- **Case Explorer**: Full inspection of state inputs, question instructions, and rubric criteria.
- **Testing & Evaluation Guide**: Built-in visual guide explaining metrics and formulas.

To view locally:
```powershell
# Open in your default browser
Start-Process results/dashboard.html
```

---

## 🛠️ Tools that Explain Testing & Visualize Decisions

This repository provides built-in CLI tools to inspect, explain, and simulate testing:

### 1. Interactive Model Race Simulation (`s1b race`)
Watch a real-time side-by-side race comparing fast System 1 logit scoring (~54ms) against standard autoregressive token generation (~780ms) across a test suite:
```powershell
uv run s1b race --suite benchmarks/diverse_300.jsonl --cases 50
```

### 2. Inspect Any Benchmark Case (`s1b explain-case`)
View the input scenario, questions, rubric scale, ground truth, and analyze model prediction errors:
```powershell
uv run s1b explain-case bank-001 --suite benchmarks/diverse_300.jsonl
```

With model error analysis:
```powershell
uv run s1b explain-case support-001 --suite benchmarks/smoke.jsonl --results results/runs/hearim-qwen35-4b-core.jsonl
```

### 3. Educational Metrics Guide (`s1b explain-metrics`)
Print a comprehensive reference of decision primitives, Brier score calibration, MAE formulas, and evaluation contracts:
```powershell
uv run s1b explain-metrics
```

### 4. Read the Methodology Guide
Read [`docs/HOW_TESTING_WORKS.md`](docs/HOW_TESTING_WORKS.md) for full mathematical definitions, benchmark suite hierarchies, and evaluation procedures.

---

## 🚀 Quick Start

### 1. Clone & Install
```powershell
git clone https://github.com/<your-username>/system1-bench.git
cd system1-bench

# Install dependencies using uv
uv sync --extra dev
```

### 2. Run Tests
```powershell
uv run pytest
```

### 3. Validate Benchmark Fixtures
```powershell
uv run s1b validate-suite benchmarks/smoke.jsonl
uv run s1b validate-suite benchmarks/jev_core.jsonl
uv run s1b validate-suite benchmarks/diverse_300.jsonl
```

### 4. View Leaderboard
```powershell
uv run s1b leaderboard
```

---

## 🔒 Security & Privacy Boundary

- **Zero-Secret Policy**: No API keys, authentication tokens, private IPs, or personal filesystem paths are committed to this repository.
- **Automated Audit**: Run `uv run python scripts/check_secrets.py` to verify repository sanitization.
- **Credential Handling**: If evaluating against external reference APIs, pass keys strictly via environment variables (`JEV_API_KEY` or `JEV_API_KEY_FILE`).

---

## 📂 Repository Layout

```
system1-bench/
├── benchmarks/               # Versioned JSONL test suites (smoke, core, complete, etc.)
├── config/                   # Non-secret configuration & templates (.example.toml)
├── data/registries/          # Token scoring profiles for open-source models
├── docs/                     # Testing methodology, research reviews, and guides
│   └── HOW_TESTING_WORKS.md  # Detailed guide on typed decisions and metrics
├── results/                  # Curated benchmark results & artifacts
│   ├── dashboard.html        # Interactive zero-dependency HTML dashboard
│   ├── leaderboard.md        # Summary leaderboard table
│   └── runs/                 # Canonical evaluation run JSONL files
├── scripts/                  # Security scan and utility scripts
├── src/                      # Core package and CLI (s1b / jevx)
├── tests/                    # Automated pytest suite
├── LICENSE                   # MIT License
└── pyproject.toml            # Project metadata and dependencies
```

---

## 📄 License

Distributed under the [MIT License](LICENSE).
