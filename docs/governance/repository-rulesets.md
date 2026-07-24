# Repository rulesets

Rulesets are a strong way to govern how people interact with branches and tags, but they are configured in GitHub settings or APIs. A markdown file can document a recommended ruleset; it does not apply the policy by itself.

## Customer outcome

Help customers understand how to keep prompt-assisted repository changes safe, reviewable, and consistent.

## Recommended ruleset posture

| Rule area | Recommendation | Reason |
| --- | --- | --- |
| Pull request required | Require pull requests for protected branches | Keeps generated content reviewable |
| Required checks | Require validation and security checks before merge | Prevents fast-but-unsafe merges |
| Review count | Require at least one informed reviewer, more for production paths | Preserves human accountability |
| Force push restriction | Block force pushes to protected branches | Keeps history auditable |
| Deletion restriction | Block branch deletion for primary branches | Reduces accidental loss |
| Signed commit or verified source policy | Use where required by enterprise policy | Strengthens provenance |
| Push restrictions | Limit who can bypass key controls | Avoids accidental policy gaps |

## Important caveats

- Repository rulesets and organization-wide rulesets do not have identical availability across every GitHub plan.
- Repository-level controls may be available before organization-scale targeting features.
- Always verify the current GitHub documentation for the target subscription before promising exact enforcement scope.

## Recommended implementation model

1. Document the desired ruleset in the repository.
2. Apply it in GitHub settings or through approved administration tooling.
3. Validate that the required checks and bypass lists match the documented intent.
4. Review exceptions regularly.

## Demo talking points

- Copilot speeds up authoring, but rulesets slow down unsafe merging in the right places.
- Prompt quality does not replace branch governance.
- Rulesets are especially useful when multiple personas contribute docs, notebooks, workflows, and model changes in one repository.

## Related guidance

- [GitHub Enterprise guidance](github-enterprise.md)
- [GitHub Advanced Security guidance](github-advanced-security.md)
