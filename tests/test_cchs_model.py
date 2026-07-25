from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL_ROOT = ROOT / "semantic-models" / "CCHSHealth"
DEFINITION_ROOT = MODEL_ROOT / "CCHSHealth.SemanticModel" / "definition"
TABLE_ROOT = DEFINITION_ROOT / "tables"

TABLE_FILES = {
    "Period": "periods.csv",
    "Geography": "geographies.csv",
    "Age Group": "age-groups.csv",
    "Sex": "sexes.csv",
    "Indicator": "indicators.csv",
    "Characteristic": "characteristics.csv",
    "Quality Status": "quality-statuses.csv",
    "Health Observation": "observations.csv",
}

EXPECTED_MEASURES = {
    "Health Estimate",
    "Percent Estimate",
    "Population Estimate",
    "British Columbia Estimate",
    "Canada Estimate",
    "BC vs Canada Difference",
    "Latest Reference Year",
    "British Columbia Province Rank",
    "Valid Province Count",
    "Use With Caution Count",
    "Suppressed Observation Count",
    "Observation Count",
    "Estimate Status Label",
    "HTML Spotlight Card",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_pbip_and_model_references_are_portable() -> None:
    pbip = json.loads(_read(MODEL_ROOT / "CCHSHealth.pbip"))
    assert pbip["artifacts"] == [{"report": {"path": "CCHSHealth.Report"}}]

    report_definition = json.loads(
        _read(MODEL_ROOT / "CCHSHealth.Report" / "definition.pbir")
    )
    assert report_definition["datasetReference"]["byPath"]["path"] == (
        "../CCHSHealth.SemanticModel"
    )

    model_text = _read(DEFINITION_ROOT / "model.tmdl")
    assert "expression 'CCHS Data Root'" in model_text
    assert "IsParameterQuery=true" in model_text
    assert "../../../datasets/public/cchs-annual/snapshot" in model_text

    all_project_text = "\n".join(
        _read(path)
        for path in MODEL_ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in {".tmdl", ".json", ".pbip", ".pbir"}
    )
    assert "/Users/" not in all_project_text
    assert not re.search(r"[A-Za-z]:\\", all_project_text)


def test_all_contract_tables_use_parameterized_import_partitions() -> None:
    assert {path.stem for path in TABLE_ROOT.glob("*.tmdl")} == set(TABLE_FILES)

    for table_name, csv_name in TABLE_FILES.items():
        text = _read(TABLE_ROOT / f"{table_name}.tmdl")
        assert f"table '{table_name}'" in text or f"table {table_name}" in text
        assert "mode: import" in text
        assert 'Text.TrimEnd(#"CCHS Data Root"' in text
        assert f'File.Contents(DataRoot & "/{csv_name}")' in text
        assert "Table.PromoteHeaders" in text
        assert "Table.TransformColumnTypes" in text
        assert "description:" in text


def test_model_has_seven_single_direction_star_relationships() -> None:
    text = _read(DEFINITION_ROOT / "relationships.tmdl")
    relationships = re.findall(r"^relationship (.+)$", text, flags=re.MULTILINE)
    assert len(relationships) == 7
    assert text.count("fromColumn: 'Health Observation'.") == 7
    assert text.count("toColumn:") == 7
    assert "bothDirections" not in text
    assert "manyToMany" not in text


def test_fact_keys_and_estimate_are_hidden_behind_explicit_measures() -> None:
    text = _read(TABLE_ROOT / "Health Observation.tmdl")
    for column_name in [
        "Period Key",
        "Geography Key",
        "Age Group Key",
        "Sex Key",
        "Indicator Key",
        "Characteristic Key",
        "Quality Status Key",
        "Estimate",
    ]:
        column_block = text.split(f"column '{column_name}'", maxsplit=1)[-1]
        if column_name == "Estimate":
            column_block = text.split("column Estimate", maxsplit=1)[-1]
        column_block = column_block.split("\n\tcolumn ", maxsplit=1)[0]
        column_block = column_block.split("\n\tmeasure ", maxsplit=1)[0]
        assert "isHidden" in column_block
        assert "summarizeBy: none" in column_block

    measures = set(re.findall(r"^\tmeasure '([^']+)' =", text, flags=re.MULTILINE))
    assert measures == EXPECTED_MEASURES
    assert "discourageImplicitMeasures" in _read(DEFINITION_ROOT / "model.tmdl")


def test_measures_guard_context_quality_and_percent_formatting() -> None:
    text = _read(TABLE_ROOT / "Health Observation.tmdl")
    assert "IF(ObservationCount = 1, PublishedValue)" in text
    assert 'REMOVEFILTERS(\'Characteristic\')' in text
    assert '"Percent Estimate"' in text
    assert r"formatString: 0.0\%;-0.0\%;0.0\%" in text
    assert "'Geography'[Is British Columbia] = TRUE()" in text
    assert "'Geography'[Is Canada Comparator] = TRUE()" in text
    assert "'Quality Status'[Is Caution] = TRUE()" in text
    assert "'Quality Status'[Is Suppressed] = TRUE()" in text
    assert "ObservationCount > 1, \"Multiple observations\"" in text

    html_measure = text.split("measure 'HTML Spotlight Card' =", maxsplit=1)[1]
    assert "<script" not in html_measure.lower()
    assert "<iframe" not in html_measure.lower()
    assert "http://" not in html_measure.lower()
    assert "https://" not in html_measure.lower()
    assert "2022 redesign limits comparison" in html_measure


def test_model_copilot_metadata_and_validation_queries_are_complete() -> None:
    copilot_root = MODEL_ROOT / "CCHSHealth.SemanticModel" / "Copilot"
    schema = json.loads(_read(copilot_root / "schema.json"))
    assert {table["name"] for table in schema["tables"]} == set(TABLE_FILES)

    health_table = next(
        table for table in schema["tables"] if table["name"] == "Health Observation"
    )
    assert {measure["name"] for measure in health_table["measures"]} == EXPECTED_MEASURES
    assert all(measure["synonyms"] for measure in health_table["measures"])

    prompts = json.loads(_read(copilot_root / "examplePrompts.json"))
    assert len(prompts["prompts"]) >= 4
    assert any("Canada excluding territories" in prompt for prompt in prompts["prompts"])

    dax = _read(MODEL_ROOT / "validation" / "model-validation.dax")
    assert len(re.findall(r"^EVALUATE$", dax, flags=re.MULTILINE)) == 5
    assert "Health Observation Rows" in dax
    assert "Difference Percentage Points" in dax
    assert "British Columbia Province Rank" in dax
    assert "Nonblank Estimate Count" in dax
    assert "Health Estimate Is Blank" in dax
