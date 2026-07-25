# Data engineer prompt guide

## Customer outcome

Stand up reliable medallion pipelines and notebooks faster without hardcoding environment details.

## Best use cases

- pipeline definitions, notebook scaffolding, schema handling, retries, logging, and late-arriving data
- first-draft planning that still needs expert review
- workshop or demo sessions that need portable prompts instead of tool-specific files

## Copy-ready prompt

```text
Act as a senior Microsoft Fabric data engineer working in a GitHub-governed analytics repository.

Business outcome:
Stand up reliable medallion pipelines and notebooks faster without hardcoding environment details.

Context:
- The repository demonstrates a synthetic retail and customer-transactions medallion architecture.
- The end-to-end path is synthetic sources -> Fabric pipeline -> bronze -> silver -> gold -> Direct Lake semantic model -> report.
- I want help with pipeline definitions, notebook scaffolding, schema handling, retries, logging, and late-arriving data.
- The response must stay portable across environments.

Constraints:
- Do not invent workspace IDs, item IDs, secrets, tokens, tenant names, or customer data.
- Use synthetic data only.
- Keep GitHub governance in mind: changes should be reviewable, explainable, and safe.
- If you suggest implementation detail, label assumptions and placeholders clearly.
- Assume deployment automation does not provision capacity, create `RetailLakehouse`, or seed OneLake.
- Assume synthetic files must already exist under `Files/landing/retail-purchases`, `Files/landing/iot-telemetry`, and `Files/landing/healthcare-claims`.

Deliver:
1. pipeline or notebook design
2. parameter and configuration strategy
3. validation and operational checks
4. risks and manual review points

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

- [01 Data pipeline generation](../scenarios/01-data-pipeline-generation.md)
- [03 PySpark notebook generation](../scenarios/03-pyspark-notebook-generation.md)
- [04 Data quality validation](../scenarios/04-data-quality-validation.md)
- [10 Fabric DevOps](../scenarios/10-fabric-devops.md)

## What Copilot should eliminate first

- repetitive scaffolding work
- first-draft documentation and explanation work
- option comparison and checklist drafting

## Related guidance

- [Prompt library README](../README.md)
- [Persona paths](../../docs/persona-paths.md)
