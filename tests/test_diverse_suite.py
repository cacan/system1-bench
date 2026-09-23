import json
from pathlib import Path
from jev_local_experiments.schema import load_suite

def test_diverse_300_suite_integrity():
    suite_path = Path("benchmarks/diverse_300.jsonl")
    assert suite_path.exists(), "benchmarks/diverse_300.jsonl must exist"

    cases = load_suite(suite_path)
    assert len(cases) == 300, f"Expected 300 cases, found {len(cases)}"

    # Also read raw json to verify domain distribution
    domains = {}
    with open(suite_path, "r", encoding="utf-8") as f:
        for line in f:
            raw = json.loads(line)
            dom = raw.get("domain")
            domains[dom] = domains.get(dom, 0) + 1

    assert len(domains) == 5, f"Expected 5 domains, got {list(domains.keys())}"
    for dom, count in domains.items():
        assert count == 60, f"Domain '{dom}' should have 60 cases, got {count}"

    for case in cases:
        # Check required fields
        assert case.case_id
        assert case.state
        assert len(case.questions) >= 2
        assert len(case.labels) >= 2

        # Check each question has a matching label
        for q_name, q in case.questions.items():
            assert q_name in case.labels, f"Missing label for question {q_name} in {case.case_id}"
            label = case.labels[q_name]
            if q.kind == "choice":
                assert label in q.criteria, f"Label '{label}' not in criteria for {case.case_id}:{q_name}"
            elif q.kind == "noul":
                assert isinstance(label, bool), f"Noul label must be bool for {case.case_id}:{q_name}"
            elif q.kind == "score":
                assert isinstance(label, (int, float)), f"Score label must be numeric for {case.case_id}:{q_name}"
