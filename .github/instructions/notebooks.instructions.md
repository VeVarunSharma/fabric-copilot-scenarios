---
applyTo: "notebooks/**/*.ipynb"
---

- Keep notebooks valid as `nbformat` v4 JSON with populated `metadata`, `execution_count`, and `outputs` fields.
- Use explicit Spark schemas, deterministic sample data handling, and Delta read/write patterns.
- Include validation cells or assertions for important transformations, row-shape checks, or quality rules.
- Parameterize environment-specific values; never hardcode workspace, lakehouse, or secret material.
- Prefer small, readable cells with structured logging over monolithic notebook scripts.
