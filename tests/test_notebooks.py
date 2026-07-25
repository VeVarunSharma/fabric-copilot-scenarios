import ast
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = REPO_ROOT / 'datasets/schemas'
NOTEBOOK_PATHS = {
    'retail_bronze': REPO_ROOT / 'notebooks/retail-medallion/01_bronze_ingestion.ipynb',
    'retail_silver': REPO_ROOT / 'notebooks/retail-medallion/02_silver_transform.ipynb',
    'retail_gold': REPO_ROOT / 'notebooks/retail-medallion/03_gold_aggregations.ipynb',
    'iot': REPO_ROOT / 'notebooks/iot-telemetry/telemetry_processing.ipynb',
    'healthcare': REPO_ROOT / 'notebooks/healthcare-quality/claims_quality.ipynb',
}
GUID_RE = re.compile(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b')
LIST_ASSIGNMENT_RE = r"{name}\s*=\s*(\[[^\]]*\])"
STRUCT_FIELD_RE = re.compile(r"StructField\('([^']+)'")


def load_notebook(path: Path):
    with path.open('r', encoding='utf-8') as handle:
        return json.load(handle)


def notebook_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def notebook_code_text(path: Path) -> str:
    payload = load_notebook(path)
    return ''.join(''.join(cell.get('source', [])) for cell in payload['cells'])


def notebook_code_cells(path: Path):
    payload = load_notebook(path)
    return [cell for cell in payload['cells'] if cell['cell_type'] == 'code']


def load_schema(path: Path):
    with path.open('r', encoding='utf-8') as handle:
        return json.load(handle)


def parse_list_assignment(text: str, variable_name: str):
    match = re.search(LIST_ASSIGNMENT_RE.format(name=re.escape(variable_name)), text, re.S)
    assert match, f'Missing assignment for {variable_name}'
    return ast.literal_eval(match.group(1))


def parse_struct_fields(text: str, schema_variable: str):
    anchor = text.index(f'{schema_variable} = T.StructType([')
    block = text[anchor:text.index('])', anchor)]
    return STRUCT_FIELD_RE.findall(block)


def test_notebooks_exist_and_are_valid_json():
    for path in NOTEBOOK_PATHS.values():
        assert path.exists(), f'Missing notebook: {path}'
        payload = load_notebook(path)
        assert payload['nbformat'] == 4
        assert payload['nbformat_minor'] >= 4


def test_notebooks_have_required_fabric_metadata():
    for path in NOTEBOOK_PATHS.values():
        payload = load_notebook(path)
        metadata = payload['metadata']
        lakehouse = metadata['dependencies']['lakehouse']
        assert lakehouse['default_lakehouse'] == '${DEFAULT_LAKEHOUSE_ID}'
        assert lakehouse['default_lakehouse_name'] == '${DEFAULT_LAKEHOUSE_NAME}'
        assert lakehouse['default_lakehouse_workspace_id'] == '${WORKSPACE_ID}'
        assert metadata['fabric']['workspaceId'] == '${WORKSPACE_ID}'
        assert metadata['fabric']['environment'] == 'parameterized'


def test_notebook_cells_have_required_fields():
    for path in NOTEBOOK_PATHS.values():
        payload = load_notebook(path)
        assert any(cell['cell_type'] == 'markdown' for cell in payload['cells'])
        assert any(cell['cell_type'] == 'code' for cell in payload['cells'])
        code_cells = [cell for cell in payload['cells'] if cell['cell_type'] == 'code']
        assert code_cells[0]['metadata'] == {'tags': ['parameters']}
        for cell in payload['cells']:
            if cell['cell_type'] == 'code':
                assert cell['outputs'] == []
                assert cell['execution_count'] is None
                assert isinstance(cell['source'], list)
                if cell is not code_cells[0]:
                    assert cell['metadata'] == {}
            else:
                assert cell['metadata'] == {}


def test_notebooks_capture_required_alignment_patterns():
    expected_fragments = {
        'retail_bronze': ['Files/landing/retail-purchases', 'retail_purchases_raw', 'customer_name', 'product_name', 'unit_cost'],
        'retail_silver': ['duplicate_purchase', 'retail_sales_enriched', 'missing_customer_dimension', 'gross_margin'],
        'retail_gold': ['gold_date_columns', 'gold_customer_columns', 'gold_product_columns', 'gold_sales_columns'],
        'iot': ['Files/landing/iot-telemetry/telemetry.jsonl', 'anomaly_labels', 'humidity_pct', 'quarantine'],
        'healthcare': ['Files/landing/healthcare-claims/claims.csv', 'claim_received_date', 'provider_code', 'quarantine'],
    }
    for key, path in NOTEBOOK_PATHS.items():
        text = notebook_text(path)
        for fragment in expected_fragments[key]:
            assert fragment in text, f'{fragment} missing from {path.name}'


def test_notebooks_have_parameter_cells_and_no_runtime_deployment_tokens_in_code():
    expected_defaults = {
        'retail_bronze': {'PROCESSING_DATE = "2026-03-02"'},
        'retail_silver': {'PROCESSING_DATE = "2026-03-02"'},
        'retail_gold': {'PROCESSING_DATE = "2026-03-02"'},
        'iot': {'PROCESSING_DATE = "2026-04-12"'},
        'healthcare': {'PROCESSING_DATE = "2026-02-07"'},
    }
    required_lines = {
        'ENVIRONMENT = "dev"',
        'PIPELINE_RUN_ID = "local-demo"',
        'environment = ENVIRONMENT',
        'processing_date = PROCESSING_DATE',
        'pipeline_run_id = PIPELINE_RUN_ID',
    }
    forbidden_tokens = ['${ENVIRONMENT}', '${PROCESSING_DATE}', '${PIPELINE_RUN_ID}']

    for key, path in NOTEBOOK_PATHS.items():
        code_cells = notebook_code_cells(path)
        parameter_cell_text = ''.join(code_cells[0]['source'])
        assert code_cells[0]['metadata'] == {'tags': ['parameters']}
        for required_line in required_lines | expected_defaults[key]:
            assert required_line in parameter_cell_text

        all_code_text = ''.join(''.join(cell['source']) for cell in code_cells)
        for token in forbidden_tokens:
            assert token not in all_code_text, f'{token} should not appear in code cells for {path.name}'


def test_retail_notebook_columns_match_committed_dataset_schemas():
    retail_text = notebook_code_text(NOTEBOOK_PATHS['retail_bronze'])
    assert parse_list_assignment(retail_text, 'purchase_input_columns') == load_schema(SCHEMA_ROOT / 'purchases.schema.json')['x-columnOrder']
    assert parse_list_assignment(retail_text, 'customer_input_columns') == load_schema(SCHEMA_ROOT / 'customers.schema.json')['x-columnOrder']
    assert parse_list_assignment(retail_text, 'product_input_columns') == load_schema(SCHEMA_ROOT / 'products.schema.json')['x-columnOrder']


def test_iot_and_healthcare_struct_fields_match_committed_schemas():
    iot_text = notebook_code_text(NOTEBOOK_PATHS['iot'])
    healthcare_text = notebook_code_text(NOTEBOOK_PATHS['healthcare'])
    assert parse_struct_fields(iot_text, 'telemetry_schema') == load_schema(SCHEMA_ROOT / 'telemetry.schema.json')['required']
    assert parse_struct_fields(healthcare_text, 'claim_schema') == load_schema(SCHEMA_ROOT / 'claims.schema.json')['x-columnOrder']


def test_retail_gold_documented_columns_match_tmdl_expectations():
    gold_text = notebook_code_text(NOTEBOOK_PATHS['retail_gold'])
    assert parse_list_assignment(gold_text, 'gold_date_columns') == ['date_key', 'date_value', 'calendar_year', 'calendar_quarter', 'month_number', 'month_name', 'year_month']
    assert parse_list_assignment(gold_text, 'gold_customer_columns') == ['customer_key', 'customer_id', 'customer_name', 'loyalty_tier', 'home_region', 'signup_date', 'email_domain', 'synthetic_record']
    assert parse_list_assignment(gold_text, 'gold_product_columns') == ['product_key', 'product_id', 'product_name', 'category', 'subcategory', 'unit_price', 'unit_cost', 'is_active', 'synthetic_record']
    assert parse_list_assignment(gold_text, 'gold_sales_columns') == ['sales_key', 'date_key', 'customer_key', 'product_key', 'purchase_id', 'purchase_ts', 'ingest_ts', 'store_id', 'channel', 'quantity', 'unit_price', 'unit_cost', 'revenue', 'cost', 'gross_margin', 'gross_margin_pct', 'anomaly_label', 'synthetic_record']


def test_notebooks_do_not_embed_guids_or_http_reads():
    for path in NOTEBOOK_PATHS.values():
        text = notebook_text(path)
        assert GUID_RE.search(text) is None, f'GUID literal found in {path}'
        assert 'load("http://' not in text
        assert 'load("https://' not in text
        assert "load('http://" not in text
        assert "load('https://" not in text
