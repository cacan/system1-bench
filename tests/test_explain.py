from pathlib import Path

from jev_local_experiments.cli import build_parser, main
from jev_local_experiments.explain import (
    explain_case_details,
    find_case_in_suites,
    format_case_explanation_text,
    get_metrics_explanation_text,
)

ROOT = Path(__file__).parents[1]


def test_find_case_in_file():
    suite_file = ROOT / "benchmarks" / "smoke.jsonl"
    case, found_file = find_case_in_suites("support-001", suite_file)

    assert case is not None
    assert case.case_id == "support-001"
    assert found_file == suite_file


def test_find_case_in_directory():
    benchmarks_dir = ROOT / "benchmarks"
    case, found_file = find_case_in_suites("support-001", benchmarks_dir)

    assert case is not None
    assert case.case_id == "support-001"
    assert found_file is not None


def test_explain_case_details_without_results():
    suite_file = ROOT / "benchmarks" / "smoke.jsonl"
    case, _ = find_case_in_suites("support-001", suite_file)
    assert case is not None

    data = explain_case_details(case, suite_path=suite_file)

    assert data["case_id"] == "support-001"
    assert data["suite"] == "smoke.jsonl"
    assert "team" in data["questions"]
    assert data["questions"]["team"]["type"] == "choice"
    assert data["questions"]["urgent"]["type"] == "noul"
    assert data["questions"]["severity"]["type"] == "score"

    formatted = format_case_explanation_text(data)
    assert "BENCHMARK CASE: support-001" in formatted
    assert "Ground Truth Label: returns" in formatted


def test_explain_case_details_with_results():
    suite_file = ROOT / "benchmarks" / "smoke.jsonl"
    results_file = ROOT / "results" / "runs" / "hearim-qwen35-4b-core.jsonl"
    case, _ = find_case_in_suites("support-001", ROOT / "benchmarks" / "jev_core.jsonl")
    assert case is not None

    data = explain_case_details(case, suite_path=suite_file, results_path=results_file)

    assert "model_evaluation" in data
    assert data["model_evaluation"]["model"] == "qwen35-4b"
    assert "predictions" in data["model_evaluation"]

    formatted = format_case_explanation_text(data)
    assert "MODEL EVALUATION: qwen35-4b" in formatted


def test_get_metrics_explanation_text():
    text = get_metrics_explanation_text()
    assert "WHAT ARE TYPED DECISIONS?" in text
    assert "Brier Score" in text
    assert "Mean Absolute Error" in text


def test_cli_explain_case(capsys):
    ret = main(["explain-case", "support-001", "--suite", str(ROOT / "benchmarks" / "smoke.jsonl")])
    assert ret == 0
    captured = capsys.readouterr()
    assert "BENCHMARK CASE: support-001" in captured.out


def test_cli_explain_case_json(capsys):
    ret = main(["explain-case", "support-001", "--suite", str(ROOT / "benchmarks" / "smoke.jsonl"), "--json"])
    assert ret == 0
    captured = capsys.readouterr()
    assert '"case_id": "support-001"' in captured.out


def test_cli_explain_metrics(capsys):
    ret = main(["explain-metrics"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "HOW TESTING WORKS" in captured.out
