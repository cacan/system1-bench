"""Client for executing benchmark suites against System One HTTP providers (Hearim, Kev, etc.)."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Iterable

from .baseline import build_systemone_request
from .config import ProviderConfig
from .schema import BenchmarkCase


class ProviderClientError(RuntimeError):
    """Raised when a provider request fails."""


class SystemOneHttpClient:
    """Client for any provider exposing TypeSafe-compatible /v1/systemone."""

    def __init__(
        self,
        *,
        base_url: str,
        endpoint: str,
        model: str,
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        self.model = model
        self.api_key = api_key or "local-dev-key"
        self.timeout = timeout

    @classmethod
    def from_provider_config(cls, provider: ProviderConfig, *, timeout: float = 30.0) -> "SystemOneHttpClient":
        if not provider.enabled:
            raise ProviderClientError(f"Provider {provider.model} is disabled in config")
        return cls(
            base_url=provider.base_url,
            endpoint=provider.endpoint,
            model=provider.model,
            timeout=timeout,
        )

    def evaluate(self, case: BenchmarkCase) -> dict[str, Any]:
        body = json.dumps(build_systemone_request(case, model=self.model)).encode("utf-8")
        req = urllib.request.Request(
            self.url,
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
                status = resp.status
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:400]
            raise ProviderClientError(f"Provider returned HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise ProviderClientError(f"Provider request failed: {exc}") from exc

        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ProviderClientError("Provider returned a non-JSON response") from exc

        return {
            "case_id": case.case_id,
            "provider": "hearim",
            "model": parsed.get("model", self.model) if isinstance(parsed, dict) else self.model,
            "status_code": status,
            "latency_ms": elapsed_ms,
            "response": parsed,
        }


def run_provider_benchmark(
    cases: Iterable[BenchmarkCase],
    client: SystemOneHttpClient,
    output_path: str | Path,
    provider_name: str = "hearim",
) -> list[dict[str, Any]]:
    """Execute cases sequentially against provider and stream results to JSONL."""
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []

    with out_file.open("w", encoding="utf-8") as handle:
        for case in cases:
            res = client.evaluate(case)
            res["provider"] = provider_name
            rows.append(res)
            handle.write(json.dumps(res, ensure_ascii=False) + "\n")
            handle.flush()
    return rows
