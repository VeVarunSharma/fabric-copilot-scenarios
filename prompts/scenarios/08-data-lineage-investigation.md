# 08 Data lineage investigation prompt pack

## Customer outcome

Explain upstream and downstream dependencies faster when a data model or pipeline change is proposed.

## Best when the customer asks for

- work in the area of cross-artifact dependency tracing, impact analysis, and visual explanation
- a strong first draft that still preserves human review
- clear explanation of what GitHub Copilot removes from the manual workflow

## Copy-ready prompt

```text
You are helping me with the repository scenario "08 Data lineage investigation".

Business outcome:
Explain upstream and downstream dependencies faster when a data model or pipeline change is proposed.

Context:
- Domain: retail medallion lineage and downstream impact
- Architecture backbone: synthetic sources -> Fabric pipeline -> bronze -> silver -> gold -> Direct Lake semantic model -> report
- The repository is customer-facing and portable.
- GitHub governance and security matter as much as artifact quality.

Constraints:
- Use only synthetic or placeholder data.
- Do not invent workspace IDs, item IDs, credentials, or customer details.
- Label assumptions and placeholders clearly.
- Emphasize what the human reviewer must still validate.

Deliver:
1. lineage summary
2. downstream impact list
3. diagram guidance
4. review checklist

Acceptance criteria:
- upstream and downstream paths are clear
- change impact is discussed in business terms
- unknowns are called out
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

- missing lineage edges
- semantic model dependencies
- pipeline parameter effects
- documentation gaps

## Related guidance

- [Prompt library README](../README.md)
- [Artifact reference](../../docs/artifact-reference.md)
- [Architecture](../../docs/architecture.md)
