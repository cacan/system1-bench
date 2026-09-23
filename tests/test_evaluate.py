from pathlib import Path

from jev_local_experiments.evaluate import (
    compare_reports,
    compute_latency_stats,
    evaluate_results,
    extract_prediction,
    load_results_jsonl,
)
from jev_local_experiments.schema import load_suite

ROOT = Path(__file__).parents[1]


def test_extract_prediction_handles_various_shapes():
    # Choice
    assert extract_prediction({"choice": "billing"}, "choice") == "billing"
    assert extract_prediction({"selected": "returns"}, "choice") == "returns"
    assert extract_prediction({"probabilities": {"a": 0.2, "b": 0.8}}, "choice") == "b"
    assert extract_prediction("docs", "choice") == "docs"

    # Noul
    assert extract_prediction({"noul": 0.8}, "noul") is True
    assert extract_prediction({"noul": 0.2}, "noul") is False
    assert extract_prediction({"decision": True}, "noul") is True
    assert extract_prediction(True, "noul") is True
    assert extract_prediction(0.7, "noul") is True
    assert extract_prediction(0.3, "noul") is False

    # Score
    assert extract_prediction({"score": 1.76}, "score") == 1.76
    assert extract_prediction(2, "score") == 2.0
    assert extract_prediction("1.5", "score") == 1.5


def test_compute_latency_stats():
    lats = [100.0, 200.0, 300.0, 400.0, 500.0]
    stats = compute_latency_stats(lats)
    assert stats.count == 5
    assert stats.min_ms == 100.0
    assert stats.max_ms == 500.0
    assert stats.mean_ms == 300.0
    assert stats.p50_ms == 300.0


def test_evaluate_smoke_baseline_matches_expected_metrics():
    cases = load_suite(ROOT / "benchmarks" / "smoke.jsonl")
    results = load_results_jsonl(ROOT / "results" / "jev-baseline.jsonl")

    report = evaluate_results(cases, results)

    assert report.total_cases == 2
    assert report.successful_cases == 2
    assert report.failed_cases == 0
    assert report.categorical_accuracy == 1.0
    assert report.score_mae == 0.24
    assert len(report.questions) == 5

    assert report.questions["team"].accuracy == 1.0
    assert report.questions["urgent"].accuracy == 1.0
    assert report.questions["urgent"].f1 == 1.0
    assert report.questions["severity"].mae == 0.24


def test_compare_reports():
    cases = load_suite(ROOT / "benchmarks" / "smoke.jsonl")
    results = load_results_jsonl(ROOT / "results" / "jev-baseline.jsonl")

    report_a = evaluate_results(cases, results)

    # Mock candidate with slightly different results
    mutated_results = [
        dict(results[0], latency_ms=500.0),
        dict(results[1], latency_ms=400.0),
    ]
    report_b = evaluate_results(cases, mutated_results)

    comparison = compare_reports(report_a, report_b)
    assert comparison["categorical_accuracy"]["delta"] == 0.0
    assert comparison["latency_p50_ms"]["candidate"] == 450.0
    assert comparison["latency_p50_ms"]["speedup_ratio"] > 1.0
