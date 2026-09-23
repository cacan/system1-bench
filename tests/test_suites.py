from pathlib import Path

from jev_local_experiments.schema import load_suite

ROOT = Path(__file__).parents[1]
BENCHMARKS_DIR = ROOT / "benchmarks"


def test_jev_complete_suite_loads_and_has_164_cases():
    cases = load_suite(BENCHMARKS_DIR / "jev_complete.jsonl")
    assert len(cases) == 164
    case_ids = [c.case_id for c in cases]
    assert len(set(case_ids)) == 164


def test_jev_domain_subsuites_load_and_match_expected_counts():
    suites = {
        "jev_core.jsonl": 36,
        "jev_agentic.jsonl": 36,
        "jev_governance.jsonl": 60,
        "jev_patterns.jsonl": 32,
    }

    total_subcases = 0
    for filename, expected_count in suites.items():
        cases = load_suite(BENCHMARKS_DIR / filename)
        assert len(cases) == expected_count
        total_subcases += len(cases)

    assert total_subcases == 164


def test_all_cases_contain_typed_questions_and_labels():
    cases = load_suite(BENCHMARKS_DIR / "jev_complete.jsonl")
    for case in cases:
        assert case.questions, f"Case {case.case_id} has no questions"
        for qid, q in case.questions.items():
            assert q.kind in {"noul", "choice", "score"}
            assert q.instructions is not None
        for qid, label in case.labels.items():
            assert qid in case.questions
