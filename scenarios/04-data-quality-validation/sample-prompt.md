# Sample prompt - Scenario 04

## Ready to copy prompt

```text
Generate a Microsoft Fabric quality-validation notebook for synthetic healthcare claims.

Target artifacts:
- notebooks/healthcare-quality/claims_quality.ipynb
- pipelines/healthcare-quality.DataPipeline/

Requirements:
- Use synthetic data only and do not include PHI.
- Define an explicit schema with fictional fields such as claim_id, member_token, provider_token, service_date, paid_amount, billed_amount, diagnosis_code, procedure_code, place_of_service, claim_status, and source_file.
- Separate quality rules into critical and warning gates.
- Critical gates must quarantine rows and signal the pipeline to stop publication when they fail. Include missing claim_id, duplicate claim_id within the batch, negative paid_amount, billed_amount lower than paid_amount, and service_date later than process_date.
- Warning gates must not block publication, but they must be counted and surfaced in the summary. Include diagnosis_code format drift, procedure_code format drift, unknown place_of_service, and unusually high paid_amount.
- Produce three outputs: clean claims, quarantined claims, and a quality metrics summary with rule_name, severity, affected_rows, pass_rate, warning_count, critical_failure_count, and process_date.
- Add structured logging and a compact notebook summary that a Fabric pipeline can branch on.
- Keep identifiers and storage locations parameterized.
- Return a short explanation of the critical-versus-warning design and the review points.
```

## Follow-up prompts
- "Add a warning rule for sudden shifts in denial rate by source_file."
- "Show how the notebook summary should signal the pipeline to continue with warnings but stop on critical failures."
- "Rewrite the explanation for a data-governance reviewer instead of a Spark developer."

## Acceptance criteria
- The notebook keeps PHI out of scope.
- Critical and warning rules are clearly separated.
- Quarantine, metrics, logging, and pipeline handoff are all included.
- The response explains what a human must review before operational use.
