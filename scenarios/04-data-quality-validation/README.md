# Scenario 04 - Synthetic healthcare quality validation

This scenario shows how GitHub Copilot can draft a Fabric quality-validation workflow for synthetic healthcare claims while keeping patient privacy, gate severity, and quarantine logic explicit.

- [Sample prompt](sample-prompt.md)
- [Expected output](expected-output.md)
- [Extension exercises](extension-exercises.md)

## Business problem
A healthcare analytics team ingests synthetic claim files and needs to block clearly broken records, isolate suspect rows, and publish a quality summary that downstream consumers can trust.

## Target personas and prerequisites
**Primary personas**
- Data engineers building healthcare quality notebooks and pipelines
- Data stewards reviewing quality-rule intent and severity
- Analytics leads deciding which issues should stop publication versus raise warnings

**Prerequisites**
- Familiarity with Spark or notebook-based quality checks
- Understanding of healthcare claims fields and basic data-quality patterns
- Agreement that all examples remain synthetic and free of PHI

## Manual baseline
Without Copilot, a practitioner usually:
1. Writes rule code for required fields, duplicate checks, amount logic, and date validity.
2. Separates critical failures from warning-only findings by hand.
3. Builds quarantine outputs and summary metrics in separate notebook cells.
4. Documents which pipeline branch should stop and which should continue.
5. Repeats the same severity and metric patterns in every new claims feed.

The repetitive work slows delivery and makes policy drift more likely.

## Copilot-assisted workflow
1. Provide the notebook target, pipeline context, and explicit rule severity requirements.
2. Ask Copilot to draft a validation notebook that produces clean rows, quarantine rows, and a metrics summary.
3. Refine the prompt until rule names, thresholds, and gate behavior match the team's governance standard.
4. Have a human reviewer approve every critical-versus-warning decision before the workflow is used operationally.

## Sample Fabric artifact
The planned canonical notebook is [../../notebooks/healthcare-quality/claims_quality.ipynb](../../notebooks/healthcare-quality/claims_quality.ipynb).

The planned orchestration artifact is [../../pipelines/healthcare-quality.DataPipeline/](../../pipelines/healthcare-quality.DataPipeline/).

A strong draft should show:
- Synthetic-only claims processing with no PHI fields
- Critical gates that stop publication when required data is broken
- Warning gates that surface quality risk without blocking every run
- Quarantine logic for failed rows and metrics for pass rate, warning counts, and rule outcomes

## Validation
After Copilot drafts the notebook or pipeline support logic, verify that:
- No PHI or real patient identifiers appear in the schema, prompts, or examples.
- Critical rules block publication only for truly breaking defects.
- Warning rules are visible in metrics and logs even when the run continues.
- Quarantine outputs preserve enough context for remediation without exposing sensitive information.
- The pipeline can branch on notebook summary results without hardcoded environment IDs.

## Learning objectives
- Encode data-quality policy in a prompt that separates critical and warning behavior.
- Review generated rule scaffolding instead of typing repetitive quality checks.
- Keep privacy constraints explicit while still producing realistic healthcare operations content.
- Use metrics and quarantine outputs as first-class deliverables from the start.

## What work did Copilot eliminate?
Copilot eliminates the repetitive first draft of rule functions, severity grouping, quarantine output code, summary-metric scaffolding, and reviewer-facing documentation. The team can focus on policy decisions, privacy review, and production fit.

## Responsible use/security
- Use synthetic claims only. Do not introduce PHI, payer member IDs, or real provider identifiers.
- Review every rule for privacy impact and downstream data exposure.
- Keep storage targets, secrets, and workspace IDs out of prompts and generated notebook code.
- Validate that quarantine outputs are access-controlled before any broader sharing.
