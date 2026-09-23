"""Testing and metric explanation tools for Jev-style typed decisions."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .evaluate import load_results_jsonl
from .schema import BenchmarkCase, Question, load_suite


def find_case_in_suites(case_id: str, suites_dir_or_file: Path) -> tuple[BenchmarkCase | None, Path | None]:
    """Find a benchmark case by ID across files in a directory or in a specific file."""
    if suites_dir_or_file.is_file():
        for case in load_suite(suites_dir_or_file):
            if case.case_id == case_id:
                return case, suites_dir_or_file
        return None, None

    # Search directory for .jsonl suites
    for jsonl_file in sorted(suites_dir_or_file.glob("*.jsonl")):
        try:
            for case in load_suite(jsonl_file):
                if case.case_id == case_id:
                    return case, jsonl_file
        except Exception:
            continue
    return None, None


def explain_case_details(
    case: BenchmarkCase,
    suite_path: Path | None = None,
    results_path: Path | None = None,
) -> dict[str, Any]:
    """Extract structured explanation data for a benchmark case."""
    questions_info: dict[str, Any] = {}
    for qid, q in case.questions.items():
        q_dict: dict[str, Any] = {
            "type": q.kind,
            "instructions": q.instructions,
            "ground_truth": case.labels.get(qid) if case.labels else None,
        }
        if q.kind == "choice":
            if isinstance(q.criteria, (dict, Mapping)):
                q_dict["options"] = list(q.criteria.keys())
                q_dict["options_descriptions"] = dict(q.criteria)
            elif isinstance(q.criteria, (list, tuple)):
                q_dict["options"] = list(q.criteria)
            else:
                q_dict["options"] = []
        elif q.kind == "score":
            if isinstance(q.criteria, dict):
                q_dict["rubric_legend"] = q.criteria.get("legend", [])
                q_dict["range"] = [q.criteria.get("min", 0), q.criteria.get("max", len(q_dict["rubric_legend"]) - 1)]
            else:
                q_dict["rubric_legend"] = list(q.criteria) if q.criteria else []
                q_dict["range"] = [0, max(0, len(q_dict["rubric_legend"]) - 1)]
        elif q.kind == "noul":
            q_dict["decision_threshold"] = 0.50

        questions_info[qid] = q_dict

    explanation: dict[str, Any] = {
        "case_id": case.case_id,
        "suite": suite_path.name if suite_path else "unknown",
        "state": case.state,
        "questions": questions_info,
    }

    # If results are provided, attach model prediction and error analysis
    if results_path and results_path.is_file():
        results = load_results_jsonl(results_path)
        matching_results = [r for r in results if r.get("case_id") == case.case_id]
        if matching_results:
            r = matching_results[0]
            resp = r.get("response") or {}
            answers = resp.get("answers") if isinstance(resp, dict) else r.get("answers", {})
            explanation["model_evaluation"] = {
                "provider": r.get("provider", "unknown"),
                "model": r.get("model", "unknown"),
                "latency_ms": r.get("latency_ms", 0.0),
                "status_code": r.get("status_code", 200),
                "predictions": {},
            }
            if answers:
                for qid, q_info in questions_info.items():
                    ans = answers.get(qid)
                    if not ans:
                        explanation["model_evaluation"]["predictions"][qid] = {"status": "MISSING"}
                        continue

                    pred_info: dict[str, Any] = {"raw_answer": ans}
                    expected = q_info["ground_truth"]

                    if q_info["type"] == "choice":
                        pred_choice = ans.get("choice")
                        pred_info["predicted_choice"] = pred_choice
                        pred_info["confidence"] = ans.get("confidence")
                        pred_info["probabilities"] = ans.get("probabilities")
                        pred_info["is_correct"] = bool(pred_choice == expected)

                    elif q_info["type"] == "noul":
                        pred_prob = ans.get("noul", 0.0)
                        pred_binary = bool(pred_prob >= 0.50)
                        pred_info["predicted_probability"] = pred_prob
                        pred_info["predicted_binary"] = pred_binary
                        expected_binary = bool(expected >= 0.50) if isinstance(expected, (int, float)) else bool(expected)
                        pred_info["is_correct"] = bool(pred_binary == expected_binary)
                        if isinstance(expected, (int, float)):
                            pred_info["brier_loss"] = round((pred_prob - float(expected)) ** 2, 4)

                    elif q_info["type"] == "score":
                        pred_score = float(ans.get("score", 0.0))
                        pred_info["predicted_score"] = pred_score
                        pred_info["probabilities"] = ans.get("probabilities")
                        if expected is not None:
                            pred_info["absolute_error"] = round(abs(pred_score - float(expected)), 4)
                            pred_info["exact_match"] = round(pred_score) == round(float(expected))

                    explanation["model_evaluation"]["predictions"][qid] = pred_info

    return explanation


def format_case_explanation_text(data: dict[str, Any]) -> str:
    """Format structured case explanation as rich human-readable terminal text."""
    lines = [
        "=" * 80,
        f"BENCHMARK CASE: {data['case_id']}  (Suite: {data['suite']})",
        "=" * 80,
        "\n--- INPUT CONTEXT / STATE ---",
    ]

    state = data.get("state", {})
    if isinstance(state, dict):
        for k, v in state.items():
            lines.append(f"  [{k}]: {v}")
    else:
        lines.append(f"  {state}")

    lines.append("\n--- QUESTIONS & EVALUATION RUBRICS ---")
    for qid, q in data["questions"].items():
        lines.append(f"\n  * Question: '{qid}'  [Type: {q['type'].upper()}]")
        lines.append(f"    Instructions: {q['instructions']}")
        gt = q.get("ground_truth")
        lines.append(f"    Ground Truth Label: {gt}")

        if q["type"] == "choice":
            lines.append(f"    Valid Options: {', '.join(repr(o) for o in q.get('options', []))}")
            if q.get("options_descriptions"):
                for opt, desc in q["options_descriptions"].items():
                    lines.append(f"      - {opt}: {desc}")
        elif q["type"] == "score":
            rubric = q.get("rubric_legend", [])
            if rubric:
                lines.append("    Rubric Scale:")
                for idx, item in enumerate(rubric):
                    lines.append(f"      [{idx}] {item}")
        elif q["type"] == "noul":
            lines.append("    Decision Threshold: >= 0.50 (True), < 0.50 (False)")

    if "model_evaluation" in data:
        me = data["model_evaluation"]
        lines.append(f"\n--- MODEL EVALUATION: {me['model']} ({me['provider']}) ---")
        lines.append(f"Latency: {me['latency_ms']:.1f}ms | HTTP Status: {me['status_code']}")
        for qid, pred in me["predictions"].items():
            qtype = data["questions"][qid]["type"]
            lines.append(f"\n  * Result for '{qid}' [{qtype.upper()}]:")
            if qtype == "choice":
                verdict = "CORRECT [PASS]" if pred.get("is_correct") else "INCORRECT [FAIL]"
                conf = f" (Confidence: {pred.get('confidence', 0):.2f})" if pred.get("confidence") is not None else ""
                lines.append(f"    Predicted: '{pred.get('predicted_choice')}'{conf} -> {verdict}")
                if pred.get("probabilities"):
                    lines.append(f"    Distribution: {pred['probabilities']}")
            elif qtype == "noul":
                verdict = "CORRECT [PASS]" if pred.get("is_correct") else "INCORRECT [FAIL]"
                prob = pred.get("predicted_probability", 0.0)
                loss_str = f" | Brier Loss: {pred.get('brier_loss')}" if "brier_loss" in pred else ""
                lines.append(f"    Probability: {prob:.4f} (Decision: {pred.get('predicted_binary')}) -> {verdict}{loss_str}")
            elif qtype == "score":
                score = pred.get("predicted_score", 0.0)
                err_str = f" | Error (|y - y_hat|): {pred.get('absolute_error')}" if "absolute_error" in pred else ""
                lines.append(f"    Predicted Score: {score:.3f}{err_str}")

    lines.append("\n" + "=" * 80)
    return "\n".join(lines)


def get_metrics_explanation_text() -> str:
    """Return comprehensive educational explanation of testing concepts, metrics, and contracts."""
    return """
