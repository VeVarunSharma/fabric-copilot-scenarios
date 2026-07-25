# Data safety

Safe customer demos depend on disciplined prompt inputs, synthetic data by
default, and clear human review before any generated output is reused.

## Customer outcome

Help teams demonstrate Copilot and Fabric value without exposing customer data, secrets, regulated records, or misleading screenshots.

## Safety rules for this repository

- Use deterministic synthetic data by default.
- Do not place real credentials, tokens, keys, or connection strings in prompts, docs, or screenshots.
- Do not paste customer records, PHI, PII, or confidential contracts into Copilot prompts.
- Keep screenshots sanitized and approved before publication.
- Label placeholders clearly until approved visuals exist.

## Narrow public-data exception

Explicitly reviewed public aggregate/open data may be committed only when all of
these controls are present:

- the data is non-sensitive and contains no customer, tenant, person-level, PII,
  PHI, credential, confidential, or restricted content
- the exact source snapshot is pinned, and every transformation is deterministic
  and documented
- provenance identifies the catalogue, resource, retrieval time, and schema
- licence terms, required attribution, byte size, and checksum are recorded
- refresh automation validates the contract and requires human diff review

This exception does not change the fictional-data guarantees in
`datasets/synthetic/` or any persona/scenario prompt that intentionally says
synthetic only.

Current governed sources are listed in
[`datasets/README.md`](../../datasets/README.md). Scenario 12 uses only
aggregated historical Statistics Canada CCHS estimates; it excludes
respondent-level records and requires the source attribution, quality symbols,
and 2022 comparability warning to remain visible.

## Prompt hygiene checklist

Before you prompt:

- remove tenant-specific names if they are sensitive
- replace live identifiers with placeholders
- confirm that any sample values are synthetic
- state that the answer must not invent secrets or production IDs

After you prompt:

- review the output for hallucinated identifiers
- remove any unnecessary environment detail before sharing
- validate that generated examples do not imply live customer access

## Screenshot handling

- Use the placeholder set in `docs/images/placeholders/` until approved screenshots are available.
- Crop or blur identifiers if you later replace placeholders with real captures from an authorized demo tenant.
- Keep captions outcome-focused rather than tenant-specific.

## Governance reminder

Secret scanning, push protection, and repository policies can help reduce risk, but safe behavior starts before content is committed. Human review is still required.

## Related guidance

- [GitHub Advanced Security guidance](github-advanced-security.md)
- [Fabric deployment guidance](fabric-deployment.md)
- [Getting started](../getting-started.md)
