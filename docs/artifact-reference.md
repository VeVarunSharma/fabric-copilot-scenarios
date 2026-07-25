# Artifact reference

This reference explains the role each repository area plays in the customer story. Use it when you need to connect a prompt to a concrete artifact family or explain how a change moves through the analytics lifecycle.

## Repository artifact map

| Repository path | Purpose | Customer value | What Copilot helps eliminate |
| --- | --- | --- | --- |
| `datasets/` | Deterministic synthetic fixtures plus specifically governed public aggregate snapshots | Safe demos with realistic shape, provenance, and repeatability | Manual sample-data invention, normalization, and cleanup |
| `pipelines/` | Fabric orchestration definitions | Repeatable ingestion and transformation control | Boilerplate activity wiring and retry setup |
| `notebooks/` | PySpark and validation logic | Reusable transformation and quality patterns | Notebook skeleton setup and repetitive code blocks |
| `semantic-models/` | Direct Lake and Import-mode PBIP model/report assets | Faster analytics consumption and clearer semantics | Measure scaffolding, model documentation, and report-definition wiring |
| `scenarios/` | Guided scenario walkthroughs | Role-based storytelling and practice | Rewriting the same workshop instructions for every audience |
| `.github/` | Automation, policy, templates, and instructions | Safer delivery and review evidence | Manual governance coordination |
| `docs/` | Customer-ready navigation and governance guidance | Faster onboarding and stronger demo consistency | First-draft documentation work |
| `prompts/` | Portable prompt library | Reusable prompt patterns across tools and events | Rebuilding prompts from scratch for every session |
| `scripts/` | Validation, generation, and deployment helpers | Repeatable execution patterns | One-off local shell steps and brittle manual deployment |
| `tests/` | Contract, syntax, and behavior checks | Trust in the repository before demo use | Manual spot checking alone |

## How to use this reference

- Use a persona prompt when the customer starts with a role.
- Use a scenario prompt when the customer starts with a work item.
- Use [architecture](architecture.md) when the customer asks how pieces connect.
- Use [Fabric deployment guidance](governance/fabric-deployment.md) when the customer asks what must happen outside source control.
- Treat deployment helpers as automation for an existing target workspace, not as a blank-environment bootstrap.

## Deployment assumptions that matter

- The target workspace must already be capacity-backed.
- A schema-enabled `RetailLakehouse` must already exist.
- Synthetic files must already be uploaded under:
  - `Files/landing/retail-purchases`
  - `Files/landing/iot-telemetry`
  - `Files/landing/healthcare-claims`
- Deployment override contract:
  - `inputs.environment` maps to CLI `--environment` and overrides the config `ENVIRONMENT` placeholder.
  - environment-scoped `FABRIC_WORKSPACE_NAME` maps to CLI `--workspace-name` and overrides config `workspace.displayName`.

## Evidence customers usually want

| Question | Best artifact family to reference |
| --- | --- |
| How does data move end to end? | `pipelines/`, `notebooks/`, `semantic-models/`, and [architecture](architecture.md) |
| How do you keep prompts portable? | `prompts/` and [prompt library README](../prompts/README.md) |
| How do you govern releases? | `.github/` and [GitHub governance docs](governance/github-enterprise.md) |
| How do you keep the demo safe? | `datasets/` and [data safety](governance/data-safety.md) |

## Review reminder

The paths shown above reflect the current repository layout. Human reviewers should still confirm that the linked artifacts and guidance stay aligned as implementation details evolve.
