#!/usr/bin/env python3
"""Validate the repository's scenario contract and source-controlled artifacts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

try:
    import yaml
except ImportError:  # pragma: no cover - CI and the dev extra install PyYAML.
    yaml = None

ROOT = Path(__file__).resolve().parents[1]

SCENARIOS = [
    "01-data-pipeline-generation",
    "02-sql-optimization",
    "03-pyspark-notebook-generation",
    "04-data-quality-validation",
    "05-semantic-model-analysis",
    "06-dax-generation",
    "07-documentation-generation",
    "08-data-lineage-investigation",
    "09-copilot-coding-agent",
    "10-fabric-devops",
    "11-github-advanced-security",
    "12-cchs-power-bi-authoring",
]

SCENARIO_FILES = [
    "README.md",
    "sample-prompt.md",
    "expected-output.md",
    "extension-exercises.md",
]

SCENARIO_HEADINGS = [
    "Business problem",
    "Learning objectives",
    "What work did Copilot eliminate?",
]

REQUIRED_PATHS = [
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "SUPPORT.md",
    "datasets",
    "notebooks",
    "semantic-models",
    "pipelines",
    "docs",
    "prompts",
    ".github/copilot-instructions.md",
    ".github/workflows",
]

UUID_PATTERN = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-"
    r"[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b"
)
PUBLIC_CATALOGUE_UUIDS = {
    "36610a52-6f90-4ed6-946d-587641a490df",
    "86839277-986a-4a29-9f70-fa9b1166f6cb",
}

MARKDOWN_LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
ACTION_PIN_PATTERN = re.compile(
    r"^\s*uses:\s+([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+"
    r"(?:/[A-Za-z0-9_.-]+)*)@([0-9a-f]{40})"
    r"(?:\s+#\s+.+)?\s*$"
)
SECRET_PATTERNS = {
    "GitHub classic token": re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    "GitHub fine-grained token": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "Bearer token": re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{24,}\b"),
}


def validate_required_paths() -> list[str]:
    errors = []
    for relative_path in REQUIRED_PATHS:
        if not (ROOT / relative_path).exists():
            errors.append(f"Missing required path: {relative_path}")
    return errors


def validate_scenarios() -> list[str]:
    errors = []
    scenarios_root = ROOT / "scenarios"
    for scenario in SCENARIOS:
        scenario_dir = scenarios_root / scenario
        if not scenario_dir.is_dir():
            errors.append(f"Missing scenario directory: scenarios/{scenario}")
            continue

        for filename in SCENARIO_FILES:
            if not (scenario_dir / filename).is_file():
                errors.append(f"Missing scenario file: scenarios/{scenario}/{filename}")

        readme = scenario_dir / "README.md"
        if not readme.is_file():
            continue

        content = readme.read_text(encoding="utf-8")
        for heading in SCENARIO_HEADINGS:
            heading_pattern = re.compile(
                rf"^#+\s+{re.escape(heading)}\s*$", re.IGNORECASE | re.MULTILINE
            )
            if not heading_pattern.search(content):
                errors.append(
                    f"Scenario heading missing in scenarios/{scenario}/README.md: "
                    f"{heading}"
                )
    return errors


def validate_notebooks() -> list[str]:
    errors = []
    notebooks_root = ROOT / "notebooks"
    if not notebooks_root.exists():
        return ["Missing notebooks directory"]

    notebooks = sorted(notebooks_root.rglob("*.ipynb"))
    if not notebooks:
        return ["No Fabric notebooks found under notebooks/"]

    for notebook_path in notebooks:
        relative_path = notebook_path.relative_to(ROOT)
        try:
            notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid notebook JSON {relative_path}: {exc}")
            continue

        if notebook.get("nbformat") != 4:
            errors.append(f"Notebook must use nbformat 4: {relative_path}")

        if not isinstance(notebook.get("metadata"), dict):
            errors.append(f"Notebook metadata must be an object: {relative_path}")

        for index, cell in enumerate(notebook.get("cells", [])):
            if not isinstance(cell.get("metadata"), dict):
                errors.append(f"{relative_path} cell {index} is missing metadata")
            if cell.get("cell_type") == "code":
                if "outputs" not in cell or not isinstance(cell["outputs"], list):
                    errors.append(f"{relative_path} code cell {index} needs outputs []")
                if "execution_count" not in cell:
                    errors.append(
                        f"{relative_path} code cell {index} needs execution_count"
                    )

        text = notebook_path.read_text(encoding="utf-8")
        if UUID_PATTERN.search(text):
            errors.append(f"Notebook contains a hardcoded GUID: {relative_path}")
    return errors


def validate_pipelines() -> list[str]:
    errors = []
    expected = [
        ROOT / "pipelines/retail-medallion.DataPipeline",
        ROOT / "pipelines/healthcare-quality.DataPipeline",
    ]
    for pipeline_dir in expected:
        for filename in (".platform", "pipeline-content.json"):
            path = pipeline_dir / filename
            if not path.is_file():
                errors.append(f"Missing pipeline definition part: {path.relative_to(ROOT)}")
                continue
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"Invalid JSON {path.relative_to(ROOT)}: {exc}")
    return errors


def validate_semantic_model() -> list[str]:
    errors = []
    base = ROOT / "semantic-models/RetailSales"
    required = [
        base / "RetailSales.pbip",
        base / "RetailSales.SemanticModel/definition.pbism",
        base / "RetailSales.SemanticModel/definition/database.tmdl",
        base / "RetailSales.SemanticModel/definition/model.tmdl",
        base / "RetailSales.SemanticModel/definition/relationships.tmdl",
        base / "RetailSales.Report/definition.pbir",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"Missing semantic model file: {path.relative_to(ROOT)}")

    table_root = base / "RetailSales.SemanticModel/definition/tables"
    for table_name in ("Date", "Customer", "Product", "Sales"):
        if not (table_root / f"{table_name}.tmdl").is_file():
            errors.append(f"Missing semantic model table: {table_name}.tmdl")

    sales_path = table_root / "Sales.tmdl"
    if sales_path.is_file():
        sales_content = sales_path.read_text(encoding="utf-8")
        required_measures = (
            "Total Revenue",
            "Total Cost",
            "Gross Margin",
            "Gross Margin %",
            "Order Count",
            "Average Order Value",
            "Revenue YTD",
            "Revenue Previous Year",
            "Revenue YoY %",
        )
        for measure in required_measures:
            if f"measure '{measure}'" not in sales_content:
                errors.append(f"Sales.tmdl is missing measure: {measure}")
    return errors


def validate_cchs_demo() -> list[str]:
    errors = []
    model_root = ROOT / "semantic-models/CCHSHealth"
    report_root = model_root / "CCHSHealth.Report"
    snapshot_root = ROOT / "datasets/public/cchs-annual/snapshot"
    scenario_root = ROOT / "scenarios/12-cchs-power-bi-authoring"

    required = [
        ROOT / "datasets/public/cchs-annual/README.md",
        ROOT / "datasets/public/cchs-annual/selection.json",
        snapshot_root / "manifest.json",
        model_root / "CCHSHealth.pbip",
        model_root / "CCHSHealth.SemanticModel/definition/model.tmdl",
        model_root / "CCHSHealth.SemanticModel/definition/relationships.tmdl",
        report_root / "definition.pbir",
        report_root / "definition/report.json",
        report_root / "definition/pages/pages.json",
        report_root
        / "StaticResources/RegisteredResources/CCHSHealthTheme.json",
        scenario_root / "artifacts/model-authoring-prompt.md",
        scenario_root / "artifacts/report-design-brief.md",
        scenario_root / "artifacts/model-validation.dax",
        scenario_root / "artifacts/live-demo-checklist.md",
        ROOT / "docs/demo-runbooks/bc-cchs-power-bi.md",
        ROOT / "prompts/scenarios/12-cchs-power-bi-authoring.md",
        ROOT / ".github/prompts/cchs-power-bi-authoring.prompt.md",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"Missing CCHS demo file: {path.relative_to(ROOT)}")

    manifest_path = snapshot_root / "manifest.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid CCHS manifest JSON: {exc}")
        else:
            expected_rows = {
                "observations.csv": 76032,
                "periods.csv": 8,
                "geographies.csv": 11,
                "indicators.csv": 8,
                "characteristics.csv": 6,
                "quality-statuses.csv": 5,
            }
            for filename, expected_count in expected_rows.items():
                actual_count = manifest.get("files", {}).get(filename, {}).get("rows")
                if actual_count != expected_count:
                    errors.append(
                        f"CCHS manifest row count for {filename} is "
                        f"{actual_count!r}; expected {expected_count}"
                    )
            if manifest.get("source", {}).get("archived") is not True:
                errors.append("CCHS manifest must mark the source as archived")
            if manifest.get("source", {}).get("referenceYears") != list(
                range(2015, 2023)
            ):
                errors.append("CCHS manifest must cover reference years 2015-2022")
            required_attribution = (
                "Adapted from Statistics Canada, Health characteristics, annual "
                "estimates, inactive, 2015 to 2022. This does not constitute an "
                "endorsement by Statistics Canada of this product."
            )
            if manifest.get("attribution") != required_attribution:
                errors.append("CCHS manifest attribution does not match the approved text")

    pages_path = report_root / "definition/pages/pages.json"
    if pages_path.is_file():
        try:
            pages = json.loads(pages_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid CCHS pages metadata JSON: {exc}")
        else:
            expected_pages = [
                "BCOverview",
                "TrendDemographics",
                "DataQualityMethodology",
            ]
            if pages.get("pageOrder") != expected_pages:
                errors.append("CCHS report page order does not match the approved design")
            if pages.get("activePageName") != "BCOverview":
                errors.append("CCHS report must open on BCOverview")
            for page_name in expected_pages:
                if not (report_root / f"definition/pages/{page_name}/page.json").is_file():
                    errors.append(f"CCHS report page is missing: {page_name}")

    if report_root.exists():
        report_text = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in report_root.rglob("*.json")
        )
        for required_text in (
            "htmlContent443BE3AD55E043BF878BED274D3A6865",
            "bcFallbackCard",
            "2022 survey redesign",
            "This does not constitute an endorsement by Statistics Canada",
            "does not imply BC Government endorsement",
        ):
            if required_text not in report_text:
                errors.append(f"CCHS report is missing required content: {required_text}")
        if list(report_root.rglob("*.pbiviz")):
            errors.append("CCHS report must not vendor a third-party .pbiviz binary")

    model_definition = model_root / "CCHSHealth.SemanticModel/definition"
    if model_definition.exists():
        model_text = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in model_definition.rglob("*.tmdl")
        )
        if "CCHS Data Root" not in model_text:
            errors.append("CCHS semantic model is missing the CCHS Data Root parameter")
        if "/Users/" in model_text or re.search(r"[A-Za-z]:\\", model_text):
            errors.append("CCHS semantic model contains a developer-specific absolute path")

    canonical_dax = model_root / "validation/model-validation.dax"
    scenario_dax = scenario_root / "artifacts/model-validation.dax"
    if canonical_dax.is_file() and scenario_dax.is_file():
        if canonical_dax.read_text(encoding="utf-8") != scenario_dax.read_text(
            encoding="utf-8"
        ):
            errors.append("Scenario CCHS DAX validation copy has drifted from canonical")

    return errors


def validate_json_and_jsonl() -> list[str]:
    errors = []
    for path in sorted(ROOT.rglob("*.json")):
        if ".git" in path.parts:
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON {path.relative_to(ROOT)}: {exc}")

    for path in sorted(ROOT.rglob("*.jsonl")):
        if ".git" in path.parts:
            continue
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line.strip():
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(
                    f"Invalid JSONL {path.relative_to(ROOT)} line {line_number}: {exc}"
                )
    return errors


def validate_yaml() -> list[str]:
    if yaml is None:
        return ["PyYAML is required to validate repository YAML"]

    errors = []
    for pattern in ("*.yml", "*.yaml"):
        for path in sorted(ROOT.rglob(pattern)):
            if ".git" in path.parts:
                continue
            try:
                yaml.safe_load(path.read_text(encoding="utf-8"))
            except yaml.YAMLError as exc:
                errors.append(f"Invalid YAML {path.relative_to(ROOT)}: {exc}")
    return errors


def validate_workflows() -> list[str]:
    errors = []
    workflows_root = ROOT / ".github/workflows"
    workflows = sorted(workflows_root.glob("*.yml")) + sorted(
        workflows_root.glob("*.yaml")
    )
    if not workflows:
        return ["No GitHub Actions workflows found"]

    for path in workflows:
        relative_path = path.relative_to(ROOT)
        content = path.read_text(encoding="utf-8")
        if "pull_request_target:" in content:
            errors.append(f"Unsafe pull_request_target trigger in {relative_path}")
        if not re.search(r"^permissions:\s*$", content, re.MULTILINE):
            errors.append(f"Workflow lacks top-level permissions: {relative_path}")
        for line_number, line in enumerate(content.splitlines(), start=1):
            if "uses:" not in line:
                continue
            stripped = line.strip()
            if stripped.startswith("uses: ./") or stripped.startswith("uses: docker://"):
                continue
            if not ACTION_PIN_PATTERN.match(line):
                errors.append(
                    f"Workflow action is not pinned to a full SHA in "
                    f"{relative_path}:{line_number}"
                )

    setup_path = workflows_root / "copilot-setup-steps.yml"
    if setup_path.is_file() and yaml is not None:
        setup = yaml.safe_load(setup_path.read_text(encoding="utf-8"))
        jobs = setup.get("jobs", {}) if isinstance(setup, dict) else {}
        if list(jobs) != ["copilot-setup-steps"]:
            errors.append(
                "copilot-setup-steps.yml must contain only the "
                "copilot-setup-steps job"
            )
    return errors


def validate_secret_safety() -> list[str]:
    errors = []
    text_suffixes = {
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
    for path in ROOT.rglob("*"):
        if (
            not path.is_file()
            or ".git" in path.parts
            or ".venv" in path.parts
            or path.suffix.lower() not in text_suffixes
        ):
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(content):
                errors.append(f"{label} detected in {path.relative_to(ROOT)}")
    return errors


def validate_markdown_links() -> list[str]:
    errors = []
    for markdown_path in sorted(ROOT.rglob("*.md")):
        if ".git" in markdown_path.parts:
            continue
        content = markdown_path.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK_PATTERN.findall(content):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if (
                not target
                or target.startswith(("#", "http://", "https://", "mailto:"))
                or "${" in target
            ):
                continue
            target_path = target.split("#", 1)[0].split("?", 1)[0]
            if not target_path:
                continue
            resolved = (markdown_path.parent / unquote(target_path)).resolve()
            if not resolved.exists():
                errors.append(
                    f"Broken local link in {markdown_path.relative_to(ROOT)}: {target}"
                )
    return errors


def validate_no_hardcoded_guids() -> list[str]:
    errors = []
    scan_suffixes = {
        ".ipynb",
        ".json",
        ".py",
        ".sql",
        ".tmdl",
        ".yaml",
        ".yml",
    }
    for path in ROOT.rglob("*"):
        if (
            not path.is_file()
            or ".git" in path.parts
            or path.suffix.lower() not in scan_suffixes
        ):
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        unexpected_guids = {
            match.group(0).lower()
            for match in UUID_PATTERN.finditer(content)
            if match.group(0).lower() not in PUBLIC_CATALOGUE_UUIDS
        }
        if unexpected_guids:
            errors.append(f"Hardcoded GUID found in {path.relative_to(ROOT)}")
    return errors


def run_validation() -> list[str]:
    checks = [
        validate_required_paths,
        validate_scenarios,
        validate_notebooks,
        validate_pipelines,
        validate_semantic_model,
        validate_cchs_demo,
        validate_json_and_jsonl,
        validate_yaml,
        validate_workflows,
        validate_secret_safety,
        validate_markdown_links,
        validate_no_hardcoded_guids,
    ]
    errors: list[str] = []
    for check in checks:
        errors.extend(check())
    return errors


def main() -> int:
    errors = run_validation()
    if errors:
        print("Repository validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Repository validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
