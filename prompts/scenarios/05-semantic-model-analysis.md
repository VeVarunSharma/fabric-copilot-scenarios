# 05 Semantic model analysis prompt pack

## Customer outcome

Review a Direct Lake semantic model design and identify practical improvements for analytics readiness.

## Best when the customer asks for

- work in the area of star schema quality, hidden keys, descriptions, relationships, measures, and usability
- a strong first draft that still preserves human review
- clear explanation of what GitHub Copilot removes from the manual workflow

## Copy-ready prompt

```text
You are helping me with the repository scenario "05 Semantic model analysis".

Business outcome:
Review a Direct Lake semantic model design and identify practical improvements for analytics readiness.

Context:
- Domain: retail sales semantic modeling
- Architecture backbone: synthetic sources -> Fabric pipeline -> bronze -> silver -> gold -> Direct Lake semantic model -> report
- The repository is customer-facing and portable.
- GitHub governance and security matter as much as artifact quality.

Constraints:
- Use only synthetic or placeholder data.
- Do not invent workspace IDs, item IDs, credentials, or customer details.
- Label assumptions and placeholders clearly.
- Emphasize what the human reviewer must still validate.

Deliver:
1. model assessment
2. improvement recommendations
3. priority order
4. review checklist

Acceptance criteria:
- recommendations align to Direct Lake and star-schema best practices
- customer-facing usability is addressed
- manual review points remain explicit
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

- relationship directions
- date intelligence assumptions
- measure naming
- model governance metadata

## Related guidance

- [Prompt library README](../README.md)
- [Artifact reference](../../docs/artifact-reference.md)
- [Architecture](../../docs/architecture.md)
