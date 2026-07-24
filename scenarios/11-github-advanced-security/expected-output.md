# Expected output

## Expected response shape
A strong answer should:
1. Distinguish passive workshop assets from active code on the default branch.
2. Explain what each GHAS feature demonstrates and what plan or setting prerequisites apply.
3. Show how Copilot can help interpret findings and draft remediations after alerts are produced.
4. End with cleanup guidance for the disposable branch.

## Canonical assets
- Safe CodeQL baseline: [demo-app/query_service.py](demo-app/query_service.py)
- CodeQL patch: [demo-patches/codeql-demo.patch](demo-patches/codeql-demo.patch)
- Dependency review patch: [demo-patches/dependency-review-demo.patch](demo-patches/dependency-review-demo.patch)
- Secret scanning guidance: [fixtures/secret-scanning-demo.txt](fixtures/secret-scanning-demo.txt)

## Important design choices
- The repository ships a safe parameterized Python baseline and passive workshop
  patches, not applied vulnerable code.
- The dependency review exercise uses a placeholder so facilitators can choose a currently vulnerable advisory at demo time.
- Secret-scanning guidance is intentionally non-secret and non-triggering.
- Dependabot is discussed as an ongoing remediation tool, not a reason to keep risky versions on the default branch.

## Review checklist
- Feature prerequisites and licensing caveats are clear.
- The path for applying and cleaning up workshop patches is explicit.
- The default branch safety rationale is easy for customers to repeat.
- Copilot remediation guidance is present but does not replace human review.
