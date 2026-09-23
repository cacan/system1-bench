# Local alternatives

Install or clone one candidate per child directory. Do not vendor third-party source or model weights into the main repository.

Recommended workflow:

1. Select a candidate from `manifest.toml`.
2. Create its declared `install_dir` under this folder.
3. Follow the upstream README using an isolated environment/container.
4. Record the exact commit, model revision, serving command, and endpoint in the manifest and in the run metadata.
5. Run the shared smoke suite before larger benchmarks.

The parent repository ignores child directories by default so model caches, virtual environments, and upstream checkouts remain local. See [`docs/SOP-POLICIES.md`](../docs/SOP-POLICIES.md) for full installation boundary policies and onboarding procedures.
