# Repository instructions for GitHub Copilot

This repository demonstrates Microsoft Fabric delivery patterns with GitHub Copilot. Optimize for customer-ready clarity, deterministic sample assets, and safe public-demo defaults.

## Fabric implementation rules

- Prefer explicit schemas over inference for Spark, notebooks, ingestion code, and semantic metadata.
- Use Bronze/Silver/Gold or equivalent layered naming when the artifact represents medallion processing.
- Treat Delta Lake as the default table format for lakehouse transformations unless the surrounding artifact explicitly requires something else.
- Preserve idempotency, retry safety, incremental processing, and parameterized environment selection.
- Never hardcode workspace IDs, lakehouse IDs, item IDs, tenant-specific URLs, or secrets into source-controlled files.
- Keep pipeline definitions focused on orchestration. Put transformation logic in notebooks or Python modules, not inline expressions that become unreadable.
- Prefer structured logging, deterministic sample outputs, and clear validation steps over clever but opaque shortcuts.

## Data safety and security

- Use synthetic or obviously fictional data by default. The only exception is
  explicitly reviewed, non-sensitive public aggregate/open data with a pinned
  snapshot, provenance, licence and attribution, checksum, and human-reviewed
  refresh. Never introduce customer, tenant, employee, person-level, PHI, PII,
  credential, or confidential data.
- Preserve synthetic fixture guarantees and any persona or scenario prompt that
  intentionally requires synthetic-only inputs; the public-data exception does
  not loosen those contracts.
- Do not add real secrets, connection strings, SAS tokens, PATs, certificates, client secrets, JWTs, or anything that resembles a live credential.
- Prefer OIDC or managed identity patterns over long-lived credentials in documentation and workflows.
- Keep intentionally insecure examples off the default branch unless they are inert text fixtures or opt-in workshop patches with clear warnings.

## Semantic model and DAX conventions

- Keep semantic models source-controlled in PBIP/TMDL-friendly layouts.
- Favor star schemas, single-direction relationships, hidden technical keys, clear measure descriptions, display folders, and consistent format strings.
- Write DAX measures with readable `VAR` blocks, `DIVIDE` for safe division, and concise comments only when the business rule is non-obvious.
- Make time-intelligence assumptions explicit. Do not imply a date table exists unless it is defined in the model.

## Testing and validation

- Add or update the smallest relevant validation for every material change.
- Keep notebook, pipeline, semantic-model, workflow, and prompt files syntactically valid.
- Preserve the scenario contract: each scenario must explain the business problem, Copilot-assisted workflow, validation, and the exact heading `What work did Copilot eliminate?`.
- When adding automation, prefer fast targeted checks first, then broader validation only when needed.

## Documentation style

- Write for customers, field sellers, architects, and workshop participants.
- Keep documentation concise, actionable, and specific to Microsoft Fabric and GitHub usage in this repository.
- Explain assumptions, prerequisites, and licensing or enablement requirements whenever a feature depends on GitHub plan, Fabric capacity, or organization settings.
- Avoid filler, marketing hype, and unexplained placeholders.
