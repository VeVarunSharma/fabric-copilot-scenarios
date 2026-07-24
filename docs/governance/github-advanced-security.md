# GitHub Advanced Security guidance

GitHub security features help teams protect analytics repositories, but they are not enabled only by committing workflow files. Alerts, scanning, and protection settings are surfaced and managed in GitHub itself.

## Customer outcome

Show how security signals can reduce release risk while keeping Copilot-assisted development practical for Fabric teams.

## Security capabilities to explain

| Capability | Why it matters to Fabric work | Important caveat |
| --- | --- | --- |
| Dependency graph | Shows what packages and actions the repository depends on | Available broadly, but still must be enabled and reviewed in GitHub |
| Dependabot alerts and security updates | Helps spot and remediate known vulnerable dependencies | Feature behavior varies by plan and repository type |
| Dependabot version updates | Keeps dependencies current and reduces drift | Config files can request updates, but GitHub still executes and manages them |
| Code scanning | Helps find code risks in Python, workflows, and other supported content | Private and internal repository coverage may require GitHub Code Security or equivalent licensing |
| Secret scanning | Detects leaked credentials in git history and other supported surfaces | Often requires GitHub Secret Protection for private or internal use cases, while many public-repo scenarios are covered at no cost |
| Push protection | Helps stop secrets before they land in the repository | Requires explicit enablement where available |

## Accurate positioning for customer conversations

- Some GitHub security features are available on all plans.
- Additional GitHub Code Security and GitHub Secret Protection capabilities are commonly licensed at the organization level.
- Public repositories can use a broader free security feature set than many private or internal repositories.
- Secret scanning and related alerts live in the GitHub security experience and settings, not only in YAML.

## Safe workshop pattern

- Use synthetic data only.
- Do not place live secrets in sample files, even for a demonstration.
- If you want to teach remediation, use text explanations or opt-in patch exercises on a non-default branch.
- Keep the default branch free of intentionally exploitable content.

## Human review checklist

- Confirm which security features are licensed and enabled for the target organization.
- Confirm alert ownership and response workflow.
- Review generated fixes before merge.
- Verify workflow permissions and action pinning rules separately from prompt content.

## Related guidance

- [GitHub Enterprise guidance](github-enterprise.md)
- [Repository rulesets](repository-rulesets.md)
- [Data safety](data-safety.md)
