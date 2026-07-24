# 03 PySpark notebook generation prompt pack

## Customer outcome

Create a Fabric-ready notebook outline for ingesting and transforming synthetic IoT telemetry or retail data.

## Best when the customer asks for

- work in the area of schema definition, transformations, Delta writes, logging, and validation cells
- a strong first draft that still preserves human review
- clear explanation of what GitHub Copilot removes from the manual workflow

## Copy-ready prompt

```text
You are helping me with the repository scenario "03 PySpark notebook generation".

Business outcome:
Create a Fabric-ready notebook outline for ingesting and transforming synthetic IoT telemetry or retail data.

Context:
- Domain: IoT telemetry and retail medallion processing
- Architecture backbone: synthetic sources -> Fabric pipeline -> bronze -> silver -> gold -> Direct Lake semantic model -> report
- The repository is customer-facing and portable.
- GitHub governance and security matter as much as artifact quality.

Constraints:
- Use only synthetic or placeholder data.
- Do not invent workspace IDs, item IDs, credentials, or customer details.
- Label assumptions and placeholders clearly.
- Emphasize what the human reviewer must still validate.

Deliver:
1. notebook structure
2. transformation plan
3. logging and validation guidance
4. review checklist

Acceptance criteria:
- explicit schemas are used
- bronze-to-silver or silver-to-gold logic is clear
- no live identifiers are invented
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

- schema accuracy
- partition strategy
- late-arriving-data assumptions
- idempotency logic

## Related guidance

- [Prompt library README](../README.md)
- [Artifact reference](../../docs/artifact-reference.md)
- [Architecture](../../docs/architecture.md)
