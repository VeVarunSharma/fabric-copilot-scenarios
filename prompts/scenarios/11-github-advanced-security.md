# 11 GitHub Advanced Security prompt pack

## Customer outcome

Explain a safe security posture for a Fabric analytics repository and identify likely gaps.

## Best when the customer asks for

- work in the area of dependency risk, secret exposure, code scanning, policy explanation, and remediation planning
- a strong first draft that still preserves human review
- clear explanation of what GitHub Copilot removes from the manual workflow

## Copy-ready prompt

```text
You are helping me with the repository scenario "11 GitHub Advanced Security".

Business outcome:
Explain a safe security posture for a Fabric analytics repository and identify likely gaps.

Context:
- Domain: repository security and governance
- Architecture backbone: synthetic sources -> Fabric pipeline -> bronze -> silver -> gold -> Direct Lake semantic model -> report
- The repository is customer-facing and portable.
- GitHub governance and security matter as much as artifact quality.

Constraints:
- Use only synthetic or placeholder data.
- Do not invent workspace IDs, item IDs, credentials, or customer details.
- Label assumptions and placeholders clearly.
- Emphasize what the human reviewer must still validate.

Deliver:
1. security posture summary
2. recommended control stack
3. licensing or enablement caveats
4. review checklist

Acceptance criteria:
- the answer distinguishes files from GitHub settings
- plan and visibility caveats are stated
- safe workshop practices are preserved
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

- actual feature enablement
- alert ownership
- branch governance alignment
- workshop safety

## Related guidance

- [Prompt library README](../README.md)
- [Artifact reference](../../docs/artifact-reference.md)
- [Architecture](../../docs/architecture.md)
