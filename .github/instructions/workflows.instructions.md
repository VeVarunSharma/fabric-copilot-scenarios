---
applyTo: ".github/workflows/**/*.yml,.github/workflows/**/*.yaml"
---

- Use GitHub-hosted runners only unless the task explicitly requires something else.
- Set explicit least-privilege `permissions` at workflow or job scope.
- Pin every external action to a full commit SHA and keep a version comment beside the pin.
- Prefer `pull_request` over `pull_request_target` for untrusted contribution paths.
- Use OIDC instead of long-lived cloud credentials and fail clearly when required configuration is missing.
