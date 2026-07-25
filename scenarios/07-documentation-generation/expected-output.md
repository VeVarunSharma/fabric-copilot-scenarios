# Expected output

A strong Copilot result should create readable, artifact-accurate draft documentation.

## Expected deliverables

| Document | Audience | Must include |
| --- | --- | --- |
| Data dictionary | Analytics consumers | Retail fixture fields, curated table purposes, and semantic-model consumption notes. |
| Pipeline runbook | Operations and on-call teams | Actual pipeline activities, notebook stages, parameters, and failure-path notes. |
| Architecture notes | Architects and technical leads | Retail-purchases sources, medallion flow, Gold semantic-model sources, and the report-scaffold dependency. |

## Canonical outputs

- [generated/data-dictionary.md](generated/data-dictionary.md)
- [generated/pipeline-runbook.md](generated/pipeline-runbook.md)
- [generated/architecture-notes.md](generated/architecture-notes.md)

## Review checklist

- [ ] Each document includes a draft notice.
- [ ] Generated content stays grounded in the manifest.
- [ ] Artifact names match the committed repository.
- [ ] Semantic-model notes reference only the four Gold source tables actually used.
- [ ] The Markdown is polished and customer-safe.

## Validation

Compare every artifact reference with [input-manifest.json](input-manifest.json) and have the relevant owner approve the wording before publication.

## What work did Copilot eliminate?

Copilot eliminated the repetitive first draft and let reviewers spend time on accuracy and approval instead of formatting.
