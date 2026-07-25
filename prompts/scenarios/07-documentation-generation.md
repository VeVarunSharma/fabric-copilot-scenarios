# 07 Documentation generation prompt pack

## Customer outcome

Generate first-draft customer documentation from repository context without losing technical accuracy.

## Best when the customer asks for

- work in the area of data dictionaries, runbooks, architecture narrative, and artifact explanation
- a strong first draft that still preserves human review
- clear explanation of what GitHub Copilot removes from the manual workflow

## Copy-ready prompt

```text
You are helping me with the repository scenario "07 Documentation generation".

Business outcome:
Generate first-draft customer documentation from repository context without losing technical accuracy.

Context:
- Domain: retail purchases and analytics repository documentation
- Architecture backbone: synthetic retail sources -> Fabric pipeline -> bronze -> silver -> gold -> Direct Lake semantic model -> report scaffold
- The repository is customer-facing and portable.
- GitHub governance and security matter as much as artifact quality.

Constraints:
- Use only synthetic or placeholder data.
- Do not invent workspace IDs, item IDs, credentials, or customer details.
- Label assumptions and placeholders clearly.
- Emphasize what the human reviewer must still validate.

Deliver:
1. documentation outline
2. key sections
3. review risks
4. acceptance checklist

Acceptance criteria:
- the draft stays customer-facing and safe
- links and artifact references are explicit
- human review responsibilities are visible
- the answer states what Copilot eliminated

End with:
- the work GitHub Copilot eliminated
- the human review checklist
- open questions that should be resolved before implementation or approval
```

## Context worth pasting into Copilot

- the target persona
- the business goal for the scenario
- approved file excerpts or artifact descriptions
- constraints on environment portability and governance

## Human review required

- technical correctness
- audience fit
- link accuracy
- overclaiming of implemented settings

## Related guidance

- [Prompt library README](../README.md)
- [Artifact reference](../../docs/artifact-reference.md)
- [Architecture](../../docs/architecture.md)
