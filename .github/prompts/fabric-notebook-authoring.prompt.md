---
description: Draft or refine a Fabric notebook with explicit schemas, Delta-safe writes, and validation cells.
mode: edit
tools:
  - codebase
---

Update the selected Fabric notebook for this repository.

Requirements:
- Keep the file valid as an `.ipynb` notebook.
- Use explicit Spark schemas instead of schema inference.
- Prefer Delta Lake reads and writes with deterministic, idempotent logic.
- Add concise structured logging and at least one validation cell for the important transformation outcome.
- Do not hardcode workspace IDs, lakehouse IDs, secrets, or tenant-specific URLs.
- Keep comments brief and customer-friendly.

Explain the key changes after editing.
