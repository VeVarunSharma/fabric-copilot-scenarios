---
applyTo: "semantic-models/**/*.tmdl,semantic-models/**/*.dax,semantic-models/**/*.json,semantic-models/**/*.pbip"
---

- Model analytics data as a clean star schema unless the surrounding scenario explicitly teaches a different pattern.
- Hide technical keys, describe business measures, and keep display folders and format strings consistent.
- Use readable DAX with `VAR` blocks, `RETURN`, `DIVIDE`, and explicit filter intent.
- Keep TMDL and PBIP artifacts source-control friendly; avoid churn in unrelated sections.
- Do not imply live Fabric IDs, credentials, or tenant metadata belong in versioned semantic-model files.
