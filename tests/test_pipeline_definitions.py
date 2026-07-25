import ast
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GUID_RE = re.compile(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b')
REQUIRED_MEASURES = [
    'Total Revenue',
    'Total Cost',
    'Gross Margin',
    'Gross Margin %',
    'Order Count',
    'Average Order Value',
    'Revenue YTD',
    'Revenue Previous Year',
    'Revenue YoY %',
]
NOTEBOOK_GOLD = REPO_ROOT / 'notebooks/retail-medallion/03_gold_aggregations.ipynb'
LIST_ASSIGNMENT_RE = r"{name}\s*=\s*(\[[^\]]*\])"
SOURCE_COLUMN_RE = re.compile(r'sourceColumn:\s*([a-zA-Z_][a-zA-Z0-9_]*)')


def load_json(path: Path):
    with path.open('r', encoding='utf-8') as handle:
        return json.load(handle)


def parse_list_assignment(text: str, variable_name: str):
    match = re.search(LIST_ASSIGNMENT_RE.format(name=re.escape(variable_name)), text, re.S)
    assert match, f'Missing assignment for {variable_name}'
    return ast.literal_eval(match.group(1))


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def notebook_code_text(path: Path) -> str:
    payload = load_json(path)
    return ''.join(''.join(cell.get('source', [])) for cell in payload['cells'])


def extract_source_columns(table_path: Path):
    return SOURCE_COLUMN_RE.findall(read_text(table_path))


def test_pipeline_files_exist_and_are_valid_json():
    pipeline_files = [
        REPO_ROOT / 'pipelines/retail-medallion.DataPipeline/pipeline-content.json',
        REPO_ROOT / 'pipelines/retail-medallion.DataPipeline/.platform',
        REPO_ROOT / 'pipelines/healthcare-quality.DataPipeline/pipeline-content.json',
        REPO_ROOT / 'pipelines/healthcare-quality.DataPipeline/.platform',
    ]
    for path in pipeline_files:
        assert path.exists(), f'Missing pipeline file: {path}'
        load_json(path)


def test_pipeline_platform_metadata_matches_expected_display_names():
    retail_platform = load_json(REPO_ROOT / 'pipelines/retail-medallion.DataPipeline/.platform')
    healthcare_platform = load_json(REPO_ROOT / 'pipelines/healthcare-quality.DataPipeline/.platform')

    assert retail_platform['metadata']['type'] == 'DataPipeline'
    assert retail_platform['metadata']['displayName'] == 'Retail Medallion Pipeline'
    assert retail_platform['metadata']['description'] == 'Retail purchases medallion Fabric pipeline source definition.'

    assert healthcare_platform['metadata']['type'] == 'DataPipeline'
    assert healthcare_platform['metadata']['displayName'] == 'Healthcare Quality Pipeline'
    assert healthcare_platform['metadata']['description'] == 'Healthcare claims quality Fabric pipeline source definition.'


def test_retail_pipeline_has_expected_dependencies_and_failure_handlers():
    payload = load_json(REPO_ROOT / 'pipelines/retail-medallion.DataPipeline/pipeline-content.json')
    activities = {activity['name']: activity for activity in payload['properties']['activities']}
    assert {'Run Bronze Ingestion', 'Run Silver Transform', 'Run Gold Aggregations', 'Bronze Failure', 'Silver Failure', 'Gold Failure', 'Mark Pipeline Success'} <= set(activities)
    assert activities['Run Silver Transform']['dependsOn'][0]['activity'] == 'Run Bronze Ingestion'
    assert activities['Run Gold Aggregations']['dependsOn'][0]['activity'] == 'Run Silver Transform'
    assert activities['Bronze Failure']['dependsOn'][0]['dependencyConditions'] == ['Failed', 'TimedOut']
    assert activities['Silver Failure']['dependsOn'][0]['dependencyConditions'] == ['Failed', 'TimedOut']
    assert activities['Gold Failure']['dependsOn'][0]['dependencyConditions'] == ['Failed', 'TimedOut']
    assert payload['properties']['parameters']['processing_date']['type'] == 'String'
    assert payload['properties']['parameters']['environment']['defaultValue'] == '${ENVIRONMENT}'


def test_pipeline_placeholders_and_policies_are_symbolic():
    for path in [
        REPO_ROOT / 'pipelines/retail-medallion.DataPipeline/pipeline-content.json',
        REPO_ROOT / 'pipelines/healthcare-quality.DataPipeline/pipeline-content.json',
    ]:
        text = read_text(path)
        assert GUID_RE.search(text) is None, f'GUID literal found in {path}'
        assert '${WORKSPACE_ID}' in text
        assert 'retry' in text
        assert 'timeout' in text


def test_pipeline_notebook_parameter_names_match_parameterized_notebooks():
    retail_payload = load_json(REPO_ROOT / 'pipelines/retail-medallion.DataPipeline/pipeline-content.json')
    retail_activities = {activity['name']: activity for activity in retail_payload['properties']['activities'] if activity['type'] == 'TridentNotebook'}
    healthcare_payload = load_json(REPO_ROOT / 'pipelines/healthcare-quality.DataPipeline/pipeline-content.json')
    healthcare_activities = {activity['name']: activity for activity in healthcare_payload['properties']['activities'] if activity['type'] == 'TridentNotebook'}

    expected_parameter_names = {'ENVIRONMENT', 'PROCESSING_DATE', 'PIPELINE_RUN_ID'}
    assert retail_payload['properties']['parameters']['environment']['defaultValue'] == '${ENVIRONMENT}'
    assert healthcare_payload['properties']['parameters']['environment']['defaultValue'] == '${ENVIRONMENT}'
    for activity in list(retail_activities.values()) + list(healthcare_activities.values()):
        parameters = activity['typeProperties']['parameters']
        assert set(parameters) == expected_parameter_names
        assert parameters['ENVIRONMENT']['type'] == 'Expression'
        assert parameters['PROCESSING_DATE']['type'] == 'Expression'
        assert parameters['PIPELINE_RUN_ID']['type'] == 'Expression'


def test_semantic_model_required_files_and_report_scaffold_exist():
    required_paths = [
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.pbip',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/definition.pbism',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/definition/database.tmdl',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/definition/model.tmdl',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/definition/relationships.tmdl',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/definition/tables/Date.tmdl',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/definition/tables/Customer.tmdl',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/definition/tables/Product.tmdl',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/definition/tables/Sales.tmdl',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/Copilot/Instructions/instructions.md',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/Copilot/schema.json',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/Copilot/settings.json',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/Copilot/examplePrompts.json',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.Report/definition.pbir',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.Report/definition/report.json',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.Report/definition/version.json',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.Report/definition/pages/pages.json',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.Report/definition/pages/SalesOverview/page.json',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.Report/definition/pages/SalesOverview/visuals/KpiRevenue/visual.json',
        REPO_ROOT / 'semantic-models/RetailSales/baseline/definition/database.tmdl',
        REPO_ROOT / 'semantic-models/RetailSales/baseline/definition/model.tmdl',
        REPO_ROOT / 'semantic-models/RetailSales/baseline/definition/relationships.tmdl',
        REPO_ROOT / 'semantic-models/RetailSales/baseline/definition/tables/Date.tmdl',
        REPO_ROOT / 'semantic-models/RetailSales/baseline/definition/tables/Customer.tmdl',
        REPO_ROOT / 'semantic-models/RetailSales/baseline/definition/tables/Product.tmdl',
        REPO_ROOT / 'semantic-models/RetailSales/baseline/definition/tables/Sales.tmdl',
    ]
    for path in required_paths:
        assert path.exists(), f'Missing semantic model artifact: {path}'


def test_semantic_model_json_measure_names_and_placeholders_are_present():
    json_files = [
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.pbip',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/definition.pbism',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/Copilot/schema.json',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/Copilot/settings.json',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/Copilot/examplePrompts.json',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.Report/definition.pbir',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.Report/definition/report.json',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.Report/definition/version.json',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.Report/definition/pages/pages.json',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.Report/definition/pages/SalesOverview/page.json',
        REPO_ROOT / 'semantic-models/RetailSales/RetailSales.Report/definition/pages/SalesOverview/visuals/KpiRevenue/visual.json',
    ]
    for path in json_files:
        load_json(path)

    sales_tmdl = read_text(REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/definition/tables/Sales.tmdl')
    for measure_name in REQUIRED_MEASURES:
        assert f"measure '{measure_name}'" in sales_tmdl
    assert 'mode: directLake' in sales_tmdl
    assert 'expressionSource: DL_RetailLakehouse' in sales_tmdl
    assert 'sourceColumn: purchase_id' in sales_tmdl
    assert 'sourceColumn: purchase_ts' in sales_tmdl
    assert 'sourceColumn: unit_cost' in sales_tmdl
    assert "SUM(Sales[Revenue Amount])" in sales_tmdl
    assert "SUM(Sales[Cost Amount])" in sales_tmdl
    assert "DISTINCTCOUNT(Sales[Order ID])" in sales_tmdl


def test_tmdl_source_columns_match_gold_notebook_output_lists():
    gold_text = notebook_code_text(NOTEBOOK_GOLD)
    expected = {
        'Date': parse_list_assignment(gold_text, 'gold_date_columns'),
        'Customer': parse_list_assignment(gold_text, 'gold_customer_columns'),
        'Product': parse_list_assignment(gold_text, 'gold_product_columns'),
        'Sales': parse_list_assignment(gold_text, 'gold_sales_columns'),
    }
    for table_name, expected_columns in expected.items():
        table_path = REPO_ROOT / f'semantic-models/RetailSales/RetailSales.SemanticModel/definition/tables/{table_name}.tmdl'
        assert extract_source_columns(table_path) == expected_columns


def test_semantic_model_uses_guidance_compliant_tmdl_patterns():
    sales_tmdl = read_text(REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/definition/tables/Sales.tmdl')
    customer_tmdl = read_text(REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/definition/tables/Customer.tmdl')
    product_tmdl = read_text(REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/definition/tables/Product.tmdl')
    date_tmdl = read_text(REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/definition/tables/Date.tmdl')

    for text in [sales_tmdl, customer_tmdl, product_tmdl, date_tmdl]:
        assert 'description:' not in text

    assert sales_tmdl.index("measure 'Total Revenue'") < sales_tmdl.index("column 'Sales Key'")
    assert "column 'Sales Key'\n\t\tdataType: int64\n\t\tisHidden" in sales_tmdl
    assert "column 'Date Key'\n\t\tdataType: int64\n\t\tisHidden" in sales_tmdl
    assert "column 'Customer Key'\n\t\tdataType: int64\n\t\tisHidden" in sales_tmdl
    assert "column 'Product Key'\n\t\tdataType: int64\n\t\tisHidden" in sales_tmdl
    assert "column Quantity\n\t\tdataType: int64\n\t\tisHidden" in sales_tmdl
    assert "column 'Revenue Amount'\n\t\tdataType: decimal\n\t\tisHidden" in sales_tmdl
    assert "column 'Cost Amount'\n\t\tdataType: decimal\n\t\tisHidden" in sales_tmdl
    assert "column 'Gross Margin Amount'\n\t\tdataType: decimal\n\t\tisHidden" in sales_tmdl
    assert "column 'Gross Margin Percent'\n\t\tdataType: decimal\n\t\tisHidden" in sales_tmdl
    assert "/// Stable business identifier for each order." in sales_tmdl
    assert "column 'Order ID'" in sales_tmdl
    assert "column 'Order Date'" in sales_tmdl
    assert "column 'Customer Name'" in customer_tmdl
    assert "column 'Product Name'" in product_tmdl
    assert "column 'Month Name'" in date_tmdl


def test_measure_section_uses_dax_bracket_references_not_tmdl_dot_column_syntax():
    sales_tmdl = read_text(REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/definition/tables/Sales.tmdl')
    measure_section = sales_tmdl.split("column 'Sales Key'", 1)[0]
    assert "Sales.'Revenue Amount'" not in measure_section
    assert "Sales.'Cost Amount'" not in measure_section
    assert "Sales.'Order ID'" not in measure_section
    assert "SUM(Sales[Revenue Amount])" in measure_section
    assert "SUM(Sales[Cost Amount])" in measure_section
    assert "DISTINCTCOUNT(Sales[Order ID])" in measure_section


def test_relationships_report_reference_and_no_guid_literals():
    relationships = read_text(REPO_ROOT / 'semantic-models/RetailSales/RetailSales.SemanticModel/definition/relationships.tmdl')
    assert 'crossFilteringBehavior: oneDirection' in relationships
    assert "relationship 'Sales to Date'" in relationships
    assert "relationship 'Sales to Customer'" in relationships
    assert "relationship 'Sales to Product'" in relationships
    assert "fromColumn: Sales.'Date Key'" in relationships
    assert "toColumn: Date.'Date Key'" in relationships
    assert "fromColumn: Sales.'Customer Key'" in relationships
    assert "toColumn: Customer.'Customer Key'" in relationships
    assert "fromColumn: Sales.'Product Key'" in relationships
    assert "toColumn: Product.'Product Key'" in relationships

    definition_pbir = load_json(REPO_ROOT / 'semantic-models/RetailSales/RetailSales.Report/definition.pbir')
    assert definition_pbir['datasetReference']['byPath']['path'] == '../RetailSales.SemanticModel'

    for path in (REPO_ROOT / 'semantic-models/RetailSales').rglob('*'):
        if path.is_file():
            text = read_text(path)
            assert GUID_RE.search(text) is None, f'GUID literal found in {path}'
