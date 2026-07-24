# Sample prompt - Scenario 01

## Ready to copy prompt

```text
You are helping me draft a Microsoft Fabric Data Pipeline for a retail medallion workflow.

Target artifact:
- Planned canonical folder: pipelines/retail-medallion.DataPipeline/

Business goal:
- Orchestrate daily retail ingestion and transformation from bronze to silver to gold.
- Support backfills by process date.
- Retry transient notebook or source failures without masking persistent failures.

Pipeline requirements:
- Create parameters for ProcessDate, Environment, SourceSystem, RetryCount, RetryIntervalSeconds, and NotebookTimeoutMinutes.
- Add notebook activities for IngestRetailSalesBronze, IngestRetailCustomersBronze, BuildRetailSilver, PublishRetailGold, and ValidateRetailGold.
- BuildRetailSilver must wait for both bronze notebook activities to succeed.
- PublishRetailGold must wait for BuildRetailSilver.
- ValidateRetailGold must wait for PublishRetailGold.
- Add a failure logging or notification activity that receives the pipeline name, failed activity name, and ProcessDate.
- Apply explicit retry counts, retry intervals, and timeouts to notebook and external activities.
- Keep workspace, lakehouse, and item identifiers parameterized or deployment-resolved.
- Return a short explanation of the parameter block, dependency graph, retry policy, and the human review points before deployment.

Do not recommend hardcoded IDs, secrets, or manual post-editing that duplicates what the pipeline JSON can already express.
```

## Follow-up prompts
- "Reduce the retry count for gold publishing but keep silver retries higher because the silver notebook calls an occasionally throttled upstream API."
- "Add a branch that skips gold publication when validation finds zero silver rows for the requested process date."
- "Summarize the dependency graph in reviewer-friendly language for a pull request description."

## Acceptance criteria
- Parameters are explicit and named for runtime control.
- Dependencies are unambiguous and match the medallion order.
- Retry and timeout settings are described, not left implicit.
- Failure handling preserves the root cause for operators.
