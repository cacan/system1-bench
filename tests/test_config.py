import os
from pathlib import Path

from jev_local_experiments.baseline import resolve_api_key
from jev_local_experiments.config import load_provider_config, load_workspace_config

ROOT = Path(__file__).parents[1]


def test_load_workspace_config_resolves_paths_from_workspace_root():
    config = load_workspace_config(ROOT / "config" / "workspace.toml")

    assert config.workspace_id == "system1-alternatives-benchmark"
    assert config.paths["alternatives"] == (ROOT / "alternatives").resolve()
    assert config.integrations["gtm"] is False


def test_load_provider_config_keeps_alternative_install_boundary():
    providers = load_provider_config(ROOT / "config" / "providers.toml")

    assert providers["kev"].install_dir == (ROOT / "alternatives" / "kev").resolve()
    assert providers["kev"].enabled is False


def test_load_provider_config_exposes_reference_only_jev_baseline():
    providers = load_provider_config(ROOT / "config" / "providers.toml")

    jev = providers["jev_reference"]
    assert jev.enabled is True
    assert jev.model == "jev-latest"
    assert jev.api_key_file == Path("~/.codex/secrets/jev").expanduser()
    assert jev.reference_only is True


def test_resolve_api_key_reads_from_environment(monkeypatch):
    monkeypatch.setenv("JEV_API_KEY", "env_secret_key_123")
    assert resolve_api_key() == "env_secret_key_123"


def test_resolve_api_key_reads_from_env_file_path(tmp_path, monkeypatch):
    key_file = tmp_path / "custom_jev.key"
    key_file.write_text("file_key_456\n", encoding="utf-8")
    monkeypatch.delenv("JEV_API_KEY", raising=False)
    monkeypatch.setenv("JEV_API_KEY_FILE", str(key_file))

    assert resolve_api_key() == "file_key_456"
