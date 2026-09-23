# Benchmark Evaluation Results

This directory contains published benchmark results, canonical model evaluation runs, and comparison dashboards for JEV typed decisions.

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

## How to Rebuild the SQLite Database Locally

The SQLite database (`results/benchmark_lab.db`) is gitignored to avoid tracking large binary blobs. You can recreate it in seconds from the versioned benchmark fixtures and curated runs:

```powershell
# 1. Initialize DB schema
uv run jevx db-init

# 2. Sync benchmark suites into DB
uv run jevx db-sync

# 3. Import canonical runs
Get-ChildItem results/runs/*.jsonl | ForEach-Object {
    uv run jevx db-import-results --results $_.FullName --suite-id jev_core
}

# 4. View Leaderboard or regenerate dashboard
uv run jevx leaderboard
uv run jevx dashboard --output results/dashboard.html
```
