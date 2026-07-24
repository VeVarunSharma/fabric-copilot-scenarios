# 09 Copilot coding agent prompt pack

## Customer outcome

Frame a coding task so Copilot can help implement a bounded analytics change safely.

## Best when the customer asks for

- work in the area of issue framing, acceptance criteria, implementation plan, and review expectations
- a strong first draft that still preserves human review
- clear explanation of what GitHub Copilot removes from the manual workflow

## Copy-ready prompt

```text
You are helping me with the repository scenario "09 Copilot coding agent".

Business outcome:
Frame a coding task so Copilot can help implement a bounded analytics change safely.

Context:
- Domain: late-arriving retail data handling
- Architecture backbone: synthetic sources -> Fabric pipeline -> bronze -> silver -> gold -> Direct Lake semantic model -> report
- The repository is customer-facing and portable.
- GitHub governance and security matter as much as artifact quality.

Constraints:
- Use only synthetic or placeholder data.
- Do not invent workspace IDs, item IDs, credentials, or customer details.
- Label assumptions and placeholders clearly.
- Emphasize what the human reviewer must still validate.

Deliver:
1. issue draft
2. implementation plan
3. test or validation expectations
4. review checklist

Acceptance criteria:
- scope is specific and reviewable
- acceptance criteria are measurable
- human approval boundaries are explicit
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

- scope creep risk
- test coverage needs
- documentation updates
- merge readiness

## Related guidance

- [Prompt library README](../README.md)
- [Artifact reference](../../docs/artifact-reference.md)
- [Architecture](../../docs/architecture.md)
