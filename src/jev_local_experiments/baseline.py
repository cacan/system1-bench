"""Reference-only client for the hosted Jev System One API."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Iterable

from .config import ProviderConfig
from .schema import BenchmarkCase


class BaselineError(RuntimeError):
    """Raised when the Jev reference baseline cannot be executed safely."""


def load_api_key(path: str | Path) -> str:
    """Read a runtime API key without ever returning it from CLI output."""

    key_path = Path(path).expanduser()
    if not key_path.is_file():
        raise BaselineError(f"Jev API key file does not exist: {key_path}")
    key = key_path.read_text(encoding="utf-8").strip()
    if not key:
        raise BaselineError(f"Jev API key file is empty: {key_path}")
    return key


def build_systemone_request(case: BenchmarkCase, *, model: str) -> dict[str, Any]:
    """Convert a validated fixture into the TypeSafe `/v1/systemone` request shape."""

    questions: dict[str, dict[str, Any]] = {}
    for question_id, question in case.questions.items():
        payload: dict[str, Any] = {
            "type": question.kind,
            "instructions": question.instructions,
        }
        if question.criteria is not None:
            if isinstance(question.criteria, tuple):
                payload["criteria"] = list(question.criteria)
            else:
                payload["criteria"] = dict(question.criteria)
        questions[question_id] = payload
    return {"model": model, "state": case.state, "questions": questions}


class JevReferenceClient:
    """Small stdlib-only client for evaluation-only Jev calls."""

    def __init__(
        self,
        *,
        base_url: str,
        endpoint: str,
        model: str,
        api_key_file: str | Path,
        timeout: float = 60.0,
    ) -> None:
        self.url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        self.model = model
        self.api_key_file = Path(api_key_file)
        self.timeout = timeout

    @classmethod
    def from_provider_config(cls, provider: ProviderConfig, *, timeout: float = 60.0) -> "JevReferenceClient":
        if not provider.api_key_file:
            raise BaselineError("jev_reference.api_key_file is required")
        if not provider.reference_only or provider.training_use:
            raise BaselineError("jev_reference must be reference_only=true and training_use=false")
        return cls(
            base_url=provider.base_url,
            endpoint=provider.endpoint,
            model=provider.model,
            api_key_file=provider.api_key_file,
            timeout=timeout,
        )

    def evaluate(self, case: BenchmarkCase) -> dict[str, Any]:
        request_body = json.dumps(build_systemone_request(case, model=self.model)).encode("utf-8")
        request = urllib.request.Request(
            self.url,
            data=request_body,
            headers={
                "Authorization": f"Bearer {load_api_key(self.api_key_file)}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw_response = response.read().decode("utf-8")
                status = response.status
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise BaselineError(f"Jev API returned HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise BaselineError(f"Jev API request failed: {exc}") from exc
        elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise BaselineError("Jev API returned a non-JSON response") from exc
        return {
            "provider": "jev_reference",
            "status_code": status,
            "case_id": case.case_id,
            "model": parsed.get("model", self.model) if isinstance(parsed, dict) else self.model,
            "latency_ms": elapsed_ms,
            "response": parsed,
        }


def run_jev_baseline(
    cases: Iterable[BenchmarkCase],
    client: JevReferenceClient,
    output_path: str | Path,
) -> list[dict[str, Any]]:
    """Evaluate cases and write only non-secret request results to JSONL."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    with output.open("w", encoding="utf-8") as handle:
        for case in cases:
            row = client.evaluate(case)
            rows.append(row)
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return rows
