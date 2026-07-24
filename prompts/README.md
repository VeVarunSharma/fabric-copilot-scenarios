# Portable prompt library

This prompt library is designed to be copied into GitHub Copilot, chat tools, or workshop materials without depending on IDE-specific prompt-file features. Each prompt emphasizes customer outcomes, explicit constraints, acceptance criteria, and human review.

## How to use these prompts

1. Start with the role or scenario that matches the customer outcome.
2. Add only approved synthetic context or a specifically reviewed aggregate public dataset with documented provenance, licence, attribution, and limitations.
3. Keep the constraints block intact unless you have a better, reviewed alternative.
4. Ask Copilot to show assumptions and open questions.
5. Review the result before reusing any code, DAX, workflow step, or governance recommendation.

## Prompt design rules

- State the business outcome first.
- Tell Copilot which artifacts it may reference.
- Ban hardcoded IDs, secrets, and customer data.
- Require acceptance criteria and a human review checklist.
- Ask Copilot to explain what work it eliminated.

## Persona guides

- [Data engineer](personas/data-engineer.md)
- [Data analyst](personas/data-analyst.md)
- [BI developer](personas/bi-developer.md)
- [Data scientist](personas/data-scientist.md)
- [Analytics architect](personas/analytics-architect.md)
- [Fabric administrator](personas/fabric-administrator.md)

## Scenario prompt packs

- [Scenario index](scenarios/README.md)
- [01 Data pipeline generation](scenarios/01-data-pipeline-generation.md)
- [02 SQL optimization](scenarios/02-sql-optimization.md)
- [03 PySpark notebook generation](scenarios/03-pyspark-notebook-generation.md)
- [04 Data quality validation](scenarios/04-data-quality-validation.md)
- [05 Semantic model analysis](scenarios/05-semantic-model-analysis.md)
- [06 DAX generation](scenarios/06-dax-generation.md)
- [07 Documentation generation](scenarios/07-documentation-generation.md)
- [08 Data lineage investigation](scenarios/08-data-lineage-investigation.md)
- [09 Copilot coding agent](scenarios/09-copilot-coding-agent.md)
- [10 Fabric DevOps](scenarios/10-fabric-devops.md)
- [11 GitHub Advanced Security](scenarios/11-github-advanced-security.md)
- [12 CCHS Power BI authoring](scenarios/12-cchs-power-bi-authoring.md)

## Related docs

- [Getting started](../docs/getting-started.md)
- [Persona paths](../docs/persona-paths.md)
- [Troubleshooting](../docs/troubleshooting.md)
