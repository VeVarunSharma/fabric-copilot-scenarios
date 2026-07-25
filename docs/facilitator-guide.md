# Facilitator guide

Use this guide to run a customer session that stays focused on outcomes, shows where Copilot removes work, and makes the human review boundary explicit.

## Facilitation principles

- Lead with the customer decision you want to improve.
- Show the baseline manual effort before showing the Copilot-assisted path.
- Keep the repository story connected from ingestion to report to governance.
- Treat prompts as working drafts that must be reviewed, not as auto-approved instructions.
- Use approved synthetic content and placeholders by default. Scenario 12 may
  use its reviewed, attributed, pinned public aggregate snapshot; do not extend
  that exception to other content or synthetic-only prompts.

## Core session roles

| Role | Responsibility |
| --- | --- |
| Facilitator | Keeps the story outcome-first and controls pace |
| Fabric practitioner | Explains the technical artifact and validates generated detail |
| GitHub practitioner | Explains review, automation, and security controls |
| Executive sponsor | Connects the demo to delivery speed, trust, and operating model |
| Scribe | Captures follow-ups, risks, and success signals |

## Session preparation

- Review the [architecture](architecture.md) and the selected [runbook](demo-runbooks/fabric-workshop.md).
- Pre-select the prompt guides you will copy from [prompts](../prompts/README.md).
- Confirm which governance topics are in scope: rulesets, security scanning, deployment approvals, or all three.
- Decide in advance which human review checkpoints you will call out.
- Keep a fallback path that uses placeholders and markdown only if live tooling is unavailable.

## Suggested facilitation pattern

### Phase 1: Frame the business problem

Explain the target outcome in one sentence. Example: "Reduce the time to build and validate a trusted Fabric analytics flow without lowering governance standards."

### Phase 2: Show the manual baseline

Describe the repetitive work the team normally performs:

- pipeline activity setup
- notebook scaffolding
- DAX boilerplate
- release checklist assembly
- documentation drafting

### Phase 3: Use a prompt pack

Copy a prompt from the persona or scenario library, add customer context, and highlight the acceptance criteria before running it.

### Phase 4: Review the result out loud

Ask the practitioner to separate:

- what is immediately useful
- what needs correction
- what still requires a human decision

### Phase 5: Close on governance and adoption

Reinforce that speed only matters if the repository remains reviewable, auditable, and safe.

## Facilitator checkpoints

- Did the audience hear what Copilot eliminated?
- Did the team inspect assumptions before accepting output?
- Did the story connect Fabric delivery with GitHub governance?
- Did the session avoid real customer data, secrets, and tenant details?
- If Scenario 12 used public data, did the team verify provenance, licence,
  attribution, checksum, and refresh review?
- Did the session end with specific follow-up actions?

## Choose the right runbook

- [Executive briefing](demo-runbooks/executive-briefing.md)
- [Fabric workshop](demo-runbooks/fabric-workshop.md)
- [GitHub Dev Day](demo-runbooks/github-dev-day.md)
- [Customer hackathon](demo-runbooks/customer-hackathon.md)
- [Data and AI accelerator](demo-runbooks/data-ai-accelerator.md)
- [BC CCHS Power BI demonstration](demo-runbooks/bc-cchs-power-bi.md)

## Common facilitation pivots

| If the audience asks for... | Pivot to... |
| --- | --- |
| Business value | [Executive briefing runbook](demo-runbooks/executive-briefing.md) |
| Hands-on delivery detail | [Fabric workshop runbook](demo-runbooks/fabric-workshop.md) |
| Power BI model and report authoring | [BC CCHS Power BI runbook](demo-runbooks/bc-cchs-power-bi.md) |
| Dev workflow and governance | [GitHub Dev Day runbook](demo-runbooks/github-dev-day.md) |
| Team problem solving | [Customer hackathon runbook](demo-runbooks/customer-hackathon.md) |
| Transformation roadmap | [Data and AI accelerator runbook](demo-runbooks/data-ai-accelerator.md) |

## Safety reminders

- [Data safety](governance/data-safety.md)
- [Troubleshooting](troubleshooting.md)
