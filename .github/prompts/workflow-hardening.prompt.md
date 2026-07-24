---
description: Harden a GitHub Actions workflow for least privilege, SHA pinning, and safe public-repo defaults.
mode: edit
tools:
  - codebase
---

Update the selected workflow to match this repository's governance standards.

Requirements:
- use GitHub-hosted runners
- set explicit least-privilege permissions
- pin every external action to a full commit SHA with a version comment
- avoid `pull_request_target` for untrusted code paths
- prefer OIDC over long-lived credentials
- fail clearly when required configuration is missing

After editing, summarize the security posture improvements.
