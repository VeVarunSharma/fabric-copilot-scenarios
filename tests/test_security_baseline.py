from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SECRET_PATTERNS = {
    "GitHub classic token": re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    "GitHub fine-grained token": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "Bearer token": re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{24,}\b"),
}

TEXT_SUFFIXES = {
    ".dax",
    ".ipynb",
    ".json",
    ".jsonl",
    ".md",
    ".patch",
    ".py",
    ".sql",
    ".tmdl",
    ".txt",
    ".yaml",
    ".yml",
}


def repository_text_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and ".venv" not in path.parts
        and path.suffix.lower() in TEXT_SUFFIXES
    ]


def test_repository_contains_no_high_confidence_secrets() -> None:
    findings: list[str] = []
    for path in repository_text_files():
        content = path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(content):
                findings.append(f"{label}: {path.relative_to(ROOT)}")
    assert findings == []


def test_notebooks_are_in_secret_scan_scope() -> None:
    assert any(path.suffix.lower() == ".ipynb" for path in repository_text_files())


def test_codeql_demo_patch_applies_to_safe_baseline() -> None:
    patch_path = (
        ROOT
        / "scenarios/11-github-advanced-security/demo-patches/codeql-demo.patch"
    )
    result = subprocess.run(
        ["git", "apply", "--check", str(patch_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_local_fabric_config_is_ignored() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "scripts/fabric/config.json" in gitignore


def test_no_environment_files_are_committed() -> None:
    committed_env_files = [
        path.relative_to(ROOT)
        for path in ROOT.rglob(".env*")
        if path.is_file() and ".git" not in path.parts
    ]
    assert committed_env_files == []
