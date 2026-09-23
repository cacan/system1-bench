"""Command-line entry points for workspace validation."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from .baseline import BaselineError, JevReferenceClient, build_systemone_request, run_jev_baseline
from .config import load_provider_config, load_workspace_config
from .dashboard import generate_dashboard_html
from .db import (
    compare_db_runs,
    get_leaderboard,
    import_results_jsonl_to_db,
    init_db,
    sync_all_suites,
)
from .evaluate import compare_reports, evaluate_results, load_results_jsonl
from .explain import (
    explain_case_details,
    find_case_in_suites,
    format_case_explanation_text,
    get_metrics_explanation_text,
)
from .provider_client import ProviderClientError, SystemOneHttpClient, run_provider_benchmark
from .schema import ValidationError, load_suite


def _default_path(relative: str) -> Path:
    return (Path.cwd() / relative).resolve()


def _validate_suite(path: Path) -> int:
    path = path.resolve()
    try:
        cases = load_suite(path)
    except (OSError, ValidationError) as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"path": str(path), "case_count": len(cases), "case_ids": [c.case_id for c in cases]}))
    return 0


def _show_config(workspace_path: Path, providers_path: Path) -> int:
    try:
        workspace = load_workspace_config(workspace_path)
        providers = load_provider_config(providers_path)
    except (OSError, ValueError) as exc:
        print(f"configuration failed: {exc}", file=sys.stderr)
        return 2
    output = {
        "workspace": {
            "id": workspace.workspace_id,
            "name": workspace.name,
            "mode": workspace.mode,
            "benchmark_profile": workspace.benchmark_profile,
            "paths": {key: str(value) for key, value in workspace.paths.items()},
            "integrations": workspace.integrations,
        },
        "providers": {
            provider_id: {
                "kind": provider.kind,
                "enabled": provider.enabled,
                "install_dir": str(provider.install_dir),
                "base_url": provider.base_url,
                "endpoint": provider.endpoint,
                "model": provider.model,
                "api_key_file": str(provider.api_key_file) if provider.api_key_file else None,
                "reference_only": provider.reference_only,
                "training_use": provider.training_use,
            }
            for provider_id, provider in providers.items()
        },
    }
    print(json.dumps(output, indent=2))
    return 0


def _benchmark_jev(
    suite_path: Path,
    providers_path: Path,
    output_path: Path,
    timeout: float,
    dry_run: bool,
) -> int:
    try:
        cases = load_suite(suite_path.resolve())
        provider = load_provider_config(providers_path.resolve()).get("jev_reference")
        if provider is None or not provider.enabled:
            raise BaselineError("enabled providers.jev_reference configuration is required")
        if dry_run:
            print(
                json.dumps(
                    [build_systemone_request(case, model=provider.model) for case in cases],
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0
        client = JevReferenceClient.from_provider_config(provider, timeout=timeout)
        rows = run_jev_baseline(cases, client, output_path.resolve())
    except (OSError, ValueError, BaselineError) as exc:
        print(f"Jev baseline failed: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "provider": "jev_reference",
                "model": provider.model,
                "case_count": len(rows),
                "output": str(output_path.resolve()),
                "reference_only": True,
            }
        )
    )
    return 0


def _benchmark_provider(
    provider_id: str,
    suite_path: Path,
    providers_path: Path,
    output_path: Path | None,
    timeout: float,
    import_db: bool,
    db_path: Path,
) -> int:
    try:
        cases = load_suite(suite_path.resolve())
        providers = load_provider_config(providers_path.resolve())
        provider = providers.get(provider_id)
        if provider is None:
            raise ProviderClientError(f"Provider {provider_id!r} not found in providers config")
        if not provider.enabled:
            raise ProviderClientError(f"Provider {provider_id!r} is disabled in config")

        client = SystemOneHttpClient.from_provider_config(provider, timeout=timeout)
        out = output_path or Path(f"results/{provider_id}-{suite_path.stem}.jsonl")
        print(f"Running benchmark on {provider_id} ({provider.model}) with suite {suite_path.name} ({len(cases)} cases)...")
        rows = run_provider_benchmark(cases, client, out, provider_name=provider_id)
        print(f"Saved {len(rows)} results to {out}")

        report = evaluate_results(cases, rows, suite_path=suite_path)
        print("\n" + report.format_summary())

        if import_db:
            run_id = f"{provider_id}_{suite_path.stem}_{int(time.time())}"
            import_results_jsonl_to_db(
                db_path,
                out,
                suite_id=suite_path.stem,
                run_id=run_id,
                provider=provider_id,
                model=provider.model,
            )
            print(f"Imported run into SQLite DB: run_id={run_id}")
    except (OSError, ValueError, ValidationError, ProviderClientError) as exc:
        print(f"Benchmark failed: {exc}", file=sys.stderr)
        return 2
    return 0


def _evaluate(suite_path: Path, results_path: Path, json_output: bool) -> int:
    try:
        cases = load_suite(suite_path.resolve())
        results = load_results_jsonl(results_path.resolve())
        report = evaluate_results(cases, results, suite_path=suite_path)
    except (OSError, ValueError, ValidationError) as exc:
        print(f"evaluation failed: {exc}", file=sys.stderr)
        return 2

    if json_output:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(report.format_summary())
    return 0


def _compare_results(
    suite_path: Path, baseline_path: Path, candidate_path: Path, json_output: bool
) -> int:
    try:
        cases = load_suite(suite_path.resolve())
        b_results = load_results_jsonl(baseline_path.resolve())
        c_results = load_results_jsonl(candidate_path.resolve())
        b_report = evaluate_results(cases, b_results, suite_path=suite_path)
        c_report = evaluate_results(cases, c_results, suite_path=suite_path)
        diff = compare_reports(b_report, c_report)
    except (OSError, ValueError, ValidationError) as exc:
        print(f"comparison failed: {exc}", file=sys.stderr)
        return 2

    if json_output:
        print(json.dumps(diff, indent=2))
    else:
        print("=== Comparison: Baseline vs Candidate ===")
        print(f"Baseline:  {diff['baseline']['provider']} ({diff['baseline']['model']})")
        print(f"Candidate: {diff['candidate']['provider']} ({diff['candidate']['model']})")
        b_acc = diff["categorical_accuracy"]["baseline"] * 100
        c_acc = diff["categorical_accuracy"]["candidate"] * 100
        d_acc = diff["categorical_accuracy"]["delta"] * 100
        sign = "+" if d_acc >= 0 else ""
        print(f"Categorical Accuracy: {b_acc:.2f}% -> {c_acc:.2f}% ({sign}{d_acc:.2f}%)")
        if diff["score_mae"]["baseline"] is not None:
            b_mae = diff["score_mae"]["baseline"]
            c_mae = diff["score_mae"]["candidate"]
            d_mae = diff["score_mae"]["delta"]
            sign_mae = "+" if d_mae >= 0 else ""
            print(f"Score MAE:            {b_mae:.3f} -> {c_mae:.3f} ({sign_mae}{d_mae:.3f})")
        if diff["latency_p50_ms"]["speedup_ratio"] is not None:
            print(
                f"Latency p50:          {diff['latency_p50_ms']['baseline']}ms -> {diff['latency_p50_ms']['candidate']}ms (Speedup: {diff['latency_p50_ms']['speedup_ratio']}x)"
            )
        print("\nPer-Question Breakdown:")
        for qid, qd in diff["questions"].items():
            sign_q = "+" if qd["acc_delta"] >= 0 else ""
            print(
                f"  - {qid} [{qd['kind']}]: {qd['baseline_acc']*100:.1f}% -> {qd['candidate_acc']*100:.1f}% ({sign_q}{qd['acc_delta']*100:.1f}%)"
            )
    return 0


def _default_db_path() -> Path:
    return _default_path("results/benchmark_lab.db")


def _db_init(db_path: Path) -> int:
    try:
        init_db(db_path.resolve())
        print(f"initialized database: {db_path.resolve()}")
    except OSError as exc:
        print(f"db init failed: {exc}", file=sys.stderr)
        return 2
    return 0


def _db_sync(db_path: Path, benchmarks_dir: Path) -> int:
    try:
        results = sync_all_suites(db_path.resolve(), benchmarks_dir.resolve())
        print(
            json.dumps(
                {
                    "database": str(db_path.resolve()),
                    "suites": results,
                    "total_suites": len(results),
                    "total_cases": sum(results.values()),
                },
                indent=2,
            )
        )
    except (OSError, ValueError, ValidationError) as exc:
        print(f"db sync failed: {exc}", file=sys.stderr)
        return 2
    return 0


def _db_import_results(
    db_path: Path,
    results_path: Path,
    suite_id: str,
    run_id: str | None,
    provider: str | None,
    model: str | None,
) -> int:
    try:
        rid = import_results_jsonl_to_db(
            db_path.resolve(),
            results_path.resolve(),
            suite_id=suite_id,
            run_id=run_id,
            provider=provider,
            model=model,
        )
        print(
            json.dumps(
                {
                    "run_id": rid,
                    "database": str(db_path.resolve()),
                    "results_file": str(results_path.resolve()),
                    "suite_id": suite_id,
                }
            )
        )
    except (OSError, ValueError, ValidationError) as exc:
        print(f"import results failed: {exc}", file=sys.stderr)
        return 2
    return 0


def _leaderboard(db_path: Path, suite_id: str | None, json_output: bool) -> int:
    try:
        rows = get_leaderboard(db_path.resolve(), suite_id=suite_id)
    except OSError as exc:
        print(f"leaderboard query failed: {exc}", file=sys.stderr)
        return 2

    if json_output:
        print(json.dumps(rows, indent=2))
    else:
        title = f"=== Benchmark Leaderboard {'(' + suite_id + ')' if suite_id else ''} ==="
        print(title)
        if not rows:
            print("No runs recorded in database yet.")
            return 0
        header = f"{'Provider':<16} {'Model':<16} {'Suite':<14} {'Accuracy':<10} {'MAE':<8} {'p50(ms)':<10} {'RPS':<8}"
        print(header)
        print("-" * len(header))
        for r in rows:
            acc_str = f"{r['categorical_accuracy']*100:.1f}%" if r["categorical_accuracy"] is not None else "N/A"
            mae_str = f"{r['score_mae']:.3f}" if r["score_mae"] is not None else "—"
            p50_str = f"{r['latency_p50_ms']:.1f}" if r["latency_p50_ms"] is not None else "—"
            rps_str = f"{r['throughput_rps']:.1f}" if r["throughput_rps"] is not None else "—"
            print(f"{r['provider']:<16} {r['model']:<16} {r['suite_id']:<14} {acc_str:<10} {mae_str:<8} {p50_str:<10} {rps_str:<8}")
    return 0


def _compare_db_runs(
    db_path: Path, baseline_run_id: str, candidate_run_id: str, json_output: bool
) -> int:
    try:
        comp = compare_db_runs(
            db_path.resolve(),
            baseline_run_id=baseline_run_id,
            candidate_run_id=candidate_run_id,
        )
    except (OSError, ValueError) as exc:
        print(f"comparison failed: {exc}", file=sys.stderr)
        return 2

    if json_output:
        print(json.dumps(comp, indent=2))
    else:
        b = comp["baseline"]
        c = comp["candidate"]
        print("=== SQLite Run Comparison ===")
        print(f"Baseline:  {b['run_id']} ({b['provider']} / {b['model']})")
        print(f"Candidate: {c['run_id']} ({c['provider']} / {c['model']})")
        print(f"Compared cases: {comp['total_compared_cases']}")
        print(f"Disagreements:  {comp['disagreement_count']}")
        print(f"Candidate errs: {comp['candidate_error_count']}")
        d_acc = comp["categorical_accuracy_delta"] * 100
        sign = "+" if d_acc >= 0 else ""
        print(f"Accuracy:      {b['categorical_accuracy']*100:.1f}% -> {c['categorical_accuracy']*100:.1f}% ({sign}{d_acc:.1f}%)")
        if comp["score_mae_delta"] is not None:
            d_mae = comp["score_mae_delta"]
            sign_mae = "+" if d_mae >= 0 else ""
            print(f"Score MAE:     {b['score_mae']:.3f} -> {c['score_mae']:.3f} ({sign_mae}{d_mae:.3f})")
        if comp["speedup_ratio"]:
            print(f"Latency p50:   {b['latency_p50_ms']}ms -> {c['latency_p50_ms']}ms (Speedup: {comp['speedup_ratio']}x)")
    return 0


def _dashboard(
    db_path: Path,
    output_html_path: Path,
    baseline_run_id: str | None,
    candidate_run_id: str | None,
) -> int:
    try:
        out_path = generate_dashboard_html(
            db_path.resolve(),
            output_html_path.resolve(),
            baseline_run_id=baseline_run_id,
            candidate_run_id=candidate_run_id,
        )
        print(f"generated interactive dashboard: {out_path}")
    except (OSError, ValueError) as exc:
        print(f"dashboard generation failed: {exc}", file=sys.stderr)
        return 2
    return 0


def _explain_case(
    case_id: str,
    suite_path: Path | None,
    benchmarks_dir: Path,
    results_path: Path | None,
    json_output: bool,
) -> int:
    search_target = suite_path.resolve() if suite_path else benchmarks_dir.resolve()
    case, resolved_suite = find_case_in_suites(case_id, search_target)
    if not case:
        print(f"Error: Case {case_id!r} not found in {search_target}", file=sys.stderr)
        return 2

    data = explain_case_details(
        case,
        suite_path=resolved_suite,
        results_path=results_path.resolve() if results_path else None,
    )
    if json_output:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(format_case_explanation_text(data))
    return 0


def _explain_metrics() -> int:
    print(get_metrics_explanation_text())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jevx", description="Jev local experiments workspace tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate-suite", help="validate a JSONL benchmark suite")
    validate.add_argument("path", nargs="?", type=Path, default=_default_path("benchmarks/smoke.jsonl"))

    show_config = subparsers.add_parser("show-config", help="show resolved non-secret workspace config")
    show_config.add_argument("--workspace-config", type=Path, default=_default_path("config/workspace.toml"))
    show_config.add_argument("--providers", type=Path, default=_default_path("config/providers.toml"))

    benchmark = subparsers.add_parser("benchmark-jev", help="run the reference-only Jev baseline")
    benchmark.add_argument("--suite", type=Path, default=_default_path("benchmarks/smoke.jsonl"))
    benchmark.add_argument("--providers", type=Path, default=_default_path("config/providers.toml"))
    benchmark.add_argument("--output", type=Path, default=_default_path("results/jev-baseline.jsonl"))
    benchmark.add_argument("--timeout", type=float, default=60.0)
    benchmark.add_argument("--dry-run", action="store_true", help="print requests without reading the key or calling Jev")

    bench_prov = subparsers.add_parser("benchmark-provider", help="run benchmarks against any configured provider (Hearim, Kev, etc.)")
    bench_prov.add_argument("--provider", type=str, default="hearim", help="provider ID from providers config")
    bench_prov.add_argument("--suite", type=Path, default=_default_path("benchmarks/smoke.jsonl"), help="path to benchmark suite")
    bench_prov.add_argument("--providers", type=Path, default=_default_path("config/providers.toml"), help="path to providers config")
    bench_prov.add_argument("--output", type=Path, default=None, help="output JSONL path")
    bench_prov.add_argument("--timeout", type=float, default=30.0, help="request timeout in seconds")
    bench_prov.add_argument("--import-db", action="store_true", help="automatically import results into SQLite DB")
    bench_prov.add_argument("--db", type=Path, default=_default_db_path(), help="path to SQLite DB file")

    eval_cmd = subparsers.add_parser("evaluate", help="evaluate run results against a benchmark suite")
    eval_cmd.add_argument("--results", type=Path, required=True, help="path to results JSONL file")
    eval_cmd.add_argument("--suite", type=Path, default=_default_path("benchmarks/smoke.jsonl"), help="path to benchmark suite")
    eval_cmd.add_argument("--json", action="store_true", help="output report as JSON")

    comp_cmd = subparsers.add_parser("compare-results", help="compare baseline and candidate results side-by-side")
    comp_cmd.add_argument("--baseline", type=Path, required=True, help="path to baseline results JSONL")
    comp_cmd.add_argument("--candidate", type=Path, required=True, help="path to candidate results JSONL")
    comp_cmd.add_argument("--suite", type=Path, default=_default_path("benchmarks/smoke.jsonl"), help="path to benchmark suite")
    comp_cmd.add_argument("--json", action="store_true", help="output comparison as JSON")

    # SQLite DB subcommands
    db_init_cmd = subparsers.add_parser("db-init", help="initialize SQLite benchmark database schema")
    db_init_cmd.add_argument("--db", type=Path, default=_default_db_path(), help="path to SQLite DB file")

    db_sync_cmd = subparsers.add_parser("db-sync", help="import all JSONL benchmark suites into SQLite DB")
    db_sync_cmd.add_argument("--db", type=Path, default=_default_db_path(), help="path to SQLite DB file")
    db_sync_cmd.add_argument("--benchmarks-dir", type=Path, default=_default_path("benchmarks"), help="path to benchmarks directory")

    db_import_cmd = subparsers.add_parser("db-import-results", help="ingest a results JSONL into SQLite DB")
    db_import_cmd.add_argument("--results", type=Path, required=True, help="path to results JSONL file")
    db_import_cmd.add_argument("--suite-id", type=str, required=True, help="suite ID matching benchmark cases in DB")
    db_import_cmd.add_argument("--db", type=Path, default=_default_db_path(), help="path to SQLite DB file")
    db_import_cmd.add_argument("--run-id", type=str, default=None, help="optional custom run ID")
    db_import_cmd.add_argument("--provider", type=str, default=None, help="optional provider name override")
    db_import_cmd.add_argument("--model", type=str, default=None, help="optional model name override")

    lb_cmd = subparsers.add_parser("leaderboard", help="display runs leaderboard from SQLite DB")
    lb_cmd.add_argument("--db", type=Path, default=_default_db_path(), help="path to SQLite DB file")
    lb_cmd.add_argument("--suite-id", type=str, default=None, help="optional filter by suite ID")
    lb_cmd.add_argument("--json", action="store_true", help="output leaderboard as JSON")

    comp_runs_cmd = subparsers.add_parser("compare-runs", help="compare two runs stored in SQLite DB")
    comp_runs_cmd.add_argument("--baseline-run", type=str, required=True, help="baseline run ID")
    comp_runs_cmd.add_argument("--candidate-run", type=str, required=True, help="candidate run ID")
    comp_runs_cmd.add_argument("--db", type=Path, default=_default_db_path(), help="path to SQLite DB file")
    comp_runs_cmd.add_argument("--json", action="store_true", help="output comparison as JSON")

    dash_cmd = subparsers.add_parser("dashboard", help="generate interactive HTML comparison dashboard")
    dash_cmd.add_argument("--db", type=Path, default=_default_db_path(), help="path to SQLite DB file")
    dash_cmd.add_argument("--output", type=Path, default=_default_path("results/dashboard.html"), help="HTML output path")
    dash_cmd.add_argument("--baseline-run", type=str, default=None, help="optional baseline run ID")
    dash_cmd.add_argument("--candidate-run", type=str, default=None, help="optional candidate run ID")

    # Explanation tools
    exp_case_cmd = subparsers.add_parser("explain-case", help="inspect and explain a test case, its rubrics, and model error analysis")
    exp_case_cmd.add_argument("case_id", type=str, help="ID of the benchmark case (e.g. support-001)")
    exp_case_cmd.add_argument("--suite", type=Path, default=None, help="optional specific benchmark suite path")
    exp_case_cmd.add_argument("--benchmarks-dir", type=Path, default=_default_path("benchmarks"), help="benchmarks directory to search")
    exp_case_cmd.add_argument("--results", type=Path, default=None, help="optional results JSONL file to analyze model errors against")
    exp_case_cmd.add_argument("--json", action="store_true", help="output structured explanation as JSON")

    subparsers.add_parser("explain-metrics", help="comprehensive educational guide to typed decisions and evaluation metrics")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "validate-suite":
        return _validate_suite(args.path)
    if args.command == "show-config":
        return _show_config(args.workspace_config, args.providers)
    if args.command == "benchmark-jev":
        return _benchmark_jev(args.suite, args.providers, args.output, args.timeout, args.dry_run)
    if args.command == "benchmark-provider":
        return _benchmark_provider(
            args.provider,
            args.suite,
            args.providers,
            args.output,
            args.timeout,
            args.import_db,
            args.db,
        )
    if args.command == "evaluate":
        return _evaluate(args.suite, args.results, args.json)
    if args.command == "compare-results":
        return _compare_results(args.suite, args.baseline, args.candidate, args.json)
    if args.command == "db-init":
        return _db_init(args.db)
    if args.command == "db-sync":
        return _db_sync(args.db, args.benchmarks_dir)
    if args.command == "db-import-results":
        return _db_import_results(args.db, args.results, args.suite_id, args.run_id, args.provider, args.model)
    if args.command == "leaderboard":
        return _leaderboard(args.db, args.suite_id, args.json)
    if args.command == "compare-runs":
        return _compare_db_runs(args.db, args.baseline_run, args.candidate_run, args.json)
    if args.command == "dashboard":
        return _dashboard(args.db, args.output, args.baseline_run, args.candidate_run)
    if args.command == "explain-case":
        return _explain_case(args.case_id, args.suite, args.benchmarks_dir, args.results, args.json)
    if args.command == "explain-metrics":
        return _explain_metrics()
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
