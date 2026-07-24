# 06 DAX generation prompt pack

## Customer outcome

Draft measures and validation steps for retail and finance KPIs faster.

## Best when the customer asks for

- work in the area of measure scaffolding, safe division, time intelligence, format strings, and descriptions
- a strong first draft that still preserves human review
- clear explanation of what GitHub Copilot removes from the manual workflow

## Copy-ready prompt

```text
You are helping me with the repository scenario "06 DAX generation".

Business outcome:
Draft measures and validation steps for retail and finance KPIs faster.

Context:
- Domain: retail and financial KPI analysis
- Architecture backbone: synthetic sources -> Fabric pipeline -> bronze -> silver -> gold -> Direct Lake semantic model -> report
- The repository is customer-facing and portable.
- GitHub governance and security matter as much as artifact quality.

Constraints:
- Use only synthetic or placeholder data.
- Do not invent workspace IDs, item IDs, credentials, or customer details.
- Label assumptions and placeholders clearly.
- Emphasize what the human reviewer must still validate.

Deliver:
1. measure draft set
2. measure explanations
3. validation-query ideas
4. review checklist

Acceptance criteria:
- measures are business-oriented and clearly named
- formatting and descriptions are addressed
- validation steps are included
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

- business logic correctness
- calendar assumptions
- filter-context behavior
- format string choices

## Related guidance

- [Prompt library README](../README.md)
- [Artifact reference](../../docs/artifact-reference.md)
- [Architecture](../../docs/architecture.md)
