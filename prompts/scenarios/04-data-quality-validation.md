# 04 Data quality validation prompt pack

## Customer outcome

Draft repeatable quality rules and quarantine handling for synthetic healthcare claims or customer transactions.

## Best when the customer asks for

- work in the area of rule definitions, invalid-record handling, summary reporting, and test thinking
- a strong first draft that still preserves human review
- clear explanation of what GitHub Copilot removes from the manual workflow

## Copy-ready prompt

```text
You are helping me with the repository scenario "04 Data quality validation".

Business outcome:
Draft repeatable quality rules and quarantine handling for synthetic healthcare claims or customer transactions.

Context:
- Domain: synthetic healthcare claims and customer transactions
- Architecture backbone: synthetic sources -> Fabric pipeline -> bronze -> silver -> gold -> Direct Lake semantic model -> report
- The repository is customer-facing and portable.
- GitHub governance and security matter as much as artifact quality.

Constraints:
- Use only synthetic or placeholder data.
- Do not invent workspace IDs, item IDs, credentials, or customer details.
- Label assumptions and placeholders clearly.
- Emphasize what the human reviewer must still validate.

Deliver:
1. quality-rule set
2. quarantine approach
3. summary-report pattern
4. review checklist

Acceptance criteria:
- rules are explicit and reviewable
- quarantine behavior is defined
- summary metrics are named
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

- threshold selection
- false-positive risk
- owner for failed-record review
- fit with downstream reporting

## Related guidance

- [Prompt library README](../README.md)
- [Artifact reference](../../docs/artifact-reference.md)
- [Architecture](../../docs/architecture.md)
