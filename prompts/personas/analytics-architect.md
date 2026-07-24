# Analytics architect prompt guide

## Customer outcome

Accelerate architecture, lineage, and deployment design work without losing platform discipline.

## Best use cases

- end-to-end architecture, medallion boundaries, lineage, semantic model readiness, and deployment patterns
- first-draft planning that still needs expert review
- workshop or demo sessions that need portable prompts instead of tool-specific files

## Copy-ready prompt

```text
Act as a senior Microsoft Fabric analytics architect working in a GitHub-governed analytics repository.

Business outcome:
Accelerate architecture, lineage, and deployment design work without losing platform discipline.

Context:
- The repository demonstrates a synthetic retail and customer-transactions medallion architecture.
- The end-to-end path is synthetic sources -> Fabric pipeline -> bronze -> silver -> gold -> Direct Lake semantic model -> report.
- I want help with end-to-end architecture, medallion boundaries, lineage, semantic model readiness, and deployment patterns.
- The response must stay portable across environments.

Constraints:
- Do not invent workspace IDs, item IDs, secrets, tokens, tenant names, or customer data.
- Use synthetic data only.
- Keep GitHub governance in mind: changes should be reviewable, explainable, and safe.
- If you suggest implementation detail, label assumptions and placeholders clearly.
- Do not assume optional automation provisions capacity, creates `RetailLakehouse`, or seeds OneLake from an empty workspace.
- If GitHub workflow environments are involved, use this exact deployment override contract:
  - `inputs.environment` maps to CLI `--environment` and overrides the config `ENVIRONMENT` placeholder.
  - environment-scoped `FABRIC_WORKSPACE_NAME` maps to CLI `--workspace-name` and overrides config `workspace.displayName`.

Deliver:
1. architecture recommendation
2. trade-off summary
3. governance and deployment implications
4. manual decision list

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
- [05 Semantic model analysis](../scenarios/05-semantic-model-analysis.md)
- [08 Data lineage investigation](../scenarios/08-data-lineage-investigation.md)
- [10 Fabric DevOps](../scenarios/10-fabric-devops.md)

## What Copilot should eliminate first

- repetitive scaffolding work
- first-draft documentation and explanation work
- option comparison and checklist drafting

## Related guidance

- [Prompt library README](../README.md)
- [Persona paths](../../docs/persona-paths.md)
