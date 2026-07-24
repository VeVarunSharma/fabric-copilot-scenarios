# Security policy

## Supported content baseline

| Branch or content line | Status |
| --- | --- |
| `main` | Supported and expected to remain free of real secrets and intentionally vulnerable runtime content |
| Workshop or demo branches | Best effort; keep unsafe exercises opt-in and clearly labeled |
| Personal forks | Maintainer support not guaranteed |

## Reporting a vulnerability

Please do **not** open a public issue for suspected vulnerabilities.

Preferred reporting path:

1. Use GitHub private vulnerability reporting if it is enabled for this repository.
2. Otherwise, contact the repository maintainers through your organization's approved security reporting channel.
3. Include reproduction details, affected paths, impact, and suggested mitigations if known.

If you are adopting this repository for your organization, replace this section with your real disclosure workflow before broad distribution.

## Security baseline for this repository

- No real secrets, customer data, PHI, or PII belong in source control.
- Use synthetic data and obviously fictional identifiers by default. Explicitly
  reviewed, non-sensitive public aggregate/open data is permitted only as a
  pinned snapshot with provenance, licence and attribution, checksum, and
  human-reviewed refresh.
- The public-data exception never permits customer, tenant, person-level, PII,
  PHI, credential, confidential, or otherwise sensitive content. Synthetic
  fixture and synthetic-only prompt guarantees remain unchanged.
- Prefer Azure OIDC federation or equivalent short-lived identity patterns over stored cloud credentials.
- Keep environment-specific values in GitHub environment variables, secrets, or deployment-time discovery rather than committed files.
- Do not use `pull_request_target` for untrusted pull-request execution paths.
- Pin GitHub Actions to full commit SHAs.

## GitHub feature prerequisites and licensing notes

GitHub feature availability changes over time. Verify current licensing and product documentation before rollout.

| Capability | Public repositories | Private/internal repositories |
| --- | --- | --- |
| CodeQL code scanning | Generally available for public open source repositories | Commonly requires GitHub Advanced Security or GitHub Code Security, plus organization enablement |
| Dependency review | Commonly available on pull requests | Availability may depend on GitHub Advanced Security or equivalent organization settings |
| Dependabot version and security updates | Broadly available | Availability and policy can vary by plan and organization configuration |
| Secret scanning and push protection | Public exposure scanning is broadly available; enforcement options vary | Private-repository coverage and custom pattern enforcement typically require GitHub Secret Protection or equivalent entitlements |
| Copilot Coding Agent and related Copilot features | Separate Copilot licensing and policy controls apply | Separate Copilot licensing and organization enablement apply |

## Controls that cannot be enforced only from source control

The following still require GitHub or cloud configuration outside this repository:

- enabling CodeQL, secret scanning, push protection, private vulnerability reporting, and Dependabot alerts where licensing permits
- creating repository rulesets, required checks, and approval policies
- configuring GitHub environments and required reviewers
- creating Azure federated credentials for OIDC-based deployment

Document these prerequisites in implementation or onboarding materials rather than implying they happen automatically.
