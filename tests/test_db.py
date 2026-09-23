import json
from pathlib import Path

from jev_local_experiments.dashboard import generate_dashboard_html
from jev_local_experiments.db import (
    compare_db_runs,
    get_leaderboard,
    import_results_jsonl_to_db,
    import_suite_to_db,
    init_db,
    load_cases_from_db,
    sync_all_suites,
)

ROOT = Path(__file__).parents[1]
SMOKE_SUITE = ROOT / "benchmarks" / "smoke.jsonl"
SMOKE_RESULTS = ROOT / "results" / "jev-baseline.jsonl"


def test_init_db_and_import_suite(tmp_path):
    db_file = tmp_path / "test.db"
    init_db(db_file)

    count = import_suite_to_db(db_file, SMOKE_SUITE, suite_id="smoke")
    assert count == 2

    cases = load_cases_from_db(db_file, "smoke")
    assert len(cases) == 2
    assert cases[0].case_id == "support-001"
    assert "team" in cases[0].questions
    assert cases[0].labels["team"] == "returns"


def test_sync_all_suites(tmp_path):
    db_file = tmp_path / "sync.db"
    suites_summary = sync_all_suites(db_file, ROOT / "benchmarks")

    assert "jev_complete" in suites_summary
    assert suites_summary["jev_complete"] == 164
    assert suites_summary["jev_core"] == 36
    assert suites_summary["jev_agentic"] == 36
    assert suites_summary["jev_governance"] == 60
    assert suites_summary["jev_patterns"] == 32
    assert suites_summary["smoke"] == 2


def test_import_results_and_leaderboard(tmp_path):
    db_file = tmp_path / "results.db"
    import_suite_to_db(db_file, SMOKE_SUITE, suite_id="smoke")

    run_id = import_results_jsonl_to_db(
        db_file,
        SMOKE_RESULTS,
        suite_id="smoke",
        run_id="run_baseline_1",
        provider="jev_reference",
        model="jev-1.13.0",
    )
    assert run_id == "run_baseline_1"

    lb = get_leaderboard(db_file, suite_id="smoke")
    assert len(lb) == 1
    assert lb[0]["run_id"] == "run_baseline_1"
    assert lb[0]["categorical_accuracy"] == 1.0
    assert lb[0]["score_mae"] == 0.24


def test_compare_db_runs_and_dashboard_generation(tmp_path):
    db_file = tmp_path / "dash.db"
    import_suite_to_db(db_file, SMOKE_SUITE, suite_id="smoke")

    # Ingest baseline
    import_results_jsonl_to_db(
        db_file,
        SMOKE_RESULTS,
        suite_id="smoke",
        run_id="b_run",
        provider="jev_reference",
        model="jev-1.13.0",
    )

    # Ingest mock candidate with mutated results
    cand_results_file = tmp_path / "candidate.jsonl"
    orig_rows = [json.loads(line) for line in SMOKE_RESULTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    # Mutate candidate to disagree on team
    orig_rows[0]["response"]["answers"]["team"]["choice"] = "shipping"
    orig_rows[0]["latency_ms"] = 120.0
    cand_results_file.write_text("\n".join(json.dumps(r) for r in orig_rows) + "\n", encoding="utf-8")

    import_results_jsonl_to_db(
        db_file,
        cand_results_file,
        suite_id="smoke",
        run_id="c_run",
        provider="kev_local",
        model="kev-0.8b",
    )

    # Comparison
    diff = compare_db_runs(db_file, "b_run", "c_run")
    assert diff["total_compared_cases"] == 2
    assert len(diff["cases"]) == 2
    assert diff["disagreement_count"] == 1
    assert diff["candidate_error_count"] == 1
    assert diff["categorical_accuracy_delta"] < 0.0

    # Dashboard HTML generation
    html_out = tmp_path / "dashboard.html"
    generated_file = generate_dashboard_html(db_file, html_out, baseline_run_id="b_run", candidate_run_id="c_run")
    assert generated_file.is_file()
    content = generated_file.read_text(encoding="utf-8")
    assert "System1-Bench" in content
    assert "kev_local" in content
    assert "jev_reference" in content
    assert "support-001" in content
    assert "docs-001" in content
