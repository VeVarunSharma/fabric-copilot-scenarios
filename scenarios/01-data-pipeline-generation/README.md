# Scenario 01 - Retail data pipeline generation

This scenario shows how GitHub Copilot can draft a Microsoft Fabric retail medallion pipeline while the engineer stays responsible for dependency logic, runtime settings, and deployment review.

- [Sample prompt](sample-prompt.md)
- [Expected output](expected-output.md)
- [Extension exercises](extension-exercises.md)

## Business problem
A retail analytics team needs a daily orchestration layer for bronze, silver, and gold processing. The pipeline must backfill by date, retry transient failures, and stop publication when upstream notebook runs fail.

## Target personas and prerequisites
**Primary personas**
- Fabric data engineers building pipeline definitions
- Analytics engineers reviewing downstream dependencies
- Technical leads approving retry and failure-handling policy

**Prerequisites**
- Working knowledge of Fabric Data Pipelines and notebook activities
- Familiarity with medallion processing order
- Ability to review parameter values, activity settings, and environment-specific references

## Manual baseline
Without Copilot, a practitioner usually:
1. Creates the pipeline shell and parameter block by hand.
2. Adds notebook activities one by one and wires success dependencies manually.
3. Re-enters retry counts, retry intervals, and timeout settings across multiple activities.
4. Adds a failure path for logging or notification and verifies it does not hide the original error.
5. Documents the dependency graph separately for reviewers.

That work is repetitive, easy to mis-wire, and slow to review when the flow changes.

## Copilot-assisted workflow
1. Start with the approved orchestration pattern and ask Copilot for a Fabric-compatible pipeline draft.
2. Have Copilot generate the parameter block, activity sequence, dependency conditions, and retry policy explanation.
3. Refine the prompt until notebook names, timeouts, and failure behavior match the team's operating model.
4. Perform a human review before deployment, focusing on identifiers, dependency correctness, and failure propagation.

## Sample Fabric artifact
The planned canonical artifact for this scenario is the retail medallion pipeline at [../../pipelines/retail-medallion.DataPipeline/](../../pipelines/retail-medallion.DataPipeline/).

A strong draft should describe or generate:

| Area | What to expect |
| --- | --- |
| Parameters | `ProcessDate`, `Environment`, `SourceSystem`, `RetryCount`, and `RetryIntervalSeconds` or equivalent runtime controls |
| Dependencies | Bronze ingestion runs before silver, silver completes before gold, and validation runs only after gold succeeds |
| Retries | Notebook and external activities use explicit retry counts, retry intervals, and timeouts rather than defaults |
| Failure path | A dedicated logging or notification activity receives pipeline context without suppressing the root failure |

## Validation
Use the [human review checklist](expected-output.md#human-review-checklist) after Copilot drafts the pipeline.

At minimum, verify that:
- Every activity name matches the intended retail notebooks.
- Parameter defaults are safe for non-production testing.
- Retry settings are consistent with the SLA for upstream sources.
- Failure handling preserves the original activity error.
- Environment-specific IDs remain parameterized or deployment-resolved.

## Learning objectives
- Translate a medallion orchestration requirement into a precise Copilot prompt.
- Review generated pipeline dependencies instead of hand-authoring every edge.
- Recognize which runtime settings must still be validated by a human.
- Separate reusable orchestration scaffolding from environment-specific configuration.

## What work did Copilot eliminate?
Copilot eliminates the first draft of the pipeline graph, repetitive parameter scaffolding, boilerplate retry settings, and the initial documentation of how activities depend on each other. The engineer can spend review time on correctness, resilience, and deployment safety instead of typing the same structure from scratch.

## Responsible use/security
- Keep workspace IDs, lakehouse IDs, and connection details out of prompts and source control.
- Review retry counts so the generated pipeline does not amplify source-system load during incidents.
- Confirm failure notifications do not leak sensitive operational data.
- Treat Copilot output as a draft that must be validated in a non-production workspace first.
