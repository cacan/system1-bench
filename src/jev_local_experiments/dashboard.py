"""Interactive HTML Comparison Dashboard Generator for System1-Bench."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .db import (
    compare_db_runs,
    get_all_benchmark_cases,
    get_all_suites,
    get_leaderboard,
    get_run,
)


def generate_dashboard_html(
    db_path: str | Path,
    output_html_path: str | Path,
    *,
    baseline_run_id: str | None = None,
    candidate_run_id: str | None = None,
    suite_id: str | None = None,
) -> Path:
    """Generate a self-contained, interactive HTML comparison dashboard."""
    leaderboard = get_leaderboard(db_path, suite_id=suite_id)
    suites = get_all_suites(db_path)
    all_benchmark_cases = get_all_benchmark_cases(db_path, suite_id=suite_id)

    comparison: dict[str, Any] | None = None
    b_id: str | None = None
    c_id: str | None = None

    if leaderboard:
        b_id = baseline_run_id or leaderboard[0]["run_id"]
        b_run = get_run(db_path, b_id)
        target_suite = suite_id or (b_run["suite_id"] if b_run else None)

        if candidate_run_id:
            c_id = candidate_run_id
        else:
            same_suite_candidates = [
                r["run_id"]
                for r in leaderboard
                if r["run_id"] != b_id and (not target_suite or r["suite_id"] == target_suite)
            ]
            c_id = same_suite_candidates[0] if same_suite_candidates else b_id

        try:
            comparison = compare_db_runs(db_path, b_id, c_id)
        except Exception:
            comparison = None

    comparisons: dict[str, Any] = {}
    if leaderboard:
        for r1 in leaderboard:
            for r2 in leaderboard:
                if r1["suite_id"] == r2["suite_id"] and r1["run_id"] != r2["run_id"]:
                    key = f"{r1['run_id']}__{r2['run_id']}"
                    try:
                        comparisons[key] = compare_db_runs(db_path, r1["run_id"], r2["run_id"])
                    except Exception:
                        pass

    out_file = Path(output_html_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    data_payload = {
        "leaderboard": leaderboard,
        "comparison": comparison,
        "comparisons": comparisons,
        "baseline_run_id": b_id,
        "candidate_run_id": c_id,
        "suites": suites,
        "benchmark_cases": all_benchmark_cases,
    }
    json_str = json.dumps(data_payload, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>System1-Bench · Comparison Suite</title>
<style>
:root {{
  --bg: #0d1117;
  --panel: #161b22;
  --panel-hover: #1c2128;
  --border: #30363d;
  --border-muted: #21262d;
  --text: #c9d1d9;
  --text-muted: #8b949e;
  --text-bright: #f0f6fc;
  --accent: #58a6ff;
  --accent-muted: #1f6feb33;
  --success: #3fb950;
  --success-bg: #23863626;
  --danger: #f85149;
  --danger-bg: #da363326;
  --warning: #d29922;
  --warning-bg: #9e6a0326;
  --purple: #bc8cff;
  --purple-bg: #8957e526;
  --code-bg: #090d13;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.5;
  padding: 24px;
}}
.container {{ max-width: 1440px; margin: 0 auto; }}

header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border);
  padding-bottom: 18px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}}
.brand {{ display: flex; align-items: center; gap: 12px; }}
.brand h1 {{ font-size: 1.5rem; font-weight: 700; color: var(--text-bright); }}
.brand span.tag {{
  background: var(--accent-muted);
  color: var(--accent);
  border: 1px solid #388bfd40;
  border-radius: 6px;
  padding: 3px 10px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}}

/* Top Navigation Tabs */
.tabs-nav {{
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 8px;
}}
.tab-btn {{
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-muted);
  padding: 8px 18px;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.15s ease;
}}
.tab-btn:hover {{
  color: var(--text-bright);
  background: #21262d;
}}
.tab-btn.active {{
  background: #1f6feb;
  color: #ffffff;
  border-color: #388bfd;
}}
.tab-badge {{
  background: rgba(255, 255, 255, 0.2);
  padding: 1px 6px;
  border-radius: 10px;
  font-size: 0.75rem;
}}

.tab-pane {{ display: none; }}
.tab-pane.active {{ display: block; }}

/* KPIs */
.grid-kpis {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}}
.kpi-card {{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
}}
.kpi-card .label {{ font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }}
.kpi-card .value {{ font-size: 1.8rem; font-weight: 700; color: var(--text-bright); margin: 6px 0; }}
.kpi-card .delta {{ font-size: 0.85rem; font-weight: 600; display: flex; align-items: center; gap: 4px; }}
.delta.pos {{ color: var(--success); }}
.delta.neg {{ color: var(--danger); }}
.delta.neutral {{ color: var(--text-muted); }}

/* Panels */
.section-panel {{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
}}
.section-panel h2 {{
  font-size: 1.15rem;
  color: var(--text-bright);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}}

table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; text-align: left; }}
th {{ background: #21262d; color: var(--text-bright); padding: 10px 14px; font-weight: 600; border-bottom: 1px solid var(--border); }}
td {{ padding: 10px 14px; border-bottom: 1px solid var(--border); vertical-align: middle; }}
tr:hover td {{ background: rgba(255, 255, 255, 0.02); }}

/* Badges & Pills */
.badge {{
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}}
.badge-blue {{ background: #1f6feb26; color: #58a6ff; border: 1px solid #388bfd40; }}
.badge-green {{ background: var(--success-bg); color: var(--success); border: 1px solid #2ea04340; }}
.badge-red {{ background: var(--danger-bg); color: var(--danger); border: 1px solid #f8514940; }}
.badge-purple {{ background: var(--purple-bg); color: var(--purple); border: 1px solid #8957e540; }}
.badge-yellow {{ background: var(--warning-bg); color: var(--warning); border: 1px solid #bb800940; }}
.badge-gray {{ background: #30363d; color: #8b949e; }}

.dec-pill {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.82rem;
  font-family: monospace;
}}
.dec-pill.match {{ background: var(--success-bg); color: var(--success); border: 1px solid #2ea04340; }}
.dec-pill.disagree {{ background: var(--danger-bg); color: var(--danger); border: 1px solid #f8514940; }}
.dec-pill.neutral {{ background: #21262d; color: #c9d1d9; border: 1px solid #30363d; }}

/* Confidence Mini-Bar */
.conf-cell {{
  display: flex;
  align-items: center;
  gap: 8px;
}}
.conf-pct {{
  font-family: monospace;
  font-weight: 600;
  font-size: 0.82rem;
  min-width: 42px;
}}
.conf-bar-track {{
  width: 54px;
  height: 6px;
  background: #21262d;
  border-radius: 3px;
  overflow: hidden;
  border: 1px solid #30363d;
}}
.conf-bar-fill {{
  height: 100%;
  border-radius: 3px;
}}
.conf-bar-fill.high {{ background: var(--success); }}
.conf-bar-fill.mid {{ background: var(--warning); }}
.conf-bar-fill.low {{ background: var(--danger); }}

/* Controls Bar */
.controls-bar {{
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
  align-items: center;
}}
.search-input {{
  background: var(--code-bg);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.85rem;
  min-width: 320px;
  flex: 1;
}}
.search-input:focus {{
  outline: none;
  border-color: var(--accent);
}}
.filter-btn {{
  background: #21262d;
  border: 1px solid var(--border);
  color: var(--text);
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}}
.filter-btn:hover {{
  background: #30363d;
  color: var(--text-bright);
}}
.filter-btn.active {{
  background: #1f6feb;
  color: #fff;
  border-color: #388bfd;
}}
.select-input {{
  background: #21262d;
  border: 1px solid var(--border);
  color: var(--text);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.85rem;
}}

/* Expandable Comparison Table */
.comp-table {{
  margin-top: 10px;
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
}}
.comp-row {{
  cursor: pointer;
  user-select: none;
}}
.comp-row:hover td {{
  background: var(--panel-hover) !important;
}}
.comp-row.expanded td {{
  background: #1f242c !important;
  border-bottom-color: transparent;
}}
.exp-caret {{
  display: inline-block;
  transition: transform 0.2s ease;
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-right: 6px;
}}
.comp-row.expanded .exp-caret {{
  transform: rotate(90deg);
  color: var(--accent);
}}

/* Expansion Drawer / Tray */
.exp-tray-row {{
  display: none;
}}
.exp-tray-row.open {{
  display: table-row;
}}
.exp-tray-cell {{
  background: #0f141c;
  padding: 16px 20px !important;
  border-bottom: 2px solid var(--border);
}}
.drawer-content {{
  display: grid;
  grid-template-columns: 1fr 1.3fr;
  gap: 20px;
}}
@media (max-width: 1024px) {{
  .drawer-content {{ grid-template-columns: 1fr; }}
}}
.drawer-box {{
  background: #161b22;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 14px;
}}
.drawer-box h4 {{
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}}
.prompt-text {{
  font-size: 0.88rem;
  color: #e6edf3;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}}
.dist-item {{
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-size: 0.82rem;
}}
.dist-label {{
  width: 110px;
  font-family: monospace;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}}
.dist-track {{
  flex: 1;
  height: 8px;
  background: #21262d;
  border-radius: 4px;
  overflow: hidden;
  margin: 0 10px;
}}
.dist-fill {{
  height: 100%;
  border-radius: 4px;
  background: var(--accent);
}}
.dist-val {{
  width: 50px;
  text-align: right;
  font-family: monospace;
  font-weight: 600;
}}
.meta-chips {{
  display: flex;
  gap: 12px;
  margin-top: 12px;
  font-size: 0.8rem;
  color: var(--text-muted);
  flex-wrap: wrap;
}}
.meta-chip {{
  background: #21262d;
  padding: 3px 8px;
  border-radius: 4px;
}}

/* Benchmark Explorer Question Cards */
.question-card {{
  background: #161b22;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 12px;
  margin-top: 8px;
}}
.question-card .instructions {{
  color: #e6edf3;
  margin: 6px 0;
  font-size: 0.88rem;
}}
.question-card .criteria-box {{
  background: #0d1117;
  padding: 8px 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-top: 6px;
}}
</style>
</head>
<body>

<div class="container">
  <header>
    <div class="brand">
      <h1>System1-Bench</h1>
      <span class="tag">Comparison Suite</span>
    </div>
    <div style="display: flex; align-items: center; gap: 12px;">
      <span style="color: var(--text-muted); font-size: 0.85rem;">Storage: <code style="color: var(--accent); background: #161b22; padding: 2px 6px; border-radius: 4px;">SQLite / Versioned Fixtures</code></span>
    </div>
  </header>

  <!-- NAVIGATION TABS -->
  <nav class="tabs-nav">
    <button class="tab-btn active" id="tab-btn-comparison" onclick="switchTab('comparison')">
      <span>📊 Run Comparison & Disagreements</span>
      <span class="tab-badge" id="tab-runs-count">0</span>
    </button>
    <button class="tab-btn" id="tab-btn-explorer" onclick="switchTab('explorer')">
      <span>🧪 Benchmark Suites & Test Cases</span>
      <span class="tab-badge" id="tab-cases-count">0</span>
    </button>
    <button class="tab-btn" id="tab-btn-guide" onclick="switchTab('guide')">
      <span>📖 Testing & Evaluation Guide</span>
    </button>
  </nav>

  <!-- TAB 1: RUN COMPARISON & DISAGREEMENTS -->
  <div id="pane-comparison" class="tab-pane active">
    <!-- KPI SUMMARY -->
    <section class="grid-kpis" id="kpis-container"></section>

    <!-- LEADERBOARD -->
    <section class="section-panel">
      <h2>Run Leaderboard</h2>
      <table>
        <thead>
          <tr>
            <th>Provider</th>
            <th>Model</th>
            <th>Suite</th>
            <th>Accuracy</th>
            <th>Score MAE</th>
            <th>p50 Latency</th>
            <th>p95 Latency</th>
            <th>Throughput</th>
            <th>Date</th>
            <th style="width: 110px;">Action</th>
          </tr>
        </thead>
        <tbody id="leaderboard-tbody"></tbody>
      </table>
    </section>

    <!-- DECISION DISAGREEMENT & COMPARISON TABLE -->
    <section class="section-panel">
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; flex-wrap: wrap; gap: 10px;">
        <h2>
          <span>Decision Comparison & Disagreements Table</span>
          <span id="case-counter" style="font-size: 0.85rem; color: var(--text-muted); font-weight: normal;"></span>
        </h2>
        <div style="display: flex; align-items: center; gap: 10px; background: var(--panel-hover); padding: 6px 12px; border-radius: 6px; border: 1px solid var(--border); flex-wrap: wrap;">
          <span style="font-size: 0.8rem; color: var(--text-muted); font-weight: 600;">Baseline:</span>
          <select id="select-baseline-run" class="select-input" onchange="onBaselineRunChange(this.value)" style="padding: 4px 8px; font-size: 0.8rem; min-width: 180px;"></select>
          <span style="font-size: 0.8rem; color: var(--text-muted); font-weight: 600;">Candidate:</span>
          <select id="select-candidate-run" class="select-input" onchange="onCandidateRunChange(this.value)" style="padding: 4px 8px; font-size: 0.8rem; min-width: 180px;"></select>
        </div>
      </div>

      <div class="controls-bar">
        <input type="text" id="filter-search-comp" class="search-input" placeholder="Search case ID, prompt, question, expected label, or prediction..."/>
        <button class="filter-btn active" id="btn-comp-disagreements" onclick="setCompFilter('disagreements')">Disagreements Only</button>
        <button class="filter-btn" id="btn-comp-errors" onclick="setCompFilter('errors')">Candidate Errors</button>
        <button class="filter-btn" id="btn-comp-matches" onclick="setCompFilter('matches')">Matches Only</button>
        <button class="filter-btn" id="btn-comp-all" onclick="setCompFilter('all')">All Questions</button>
      </div>

      <div class="comp-table">
        <table>
          <thead>
            <tr>
              <th style="width: 140px;">Case ID</th>
              <th>Input Prompt Preview</th>
              <th style="width: 130px;">Question</th>
              <th style="width: 120px;">Ground Truth</th>
              <th style="width: 180px;" id="th-baseline-name">Baseline (Jev)</th>
              <th style="width: 180px;" id="th-candidate-name">Candidate (Hearim)</th>
              <th style="width: 130px;">Status</th>
            </tr>
          </thead>
          <tbody id="comp-table-tbody"></tbody>
        </table>
      </div>
    </section>
  </div>

  <!-- TAB 2: BENCHMARK SUITES & TEST CASES EXPLORER -->
  <div id="pane-explorer" class="tab-pane">
    <section class="section-panel">
      <h2>
        <span>Benchmark Test Cases Explorer</span>
        <span id="explorer-counter" style="font-size: 0.85rem; color: var(--text-muted); font-weight: normal;"></span>
      </h2>

      <div class="controls-bar">
        <input type="text" id="filter-search-exp" class="search-input" placeholder="Search test cases by ID, experiment, state text, or question..."/>
        <select id="select-suite-filter" class="select-input" onchange="onSuiteFilterChange(this.value)">
          <option value="all">All Suites</option>
        </select>
      </div>

      <div id="benchmark-cases-list"></div>
    </section>
  </div>

  <!-- TAB 3: TESTING & EVALUATION GUIDE -->
  <div id="pane-guide" class="tab-pane">
    <section class="section-panel">
      <h2>How Testing Works: JEV Typed Decisions</h2>
      <p style="color: var(--text-muted); margin-bottom: 20px; font-size: 0.95rem;">
        Standard LLMs produce unstructured text requiring slow, non-deterministic decoding. 
        <strong>Typed Decisions</strong> replace text generation with constrained decision heads outputting exact continuous probabilities, categorical distributions, and ordered rubric ratings with sub-second latency.
      </p>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 16px; margin-bottom: 24px;">
        <!-- Card 1: Noul -->
        <div style="background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 18px;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
            <span class="badge badge-blue" style="font-size: 0.85rem; padding: 4px 10px;">NOUL (Binary Decision)</span>
            <span style="font-family: monospace; color: var(--accent); font-size: 0.8rem;">p ∈ [0.0, 1.0]</span>
          </div>
          <p style="font-size: 0.88rem; color: #e6edf3; margin-bottom: 12px;">
            Evaluates a boolean hypothesis, outputting a continuous probability. Thresholded at <strong>0.50</strong> for binary classification (True/False).
          </p>
          <div style="background: #161b22; border-radius: 6px; padding: 10px; font-size: 0.8rem; color: var(--text-muted);">
            <div><strong>Accuracy:</strong> Binary match at p ≥ 0.50</div>
            <div style="margin-top: 4px;"><strong>Brier Score:</strong> Calibration MSE = <code>(1/N) * Σ(p - y)²</code>. Lower is better (0.0 is perfect).</div>
          </div>
        </div>

        <!-- Card 2: Choice -->
        <div style="background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 18px;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
            <span class="badge badge-purple" style="font-size: 0.85rem; padding: 4px 10px;">CHOICE (Categorical Decision)</span>
            <span style="font-family: monospace; color: var(--purple); font-size: 0.8rem;">P(C = k) distribution</span>
          </div>
          <p style="font-size: 0.88rem; color: #e6edf3; margin-bottom: 12px;">
            Selects one label from mutually exclusive criteria options and returns full probability distributions over all candidates.
          </p>
          <div style="background: #161b22; border-radius: 6px; padding: 10px; font-size: 0.8rem; color: var(--text-muted);">
            <div><strong>Categorical Accuracy:</strong> <code>argmax(P) == Ground Truth</code></div>
            <div style="margin-top: 4px;"><strong>Confidence:</strong> Winning probability vs actual correctness correlation.</div>
          </div>
        </div>

        <!-- Card 3: Score -->
        <div style="background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 18px;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
            <span class="badge badge-yellow" style="font-size: 0.85rem; padding: 4px 10px;">SCORE (Ordered Rubric)</span>
            <span style="font-family: monospace; color: var(--warning); font-size: 0.8rem;">E[Score] = Σ i·P(S=i)</span>
          </div>
          <p style="font-size: 0.88rem; color: #e6edf3; margin-bottom: 12px;">
            Rates a scenario against an ordered rubric scale (e.g. 0 to 3 severity). Outputs class probabilities and continuous expected score.
          </p>
          <div style="background: #161b22; border-radius: 6px; padding: 10px; font-size: 0.8rem; color: var(--text-muted);">
            <div><strong>Mean Absolute Error (MAE):</strong> <code>(1/N) * Σ|Score - Expected|</code></div>
            <div style="margin-top: 4px;"><strong>Exact Match:</strong> <code>round(Score) == Expected</code></div>
          </div>
        </div>
      </div>

      <h3 style="margin-bottom: 10px; font-size: 1.1rem; color: var(--text-bright);">CLI Inspection & Explanation Commands</h3>
      <div style="background: var(--code-bg); border: 1px solid var(--border); border-radius: 6px; padding: 14px; font-family: monospace; font-size: 0.85rem; color: #e6edf3; line-height: 1.6;">
        <div><span style="color: var(--accent);"># Inspect a test case and error analysis:</span><br/>uv run s1b explain-case support-001 --suite benchmarks/smoke.jsonl</div>
        <div style="margin-top: 8px;"><span style="color: var(--accent);"># Print comprehensive testing guide & formulas:</span><br/>uv run s1b explain-metrics</div>
        <div style="margin-top: 8px;"><span style="color: var(--accent);"># Compare candidate vs baseline:</span><br/>uv run s1b compare-runs --baseline-run &lt;r1&gt; --candidate-run &lt;r2&gt;</div>
      </div>
    </section>
  </div>
</div>

<script>
const DATA = {json_str};

let activeTab = 'comparison';
let currentCompFilter = 'disagreements'; // Default to Disagreements so differences are immediate!
let searchCompQuery = '';
let currentSuiteFilter = 'all';
let searchExpQuery = '';
let expandedRows = new Set();

let currentBaselineId = DATA.baseline_run_id;
let currentCandidateId = DATA.candidate_run_id;

function populateRunSelectors() {{
  const bSelect = document.getElementById('select-baseline-run');
  const cSelect = document.getElementById('select-candidate-run');
  if (!bSelect || !cSelect || !DATA.leaderboard) return;

  bSelect.innerHTML = DATA.leaderboard.map(r => `
    <option value="${{r.run_id}}" ${{r.run_id === currentBaselineId ? 'selected' : ''}}>
      ${{r.provider}} (${{r.model}}) · ${{r.suite_id}}
    </option>
  `).join('');

  const currentB = DATA.leaderboard.find(r => r.run_id === currentBaselineId);
  const targetSuite = currentB ? currentB.suite_id : null;

  const candidateRuns = DATA.leaderboard.filter(r => r.run_id !== currentBaselineId && (!targetSuite || r.suite_id === targetSuite));
  cSelect.innerHTML = candidateRuns.map(r => `
    <option value="${{r.run_id}}" ${{r.run_id === currentCandidateId ? 'selected' : ''}}>
      ${{r.provider}} (${{r.model}}) · ${{r.suite_id}}
    </option>
  `).join('');
}}

function onBaselineRunChange(newBId) {{
  currentBaselineId = newBId;
  const currentB = DATA.leaderboard.find(r => r.run_id === newBId);
  const targetSuite = currentB ? currentB.suite_id : null;
  const candidates = DATA.leaderboard.filter(r => r.run_id !== newBId && (!targetSuite || r.suite_id === targetSuite));
  if (candidates.length > 0) {{
    if (!candidates.some(c => c.run_id === currentCandidateId)) {{
      currentCandidateId = candidates[0].run_id;
    }}
  }} else {{
    currentCandidateId = newBId;
  }}
  populateRunSelectors();
  updateActiveComparison();
}}

function onCandidateRunChange(newCId) {{
  currentCandidateId = newCId;
  updateActiveComparison();
}}

function setCandidateRun(cId) {{
  const cand = DATA.leaderboard.find(r => r.run_id === cId);
  if (!cand) return;
  const base = DATA.leaderboard.find(r => r.run_id === currentBaselineId);
  if (!base || base.suite_id !== cand.suite_id || currentBaselineId === cId) {{
    const defaultBase = DATA.leaderboard.find(r => r.suite_id === cand.suite_id && r.provider === 'jev_reference')
      || DATA.leaderboard.find(r => r.suite_id === cand.suite_id && r.run_id !== cId);
    if (defaultBase) {{
      currentBaselineId = defaultBase.run_id;
    }}
  }}
  currentCandidateId = cId;
  populateRunSelectors();
  updateActiveComparison();
}}

function updateActiveComparison() {{
  const key = `${{currentBaselineId}}__${{currentCandidateId}}`;
  if (DATA.comparisons && DATA.comparisons[key]) {{
    DATA.comparison = DATA.comparisons[key];
  }}
  renderComparisonView();
}}

function switchTab(tabName) {{
  activeTab = tabName;
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

  document.getElementById('tab-btn-' + tabName).classList.add('active');
  document.getElementById('pane-' + tabName).classList.add('active');

  if (tabName === 'explorer') {{
    renderBenchmarkExplorer();
  }}
}}

function initDashboard() {{
  const runCount = DATA.leaderboard ? DATA.leaderboard.length : 0;
  const casesCount = DATA.benchmark_cases ? DATA.benchmark_cases.length : 0;
  document.getElementById('tab-runs-count').innerText = runCount;
  document.getElementById('tab-cases-count').innerText = casesCount;

  // Populate Suite Filter in Explorer
  const suiteSelect = document.getElementById('select-suite-filter');
  if (DATA.suites && DATA.suites.length) {{
    DATA.suites.forEach(s => {{
      const opt = document.createElement('option');
      opt.value = s.suite_id;
      opt.innerText = `${{s.name}} (${{s.case_count}} cases)`;
      suiteSelect.appendChild(opt);
    }});
  }}

  populateRunSelectors();

  if (DATA.comparison) {{
    renderComparisonView();
  }} else {{
    switchTab('explorer');
  }}

  renderBenchmarkExplorer();
}}

function renderComparisonView() {{
  const comp = DATA.comparison;
  if (!comp) return;
  const b = comp.baseline;
  const c = comp.candidate;

  document.getElementById('th-baseline-name').innerText = `${{b.provider}} (${{b.model}})`;
  document.getElementById('th-candidate-name').innerText = `${{c.provider}} (${{c.model}})`;

  // KPIs
  const accDelta = comp.categorical_accuracy_delta;
  const maeDelta = comp.score_mae_delta;
  const speedup = comp.speedup_ratio;
  const total = comp.total_compared_cases;
  const matchesCount = (comp.cases || []).filter(item => !item.candidate_error && !item.disagreement).length;

  document.getElementById('kpis-container').innerHTML = `
    <div class="kpi-card">
      <div class="label">Candidate Accuracy</div>
      <div class="value">${{(c.categorical_accuracy * 100).toFixed(1)}}%</div>
      <div class="delta ${{accDelta >= 0 ? 'pos' : 'neg'}}">
        ${{accDelta >= 0 ? '+' : ''}}${{(accDelta * 100).toFixed(1)}}% vs ${{b.provider}}
      </div>
    </div>
    <div class="kpi-card">
      <div class="label">Score MAE</div>
      <div class="value">${{c.score_mae !== null ? c.score_mae.toFixed(3) : 'N/A'}}</div>
      <div class="delta ${{maeDelta !== null ? (maeDelta <= 0 ? 'pos' : 'neg') : 'neutral'}}">
        ${{maeDelta !== null ? (maeDelta > 0 ? '+' : '') + maeDelta.toFixed(3) + ' delta' : 'No score questions'}}
      </div>
    </div>
    <div class="kpi-card">
      <div class="label">Latency p50</div>
      <div class="value">${{c.latency_p50_ms ? c.latency_p50_ms.toFixed(0) + 'ms' : 'N/A'}}</div>
      <div class="delta ${{speedup && speedup >= 1.0 ? 'pos' : 'neg'}}">
        ${{speedup ? speedup.toFixed(2) + 'x speedup' : '—'}}
      </div>
    </div>
    <div class="kpi-card">
      <div class="label">Evaluated Cases</div>
      <div class="value">${{total}}</div>
      <div class="delta neutral">
        ${{comp.disagreement_count}} disagreements · ${{comp.candidate_error_count}} errors
      </div>
    </div>
  `;

  // Button counts
  document.getElementById('btn-comp-disagreements').innerText = `Disagreements Only (${{comp.disagreement_count}})`;
  document.getElementById('btn-comp-errors').innerText = `Candidate Errors (${{comp.candidate_error_count}})`;
  document.getElementById('btn-comp-matches').innerText = `Matches Only (${{matchesCount}})`;
  document.getElementById('btn-comp-all').innerText = `All Cases (${{total}})`;

  // Leaderboard
  const lbBody = document.getElementById('leaderboard-tbody');
  lbBody.innerHTML = (DATA.leaderboard || []).map(r => `
    <tr>
      <td><strong>${{r.provider}}</strong></td>
      <td><code>${{r.model}}</code></td>
      <td><span class="badge badge-gray">${{r.suite_id}}</span></td>
      <td><strong style="color: var(--success);">${{r.categorical_accuracy !== null ? (r.categorical_accuracy * 100).toFixed(1) + '%' : '—'}}</strong></td>
      <td>${{r.score_mae !== null ? r.score_mae.toFixed(3) : '—'}}</td>
      <td>${{r.latency_p50_ms ? r.latency_p50_ms.toFixed(1) + 'ms' : '—'}}</td>
      <td>${{r.latency_p95_ms ? r.latency_p95_ms.toFixed(1) + 'ms' : '—'}}</td>
      <td>${{r.throughput_rps ? r.throughput_rps.toFixed(1) + ' rps' : '—'}}</td>
      <td style="color: var(--text-muted); font-size: 0.8rem;">${{r.finished_at ? r.finished_at.split('T')[0] : '—'}}</td>
      <td>
        ${{r.run_id === currentBaselineId ? '<span class="badge badge-purple">Baseline</span>' :
          r.run_id === currentCandidateId ? '<span class="badge badge-accent">Candidate</span>' :
          `<button class="filter-btn" style="padding: 2px 8px; font-size: 0.75rem;" onclick="setCandidateRun('${{r.run_id}}')">Compare</button>`}}
      </td>
    </tr>
  `).join('');

  renderCompTable();
}}

// Helper: unroll cases into individual question items
function getQuestionRows() {{
  const comp = DATA.comparison;
  if (!comp || !comp.cases) return [];

  const items = [];
  comp.cases.forEach(c => {{
    const qKeys = Object.keys(c.labels || {{}});
    // If no labels, check baseline answers
    const allQids = qKeys.length ? qKeys : Object.keys(c.baseline_predictions || {{}});

    allQids.forEach(qid => {{
      const expected = c.labels ? c.labels[qid] : null;
      const bp = c.baseline_predictions ? c.baseline_predictions[qid] : null;
      const cp = c.candidate_predictions ? c.candidate_predictions[qid] : null;
      const bAns = c.baseline_answers ? c.baseline_answers[qid] : {{}};
      const cAns = c.candidate_answers ? c.candidate_answers[qid] : {{}};
      const qMeta = (c.questions && c.questions[qid]) ? c.questions[qid] : {{ type: 'unknown' }};

      const isDisagreement = bp !== cp;
      let isError = false;
      if (expected !== null && expected !== undefined) {{
        isError = (cp !== expected);
      }}

      // Format prompt text
      let promptText = '';
      if (typeof c.state === 'string') {{
        promptText = c.state;
      }} else if (c.state && c.state.text) {{
        promptText = c.state.text;
      }} else if (c.state && (c.state.source || c.state.claim)) {{
        promptText = `Source: ${{c.state.source || ''}}\nClaim: ${{c.state.claim || ''}}`;
      }} else {{
        promptText = JSON.stringify(c.state);
      }}

      // Extract confidence
      let bConf = bAns.confidence;
      if (bConf === undefined && typeof bAns.noul === 'number') {{
        bConf = Math.abs(bAns.noul - 0.5) * 2;
      }}
      let cConf = cAns.confidence;
      if (cConf === undefined && typeof cAns.noul === 'number') {{
        cConf = Math.abs(cAns.noul - 0.5) * 2;
      }}

      items.push({{
        uid: `${{c.case_id}}_${{qid}}`,
        case_id: c.case_id,
        experiment_id: c.experiment_id,
        state: c.state,
        prompt_text: promptText,
        question_id: qid,
        question_meta: qMeta,
        expected: expected,
        baseline_pred: bp,
        candidate_pred: cp,
        baseline_ans: bAns,
        candidate_ans: cAns,
        baseline_conf: bConf,
        candidate_conf: cConf,
        baseline_latency: c.baseline_latency_ms,
        candidate_latency: c.candidate_latency_ms,
        is_disagreement: isDisagreement,
        is_error: isError,
      }});
    }});
  }});

  return items;
}}

function renderCompTable() {{
  const allItems = getQuestionRows();
  let filtered = allItems;

  if (currentCompFilter === 'disagreements') {{
    filtered = allItems.filter(item => item.is_disagreement);
  }} else if (currentCompFilter === 'errors') {{
    filtered = allItems.filter(item => item.is_error);
  }} else if (currentCompFilter === 'matches') {{
    filtered = allItems.filter(item => !item.is_disagreement && !item.is_error);
  }}

  if (searchCompQuery.trim()) {{
    const q = searchCompQuery.toLowerCase();
    filtered = filtered.filter(item =>
      item.case_id.toLowerCase().includes(q) ||
      item.experiment_id.toLowerCase().includes(q) ||
      item.question_id.toLowerCase().includes(q) ||
      item.prompt_text.toLowerCase().includes(q) ||
      String(item.expected).toLowerCase().includes(q) ||
      String(item.baseline_pred).toLowerCase().includes(q) ||
      String(item.candidate_pred).toLowerCase().includes(q)
    );
  }}

  document.getElementById('case-counter').innerText = `Showing ${{filtered.length}} of ${{allItems.length}} decisions`;

  const tbody = document.getElementById('comp-table-tbody');
  if (!filtered.length) {{
    tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 36px;">No decision rows match the filter.</td></tr>`;
    return;
  }}

  tbody.innerHTML = filtered.map(item => {{
    const isExpanded = expandedRows.has(item.uid);

    // Format value and confidence for baseline
    const bValStr = item.baseline_pred !== null ? String(item.baseline_pred) : '—';
    const bConfPct = item.baseline_conf !== undefined ? Math.round(item.baseline_conf * 100) : null;
    const bBarClass = bConfPct !== null ? (bConfPct >= 80 ? 'high' : bConfPct >= 50 ? 'mid' : 'low') : '';

    // Format value and confidence for candidate
    const cValStr = item.candidate_pred !== null ? String(item.candidate_pred) : '—';
    const cConfPct = item.candidate_conf !== undefined ? Math.round(item.candidate_conf * 100) : null;
    const cBarClass = cConfPct !== null ? (cConfPct >= 80 ? 'high' : cConfPct >= 50 ? 'mid' : 'low') : '';

    const isMatch = !item.is_disagreement;
    const statusBadge = item.is_disagreement
      ? `<span class="badge badge-red">Disagreement</span>`
      : `<span class="badge badge-green">Match</span>`;

    // Prompt preview (truncated to 70 chars)
    const promptSnippet = item.prompt_text.length > 70
      ? item.prompt_text.substring(0, 70) + '...'
      : item.prompt_text;

    // Build expandable drawer content
    let probabilitiesHtml = '';
    const cProbs = item.candidate_ans.probabilities || {{}};
    const bProbs = item.baseline_ans.probabilities || {{}};
    const probKeys = Object.keys(cProbs).length ? Object.keys(cProbs) : Object.keys(bProbs);

    if (probKeys.length) {{
      probabilitiesHtml = probKeys.map(opt => {{
        const cP = cProbs[opt] !== undefined ? (cProbs[opt] * 100).toFixed(1) : '—';
        const bP = bProbs[opt] !== undefined ? (bProbs[opt] * 100).toFixed(1) : '—';
        const cWidth = cProbs[opt] !== undefined ? Math.min(100, Math.max(0, cProbs[opt] * 100)) : 0;
        const isOptWinner = (String(item.candidate_pred) === opt);

        return `
          <div class="dist-item">
            <span class="dist-label" style="${{isOptWinner ? 'color: var(--accent); font-weight: 700;' : ''}}">${{opt}}</span>
            <div class="dist-track">
              <div class="dist-fill" style="width: ${{cWidth}}%; background: ${{isOptWinner ? 'var(--accent)' : '#30363d'}};"></div>
            </div>
            <span class="dist-val" style="${{isOptWinner ? 'color: var(--accent); font-weight: 700;' : ''}}">${{cP}}%</span>
          </div>
        `;
      }}).join('');
    }} else if (item.question_meta.type === 'noul') {{
      const cN = typeof item.candidate_ans.noul === 'number' ? (item.candidate_ans.noul * 100).toFixed(1) : '—';
      const bN = typeof item.baseline_ans.noul === 'number' ? (item.baseline_ans.noul * 100).toFixed(1) : '—';
      probabilitiesHtml = `
        <div class="dist-item">
          <span class="dist-label">True Prob</span>
          <div class="dist-track"><div class="dist-fill" style="width: ${{cN !== '—' ? cN : 0}}%;"></div></div>
          <span class="dist-val">${{cN}}%</span>
        </div>
        <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">Baseline: ${{bN}}% · Candidate: ${{cN}}%</div>
      `;
    }} else if (item.question_meta.type === 'score') {{
      probabilitiesHtml = `
        <div style="font-size: 0.85rem; color: #e6edf3;">
          <div>Continuous Score: <strong style="color: var(--accent);">${{typeof item.candidate_ans.score === 'number' ? item.candidate_ans.score.toFixed(3) : item.candidate_pred}}</strong></div>
          <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">Baseline Score: ${{item.baseline_pred}} · Expected: ${{item.expected}}</div>
        </div>
      `;
    }}

    return `
      <tr class="comp-row ${{isExpanded ? 'expanded' : ''}}" onclick="toggleRow('${{item.uid}}')">
        <td>
          <span class="exp-caret">▶</span>
          <strong style="color: var(--accent); font-family: monospace;">${{item.case_id}}</strong>
          <span class="badge badge-gray" style="margin-left: 4px;">${{item.experiment_id}}</span>
        </td>
        <td><span style="color: #c9d1d9; font-size: 0.84rem;">${{escapeHtml(promptSnippet)}}</span></td>
        <td>
          <code>${{item.question_id}}</code>
          <span class="badge ${{item.question_meta.type === 'noul' ? 'badge-blue' : item.question_meta.type === 'choice' ? 'badge-purple' : 'badge-yellow'}}" style="margin-left: 4px;">${{item.question_meta.type}}</span>
        </td>
        <td>
          <span class="dec-pill neutral">${{item.expected !== null ? escapeHtml(String(item.expected)) : '<span style=\"color: var(--text-muted);\">none</span>'}}</span>
        </td>
        <td>
          <div class="conf-cell">
            <span class="dec-pill neutral">${{escapeHtml(bValStr)}}</span>
            ${{bConfPct !== null ? `
              <div class="conf-bar-track" title="Confidence: ${{bConfPct}}%">
                <div class="conf-bar-fill ${{bBarClass}}" style="width: ${{bConfPct}}%;"></div>
              </div>
              <span class="conf-pct">${{bConfPct}}%</span>
            ` : ''}}
          </div>
        </td>
        <td>
          <div class="conf-cell">
            <span class="dec-pill ${{isMatch ? 'match' : 'disagree'}}">${{escapeHtml(cValStr)}}</span>
            ${{cConfPct !== null ? `
              <div class="conf-bar-track" title="Confidence: ${{cConfPct}}%">
                <div class="conf-bar-fill ${{cBarClass}}" style="width: ${{cConfPct}}%;"></div>
              </div>
              <span class="conf-pct">${{cConfPct}}%</span>
            ` : ''}}
          </div>
        </td>
        <td>${{statusBadge}}</td>
      </tr>

      <tr class="exp-tray-row ${{isExpanded ? 'open' : ''}}" id="tray-${{item.uid}}">
        <td colspan="7" class="exp-tray-cell">
          <div class="drawer-content">
            <!-- Left: Full Context -->
            <div class="drawer-box">
              <h4>Full Input Context Prompt</h4>
              <div class="prompt-text">${{escapeHtml(item.prompt_text)}}</div>
              <div class="meta-chips">
                <span class="meta-chip">Question: <code>${{item.question_id}}</code></span>
                <span class="meta-chip">Type: <strong>${{item.question_meta.type}}</strong></span>
                <span class="meta-chip">Expected: <strong>${{item.expected !== null ? item.expected : 'None'}}</strong></span>
              </div>
            </div>

            <!-- Right: Probabilities & Decision Breakdown -->
            <div class="drawer-box">
              <h4>Candidate Probability Distribution & Execution</h4>
              <div style="margin-bottom: 12px;">${{probabilitiesHtml}}</div>
              <div class="meta-chips" style="border-top: 1px solid var(--border); padding-top: 10px;">
                <span class="meta-chip">Baseline Conf: <strong>${{bConfPct !== null ? bConfPct + '%' : 'N/A'}}</strong></span>
                <span class="meta-chip">Candidate Conf: <strong>${{cConfPct !== null ? cConfPct + '%' : 'N/A'}}</strong></span>
                <span class="meta-chip">Candidate Latency: <strong>${{item.candidate_latency ? item.candidate_latency.toFixed(0) + 'ms' : 'N/A'}}</strong></span>
              </div>
            </div>
          </div>
        </td>
      </tr>
    `;
  }}).join('');
}}

function toggleRow(uid) {{
  if (expandedRows.has(uid)) {{
    expandedRows.delete(uid);
  }} else {{
    expandedRows.add(uid);
  }}
  renderCompTable();
}}

function setCompFilter(filter) {{
  currentCompFilter = filter;
  document.querySelectorAll('#pane-comparison .filter-btn').forEach(btn => btn.classList.remove('active'));
  document.getElementById('btn-comp-' + filter).classList.add('active');
  renderCompTable();
}}

document.getElementById('filter-search-comp').addEventListener('input', (e) => {{
  searchCompQuery = e.target.value;
  renderCompTable();
}});

function escapeHtml(str) {{
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}}

// Benchmark Test Cases Explorer
function onSuiteFilterChange(suiteId) {{
  currentSuiteFilter = suiteId;
  renderBenchmarkExplorer();
}}

document.getElementById('filter-search-exp').addEventListener('input', (e) => {{
  searchExpQuery = e.target.value;
  renderBenchmarkExplorer();
}});

function renderBenchmarkExplorer() {{
  const allCases = DATA.benchmark_cases || [];
  let filtered = allCases;

  if (currentSuiteFilter !== 'all') {{
    filtered = filtered.filter(c => c.suite_id === currentSuiteFilter);
  }}

  if (searchExpQuery.trim()) {{
    const q = searchExpQuery.toLowerCase();
    filtered = filtered.filter(c =>
      c.case_id.toLowerCase().includes(q) ||
      c.experiment_id.toLowerCase().includes(q) ||
      c.suite_id.toLowerCase().includes(q) ||
      JSON.stringify(c.state).toLowerCase().includes(q) ||
      JSON.stringify(c.questions).toLowerCase().includes(q) ||
      JSON.stringify(c.labels).toLowerCase().includes(q)
    );
  }}

  document.getElementById('explorer-counter').innerText = `Showing ${{filtered.length}} of ${{allCases.length}} test cases`;

  const listEl = document.getElementById('benchmark-cases-list');
  if (!filtered.length) {{
    listEl.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 36px;">No benchmark test cases match the filter.</div>`;
    return;
  }}

  listEl.innerHTML = filtered.map(c => {{
    const qKeys = Object.keys(c.questions || {{}});
    const questionsHtml = qKeys.map(qid => {{
      const q = c.questions[qid];
      const expectedLabel = c.labels[qid];
      let criteriaHtml = '';
      if (q.criteria) {{
        if (Array.isArray(q.criteria)) {{
          criteriaHtml = `<div class="criteria-box"><strong>Levels:</strong> ${{q.criteria.join(' → ')}}</div>`;
        }} else if (typeof q.criteria === 'object') {{
          const items = Object.entries(q.criteria).map(([k, v]) => `<code>${{k}}</code>: ${{v}}`).join('<br/>');
          criteriaHtml = `<div class="criteria-box"><strong>Rubric:</strong><br/>${{items}}</div>`;
        }}
      }}

      return `
        <div class="question-card">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
              <strong><code>${{qid}}</code></strong>
              <span class="badge ${{q.type === 'noul' ? 'badge-blue' : q.type === 'choice' ? 'badge-purple' : 'badge-yellow'}}" style="margin-left: 6px;">${{q.type}}</span>
            </div>
            <div>
              <span class="badge badge-green">Label: ${{JSON.stringify(expectedLabel)}}</span>
            </div>
          </div>
          <div class="instructions">${{escapeHtml(q.instructions)}}</div>
          ${{criteriaHtml}}
        </div>
      `;
    }}).join('');

    return `
      <div class="case-card">
        <div class="case-header">
          <div>
            <span class="case-id">${{c.case_id}}</span>
            <span class="badge badge-purple" style="margin-left: 8px;">${{c.experiment_id}}</span>
            <span class="badge badge-gray" style="margin-left: 6px;">Suite: ${{c.suite_id}}</span>
          </div>
          <div>
            <span class="badge badge-blue">${{qKeys.length}} Question(s)</span>
          </div>
        </div>
        <div class="case-state">
          <strong>State / Input Context:</strong>
          ${{typeof c.state === 'string' ? escapeHtml(c.state) : `<pre style="white-space: pre-wrap; font-size: 0.82rem;">${{escapeHtml(JSON.stringify(c.state, null, 2))}}</pre>`}}
        </div>
        <div>
          <strong style="color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase;">Typed Questions & Criteria:</strong>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 10px; margin-top: 6px;">
            ${{questionsHtml}}
          </div>
        </div>
      </div>
    `;
  }}).join('');
}}

initDashboard();
</script>

</body>
</html>
"""
    out_file.write_text(html_content, encoding="utf-8")
    return out_file
