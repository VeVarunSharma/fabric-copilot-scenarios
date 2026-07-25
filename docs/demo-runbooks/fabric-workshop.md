# Fabric workshop runbook

## Goals

- Help practitioners use prompt packs to accelerate Fabric delivery tasks.
- Show how medallion design, Direct Lake modeling, and governance fit together.
- Build confidence in human review practices for generated output.

## Best fit

Use this runbook for engineers, analysts, BI developers, architects, and mixed builder audiences who want a hands-on session.

## Flow

1. Start with the [getting started guide](../getting-started.md).
2. Walk through the [architecture](../architecture.md) and define the selected business outcome.
3. Split the room by persona and use the matching prompt guides.
4. Run one scenario from ingestion or notebook generation and one scenario from model, DAX, or documentation generation.
5. Compare generated drafts against acceptance criteria and discuss what still requires human correction.
6. Close with deployment and governance questions.

## Roles

- Lead facilitator
- Fabric subject matter expert
- GitHub workflow and governance guide
- Table leads for small-group prompt practice

## Setup

- Share the [prompt library](../../prompts/README.md).
- Keep the [placeholder images](../images/placeholders/README.md) ready in case live artifacts are unavailable.
- Choose the scenario prompt files that match the audience skill level.
- Agree on the no-secrets and safe-data boundary before prompting begins:
  synthetic data by default, with public aggregate data allowed only for an
  explicitly governed scenario such as the historical CCHS demonstration.

## Checkpoints

- Each group can explain the acceptance criteria they gave Copilot.
- Each group can identify at least one generated section they would reject or rewrite.
- The session surfaces a repeatable prompt pattern the customer can reuse.
- The audience understands how GitHub review and security controls fit after generation.

## Exit criteria

- Each persona leaves with a reusable prompt starter.
- The customer identifies one candidate repository or workstream for a pilot.
- Risks, missing artifacts, and admin dependencies are captured for follow-up.
