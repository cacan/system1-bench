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
