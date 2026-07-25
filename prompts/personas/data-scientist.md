# Data scientist prompt guide

## Customer outcome

Reduce setup time for notebook-based analysis so more effort goes into experimentation and interpretation.

## Best use cases

- PySpark notebooks, validation logic, anomaly exploration, and experimental workflow framing
- first-draft planning that still needs expert review
- workshop or demo sessions that need portable prompts instead of tool-specific files

## Copy-ready prompt

```text
Act as a senior Microsoft Fabric data scientist working in a GitHub-governed analytics repository.

Business outcome:
Reduce setup time for notebook-based analysis so more effort goes into experimentation and interpretation.

Context:
- The repository demonstrates a synthetic retail and customer-transactions medallion architecture.
- The end-to-end path is synthetic sources -> Fabric pipeline -> bronze -> silver -> gold -> Direct Lake semantic model -> report.
- I want help with PySpark notebooks, validation logic, anomaly exploration, and experimental workflow framing.
- The response must stay portable across environments.

Constraints:
- Do not invent workspace IDs, item IDs, secrets, tokens, tenant names, or customer data.
- Use synthetic data only.
- Keep GitHub governance in mind: changes should be reviewable, explainable, and safe.
- If you suggest implementation detail, label assumptions and placeholders clearly.

Deliver:
1. notebook outline
2. data quality or experiment plan
3. assumptions and open questions
4. review points before execution

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

- [03 PySpark notebook generation](../scenarios/03-pyspark-notebook-generation.md)
- [04 Data quality validation](../scenarios/04-data-quality-validation.md)
- [08 Data lineage investigation](../scenarios/08-data-lineage-investigation.md)

## What Copilot should eliminate first

- repetitive scaffolding work
- first-draft documentation and explanation work
- option comparison and checklist drafting

## Related guidance

- [Prompt library README](../README.md)
- [Persona paths](../../docs/persona-paths.md)
