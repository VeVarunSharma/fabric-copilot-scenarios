# Expected output - Scenario 03

## Canonical files
- [Telemetry processing notebook](../../notebooks/iot-telemetry/telemetry_processing.ipynb)
- [Telemetry dataset path](../../datasets/synthetic/iot-telemetry/)

The ideal Copilot response should summarize the notebook structure and point to the generated notebook file. It should not flood the user with raw notebook JSON.

## Key generated structures

### Notebook sections to expect

| Notebook section | Why it matters |
| --- | --- |
| Parameter cell | Makes process date, source path, target tables, and pipeline run ID easy to review and reuse |
| Imports and schema | Ensures the telemetry contract is explicit and not inferred from one sample file |
| Raw ingest and metadata | Adds ingestion timestamp and run identifiers for lineage and replay support |
| Deduplication | Uses window logic to keep the intended record when duplicates appear |
| Range checks and quarantine | Separates bad measurements from curated telemetry instead of silently filtering them out |
| Windowed metrics | Produces rolling health indicators such as moving temperature averages and max vibration |
| Delta writes | Persists curated and quarantine outputs in a format Fabric teams can operationalize |
| Validation cells | Gives the reviewer immediate row-count and rule-count checkpoints |

### Review emphasis
A strong answer explains where humans still need to review thresholds, watermark assumptions, and target names. It should also mention that logging must be safe for shared workspaces.

## Human review checklist
- Confirm every schema field name and data type against the source contract.
- Check that deduplication preserves the desired record when late files arrive.
- Review range thresholds with an operations subject matter expert.
- Verify window definitions use the intended ordering and partition keys.
- Confirm Delta targets and logging are parameterized for deployment.
