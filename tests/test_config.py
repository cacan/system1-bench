from pathlib import Path

from jev_local_experiments.config import load_provider_config, load_workspace_config


ROOT = Path(__file__).parents[1]


def test_load_workspace_config_resolves_paths_from_workspace_root():
    config = load_workspace_config(ROOT / "config" / "workspace.toml")

    assert config.workspace_id == "jev-local-experiments"
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
    assert jev.api_key_file == Path(r"C:\Users\cacan\.codex\secrets\jev")
    assert jev.reference_only is True
