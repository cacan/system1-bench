"""Evaluation and comparison metrics for Jev-style typed decisions."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from .schema import BenchmarkCase, load_suite


@dataclass
class QuestionMetric:
    question_id: str
    kind: str
    total: int = 0
    correct: int = 0
    accuracy: float = 0.0
    # For noul
    precision: float | None = None
    recall: float | None = None
    f1: float | None = None
    brier_score: float | None = None
    # For score
    mae: float | None = None
    exact_accuracy: float | None = None


@dataclass
class LatencyStats:
    count: int = 0
    mean_ms: float = 0.0
    p50_ms: float = 0.0
    p90_ms: float = 0.0
    p95_ms: float = 0.0
    min_ms: float = 0.0
    max_ms: float = 0.0


@dataclass
class EvaluationReport:
    provider: str
    model: str
    suite_path: str | None
    total_cases: int
    successful_cases: int
    failed_cases: int
    categorical_accuracy: float
    score_mae: float | None
    latency: LatencyStats
    questions: dict[str, QuestionMetric] = field(default_factory=dict)
    total_input_tokens: int = 0
    total_output_tokens: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "suite_path": self.suite_path,
            "total_cases": self.total_cases,
            "successful_cases": self.successful_cases,
            "failed_cases": self.failed_cases,
            "categorical_accuracy": round(self.categorical_accuracy, 4),
            "score_mae": round(self.score_mae, 4) if self.score_mae is not None else None,
            "latency": {
                "count": self.latency.count,
                "mean_ms": round(self.latency.mean_ms, 2),
                "p50_ms": round(self.latency.p50_ms, 2),
                "p90_ms": round(self.latency.p90_ms, 2),
                "p95_ms": round(self.latency.p95_ms, 2),
                "min_ms": round(self.latency.min_ms, 2),
                "max_ms": round(self.latency.max_ms, 2),
            },
            "token_usage": {
                "input_tokens": self.total_input_tokens,
                "output_tokens": self.total_output_tokens,
            },
            "questions": {
                qid: {
                    "kind": qm.kind,
                    "total": qm.total,
                    "accuracy": round(qm.accuracy, 4),
                    **({"precision": round(qm.precision, 4)} if qm.precision is not None else {}),
                    **({"recall": round(qm.recall, 4)} if qm.recall is not None else {}),
                    **({"f1": round(qm.f1, 4)} if qm.f1 is not None else {}),
                    **({"brier_score": round(qm.brier_score, 4)} if qm.brier_score is not None else {}),
                    **({"mae": round(qm.mae, 4)} if qm.mae is not None else {}),
                    **({"exact_accuracy": round(qm.exact_accuracy, 4)} if qm.exact_accuracy is not None else {}),
                }
                for qid, qm in self.questions.items()
            },
        }

    def format_summary(self) -> str:
        lines = [
            f"=== Evaluation Report: {self.provider} ({self.model}) ===",
            f"Cases evaluated: {self.successful_cases}/{self.total_cases} (failed: {self.failed_cases})",
            f"Categorical Accuracy (Choice + Noul): {self.categorical_accuracy * 100:.2f}%",
        ]
        if self.score_mae is not None:
            lines.append(f"Score Mean Absolute Error (MAE): {self.score_mae:.3f}")
        if self.latency.count > 0:
            lines.append(
                f"Latency: p50={self.latency.p50_ms:.1f}ms, p95={self.latency.p95_ms:.1f}ms, mean={self.latency.mean_ms:.1f}ms"
            )
        if self.total_input_tokens > 0 or self.total_output_tokens > 0:
            lines.append(f"Tokens: in={self.total_input_tokens}, out={self.total_output_tokens}")

        lines.append("\nPer-Question Breakdown:")
        for qid, qm in sorted(self.questions.items()):
            if qm.kind == "score":
                lines.append(
                    f"  - {qid} [score]: MAE={qm.mae:.3f}, exact_acc={qm.exact_accuracy * 100:.1f}% (n={qm.total})"
                )
            elif qm.kind == "noul":
                f1_str = f", F1={qm.f1:.3f}" if qm.f1 is not None else ""
                lines.append(f"  - {qid} [noul]: acc={qm.accuracy * 100:.1f}%{f1_str} (n={qm.total})")
            else:
                lines.append(f"  - {qid} [choice]: acc={qm.accuracy * 100:.1f}% (n={qm.total})")
        return "\n".join(lines)


def _percentile(values: Sequence[float], p: float) -> float:
    if not values:
        return 0.0
    k = (len(values) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return float(values[int(k)])
    d0 = values[int(f)] * (c - k)
    d1 = values[int(c)] * (k - f)
    return float(d0 + d1)


def compute_latency_stats(latencies: Sequence[float]) -> LatencyStats:
    if not latencies:
        return LatencyStats()
    sorted_lats = sorted(latencies)
    return LatencyStats(
        count=len(latencies),
        mean_ms=sum(latencies) / len(latencies),
        p50_ms=_percentile(sorted_lats, 50),
        p90_ms=_percentile(sorted_lats, 90),
        p95_ms=_percentile(sorted_lats, 95),
        min_ms=sorted_lats[0],
        max_ms=sorted_lats[-1],
    )


def extract_prediction(raw_answer: Any, kind: str, noul_threshold: float = 0.5) -> Any:
    """Extract a normalized predicted value from various provider answer shapes."""
    if raw_answer is None:
        return None

    if isinstance(raw_answer, dict):
        if kind == "choice":
            if "choice" in raw_answer:
                return str(raw_answer["choice"])
            if "selected" in raw_answer:
                return str(raw_answer["selected"])
            if "value" in raw_answer:
                return str(raw_answer["value"])
            if "probabilities" in raw_answer and isinstance(raw_answer["probabilities"], dict):
                probs = raw_answer["probabilities"]
                return max(probs.keys(), key=lambda k: float(probs[k]))
        elif kind == "noul":
            if "decision" in raw_answer and isinstance(raw_answer["decision"], bool):
                return raw_answer["decision"]
            if "noul" in raw_answer:
                val = raw_answer["noul"]
                return bool(val >= noul_threshold) if isinstance(val, (int, float)) else bool(val)
            if "probability" in raw_answer:
                return float(raw_answer["probability"]) >= noul_threshold
            if "value" in raw_answer:
                val = raw_answer["value"]
                return bool(val >= noul_threshold) if isinstance(val, (int, float)) else bool(val)
        elif kind == "score":
            if "score" in raw_answer:
                return float(raw_answer["score"])
            if "value" in raw_answer:
                return float(raw_answer["value"])
            if "probabilities" in raw_answer and isinstance(raw_answer["probabilities"], dict):
                probs = raw_answer["probabilities"]
                return sum(float(lvl) * float(p) for lvl, p in probs.items())
        return None

    # Scalar values
    if kind == "noul":
        if isinstance(raw_answer, bool):
            return raw_answer
        if isinstance(raw_answer, (int, float)):
            return raw_answer >= noul_threshold
        if isinstance(raw_answer, str):
            return raw_answer.lower() in ("true", "1", "yes")
    elif kind == "score":
        if isinstance(raw_answer, (int, float)):
            return float(raw_answer)
        try:
            return float(raw_answer)
        except (ValueError, TypeError):
            return None
    elif kind == "choice":
        return str(raw_answer)

    return None


def evaluate_results(
    cases: Mapping[str, BenchmarkCase] | Sequence[BenchmarkCase],
    results: Sequence[Mapping[str, Any]],
    *,
    suite_path: str | Path | None = None,
    noul_threshold: float = 0.5,
) -> EvaluationReport:
    """Evaluate a set of run results against ground-truth benchmark cases."""

    cases_map: dict[str, BenchmarkCase]
    if isinstance(cases, Mapping):
        cases_map = dict(cases)
    else:
        cases_map = {c.case_id: c for c in cases}

    provider = "unknown"
    model = "unknown"
    latencies: list[float] = []
    total_in_tokens = 0
    total_out_tokens = 0
    successful = 0
    failed = 0

    # Accumulators per question
    q_data: dict[str, dict[str, Any]] = {}

    for row in results:
        case_id = row.get("case_id")
        if not case_id or case_id not in cases_map:
            continue

        case = cases_map[case_id]
        provider = row.get("provider", provider)
        model = row.get("model", model)

        status_code = row.get("status_code", 200)
        if status_code != 200:
            failed += 1
            continue

        successful += 1
        lat = row.get("latency_ms")
        if isinstance(lat, (int, float)):
            latencies.append(float(lat))

        # Tokens
        response = row.get("response", {})
        if isinstance(response, dict):
            usage = response.get("usage", {})
            if isinstance(usage, dict):
                total_in_tokens += int(usage.get("input_tokens", 0))
                total_out_tokens += int(usage.get("output_tokens", 0))

        # Extract predictions
        answers: dict[str, Any] = {}
        if isinstance(response, dict):
            raw_answers = response.get("answers") or response.get("decisions") or response.get("predictions")
            if isinstance(raw_answers, dict):
                answers = raw_answers
            elif not raw_answers and "team" in response:
                answers = response

        for qid, question in case.questions.items():
            if qid not in case.labels:
                continue
            expected_label = case.labels[qid]

            if qid not in q_data:
                q_data[qid] = {
                    "kind": question.kind,
                    "preds": [],
                    "labels": [],
                    "raw_answers": [],
                }

            pred = extract_prediction(answers.get(qid), question.kind, noul_threshold=noul_threshold)
            q_data[qid]["preds"].append(pred)
            q_data[qid]["labels"].append(expected_label)
            q_data[qid]["raw_answers"].append(answers.get(qid))

    # Compute metrics per question
    question_metrics: dict[str, QuestionMetric] = {}
    total_cat_evaluated = 0
    total_cat_correct = 0
    all_score_errors: list[float] = []

    for qid, d in q_data.items():
        kind = d["kind"]
        preds = d["preds"]
        labels = d["labels"]
        total = len(preds)
        if total == 0:
            continue

        if kind == "choice":
            correct = sum(1 for p, y in zip(preds, labels) if p == y)
            acc = correct / total
            question_metrics[qid] = QuestionMetric(
                question_id=qid, kind=kind, total=total, correct=correct, accuracy=acc
            )
            total_cat_evaluated += total
            total_cat_correct += correct

        elif kind == "noul":
            correct = sum(1 for p, y in zip(preds, labels) if p == y)
            acc = correct / total
            tp = sum(1 for p, y in zip(preds, labels) if p is True and y is True)
            fp = sum(1 for p, y in zip(preds, labels) if p is True and y is False)
            fn = sum(1 for p, y in zip(preds, labels) if p is False and y is True)
            tn = sum(1 for p, y in zip(preds, labels) if p is False and y is False)

            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

            # Brier score
            brier_sum = 0.0
            brier_count = 0
            for raw, y in zip(d["raw_answers"], labels):
                prob = None
                if isinstance(raw, dict):
                    prob = raw.get("noul") or raw.get("probability")
                elif isinstance(raw, (int, float)):
                    prob = float(raw)
                if isinstance(prob, (int, float)):
                    brier_sum += (prob - (1.0 if y else 0.0)) ** 2
                    brier_count += 1
            brier = brier_sum / brier_count if brier_count > 0 else None

            question_metrics[qid] = QuestionMetric(
                question_id=qid,
                kind=kind,
                total=total,
                correct=correct,
                accuracy=acc,
                precision=prec,
                recall=rec,
                f1=f1,
                brier_score=brier,
            )
            total_cat_evaluated += total
            total_cat_correct += correct

        elif kind == "score":
            errors = []
            exact = 0
            for p, y in zip(preds, labels):
                if p is not None:
                    err = abs(float(p) - float(y))
                    errors.append(err)
                    all_score_errors.append(err)
                    if round(float(p)) == int(y):
                        exact += 1
            mae = sum(errors) / len(errors) if errors else 0.0
            exact_acc = exact / len(errors) if errors else 0.0
            question_metrics[qid] = QuestionMetric(
                question_id=qid,
                kind=kind,
                total=len(errors),
                correct=exact,
                accuracy=exact_acc,
                mae=mae,
                exact_accuracy=exact_acc,
            )

    cat_acc = total_cat_correct / total_cat_evaluated if total_cat_evaluated > 0 else 0.0
    overall_mae = sum(all_score_errors) / len(all_score_errors) if all_score_errors else None
    lat_stats = compute_latency_stats(latencies)

    return EvaluationReport(
        provider=provider,
        model=model,
        suite_path=str(suite_path) if suite_path else None,
        total_cases=len(cases_map),
        successful_cases=successful,
        failed_cases=failed,
        categorical_accuracy=cat_acc,
        score_mae=overall_mae,
        latency=lat_stats,
        questions=question_metrics,
        total_input_tokens=total_in_tokens,
        total_output_tokens=total_out_tokens,
    )


def compare_reports(baseline: EvaluationReport, candidate: EvaluationReport) -> dict[str, Any]:
    """Produce a comparative delta analysis between baseline and candidate reports."""

    cat_delta = candidate.categorical_accuracy - baseline.categorical_accuracy
    mae_delta = None
    if candidate.score_mae is not None and baseline.score_mae is not None:
        mae_delta = candidate.score_mae - baseline.score_mae

    speedup = None
    if baseline.latency.p50_ms > 0 and candidate.latency.p50_ms > 0:
        speedup = baseline.latency.p50_ms / candidate.latency.p50_ms

    question_comparisons: dict[str, Any] = {}
    all_qids = set(baseline.questions.keys()) | set(candidate.questions.keys())
    for qid in sorted(all_qids):
        bq = baseline.questions.get(qid)
        cq = candidate.questions.get(qid)
        if bq and cq:
            question_comparisons[qid] = {
                "kind": bq.kind,
                "baseline_acc": round(bq.accuracy, 4),
                "candidate_acc": round(cq.accuracy, 4),
                "acc_delta": round(cq.accuracy - bq.accuracy, 4),
                **({"baseline_mae": round(bq.mae, 4), "candidate_mae": round(cq.mae, 4)} if bq.mae is not None and cq.mae is not None else {}),
            }

    return {
        "baseline": {"provider": baseline.provider, "model": baseline.model},
        "candidate": {"provider": candidate.provider, "model": candidate.model},
        "categorical_accuracy": {
            "baseline": round(baseline.categorical_accuracy, 4),
            "candidate": round(candidate.categorical_accuracy, 4),
            "delta": round(cat_delta, 4),
        },
        "score_mae": {
            "baseline": round(baseline.score_mae, 4) if baseline.score_mae is not None else None,
            "candidate": round(candidate.score_mae, 4) if candidate.score_mae is not None else None,
            "delta": round(mae_delta, 4) if mae_delta is not None else None,
        },
        "latency_p50_ms": {
            "baseline": round(baseline.latency.p50_ms, 2),
            "candidate": round(candidate.latency.p50_ms, 2),
            "speedup_ratio": round(speedup, 2) if speedup is not None else None,
        },
        "questions": question_comparisons,
    }


def load_results_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Load JSONL results file."""
    rows: list[dict[str, Any]] = []
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Results file does not exist: {p}")
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows
