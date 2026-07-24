# BI developer prompt guide

## Customer outcome

Improve semantic models and measures faster while preserving naming, usability, and trust.

## Best use cases

- Direct Lake semantic model quality, DAX measures, descriptions, display folders, and report readiness
- first-draft planning that still needs expert review
- workshop or demo sessions that need portable prompts instead of tool-specific files

## Copy-ready prompt

```text
Act as a senior Microsoft Fabric bi developer working in a GitHub-governed analytics repository.

Business outcome:
Improve semantic models and measures faster while preserving naming, usability, and trust.

Context:
- The repository demonstrates a synthetic retail and customer-transactions medallion architecture.
- The end-to-end path is synthetic sources -> Fabric pipeline -> bronze -> silver -> gold -> Direct Lake semantic model -> report.
- I want help with Direct Lake semantic model quality, DAX measures, descriptions, display folders, and report readiness.
- The response must stay portable across environments.

Constraints:
- Do not invent workspace IDs, item IDs, secrets, tokens, tenant names, or customer data.
- Use synthetic data only.
- Keep GitHub governance in mind: changes should be reviewable, explainable, and safe.
- If you suggest implementation detail, label assumptions and placeholders clearly.

Deliver:
1. model review findings
2. measure drafts and naming guidance
3. metadata improvement list
4. human validation steps

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

- [05 Semantic model analysis](../scenarios/05-semantic-model-analysis.md)
- [06 DAX generation](../scenarios/06-dax-generation.md)
- [07 Documentation generation](../scenarios/07-documentation-generation.md)

## What Copilot should eliminate first

- repetitive scaffolding work
- first-draft documentation and explanation work
- option comparison and checklist drafting

## Related guidance

- [Prompt library README](../README.md)
- [Persona paths](../../docs/persona-paths.md)
