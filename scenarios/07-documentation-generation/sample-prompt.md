# Sample prompt

```text
Use scenarios/07-documentation-generation/input-manifest.json as the only source of truth.

Generate three separate GitHub-flavored Markdown documents:
1. A data dictionary for analytics consumers.
2. A pipeline runbook for operations.
3. Architecture notes for solution reviewers.

Requirements:
- Every document must begin with a clear notice that it is generated draft content pending human approval.
- Use the committed retail-purchases fixtures and actual Fabric artifact names from the manifest.
- Do not invent schedules, credentials, workspace IDs, or extra tables.
- Keep notebook, pipeline, Bronze, Silver, Gold, semantic-model, and report names exactly as provided.
- Turn technical metadata into readable prose, tables, and review checklists.
```

## Follow-up prompts

- "Rewrite the runbook to emphasize failure handling in the committed pipeline definition."
- "Condense the data dictionary into a customer-safe glossary."
- "Add an architecture review checklist focused on Direct Lake readiness."

## What work did Copilot eliminate?

The prompt removes the need to manually synthesize the retail-purchases metadata into three different documentation formats.
