# Extension exercises

## Guided variations
1. Add reviewer notes that map each selected GitHub environment name (`dev`, `test`, `prod`) to its own `ENVIRONMENT` override and `FABRIC_WORKSPACE_NAME` override.
2. Extend the checklist with a pre-`run` data readiness gate for the documented `Files/landing/...` paths.
3. Add a rollback evidence section that records which item definitions were restored after a failed deploy or verify step.

## Persona-specific extensions
- **Fabric admin**: Add a short checklist proving the workspace is capacity-backed and `RetailLakehouse` is schema-enabled before approval.
- **Security lead**: Add a checklist of which GitHub environment variables must stay outside source control.
- **Release manager**: Add a go or no-go template that names the exact target workspace and required landing-file confirmation.

## Production-hardening exercises
- Define how the team verifies `inputs.environment` and `FABRIC_WORKSPACE_NAME` were both passed correctly before running `deploy` or `run`.
- Add a control that captures long-running operation request IDs in release evidence.
- Add an operational check that confirms fixture uploads are complete before any pipeline or notebook job is started.
