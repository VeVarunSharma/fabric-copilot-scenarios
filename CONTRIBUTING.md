# Contributing

Thank you for helping improve this Microsoft Fabric and GitHub Copilot demo repository.

## Contribution goals

Prioritize contributions that keep the repository:

- customer-ready and easy to demo
- safe for a public default branch
- faithful to Microsoft Fabric source formats and operational patterns
- clear about what GitHub Copilot eliminates versus what still needs human review

## Required contribution standards

- Use synthetic or fictional data by default. A narrow exception is allowed for
  explicitly reviewed, non-sensitive public aggregate/open data when the
  committed snapshot is pinned and includes provenance, licence and attribution,
  checksum, and a human-reviewed refresh process.
- Preserve all guarantees for `datasets/synthetic/` and do not loosen persona or
  scenario prompts that intentionally require synthetic-only inputs.
- Never commit customer, tenant, person-level, PII, PHI, credential,
  confidential, or otherwise sensitive data under the public-data exception.
- Do not commit secrets, credentials, workspace IDs, tenant-specific endpoints, or long-lived tokens.
- Prefer explicit schemas, Delta-friendly patterns, and parameterized environment configuration.
- Keep customer-facing documentation concise and concrete.
- Update the smallest relevant validation or test coverage for each meaningful change.
- Preserve the standard scenario contract, including the exact heading `What work did Copilot eliminate?`.

## Pull request process

1. Scope the change to a clear artifact, scenario, or governance task.
2. Update related documentation when behavior, prerequisites, or operating guidance changes.
3. Run the relevant validation commands before requesting review.
4. Summarize the customer impact, validation, and follow-up work in the pull request template.

## CODEOWNERS placeholder

`.github/CODEOWNERS` is intentionally committed as a commented template so the default repository does not contain invalid active ownership rules.

Before enabling required CODEOWNERS review enforcement, uncomment the example entries and replace the placeholder with a real write-capable GitHub user or team from your organization. The template is documentation only and is not a credential.

## Repository settings that must be configured manually

The following controls are important, but they are **not** applied by files in this repository:

- branch protection or rulesets for `main`
- required status checks such as `Validate repository content`, `Analyze (python)`, `Analyze (actions)`, and `Review dependency changes`
- required reviewers or CODEOWNERS review enforcement
- environment protection rules and approval gates for `dev`, `test`, and `prod`
- secret scanning, push protection, Dependabot alerts, and private vulnerability reporting enablement
- GitHub Copilot feature enablement, including Coding Agent access where applicable

Document any required settings changes in pull requests when relevant.

## Recommended GitHub governance baseline

For customer demos and workshop environments, maintainers should:

- protect `main` with pull-request-only changes
- require passing validation, CodeQL, and dependency review checks
- replace placeholder owners in CODEOWNERS before enforcing review rules
- use GitHub environments for deployment approvals and environment-specific variables
- use Azure OIDC federation instead of stored cloud credentials

## Support boundaries

This repository is sample content for demos, workshops, and field enablement. Contributions should avoid promises of production support, SLA-backed operations, or tenant-specific customization unless that material is explicitly added elsewhere.
