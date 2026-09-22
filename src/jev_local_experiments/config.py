"""Load non-secret workspace and provider configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.12+ includes tomllib
    import tomli as tomllib  # type: ignore[no-redef]


@dataclass(frozen=True)
class WorkspaceConfig:
    workspace_id: str
    name: str
    mode: str
    benchmark_profile: str
    paths: dict[str, Path]
    integrations: dict[str, bool]


@dataclass(frozen=True)
class ProviderConfig:
    provider_id: str
    kind: str
    enabled: bool
    install_dir: Path
    base_url: str
    endpoint: str
    model: str
    api_key_file: Path | None = None
    reference_only: bool = False
    training_use: bool = True


def _read_toml(path: str | Path) -> tuple[Path, dict[str, Any]]:
    config_path = Path(path).resolve()
    if not config_path.is_file():
        raise FileNotFoundError(config_path)
    with config_path.open("rb") as handle:
        return config_path, tomllib.load(handle)


def load_workspace_config(path: str | Path) -> WorkspaceConfig:
    config_path, raw = _read_toml(path)
    root = config_path.parent.parent
    workspace = raw.get("workspace") or {}
    if not workspace.get("id"):
        raise ValueError("workspace.id is required")
    paths = {
        key: (root / value).resolve() if not Path(value).is_absolute() else Path(value).resolve()
        for key, value in (raw.get("paths") or {}).items()
    }
    return WorkspaceConfig(
        workspace_id=str(workspace["id"]),
        name=str(workspace.get("name", workspace["id"])),
        mode=str(workspace.get("mode", "local_open_source_evaluation")),
        benchmark_profile=str(workspace.get("benchmark_profile", "generic_typed_decisions")),
        paths=paths,
        integrations={key: bool(value) for key, value in (raw.get("integrations") or {}).items()},
    )


def load_provider_config(path: str | Path) -> dict[str, ProviderConfig]:
    config_path, raw = _read_toml(path)
    root = config_path.parent.parent
    providers: dict[str, ProviderConfig] = {}
    for provider_id, values in (raw.get("providers") or {}).items():
        install_dir = Path(values.get("install_dir", "alternatives") or "alternatives")
        if not install_dir.is_absolute():
            install_dir = (root / install_dir).resolve()
        providers[provider_id] = ProviderConfig(
            provider_id=provider_id,
            kind=str(values.get("kind", "unknown")),
            enabled=bool(values.get("enabled", False)),
            install_dir=install_dir,
            base_url=str(values.get("base_url", "")),
            endpoint=str(values.get("endpoint", "")),
            model=str(values.get("model", "")),
            api_key_file=(
                Path(str(values["api_key_file"])).expanduser()
                if values.get("api_key_file")
                else None
            ),
            reference_only=bool(values.get("reference_only", False)),
            training_use=bool(values.get("training_use", True)),
        )
    return providers
