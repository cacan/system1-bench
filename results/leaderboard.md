# Benchmark Leaderboard: Core Typed Decisions (`jev_core`)

**Benchmark Suite:** `benchmarks/jev_core.jsonl` (37 cases, customer support triage & routing)  
**Evaluation Primitives:** Noul (Binary), Choice (Categorical), Score (Rubric)

| Provider | Model | Categorical Accuracy | Score MAE | Latency p50 | Throughput | Model Type |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **`jev_reference`** | `jev-1.13.0` | **100.0%** | **0.000** | 744.4 ms | 1.4 RPS | Closed / Hosted API Baseline |
| **`hearim_ornith35b`** | `ornith-35b` | **100.0%** | 0.167 | 5,813.4 ms | 0.2 RPS | Open-Weights Local Engine |
| **`hearim_kwei`** | `kwei` | **98.2%** | 0.061 | 5,212.1 ms | 0.2 RPS | Open-Weights Local Engine |
| **`hearim_gemma26b`** | `gemma-26b` | **96.4%** | **0.000** | 1,211.8 ms | 0.8 RPS | Open-Weights Local Engine |
| **`laya`** | `laya-typed-decisions`| **96.4%** | 0.671 | **53.7 ms** | **16.9 RPS** | Specialized Low-Latency Classifier |
| **`hearim_qwen35_9b`** | `qwen35-9b` | **94.6%** | 0.146 | 646.1 ms | 1.6 RPS | Open-Weights Local Engine |
| **`hearim`** | `gemma4` | **91.1%** | 0.162 | 891.1 ms | 1.1 RPS | Open-Weights Local Engine |
| **`hearim_bonsai27b`** | `bonsai-27b` | **91.1%** | 0.242 | 2,079.0 ms | 0.6 RPS | Open-Weights Local Engine |
| **`hearim_qwen35_4b`** | `qwen35-4b` | **89.3%** | 0.100 | 685.6 ms | 1.5 RPS | Open-Weights Local Engine (4B) |
| **`hearim_qwen3_2507`** | `qwen3-2507` | **87.5%** | 0.316 | 150.3 ms | 6.7 RPS | Fast Local Distilled Head |
| **`hearim_spark4b`** | `spark-4b` | **75.0%** | 0.045 | 489.5 ms | 1.9 RPS | Open-Weights Local Engine (4B) |
| **`hearim_minicpm5_2b`**| `minicpm5-2b` | **80.4%** | 0.405 | 139.6 ms | 7.0 RPS | Compact Edge Head (2B) |

---

### Key Takeaways

1. **Accuracy Parity**: Open-weights models (`ornith-35b`, `kwei`, `gemma-26b`) match or approach 100% accuracy of the proprietary Jev baseline on categorical and binary decisions.
2. **Ultra-Low Latency Alternatives**: Specialized classifiers like `laya` achieve **96.4% accuracy at 53.7ms latency** (14x faster than hosted Jev API).
3. **Reproducibility**: All raw runs are published in `results/runs/` and viewable interactively in `results/dashboard.html`.
