# Benchmark Evaluation Results

This directory contains published benchmark results, canonical model evaluation runs, and comparison dashboards for System 1 typed decisions.

---

## Directory Contents

- **`dashboard.html`**: A standalone, zero-dependency interactive HTML dashboard. Open in any browser to explore win/loss matrices, confidence distributions, and decision disagreements.
- **`leaderboard.md`**: Formatted leaderboard comparing all tested models on accuracy, MAE, and latency.
- **`leaderboard.json`**: Machine-readable JSON metrics for all benchmark runs.
- **`runs/`**: Curated, sanitized evaluation JSONL files containing case-by-case outputs for each model.

---

## How to View the Dashboard

Simply open `results/dashboard.html` in your web browser:

```powershell
# Windows
Start-Process results/dashboard.html

# macOS
open results/dashboard.html

# Linux
xdg-open results/dashboard.html
```

---

## Evaluation Runs & Reproducibility

Each `.jsonl` file in `results/runs/` corresponds to a recorded benchmark evaluation run:
- Contains line-by-line responses, evaluated probabilities, selected categorical labels, and rubric score predictions.
- Metrics reported on the leaderboard and dashboard are calculated directly from these canonical run files.
- Raw outputs are audited for zero secrets, private credentials, or personal filesystem paths.


## Microsoft-Decision-1 — Diverse 300

The [2026-10-11 raw run](runs/microsoft_decision1_diverse_300_20261011.jsonl) and [evidence bundle](runs/microsoft_decision1_diverse_300_20261011.evidence.json) record 300 cases, 900 decisions, and zero failures/refusals from snapshot `microsoft/microsoft-decision-1-20261009` via OpenRouter/Azure.

JEV-aligned Choice + Noul accuracy / Score MAE: **92.00% / 0.2946**. The same predictions scored against the [original labels](../benchmarks/diverse_300_original.jsonl): **86.33% / 0.5623**. Client p50/p95: **443.79 / 520.71 ms**; API-reported suite cost: **$0.002692788**. Server weights, runtime, precision, and VRAM are not exposed. Historical provider rows were not re-run as a matched comparison.

The standalone master dashboard and its Compare view contain both scoring bases. `leaderboard.md` and `leaderboard.json` describe the separate Core suite; Diverse 300 measurements are kept in their own dataset rather than mixed into those Core rankings.
