"""SQLite database layer for benchmark suites and execution results."""

from __future__ import annotations

import json
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .evaluate import evaluate_results, extract_prediction, load_results_jsonl
from .schema import BenchmarkCase, Question, load_suite


def get_connection(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: str | Path) -> None:
    """Initialize database tables for suites, cases, runs, and results."""
    with get_connection(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS benchmark_suites (
                suite_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                case_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS benchmark_cases (
                suite_id TEXT NOT NULL,
                case_id TEXT NOT NULL,
                experiment_id TEXT NOT NULL,
                state_json TEXT NOT NULL,
                questions_json TEXT NOT NULL,
                labels_json TEXT NOT NULL,
                PRIMARY KEY (suite_id, case_id),
                FOREIGN KEY (suite_id) REFERENCES benchmark_suites(suite_id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_cases_suite_id ON benchmark_cases(suite_id);
            CREATE INDEX IF NOT EXISTS idx_cases_experiment_id ON benchmark_cases(experiment_id);

            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                suite_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'completed',
                started_at TEXT NOT NULL,
                finished_at TEXT NOT NULL,
                total_cases INTEGER NOT NULL,
                successful_cases INTEGER NOT NULL,
                failed_cases INTEGER NOT NULL DEFAULT 0,
                categorical_accuracy REAL,
                score_mae REAL,
                latency_p50_ms REAL,
                latency_p95_ms REAL,
                throughput_rps REAL,
                total_input_tokens INTEGER NOT NULL DEFAULT 0,
                total_output_tokens INTEGER NOT NULL DEFAULT 0,
                metadata_json TEXT,
                FOREIGN KEY (suite_id) REFERENCES benchmark_suites(suite_id)
            );

            CREATE INDEX IF NOT EXISTS idx_runs_suite_id ON runs(suite_id);
            CREATE INDEX IF NOT EXISTS idx_runs_provider ON runs(provider);

            CREATE TABLE IF NOT EXISTS run_case_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                case_id TEXT NOT NULL,
                status_code INTEGER NOT NULL,
                latency_ms REAL,
                predictions_json TEXT NOT NULL,
                raw_response_json TEXT,
                correct_categorical INTEGER NOT NULL DEFAULT 0,
                total_categorical INTEGER NOT NULL DEFAULT 0,
                all_correct INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (run_id) REFERENCES runs(run_id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_case_results_run_id ON run_case_results(run_id);
            CREATE INDEX IF NOT EXISTS idx_case_results_case_id ON run_case_results(case_id);
            """
        )


def import_suite_to_db(
    db_path: str | Path,
    suite_path: str | Path,
    *,
    suite_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
) -> int:
    """Import a JSONL benchmark suite into the SQLite database."""
    init_db(db_path)
    suite_file = Path(suite_path)
    cases = load_suite(suite_file)

    sid = suite_id or suite_file.stem
    sname = name or sid.replace("_", " ").replace("-", " ").title()
    sdesc = description or f"Imported from {suite_file.name} ({len(cases)} cases)"
    now = datetime.now(timezone.utc).isoformat()

    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO benchmark_suites (suite_id, name, description, case_count, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(suite_id) DO UPDATE SET
                name = excluded.name,
                description = excluded.description,
                case_count = excluded.case_count,
                created_at = excluded.created_at
            """,
            (sid, sname, sdesc, len(cases), now),
        )

        for case in cases:
            # Extract experiment_id from case_id (e.g. support-001 -> support)
            exp_id = case.case_id.split("-")[0] if "-" in case.case_id else "default"
            questions_payload = {
                qid: {
                    "type": q.kind,
                    "instructions": q.instructions,
                    **({"criteria": dict(q.criteria) if isinstance(q.criteria, Mapping) else list(q.criteria)} if q.criteria else {}),
                }
                for qid, q in case.questions.items()
            }

            conn.execute(
                """
                INSERT INTO benchmark_cases (suite_id, case_id, experiment_id, state_json, questions_json, labels_json)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(suite_id, case_id) DO UPDATE SET
                    experiment_id = excluded.experiment_id,
                    state_json = excluded.state_json,
                    questions_json = excluded.questions_json,
                    labels_json = excluded.labels_json
                """,
                (
                    sid,
                    case.case_id,
                    exp_id,
                    json.dumps(case.state, ensure_ascii=False),
                    json.dumps(questions_payload, ensure_ascii=False),
                    json.dumps(case.labels, ensure_ascii=False),
                ),
            )
    return len(cases)


def sync_all_suites(db_path: str | Path, benchmarks_dir: str | Path) -> dict[str, int]:
    """Scan benchmarks directory and import all .jsonl files into SQLite."""
    init_db(db_path)
    bdir = Path(benchmarks_dir)
    results: dict[str, int] = {}
    for jsonl_file in sorted(bdir.glob("*.jsonl")):
        count = import_suite_to_db(db_path, jsonl_file)
        results[jsonl_file.stem] = count
    return results


def load_cases_from_db(db_path: str | Path, suite_id: str) -> list[BenchmarkCase]:
    """Load benchmark cases from SQLite and convert back to BenchmarkCase objects."""
    init_db(db_path)
    cases: list[BenchmarkCase] = []
    with get_connection(db_path) as conn:
        if suite_id == "all":
            rows = conn.execute("SELECT * FROM benchmark_cases ORDER BY rowid").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM benchmark_cases WHERE suite_id = ? ORDER BY rowid", (suite_id,)
            ).fetchall()

        for row in rows:
            raw_questions = json.loads(row["questions_json"])
            questions: dict[str, Question] = {}
            for qid, q in raw_questions.items():
                crit = q.get("criteria")
                if isinstance(crit, list):
                    crit = tuple(crit)
                questions[qid] = Question(kind=q["type"], instructions=q["instructions"], criteria=crit)

            cases.append(
                BenchmarkCase(
                    case_id=row["case_id"],
                    state=json.loads(row["state_json"]),
                    questions=questions,
                    labels=json.loads(row["labels_json"]),
                )
            )
    return cases


def import_results_jsonl_to_db(
    db_path: str | Path,
    results_path: str | Path,
    suite_id: str,
    *,
    run_id: str | None = None,
    provider: str | None = None,
    model: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Ingest a JSONL results file into SQLite and compute aggregate run statistics."""
    init_db(db_path)
    res_path = Path(results_path)
    rows = load_results_jsonl(res_path)
    if not rows:
        raise ValueError(f"Results file is empty: {res_path}")

    # Load cases for evaluation
    cases = load_cases_from_db(db_path, suite_id)
    if not cases:
        # Fallback to loading from benchmarks/ folder if suite exists as file
        suite_fallback = res_path.parents[1] / "benchmarks" / f"{suite_id}.jsonl"
        if suite_fallback.is_file():
            import_suite_to_db(db_path, suite_fallback, suite_id=suite_id)
            cases = load_cases_from_db(db_path, suite_id)
        else:
            raise ValueError(f"No cases found in DB for suite_id={suite_id!r}")

    cases_map = {c.case_id: c for c in cases}
    report = evaluate_results(cases, rows, suite_path=res_path)

    p_val = provider or report.provider or "unknown"
    m_val = model or report.model or "unknown"
    now_ts = datetime.now(timezone.utc).isoformat()
    rid = run_id or f"{p_val}_{m_val}_{int(time.time())}"

    # Calculate throughput
    total_time_s = sum(r.get("latency_ms", 0.0) for r in rows) / 1000.0
    throughput = len(rows) / total_time_s if total_time_s > 0 else 0.0

    meta_str = json.dumps(metadata or {}, ensure_ascii=False)

    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO runs (
                run_id, provider, model, suite_id, status, started_at, finished_at,
                total_cases, successful_cases, failed_cases, categorical_accuracy, score_mae,
                latency_p50_ms, latency_p95_ms, throughput_rps, total_input_tokens, total_output_tokens,
                metadata_json
            ) VALUES (?, ?, ?, ?, 'completed', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(run_id) DO UPDATE SET
                status = excluded.status,
                finished_at = excluded.finished_at,
                total_cases = excluded.total_cases,
                successful_cases = excluded.successful_cases,
                failed_cases = excluded.failed_cases,
                categorical_accuracy = excluded.categorical_accuracy,
                score_mae = excluded.score_mae,
                latency_p50_ms = excluded.latency_p50_ms,
                latency_p95_ms = excluded.latency_p95_ms,
                throughput_rps = excluded.throughput_rps,
                total_input_tokens = excluded.total_input_tokens,
                total_output_tokens = excluded.total_output_tokens,
                metadata_json = excluded.metadata_json
            """,
            (
                rid,
                p_val,
                m_val,
                suite_id,
                now_ts,
                now_ts,
                report.total_cases,
                report.successful_cases,
                report.failed_cases,
                report.categorical_accuracy,
                report.score_mae,
                report.latency.p50_ms,
                report.latency.p95_ms,
                round(throughput, 2),
                report.total_input_tokens,
                report.total_output_tokens,
                meta_str,
            ),
        )

        # Clear existing case results for this run if replacing
        conn.execute("DELETE FROM run_case_results WHERE run_id = ?", (rid,))

        # Insert per-case results
        for row in rows:
            cid = row.get("case_id")
            if not cid or cid not in cases_map:
                continue
            case = cases_map[cid]

            resp = row.get("response", {})
            answers = {}
            if isinstance(resp, dict):
                answers = resp.get("answers") or resp.get("decisions") or resp.get("predictions") or {}
                if not answers and "team" in resp:
                    answers = resp

            preds = {}
            correct_cat = 0
            total_cat = 0
            all_correct = 1

            for qid, question in case.questions.items():
                val = extract_prediction(answers.get(qid), question.kind)
                preds[qid] = val
                expected = case.labels.get(qid)
                if expected is not None:
                    if question.kind in ("choice", "noul"):
                        total_cat += 1
                        if val == expected:
                            correct_cat += 1
                        else:
                            all_correct = 0
                    elif question.kind == "score":
                        if val is None or round(float(val)) != int(expected):
                            all_correct = 0

            conn.execute(
                """
                INSERT INTO run_case_results (
                    run_id, case_id, status_code, latency_ms, predictions_json,
                    raw_response_json, correct_categorical, total_categorical, all_correct
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rid,
                    cid,
                    row.get("status_code", 200),
                    row.get("latency_ms"),
                    json.dumps(preds, ensure_ascii=False),
                    json.dumps(resp, ensure_ascii=False),
                    correct_cat,
                    total_cat,
                    all_correct,
                ),
            )
    return rid


def get_leaderboard(db_path: str | Path, suite_id: str | None = None) -> list[dict[str, Any]]:
    """Retrieve run leaderboard ranked by categorical accuracy, score MAE, and latency."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        query = """
            SELECT run_id, provider, model, suite_id, total_cases, successful_cases,
                   categorical_accuracy, score_mae, latency_p50_ms, latency_p95_ms,
                   throughput_rps, total_input_tokens, total_output_tokens, finished_at
            FROM runs
        """
        params: list[Any] = []
        if suite_id:
            query += " WHERE suite_id = ?"
            params.append(suite_id)
        query += " ORDER BY categorical_accuracy DESC, score_mae ASC, latency_p50_ms ASC"

        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def get_run(db_path: str | Path, run_id: str) -> dict[str, Any] | None:
    """Fetch run metadata and aggregate stats."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        return dict(row) if row else None


def get_run_case_results(db_path: str | Path, run_id: str) -> dict[str, dict[str, Any]]:
    """Fetch case results indexed by case_id for a given run."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT cr.*, c.state_json, c.questions_json, c.labels_json, c.experiment_id
            FROM run_case_results cr
            JOIN runs r ON cr.run_id = r.run_id
            JOIN benchmark_cases c ON cr.case_id = c.case_id AND c.suite_id = r.suite_id
            WHERE cr.run_id = ?
            """,
            (run_id,),
        ).fetchall()
        return {r["case_id"]: dict(r) for r in rows}


def compare_db_runs(
    db_path: str | Path,
    baseline_run_id: str,
    candidate_run_id: str,
) -> dict[str, Any]:
    """Compare two runs in SQLite and extract disagreements and accuracy deltas."""
    b_run = get_run(db_path, baseline_run_id)
    c_run = get_run(db_path, candidate_run_id)
    if not b_run:
        raise ValueError(f"Baseline run not found: {baseline_run_id}")
    if not c_run:
        raise ValueError(f"Candidate run not found: {candidate_run_id}")

    b_cases = get_run_case_results(db_path, baseline_run_id)
    c_cases = get_run_case_results(db_path, candidate_run_id)

    common_cids = sorted(set(b_cases.keys()) & set(c_cases.keys()))
    all_cases: list[dict[str, Any]] = []
    disagreements = []
    candidate_errors = []
    both_correct = 0

    for cid in common_cids:
        b_res = b_cases[cid]
        c_res = c_cases[cid]
        b_preds = json.loads(b_res["predictions_json"])
        c_preds = json.loads(c_res["predictions_json"])
        labels = json.loads(b_res["labels_json"])
        state = json.loads(b_res["state_json"])

        has_disagreement = False
        has_error = False

        for qid, expected in labels.items():
            bp = b_preds.get(qid)
            cp = c_preds.get(qid)
            if bp != cp:
                has_disagreement = True
            if cp != expected:
                has_error = True

        b_raw = json.loads(b_res["raw_response_json"]) if b_res.get("raw_response_json") else {}
        c_raw = json.loads(c_res["raw_response_json"]) if c_res.get("raw_response_json") else {}
        questions = json.loads(b_res["questions_json"]) if b_res.get("questions_json") else {}

        case_item = {
            "case_id": cid,
            "experiment_id": b_res["experiment_id"],
            "state": state,
            "labels": labels,
            "questions": questions,
            "baseline_predictions": b_preds,
            "candidate_predictions": c_preds,
            "baseline_answers": b_raw.get("answers") or b_raw.get("decisions") or {},
            "candidate_answers": c_raw.get("answers") or c_raw.get("decisions") or {},
            "baseline_latency_ms": b_res.get("latency_ms"),
            "candidate_latency_ms": c_res.get("latency_ms"),
            "disagreement": has_disagreement,
            "candidate_error": has_error,
        }

        all_cases.append(case_item)
        if has_disagreement:
            disagreements.append(case_item)
        if has_error:
            candidate_errors.append(case_item)
        if not has_error:
            both_correct += 1

    cat_delta = (c_run["categorical_accuracy"] or 0) - (b_run["categorical_accuracy"] or 0)
    mae_delta = None
    if c_run["score_mae"] is not None and b_run["score_mae"] is not None:
        mae_delta = c_run["score_mae"] - b_run["score_mae"]

    speedup = None
    if b_run["latency_p50_ms"] and c_run["latency_p50_ms"]:
        speedup = round(b_run["latency_p50_ms"] / c_run["latency_p50_ms"], 2)

    return {
        "baseline": b_run,
        "candidate": c_run,
        "total_compared_cases": len(common_cids),
        "disagreement_count": len(disagreements),
        "candidate_error_count": len(candidate_errors),
        "categorical_accuracy_delta": round(cat_delta, 4),
        "score_mae_delta": round(mae_delta, 4) if mae_delta is not None else None,
        "speedup_ratio": speedup,
        "cases": all_cases,
        "disagreements": disagreements,
        "candidate_errors": candidate_errors,
    }


def get_all_suites(db_path: str | Path) -> list[dict[str, Any]]:
    """Fetch all registered benchmark suites."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT * FROM benchmark_suites ORDER BY case_count DESC").fetchall()
        return [dict(r) for r in rows]


def get_all_benchmark_cases(db_path: str | Path, suite_id: str | None = None) -> list[dict[str, Any]]:
    """Fetch benchmark cases from SQLite with parsed JSON fields."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        if suite_id and suite_id != "all":
            rows = conn.execute(
                "SELECT * FROM benchmark_cases WHERE suite_id = ? ORDER BY rowid",
                (suite_id,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM benchmark_cases ORDER BY suite_id, rowid").fetchall()

        cases: list[dict[str, Any]] = []
        for r in rows:
            cases.append(
                {
                    "case_id": r["case_id"],
                    "suite_id": r["suite_id"],
                    "experiment_id": r["experiment_id"],
                    "state": json.loads(r["state_json"]),
                    "questions": json.loads(r["questions_json"]),
                    "labels": json.loads(r["labels_json"]),
                }
            )
        return cases

