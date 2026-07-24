# Persona paths

These role-based paths help customers find the fastest route to value while keeping prompts grounded in accepted constraints and human review.

## Persona matrix

| Persona | Primary customer outcome | Best first prompt | What Copilot helps eliminate | Start here |
| --- | --- | --- | --- | --- |
| Data engineer | Faster pipeline and notebook scaffolding with operational guardrails | Pipeline, notebook, and quality prompts | Boilerplate activity wiring, schema setup, and logging scaffolds | [Data engineer prompt guide](../prompts/personas/data-engineer.md) |
| Data analyst | Faster SQL, metric explanation, and documentation drafts | SQL optimization and documentation prompts | Repetitive query tuning notes and report narrative drafting | [Data analyst prompt guide](../prompts/personas/data-analyst.md) |
| BI developer | Better semantic models, measures, report metadata, and accessible visuals | Semantic model, DAX, and CCHS Power BI prompts | Measure scaffolding, naming drafts, model inventory, and visual-definition wiring | [BI developer prompt guide](../prompts/personas/bi-developer.md) |
| Data scientist | Faster experimental notebook setup and data quality exploration | Notebook and quality prompts | Notebook skeletons, validation steps, and experiment framing | [Data scientist prompt guide](../prompts/personas/data-scientist.md) |
| Analytics architect | Clearer end-to-end design and operating model decisions | Architecture, lineage, and deployment prompts | Cross-artifact mapping, option comparison, and design narrative drafting | [Analytics architect prompt guide](../prompts/personas/analytics-architect.md) |
| Fabric administrator | Safer deployment, environment readiness, and governance alignment | Deployment and GHAS prompts | Environment checklist assembly and policy explanation drafts | [Fabric administrator prompt guide](../prompts/personas/fabric-administrator.md) |

## Suggested journey by role

### Data engineer

- Read [architecture](architecture.md)
- Use [01 data pipeline generation](../prompts/scenarios/01-data-pipeline-generation.md) and [03 notebook generation](../prompts/scenarios/03-pyspark-notebook-generation.md)
- Close with [troubleshooting](troubleshooting.md)

### Data analyst

- Start with [02 SQL optimization](../prompts/scenarios/02-sql-optimization.md)
- Add [07 documentation generation](../prompts/scenarios/07-documentation-generation.md)
- Review [artifact reference](artifact-reference.md)

### BI developer

- Start with [05 semantic model analysis](../prompts/scenarios/05-semantic-model-analysis.md)
- Continue with [06 DAX generation](../prompts/scenarios/06-dax-generation.md)
- Practice the end-to-end public-data workflow with [12 CCHS Power BI authoring](../prompts/scenarios/12-cchs-power-bi-authoring.md)
- Review [architecture](architecture.md)

### Data scientist

- Start with [03 notebook generation](../prompts/scenarios/03-pyspark-notebook-generation.md)
- Add [04 data quality validation](../prompts/scenarios/04-data-quality-validation.md)
- Review [data safety](governance/data-safety.md)

### Analytics architect

- Start with [08 data lineage investigation](../prompts/scenarios/08-data-lineage-investigation.md)
- Add [10 Fabric DevOps](../prompts/scenarios/10-fabric-devops.md)
- Review [Fabric deployment guidance](governance/fabric-deployment.md)

### Fabric administrator

- Start with [10 Fabric DevOps](../prompts/scenarios/10-fabric-devops.md)
- Add [11 GitHub Advanced Security](../prompts/scenarios/11-github-advanced-security.md)
- Review [GitHub Enterprise guidance](governance/github-enterprise.md)

## Human review boundary

Every persona should validate:

- assumptions that Copilot made from limited context
- environment-specific details such as workspace names, rulesets, permissions, and IDs
- licensing and feature availability claims
- business definitions, measure logic, and data quality thresholds

## Related content

- [Getting started](getting-started.md)
- [Prompt library](../prompts/README.md)
- [Runbooks](facilitator-guide.md)
