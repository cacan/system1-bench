"""Command-line entry points for workspace validation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

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
            }
            for provider_id, provider in providers.items()
        },
    }
    print(json.dumps(output, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jevx", description="Jev local experiments workspace tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate-suite", help="validate a JSONL benchmark suite")
    validate.add_argument("path", nargs="?", type=Path, default=_default_path("benchmarks/smoke.jsonl"))

    show_config = subparsers.add_parser("show-config", help="show resolved non-secret workspace config")
    show_config.add_argument("--workspace-config", type=Path, default=_default_path("config/workspace.toml"))
    show_config.add_argument("--providers", type=Path, default=_default_path("config/providers.toml"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "validate-suite":
        return _validate_suite(args.path)
    if args.command == "show-config":
        return _show_config(args.workspace_config, args.providers)
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
