# System1-Bench: Open-Source System 1 Decision Benchmarks

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Zero Secrets](https://img.shields.io/badge/security-audited-success.svg)]()
[![Dashboard: Interactive](https://img.shields.io/badge/dashboard-interactive_HTML-blue.svg)](index.html)

> **Benchmarking open-source System 1 decision alternatives.**
> 
> An open, reproducible benchmark evaluation suite and interactive dashboard comparing open-source alternatives for **System 1 typed decisions** (fast constrained decision heads, evaluated against hosted reference baselines).

---

## 📊 Interactive Comparison Dashboard

The complete benchmark evaluation is available as a zero-dependency, self-contained interactive dashboard in **[`index.html`](index.html)** (also mirrored at [`results/dashboard.html`](results/dashboard.html)).

### Key Features:
- 🏆 **Winners Matrix**: Clear identification of Pareto champions, accuracy leaders, and ultra-fast edge candidates.
- ⚡ **Model Race Simulation**: Side-by-side visual race illustrating single forward-pass logit scoring (~54 ms) versus autoregressive token generation (~780 ms).
- 📊 **Diverging Latency Waterfall**: Latency comparison relative to the 744 ms reference baseline (speedups in green, overhead in purple).
- 🗺️ **2D Accuracy vs. Speedup Map**: Interactive quadrant scatter plot mapping categorical accuracy against speedup factor.
- 📋 **Master Leaderboard Table**: Searchable, filterable table covering p50 latency, throughput (RPS), categorical accuracy, rubric MAE, and VRAM footprints.
- 🔍 **Urgency Anomaly Deep-Dive**: Analysis of edge cases (e.g., billing disputes) where instruct models diverge from conservative baseline ground truth.

### How to View:
Simply open `index.html` in any web browser:
```powershell
# Windows
Start-Process index.html

# macOS
open index.html

# Linux
xdg-open index.html
```

---

## ⚡ What are Typed Decisions?

Traditional LLM workflows force language models to output free-form text or JSON strings via auto-regressive decoding. This approach suffers from non-deterministic latency, high token costs, JSON syntax errors, and hallucinations.

**Typed Decisions** constrain the model directly at inference time, outputting mathematically rigorous structured predictions:

- **Noul (Binary)**: Continuous probability \(p \in [0.0, 1.0]\) evaluated via Brier score calibration and decision thresholds.
- **Choice (Categorical)**: Exact probability distribution over mutually exclusive criteria.
- **Score (Ordered Rubric)**: Class probabilities and continuous expected score evaluated against rubrics via Mean Absolute Error (MAE).

---

## 🏆 Benchmark Highlights (`jev_core`)

Evaluation of top open-source models versus the reference baseline across 36 enterprise triage cases (56 decision questions):

| Model | Provider | Clean Accuracy (44 Qs)* | Full Accuracy (56 Qs) | Score MAE | Latency p50 | Throughput | Notes |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`jev-1.13.0`** | `jev_reference` | **100.0%** | **100.0%** | **0.000** | 744 ms | 1.4 RPS | Hosted Baseline Standard |
| **`ornith-35b`** | `hearim` | **100.0%** | **100.0%** | 0.167 | 5,813 ms | 0.2 RPS | Full accuracy parity across all cases |
| **`kwei`** | `hearim` | **100.0%** | 98.2% | 0.061 | 5,212 ms | 0.2 RPS | High calibration & reasoning depth |
| **`gemma-26b`** | `hearim` | **100.0%** | 96.4% | **0.000** | 1,212 ms | 0.8 RPS | Exact rubric match (0.000 MAE) |
| **`laya-typed`** | `laya` | **100.0%** | 96.4% | 0.671 | **54 ms** | **16.9 RPS** | **14x faster** than hosted baseline |
| **`qwen35-9b`** | `hearim` | **100.0%** | 94.6% | 0.146 | 646 ms | 1.6 RPS | Balanced open enterprise model |
| **`qwen35-4b`** | `hearim` | 93.2% | 89.3% | 0.100 | 686 ms | 1.5 RPS | Lightweight edge deployment candidate |

*\* **Clean Accuracy (Without Urgency\*)**: Evaluates the 44 objective multi-class routing, topic classification, churn risk, and claim verification decisions, isolating structural decision capability from conservative vs. liberal urgency labeling.*

*Full metrics and case-by-case outputs are available in [`results/leaderboard.md`](results/leaderboard.md) and [`results/runs/`](results/runs/).*

---

## 📁 Public Evaluation Datasets (`benchmarks/`)

The repository includes versioned benchmark suites formatted in JSON Lines (`.jsonl`):

- **[`diverse_300.jsonl`](benchmarks/diverse_300.jsonl)**: 300 curated test cases across 5 diverse domains:
  - Banking & Financial Services (PolyAI Banking77)
  - Intent Routing & Virtual Assistants (CLINC150)
  - Trust & Safety / Content Moderation
  - E-Commerce Support & Retail Inquiries
  - News & Topic Categorization (AG News)
- **[`jev_core.jsonl`](benchmarks/jev_core.jsonl)**: Canonical 36-case benchmark covering Support Triage, Semantic Ranking, Citation Verification, and Feedback Signals.
- **[`jev_complete.jsonl`](benchmarks/jev_complete.jsonl)**: 164 cases spanning 27 typed-decision experiment patterns.
- **[`jev_agentic.jsonl`](benchmarks/jev_agentic.jsonl)**: Agent reasoning, plan scope, behavioral contracts, and stopping signals.
- **[`jev_governance.jsonl`](benchmarks/jev_governance.jsonl)**: Policy compliance, safety thresholds, and instruction boundary tests.

---

## 📂 Repository Contents

```
system1-bench/
├── index.html                # Standalone interactive dashboard & model race simulation
├── benchmarks/               # Public evaluation test suites (.jsonl)
│   ├── diverse_300.jsonl     # 300-case multi-domain benchmark suite
│   ├── jev_core.jsonl        # Core enterprise triage benchmark suite
│   ├── jev_complete.jsonl    # Comprehensive 27-experiment test suite
│   └── README.md             # Dataset documentation and question schema
├── results/                  # Published benchmark results & artifacts
│   ├── dashboard.html        # Interactive HTML dashboard mirror
│   ├── leaderboard.md        # Formatted markdown leaderboard table
│   ├── leaderboard.json      # Machine-readable evaluation metrics
│   ├── runs/                 # Case-by-case raw evaluation logs for reproducibility
│   └── README.md             # Results overview and reproduction notes
└── LICENSE                   # MIT License
```

---

## 🔒 Security & Sanitization

- **Zero-Secret Policy**: All published artifacts are sanitized. No API keys, credentials, private IPs, or personal paths are stored.
- **Evaluation Integrity**: All outputs in `results/runs/` reflect reproducible, recorded executions.
