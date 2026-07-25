# Scenario 11 - GitHub Advanced Security safe workshop lab

## Business problem
A customer wants to demonstrate GitHub Advanced Security features for Fabric-adjacent Python and workflow code, but they do not want the default branch to contain live secrets, exploitable code, or intentionally vulnerable dependencies. The workshop needs safe assets that explain how to show CodeQL, dependency review, Dependabot, secret scanning, and push protection without turning the repository itself into a security liability.

## Target personas and prerequisites
- Security champion or platform engineer
- Workshop facilitator
- Repository admin managing GHAS and secret protection settings

Prerequisites:
- GitHub plan and licensing that include the features being demonstrated
- Repository or organization settings enabled for the selected features
- A disposable workshop branch for any live demo that requires applying a patch or generating a temporary secret outside the default branch

## Manual baseline or starting state
The default branch stays clean. The repository includes a safe parameterized query
baseline under [demo-app/](demo-app/), plus passive text fixtures and patches.
Facilitators apply an insecure patch only on a disposable branch during a live lab
and remove that branch after the demo.

## Copilot-assisted workflow
1. Use Copilot to explain which GHAS features are enabled in the customer's plan and what repository settings must exist first.
2. Review the safe query baseline under [demo-app/](demo-app/), then inspect the
   workshop assets under [demo-patches/](demo-patches/) and [fixtures/](fixtures/).
3. If a live lab is required, create a disposable workshop branch and run
   `git apply demo-patches/codeql-demo.patch` from this scenario directory.
4. Let CodeQL, dependency review, secret scanning, or push protection produce findings in that isolated branch or pull request.
5. Ask Copilot to help explain remediation options and draft the fix after the alert appears.
6. Delete the workshop branch or revert the demo change so the default branch remains clean.

## Feature and prerequisite notes
- **CodeQL**: Requires code scanning to be enabled. The committed
  [demo-app/query_service.py](demo-app/query_service.py) uses a parameterized query.
  Apply [demo-patches/codeql-demo.patch](demo-patches/codeql-demo.patch) only on a
  disposable branch to introduce an injection-style regression for scanning.
- **Dependency review**: Demonstrates pull request risk analysis. Use [demo-patches/dependency-review-demo.patch](demo-patches/dependency-review-demo.patch) and select a currently vulnerable advisory at demo time instead of committing an obsolete version now.
- **Dependabot**: Explain that Dependabot proposes updates after dependencies are in a supported manifest and the feature is enabled. It does not require the default branch to stay vulnerable.
- **Secret scanning and push protection**: These are settings and licensing features, not just workflow files. Use [fixtures/secret-scanning-demo.txt](fixtures/secret-scanning-demo.txt) as safe facilitator guidance and create any true test credential only outside the repository on a disposable branch.
- **Remediation with Copilot**: After an alert exists, Copilot can help explain the issue, suggest safer query patterns, or draft a fix PR. A human still validates the patch and security impact.

## Validation
Validate that the safe baseline remains parameterized and that the workshop patch
applies cleanly without being applied on the default branch.

```bash
git apply --check scenarios/11-github-advanced-security/demo-patches/codeql-demo.patch
pytest tests/test_security_baseline.py
```

Reviewers should confirm the default-branch Python baseline still uses a `?`
placeholder and that the insecure query exists only in the patch.

## Learning objectives
- Demonstrate GHAS features without storing live secrets or active vulnerabilities on the default branch.
- Explain which security controls come from repository settings, plan entitlements, or organization policies.
- Use Copilot to summarize findings and propose remediations after alerts are raised.
- Teach customers why disposable branches are safer than seeding the main branch with known-bad examples.

## Review checklist
- The scenario explains CodeQL, dependency review, Dependabot, secret scanning, and push protection.
- Licensing and enablement caveats are explicit.
- The committed Python baseline is safe, and the vulnerable change exists only in
  the disposable-branch patch.
- The CodeQL patch applies cleanly to the committed baseline.
- The dependency review patch tells facilitators to select a current advisory at demo time.
- The docs explain why the default branch remains clean.

## What work did Copilot eliminate?
Copilot removes the repetitive analysis and remediation narration: summarizing what an alert means, drafting safer replacement code, proposing follow-up review steps, and turning security findings into customer-readable guidance. Humans still control feature enablement, patch application, and remediation approval.
