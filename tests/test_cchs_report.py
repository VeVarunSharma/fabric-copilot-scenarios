from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOT = (
    ROOT
    / "semantic-models"
    / "CCHSHealth"
    / "CCHSHealth.Report"
)
DEFINITION_ROOT = REPORT_ROOT / "definition"
PAGES_ROOT = DEFINITION_ROOT / "pages"

EXPECTED_PAGE_ORDER = [
    "BCOverview",
    "TrendDemographics",
    "DataQualityMethodology",
]
ATTRIBUTION = (
    "Adapted from Statistics Canada, Health characteristics, annual estimates, "
    "inactive, 2015 to 2022. This does not constitute an endorsement by "
    "Statistics Canada of this product."
)
HTML_CONTENT_LITE = "htmlContent443BE3AD55E043BF878BED274D3A6865"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _visuals(page_name: str) -> list[dict[str, Any]]:
    return [
        _read_json(path)
        for path in sorted((PAGES_ROOT / page_name / "visuals").glob("*/visual.json"))
    ]


def _query_refs(visual: dict[str, Any]) -> set[str]:
    refs: set[str] = set()

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            query_ref = value.get("queryRef")
            if isinstance(query_ref, str):
                refs.add(query_ref)
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(visual)
    return refs


def _literal_values(visual: dict[str, Any]) -> set[str]:
    values: set[str] = set()

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            literal = value.get("Literal")
            if isinstance(literal, dict) and isinstance(literal.get("Value"), str):
                values.add(literal["Value"])
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(visual)
    return values


def test_report_has_expected_page_order_theme_and_portable_resources() -> None:
    pages = _read_json(PAGES_ROOT / "pages.json")
    assert pages["pageOrder"] == EXPECTED_PAGE_ORDER
    assert pages["activePageName"] == "BCOverview"

    report = _read_json(DEFINITION_ROOT / "report.json")
    assert report["themeCollection"]["customTheme"]["name"] == "CCHSHealthTheme.json"
    package = next(
        package
        for package in report["resourcePackages"]
        if package["name"] == "RegisteredResources"
    )
    assert package["items"] == [
        {
            "name": "CCHSHealthTheme.json",
            "path": "CCHSHealthTheme.json",
            "type": "CustomTheme",
        }
    ]
    assert (
        REPORT_ROOT
        / "StaticResources"
        / "RegisteredResources"
        / "CCHSHealthTheme.json"
    ).is_file()


def test_pages_and_visual_containers_are_well_formed_and_accessible() -> None:
    for page_name in EXPECTED_PAGE_ORDER:
        page = _read_json(PAGES_ROOT / page_name / "page.json")
        assert page["name"] == page_name
        assert page["width"] == 1280
        assert page["height"] == 720

        visuals = _visuals(page_name)
        assert visuals
        assert len({visual["name"] for visual in visuals}) == len(visuals)
        assert len({visual["position"]["tabOrder"] for visual in visuals}) == len(visuals)

        for visual in visuals:
            position = visual["position"]
            assert position["x"] >= 0
            assert position["y"] >= 0
            assert position["x"] + position["width"] <= page["width"]
            assert position["y"] + position["height"] <= page["height"]

            visual_type = visual["visual"]["visualType"]
            assert visual_type
            alt_text = (
                visual["visual"]
                ["visualContainerObjects"]
                ["general"]
                [0]
                ["properties"]
                ["altText"]
                ["expr"]
                ["Literal"]
                ["Value"]
            )
            assert alt_text.strip("'")


def test_overview_has_defaults_custom_visual_and_native_fallback() -> None:
    visuals = {visual["name"]: visual for visual in _visuals("BCOverview")}
    types = {visual["visual"]["visualType"] for visual in visuals.values()}
    assert {"slicer", "card", "barChart", "textbox", HTML_CONTENT_LITE} <= types

    defaults = {
        "indicatorSlicer": "'Perceived Health'",
        "ageSlicer": "'Total, 12 years and over'",
        "sexSlicer": "'Both sexes'",
        "yearSlicer": "2022L",
        "characteristicSlicer": "'Percent Estimate'",
    }
    for visual_name, expected_value in defaults.items():
        assert expected_value in _literal_values(visuals[visual_name])

    html_visual = visuals["htmlSpotlight"]
    assert html_visual["visual"]["visualType"] == HTML_CONTENT_LITE
    assert "Health Observation.HTML Spotlight Card" in _query_refs(html_visual)
    assert "content" in html_visual["visual"]["query"]["queryState"]

    fallback = visuals["bcFallbackCard"]
    assert fallback["visual"]["visualType"] == "card"
    assert "Health Observation.Percent Estimate" in _query_refs(fallback)
    assert "'British Columbia'" in _literal_values(fallback)

    comparison = visuals["provinceComparison"]
    assert {
        "Geography.Geography Name",
        "Health Observation.Health Estimate",
    } <= _query_refs(comparison)
    assert "'Province'" in _literal_values(comparison)


def test_trend_page_has_comparison_demographics_status_and_redesign_warning() -> None:
    visuals = {visual["name"]: visual for visual in _visuals("TrendDemographics")}
    assert visuals["bcCanadaTrend"]["visual"]["visualType"] == "lineChart"
    assert {
        "Period.Reference Year",
        "Geography.Geography Name",
        "Health Observation.Percent Estimate",
    } <= _query_refs(visuals["bcCanadaTrend"])
    assert {
        "'British Columbia'",
        "'Canada (excluding territories)'",
    } <= _literal_values(visuals["bcCanadaTrend"])

    assert visuals["ageComparison"]["visual"]["visualType"] == "barChart"
    assert visuals["sexComparison"]["visual"]["visualType"] == "barChart"
    assert visuals["demographicDetail"]["visual"]["visualType"] == "tableEx"
    assert "Quality Status.Status Label" in _query_refs(
        visuals["demographicDetail"]
    )

    page_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (PAGES_ROOT / "TrendDemographics").rglob("*.json")
    )
    assert "2022 survey redesign" in page_text
    assert "comparability break" in page_text
    assert "No causal interpretation" in page_text


def test_methodology_page_contains_quality_logic_source_and_replacement_contract() -> None:
    visuals = {visual["name"]: visual for visual in _visuals("DataQualityMethodology")}
    assert {
        "Health Observation.Use With Caution Count",
        "Health Observation.Suppressed Observation Count",
        "Health Observation.Observation Count",
        "Health Observation.Latest Reference Year",
    } <= set().union(*(_query_refs(visual) for visual in visuals.values()))

    assert visuals["statusDistribution"]["visual"]["visualType"] == "barChart"
    assert visuals["statusDefinitions"]["visual"]["visualType"] == "tableEx"
    assert {
        "Quality Status.Source Status",
        "Quality Status.Status Label",
        "Quality Status.Status Description",
        "Health Observation.Observation Count",
    } <= _query_refs(visuals["statusDefinitions"])

    report_text = "\n".join(
        path.read_text(encoding="utf-8") for path in REPORT_ROOT.rglob("*.json")
    )
    assert ATTRIBUTION in report_text
    assert "Statistics Canada Open Licence" in report_text
    assert "No current 2023-2025 CCHS claims are made" in report_text
    assert "CCHS Data Root parameter" in report_text
    assert "does not imply BC Government endorsement" in report_text
    assert "F and x estimates stay blank and are never zero-filled" in report_text