================================================================================
       HOW TESTING WORKS: JEV TYPED DECISIONS & BENCHMARK METRICS
================================================================================

1. WHAT ARE TYPED DECISIONS?
--------------------------------------------------------------------------------
Traditional LLM inference produces unstructured, unpredictable free-form text:
  LLM -> "Based on your billing problem, I would classify this as high severity..."

Typed Decisions replace text generation with deterministic, structured decision heads:
  Engine -> {
    "category": {"choice": "billing", "probabilities": {"billing": 0.98, ...}},
    "urgent":   {"noul": 0.85},
    "severity": {"score": 2.74}
  }

This guarantees exact JSON schemas, valid enumerated keys, continuous probabilities,
and sub-second inference speeds with zero regex parsing or hallucinations.


2. THE THREE TYPED DECISION PRIMITIVES
--------------------------------------------------------------------------------
A. NOUL (Binary Decision Head):
   - Contract: Outputs a continuous probability p in [0.0, 1.0].
   - Binary Decision Rule: Decides TRUE if p >= 0.50, FALSE otherwise.
   - Evaluation Metrics:
     * Accuracy: Binary match against ground truth threshold.
     * Brier Score: Calibration mean squared error: (1/N) * sum((p_i - y_i)^2).
       Lower is better (0.00 is perfect calibration).
     * Precision / Recall / F1: Evaluates positive label detection balance.

