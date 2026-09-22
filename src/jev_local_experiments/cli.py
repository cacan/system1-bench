"""Command-line entry points for workspace validation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .baseline import BaselineError, JevReferenceClient, build_systemone_request, run_jev_baseline
from .config import load_provider_config, load_workspace_config
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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "validate-suite":
        return _validate_suite(args.path)
    if args.command == "show-config":
        return _show_config(args.workspace_config, args.providers)
    if args.command == "benchmark-jev":
        return _benchmark_jev(args.suite, args.providers, args.output, args.timeout, args.dry_run)
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
