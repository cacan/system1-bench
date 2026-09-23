# How Testing Works: Typed Decisions & Benchmark Methodology

This guide explains the testing architecture, evaluation contracts, and scoring methodology used in **System1-Alternatives-Benchmark**.

---

## 1. What are Jev-Style Typed Decisions?

Standard Large Language Models (LLMs) operate via auto-regressive next-token text prediction. Generating structured outputs (such as JSON or routing classifications) via prompting requires decoding dozens or hundreds of tokens, often resulting in syntax errors, hallucinated fields, non-deterministic latency, and high token costs.

**Typed Decisions** replace free-form chat generation with deterministic, constrained decision heads:

```
                      +-------------------+
                      |   Input State     |
                      | (Customer Ticket) |
                      +---------+---------+
                                |
                                v
                   +------------------------+
                   |  Typed Decision Engine |
                   |  (Hearim / Laya / Jev) |
                   +------------+-----------+
                                |
        +-----------------------+-----------------------+
        |                       |                       |
        v                       v                       v
+---------------+       +---------------+       +---------------+
|     NOUL      |       |    CHOICE     |       |     SCORE     |
| [Binary Prob] |       | [Categorical] |       |   [Rubric]    |
| Urgent: 0.82  |       | Team: Billing |       | Disruption: 2 |
+---------------+       +---------------+       +---------------+
```

Each typed decision query specifies:
- **`state`**: A string or structured context (e.g. support ticket, error log, transaction).
- **`questions`**: A dictionary of typed queries (`noul`, `choice`, or `score`).
- **`criteria`**: Enumerated options, rubrics, or instructions.

---

## 2. The Three Core Decision Primitives

### A. Noul (Binary Probability Decision)
A **Noul** decision evaluates a boolean hypothesis and outputs a continuous probability \(p \in [0.0, 1.0]\).

- **Inference Output**:
  ```json
  "urgent": {
    "type": "noul",
    "noul": 0.8203
  }
  ```
- **Decision Rule**: A prediction is classified as **True** if \(p \ge 0.50\), and **False** if \(p < 0.50\).
- **Evaluation Metrics**:
  - **Categorical Accuracy**: % of cases where the binary decision matches the ground truth label.
  - **Brier Score**: Quadratic penalty measuring probability calibration:
    $$BS = \frac{1}{N} \sum_{i=1}^N (p_i - y_i)^2$$
    where \(y_i \in \{0, 1\}\) and \(p_i \in [0.0, 1.0]\). A lower score indicates better probability calibration (0.00 is perfect).

---

### B. Choice (Multi-Option Categorical Decision)
A **Choice** decision selects a single category from a mutually exclusive list of options and provides a full probability distribution.

- **Inference Output**:
  ```json
  "category": {
    "type": "choice",
    "choice": "billing",
    "confidence": 0.9699,
    "probabilities": {
      "billing": 0.9940,
      "technical": 0.0037,
      "sales": 0.0005,
      "other": 0.0016
    }
  }
  ```
- **Evaluation Metrics**:
  - **Categorical Accuracy**:
    $$\text{Accuracy} = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(\hat{c}_i = c_i)$$
  - **Confidence Calibration**: Correlation between the winning probability \(\max(P)\) and actual accuracy.

---

### C. Score (Ordered Rubric Rating)
A **Score** decision rates a situation against an ordered discrete scale (e.g. 0 to 3 severity level), returning both bucket probabilities and an expected continuous score.

- **Inference Output**:
  ```json
  "severity": {
    "type": "score",
    "score": 2.761,
    "probabilities": {
      "0": 0.012,
      "1": 0.045,
      "2": 0.182,
      "3": 0.761
    }
  }
  ```
- **Expected Score Formula**:
  $$\mathbb{E}[\text{Score}] = \sum_{k=0}^K k \cdot P(S = k)$$
- **Evaluation Metrics**:
  - **Mean Absolute Error (MAE)**:
    $$\text{MAE} = \frac{1}{N} \sum_{i=1}^N |s_i - \hat{s}_i|$$
  - **Exact Match Rate**: % of predictions where \(\text{round}(\hat{s}_i) = s_i\).

---

## 3. Benchmark Suites Overview

All benchmark fixtures are versioned JSONL files in the `benchmarks/` directory:

| Suite | File | Cases | Focus Area |
| :--- | :--- | :--- | :--- |
| **Smoke** | `benchmarks/smoke.jsonl` | 2 | Fast schema and API contract sanity check. |
| **Core** | `benchmarks/jev_core.jsonl` | 37 | Primary customer support triage and decision test set. |
| **Agentic** | `benchmarks/jev_agentic.jsonl` | 25 | Multi-step agent tool invocation and workflow routing decisions. |
| **Governance**| `benchmarks/jev_governance.jsonl`| 20 | Policy compliance, safety guardrails, and permission gating. |
| **Patterns** | `benchmarks/jev_patterns.jsonl` | 30 | Enterprise entity classification and categorization patterns. |
| **Complete** | `benchmarks/jev_complete.jsonl` | 114 | Full comprehensive benchmark across all categories. |

---

## 4. Built-in Testing & Explanation Tools

This repository provides built-in CLI tools to inspect, explain, and evaluate decisions:

### 1. Explain Any Test Case (`s1b explain-case`)
Inspect input context, question types, rubric legends, and ground-truth answers:
```powershell
uv run s1b explain-case support-001 --suite benchmarks/smoke.jsonl
```

Compare a specific test case against a candidate model's actual predictions and error loss:
```powershell
uv run s1b explain-case support-001 --suite benchmarks/smoke.jsonl --results results/hearim-qwen35-4b-smoke.jsonl
```

### 2. Explain Metrics & Methodology (`s1b explain-metrics`)
Print a terminal reference of mathematical formulas, calibration rules, and primitives:
```powershell
uv run s1b explain-metrics
```

### 3. Validate Suite Contracts (`s1b validate-suite`)
Ensure all test cases in a `.jsonl` file follow the strict schema:
```powershell
uv run s1b validate-suite benchmarks/jev_core.jsonl
```

### 4. Side-by-Side Model Comparison (`s1b compare-results`)
Compare two models with per-question win/loss delta:
```powershell
uv run s1b compare-results --baseline results/runs/jev-core-baseline.jsonl --candidate results/runs/hearim-qwen35-4b-core.jsonl --suite benchmarks/jev_core.jsonl
```

### 5. Interactive Visual Dashboard (`results/dashboard.html`)
Generate a self-contained, interactive HTML dashboard with interactive charts, confusion matrices, and testing guides:
```powershell
uv run s1b dashboard --output results/dashboard.html
```

---

## 5. Benchmarking a New Model

To evaluate a new model or local inference server:

1. **Add Provider in `config/providers.toml`**:
   ```toml
   [providers.my_model]
   kind = "systemone_http"
   enabled = true
   base_url = "http://127.0.0.1:8000"
   endpoint = "/v1/systemone"
   model = "my-custom-model"
   ```

2. **Run Benchmark**:
   ```powershell
   uv run s1b benchmark-provider --provider my_model --suite benchmarks/jev_core.jsonl --output results/my_model-core.jsonl
   ```

3. **Evaluate Results**:
   ```powershell
   uv run s1b evaluate --results results/my_model-core.jsonl --suite benchmarks/jev_core.jsonl
   ```