B. CHOICE (Categorical Decision Head):
   - Contract: Outputs a selected label choice and a probability distribution
     over a fixed set of mutual-exclusive criteria options.
   - Evaluation Metrics:
     * Categorical Accuracy: % of cases where argmax(P) == Ground Truth.
     * Confidence Calibration: Average predicted probability on winner vs actual hit rate.
     * Log Loss / Cross-Entropy: Penalizes confident misclassifications.

C. SCORE (Ordered Rubric Head):
   - Contract: Evaluates a scenario against an ordered rubric (e.g. 0 to 3 scale).
     Outputs discrete class probabilities and an expectation score:
       E[Score] = sum(i * P(Score = i))
   - Evaluation Metrics:
     * Mean Absolute Error (MAE): (1/N) * sum(|Score_pred - Score_true|).
       Measures how far the model's continuous prediction is from the target.
     * Exact Match: % of cases where round(Score_pred) == Ground Truth.


3. SPEED & SYSTEM METRICS
--------------------------------------------------------------------------------
- Latency (p50, p90, p95): Round-trip inference time per decision case in milliseconds.
- Throughput (RPS): Completed typed-decision queries per second.
- Token Efficiency: Input tokens vs Output tokens (typically 3 tokens per decision vs
  hundreds of tokens for text-generation LLMs).


4. BENCHMARK SUITE STRUCTURE
--------------------------------------------------------------------------------
The repository provides versioned JSONL fixtures in 'benchmarks/':
- smoke.jsonl:          Contract & schema sanity test (2 cases).
- jev_core.jsonl:       Primary typed decision evaluation (37 cases).
- jev_agentic.jsonl:    Complex multi-step tool and planning decisions.
- jev_governance.jsonl: Safety, policy violation, and access control decisions.
- jev_patterns.jsonl:   Classification taxonomy patterns across enterprise domains.
- jev_complete.jsonl:   Unified comprehensive benchmark across all categories.


5. HOW TO RUN & VERIFY BENCHMARKS
--------------------------------------------------------------------------------
- Validate a suite:      uv run s1b validate-suite benchmarks/smoke.jsonl
- Inspect a test case:   uv run s1b explain-case support-001 --suite benchmarks/smoke.jsonl
- Run evaluation:        uv run s1b benchmark-provider --provider hearim_qwen35_4b --suite benchmarks/smoke.jsonl
- Compare models:        uv run s1b compare-results --baseline results/runs/jev-core-baseline.jsonl --candidate results/runs/hearim-qwen35-4b-core.jsonl
- View Leaderboard:      uv run s1b leaderboard
- Open Dashboard:        Open 'results/dashboard.html' in your browser!
================================================================================
"""
