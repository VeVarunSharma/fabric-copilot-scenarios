# Expected output - Scenario 04

## Canonical files
- [Claims quality notebook](../../notebooks/healthcare-quality/claims_quality.ipynb)
- [Healthcare quality pipeline](../../pipelines/healthcare-quality.DataPipeline/)

The ideal Copilot response should summarize the generated notebook and pipeline handoff. It should link to the canonical artifacts instead of reproducing a large notebook or pipeline definition inline.

## Key generated structures

### Quality-rule layout
A strong draft separates rules by severity:

| Severity | Expected examples | Expected behavior |
| --- | --- | --- |
| Critical | Missing `claim_id`, duplicate `claim_id`, negative `paid_amount`, `billed_amount` lower than `paid_amount`, future `service_date` | Quarantine affected rows and signal the pipeline to stop publication |
| Warning | Diagnosis or procedure format drift, unknown place of service, paid-amount outliers | Keep processing, but publish counts and metrics for review |

### Output structure
The generated notebook should describe or emit:
- a clean claims output for downstream reporting
- a quarantine output with rule attribution
- a quality metrics summary keyed by rule name, severity, and process date
- a compact notebook result that the pipeline can branch on

### Privacy posture
The answer should explicitly state that the scenario uses synthetic claims and excludes PHI. A strong draft also notes that quarantine access must be controlled.

## Human review checklist
- Verify that the schema and examples contain no PHI.
- Review whether each rule is correctly classified as critical or warning.
- Confirm the quality summary gives the pipeline enough information to branch safely.
- Check that quarantined rows include remediation context without exposing sensitive data.
- Validate storage and identifiers remain parameterized.
