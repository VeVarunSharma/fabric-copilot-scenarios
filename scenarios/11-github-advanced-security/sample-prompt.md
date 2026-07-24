# Sample prompt

## Ready-to-copy prompt
```text
I need a safe GitHub Advanced Security workshop for this repository. Read scenarios/11-github-advanced-security/ and explain how to demonstrate CodeQL, dependency review, Dependabot, secret scanning, and push protection without leaving active vulnerabilities or real secrets on the default branch. Include licensing and repository-setting caveats, then outline how Copilot can help remediate findings after alerts appear.
```

## Context supplied to Copilot
- The repository must remain safe on the default branch.
- Workshop assets can only be passive `.patch` or `.txt` files.
- Any live demo happens on a disposable branch with human approval.

## Constraints and acceptance criteria
- Do not recommend committing real credentials.
- Do not pin an intentionally vulnerable package version in the default branch.
- Explain the difference between source-controlled assets and repository settings.
- Include a cleanup step so the workshop branch does not persist.

## Follow-up prompts
```text
Draft a short facilitator script for applying the CodeQL patch on a disposable branch and then asking Copilot for a remediation summary.
```

```text
What should I verify in licensing, security settings, and branch protections before promising this workshop to a customer?
```
