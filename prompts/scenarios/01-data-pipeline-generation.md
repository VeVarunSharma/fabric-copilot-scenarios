# 01 Data pipeline generation prompt pack

## Customer outcome

Produce a first-draft Fabric orchestration design for synthetic retail purchases and customer transactions.

## Best when the customer asks for

- work in the area of pipeline structure, parameters, retries, failure handling, and notebook handoffs
- a strong first draft that still preserves human review
- clear explanation of what GitHub Copilot removes from the manual workflow

## Copy-ready prompt

```text
You are helping me with the repository scenario "01 Data pipeline generation".

Business outcome:
Produce a first-draft Fabric orchestration design for synthetic retail purchases and customer transactions.

Context:
- Domain: retail purchases and customer transactions
- Architecture backbone: synthetic sources -> Fabric pipeline -> bronze -> silver -> gold -> Direct Lake semantic model -> report
- The repository is customer-facing and portable.
- GitHub governance and security matter as much as artifact quality.

Constraints:
- Use only synthetic or placeholder data.
- Do not invent workspace IDs, item IDs, credentials, or customer details.
- Label assumptions and placeholders clearly.
- Emphasize what the human reviewer must still validate.

Deliver:
1. recommended pipeline design
2. activity breakdown
3. parameter and retry strategy
4. validation and review checklist

Acceptance criteria:
- bronze, silver, and gold are represented
- no hardcoded IDs or secrets appear
- failure handling and retries are explicit
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

- activity dependencies
- naming conventions
- operational thresholds
- environment parameter model

## Related guidance

- [Prompt library README](../README.md)
- [Artifact reference](../../docs/artifact-reference.md)
- [Architecture](../../docs/architecture.md)
