import json
from pathlib import Path

from jev_local_experiments.baseline import build_systemone_request, load_api_key
from jev_local_experiments.schema import load_suite


ROOT = Path(__file__).parents[1]


def test_build_systemone_request_matches_jev_contract():
    case = load_suite(ROOT / "benchmarks" / "smoke.jsonl")[0]

    request = build_systemone_request(case, model="jev-latest")

    assert request["model"] == "jev-latest"
    assert request["state"] == case.state
    assert request["questions"]["team"]["type"] == "choice"
    assert request["questions"]["team"]["criteria"]["returns"]
    assert request["questions"]["urgent"]["type"] == "noul"
    assert "labels" not in request


def test_load_api_key_reads_a_file_without_transforming_it(tmp_path):
    key_file = tmp_path / "jev"
    key_file.write_text("  jv_test_key  \n", encoding="utf-8")

    assert load_api_key(key_file) == "jv_test_key"
