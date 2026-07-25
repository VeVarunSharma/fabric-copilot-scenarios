# Data analyst prompt guide

## Customer outcome

Get faster query, metric, and narrative drafts so more time stays on business interpretation.

## Best use cases

- warehouse SQL, KPI explanation, documentation drafting, and report-facing business logic
- first-draft planning that still needs expert review
- workshop or demo sessions that need portable prompts instead of tool-specific files

## Copy-ready prompt

```text
Act as a senior Microsoft Fabric data analyst working in a GitHub-governed analytics repository.

Business outcome:
Get faster query, metric, and narrative drafts so more time stays on business interpretation.

Context:
- The repository demonstrates a synthetic retail and customer-transactions medallion architecture.
- The end-to-end path is synthetic sources -> Fabric pipeline -> bronze -> silver -> gold -> Direct Lake semantic model -> report.
- I want help with warehouse SQL, KPI explanation, documentation drafting, and report-facing business logic.
- The response must stay portable across environments.

Constraints:
- Do not invent workspace IDs, item IDs, secrets, tokens, tenant names, or customer data.
- Use synthetic data only.
- Keep GitHub governance in mind: changes should be reviewable, explainable, and safe.
- If you suggest implementation detail, label assumptions and placeholders clearly.

Deliver:
1. optimized query or measure draft
2. plain-language explanation
3. validation steps
4. review checklist for business correctness

Acceptance criteria:
- The answer is specific to Microsoft Fabric and GitHub delivery workflows.
- The answer calls out what GitHub Copilot eliminates.
- The answer ends with a human review checklist and open questions.
```

## Human review required

- Validate business definitions, thresholds, and schema assumptions.
- Validate any generated code, DAX, SQL, or workflow step before reuse.
- Confirm feature availability and permissions in the target tenant or organization.

## Recommended scenario prompt packs

- [02 SQL optimization](../scenarios/02-sql-optimization.md)
- [06 DAX generation](../scenarios/06-dax-generation.md)
- [07 Documentation generation](../scenarios/07-documentation-generation.md)

## What Copilot should eliminate first

- repetitive scaffolding work
- first-draft documentation and explanation work
- option comparison and checklist drafting

## Related guidance

- [Prompt library README](../README.md)
- [Persona paths](../../docs/persona-paths.md)
