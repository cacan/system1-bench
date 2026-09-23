"""Audit script to verify that no credentials, private paths, or secrets are present in tracked files."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# Patterns that indicate leaks of sensitive or machine-local data
SUSPICIOUS_PATTERNS = [
    (re.compile(r"cacan", re.IGNORECASE), "Personal username / machine path ('cacan')"),
    (re.compile(r"192\.168\.\d+\.\d+"), "Private LAN IP address (192.168.x.x)"),
    (re.compile(r"stellar-insights\.com", re.IGNORECASE), "Private domain / email address ('stellar-insights.com')"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "Private key header"),
    (re.compile(r"(?:api_key|client_secret)\s*=\s*['\"][a-zA-Z0-9_\-]{16,}['\"]", re.IGNORECASE), "Hardcoded API key or secret token"),
    (re.compile(r"C:[\\/]Users[\\/][a-zA-Z0-9_\-]+[\\/]", re.IGNORECASE), "Windows user home directory path"),
]

# Files or extensions allowed to contain specific patterns if any (e.g. this checker script itself)
WHITELISTED_FILES = {
    Path("scripts/check_secrets.py"),
}

FORBIDDEN_EXTENSIONS = {".key", ".pem", ".p12", ".secret", ".env"}


def get_candidate_files() -> list[Path]:
    """Retrieve list of files tracked by git plus untracked unignored files."""
    try:
        output_tracked = subprocess.check_output(["git", "ls-files"], text=True, encoding="utf-8")
        output_untracked = subprocess.check_output(
            ["git", "ls-files", "-o", "--exclude-standard"], text=True, encoding="utf-8"
        )
        all_lines = set(output_tracked.splitlines() + output_untracked.splitlines())
        return sorted([Path(line.strip()) for line in all_lines if line.strip()])
    except Exception as exc:
        print(f"Error checking git files: {exc}", file=sys.stderr)
        return []


def audit_file(path: Path) -> list[str]:
    """Check a single file for suspicious patterns."""
    issues = []
    if path.suffix in FORBIDDEN_EXTENSIONS:
        issues.append(f"Forbidden sensitive file extension: {path.suffix}")

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [f"Unable to read file: {exc}"]

    lines = content.splitlines()
    for line_idx, line in enumerate(lines, start=1):
        for pattern, description in SUSPICIOUS_PATTERNS:
            if pattern.search(line):
                issues.append(f"Line {line_idx}: {description} -> {line.strip()[:80]}")
    return issues


def main() -> int:
    candidate_files = get_candidate_files()
    if not candidate_files:
        print("No candidate files found or not a git repository.")
        return 0

    print(f"Auditing {len(candidate_files)} files for credentials, private IPs, and personal paths...")
    violations: dict[str, list[str]] = {}

    for file_path in candidate_files:
        # Normalize relative path
        norm_path = Path(file_path.as_posix())
        if norm_path in WHITELISTED_FILES:
            continue

        if not norm_path.is_file():
            continue

        file_issues = audit_file(norm_path)
        if file_issues:
            violations[str(norm_path)] = file_issues

    if violations:
        print("\n\033[91m[SECURITY AUDIT FAILED]\033[0m Potential sensitive data detected in tracked files:\n")
        for fpath, issues in violations.items():
            print(f"  \033[1m{fpath}\033[0m:")
            for issue in issues:
                print(f"    - {issue}")
        print("\nPlease remove or sanitize these entries before publishing.")
        return 1

    print("\033[92m[SECURITY AUDIT PASSED]\033[0m No secrets, personal usernames, or private IPs found in tracked files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
