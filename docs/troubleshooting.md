# Troubleshooting

Use this guide when prompts become too generic, when governance claims sound stronger than the implementation, or when a demo needs a safe fallback path.

## Common issues

| Symptom | Likely cause | What to do next |
| --- | --- | --- |
| Copilot returns generic Fabric advice | The prompt did not include the business outcome, constraints, or acceptance criteria | Start with a persona or scenario prompt from [prompts](../prompts/README.md) and add concrete constraints |
| Generated steps include hardcoded workspace IDs or secrets | The prompt did not forbid live identifiers | Restate that the repository must stay portable and that IDs are resolved at deploy time |
| The audience thinks rulesets or secret scanning come only from files | Governance settings were described without the GitHub settings boundary | Use [repository rulesets](governance/repository-rulesets.md) and [GHAS guidance](governance/github-advanced-security.md) |
| The customer asks whether the placeholders are real screenshots | The placeholder purpose was not explained | Use [placeholder guidance](images/placeholders/README.md) and say they are deliberate stand-ins for approved captures |
| A prompt produces too much code too early | The request skipped design and review steps | Ask Copilot for options, assumptions, and a checklist before asking for implementation detail |
| A deployment answer assumes live tenant access | The prompt lacked an environment boundary | Redirect to [Fabric deployment guidance](governance/fabric-deployment.md) and keep the discussion at design level |
| A deployment answer implies the workflow can start from a blank workspace | The prerequisites were not stated clearly enough | Restate that automation does not provision capacity, create `RetailLakehouse`, or seed OneLake, and that landing files must already exist under the documented `Files/landing/...` paths |
| A workflow appears to target the wrong environment or workspace | The deployment override contract was not applied correctly | Check that `inputs.environment` maps to CLI `--environment` and overrides the config `ENVIRONMENT` placeholder, and that environment-scoped `FABRIC_WORKSPACE_NAME` maps to CLI `--workspace-name` and overrides config `workspace.displayName` |

## Prompt tuning moves that work well

- Add the target persona.
- State the customer outcome in one sentence.
- List the artifacts Copilot may reference.
- Ban hardcoded IDs, credentials, and tenant-specific assumptions.
- State whether `RetailLakehouse` and the landing-file paths already exist.
- Demand acceptance criteria and a human review checklist.
- Ask Copilot to explain what work it eliminated.

## Safe fallback paths

If live tooling or unfinished artifacts are unavailable, you can still run a strong session by using:

- [architecture](architecture.md)
- [persona paths](persona-paths.md)
- [runbooks](facilitator-guide.md)
- [prompt packs](../prompts/scenarios/README.md)
- [placeholder screenshots](images/placeholders/README.md)

## Escalation questions for the human team

- Does this answer depend on a feature that may vary by GitHub plan or repository visibility?
- Does this step require a Fabric admin, GitHub org admin, or security owner?
- Is the generated DAX, SQL, or notebook logic business-correct?
- Should this output remain a draft until a named owner reviews it?
