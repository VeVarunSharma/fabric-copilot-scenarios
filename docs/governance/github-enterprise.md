# GitHub Enterprise guidance

This repository demonstrates governance by example, but enterprise control points such as policy, access, review requirements, and feature enablement are applied in GitHub settings and organizational processes, not solely through committed files.

## Customer outcome

Help platform owners explain how GitHub can support faster Fabric delivery while preserving reviewability, traceability, and policy compliance.

## What this repository can show

- repository-structured prompts, docs, and scenario guidance
- examples of how checks, templates, and workflows can support governance
- recommended patterns for safe automation and approval boundaries
- documentation that helps teams know which settings must be turned on outside source control

## What must still be configured in GitHub

- repository visibility and access model
- branch protection or rulesets
- required reviewers and code owners
- environment approvals and deployment permissions
- GitHub Copilot seat assignment and policy enablement
- security feature enablement for the target repository or organization

## Recommended enterprise control stack

| Control area | Recommendation | Where it is actually configured |
| --- | --- | --- |
| Identity and access | Use least privilege, team-based ownership, and audited admin roles | GitHub organization and repository settings |
| Change management | Require pull requests, review, and required checks | GitHub repository settings or rulesets |
| Deployment safety | Use protected environments and approvals for production paths | GitHub Actions environments and repository settings |
| Copilot governance | Define allowed use, review expectations, and enablement scope | Organizational policy plus Copilot administration |
| Security visibility | Route alerts and ownership clearly | GitHub security settings, notification paths, and operational process |

## Plan and feature caveats

- GitHub feature availability varies by plan, repository visibility, and organization settings.
- Some controls are broadly available, while organization-scale governance features may require Team or Enterprise offerings.
- Repository-wide and organization-wide ruleset capabilities can differ. Validate the current product availability before promising a specific rollout path.
- GitHub Copilot features and coding-agent style capabilities require separate licensing and enablement decisions from core repository hosting.

## Recommended rollout conversation

1. Decide which Fabric repositories need enterprise controls first.
2. Identify the minimum review, approval, and evidence requirements.
3. Confirm which features are already licensed and enabled.
4. Use this repository's docs and prompts as a demonstration layer, not as proof that settings are already applied.

## Related guidance

- [GitHub Advanced Security guidance](github-advanced-security.md)
- [Repository rulesets](repository-rulesets.md)
- [Fabric deployment guidance](fabric-deployment.md)
