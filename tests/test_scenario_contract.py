from scripts.validate_repository import (
    SCENARIOS,
    validate_cchs_demo,
    validate_json_and_jsonl,
    validate_markdown_links,
    validate_no_hardcoded_guids,
    validate_required_paths,
    validate_scenarios,
    validate_workflows,
    validate_yaml,
)


def test_all_expected_scenarios_are_declared() -> None:
    assert len(SCENARIOS) == 12
    assert SCENARIOS[0] == "01-data-pipeline-generation"
    assert SCENARIOS[-1] == "12-cchs-power-bi-authoring"


def test_required_repository_paths_exist() -> None:
    assert validate_required_paths() == []


def test_scenario_contract() -> None:
    assert validate_scenarios() == []


def test_cchs_demo_contract() -> None:
    assert validate_cchs_demo() == []


def test_local_markdown_links() -> None:
    assert validate_markdown_links() == []


def test_json_and_jsonl_are_valid() -> None:
    assert validate_json_and_jsonl() == []


def test_yaml_is_valid() -> None:
    assert validate_yaml() == []


def test_workflows_are_hardened() -> None:
    assert validate_workflows() == []


def test_no_environment_specific_guids_are_committed() -> None:
    assert validate_no_hardcoded_guids() == []
