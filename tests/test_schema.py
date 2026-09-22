import json
from pathlib import Path

import pytest

from jev_local_experiments.schema import ValidationError, load_suite, validate_case


ROOT = Path(__file__).parents[1]


def test_validate_case_accepts_binary_choice_and_score_questions():
    case = json.loads((ROOT / "benchmarks" / "smoke.jsonl").read_text(encoding="utf-8").splitlines()[0])

    validated = validate_case(case)

    assert validated.case_id == "support-001"
    assert validated.questions["urgent"].kind == "noul"
    assert validated.questions["team"].criteria["returns"]
    assert validated.questions["severity"].criteria == ("low", "medium", "high")
    assert validated.labels["severity"] == 2


def test_validate_case_rejects_score_label_outside_levels():
    case = {
        "id": "bad-score",
        "state": "example",
        "questions": {
            "severity": {
                "type": "score",
                "instructions": "How severe?",
                "criteria": ["low", "high"],
            }
        },
        "labels": {"severity": 2},
    }

    with pytest.raises(ValidationError, match="label"):
        validate_case(case)


def test_load_suite_reads_all_jsonl_cases():
    cases = load_suite(ROOT / "benchmarks" / "smoke.jsonl")

    assert [case.case_id for case in cases] == ["support-001", "docs-001"]
