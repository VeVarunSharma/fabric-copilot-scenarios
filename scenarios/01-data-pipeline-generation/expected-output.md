# Expected output - Scenario 01

## Canonical file
- [Retail medallion pipeline](../../pipelines/retail-medallion.DataPipeline/)

Do not expect the ideal Copilot response to inline a large pipeline JSON file in chat. The better outcome is a generated artifact in the canonical folder plus a short explanation of the important structures.

## Key generated structures

### Parameter block
A strong draft includes a compact runtime parameter set such as:
- `ProcessDate` for backfills and reprocessing
- `Environment` for environment-aware resolution
- `SourceSystem` for source-specific logging
- `RetryCount` and `RetryIntervalSeconds` for transient failure policy
- `NotebookTimeoutMinutes` for activity-level timeout control

### Activity graph
The expected dependency pattern is:

| Activity | Purpose | Depends on |
| --- | --- | --- |
| `IngestRetailSalesBronze` | Load daily sales into bronze | None |
| `IngestRetailCustomersBronze` | Load customer reference data into bronze | None |
| `BuildRetailSilver` | Clean, deduplicate, and conform bronze data | Both bronze activities succeed |
| `PublishRetailGold` | Build serving-ready gold tables | `BuildRetailSilver` succeeds |
| `ValidateRetailGold` | Check row counts and required business rules | `PublishRetailGold` succeeds |
| `LogPipelineFailure` | Capture operational context on failure | Triggered by failed upstream activity |

### Retry and timeout policy
The explanation should call out why retries differ by activity. For example, bronze ingestion might allow more retries for transient source availability, while gold publication might use a lower retry count to avoid repeated downstream write pressure.

### Failure behavior
The generated design should describe how the failure path receives context such as pipeline name, activity name, and process date, while still surfacing the original failed activity in Fabric monitoring.

## Human review checklist
- Confirm the activity names align with the intended notebooks and not placeholder names.
- Check that all success dependencies use the right dependency condition and no branch can publish gold early.
- Validate timeout values against realistic notebook durations.
- Verify retry policy is appropriate for each activity and not copied blindly.
- Ensure the failure path records context without swallowing the primary exception.
- Confirm IDs and connections are parameterized or resolved by deployment tooling.
- Make sure default parameter values are safe for a demo or development workspace.
