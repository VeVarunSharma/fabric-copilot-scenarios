---
applyTo: "pipelines/**/*"
---

- Preserve Fabric source-control structure, including `pipeline-content.json` and `.platform` files where required.
- Keep pipelines focused on orchestration, dependencies, retries, timeouts, and parameter flow.
- Resolve environment-specific identifiers at deployment time instead of committing tenant-specific values.
- Make success and failure paths explicit; do not rely on implicit ordering.
- Keep pipeline JSON stable, readable, and minimally changed when editing generated definitions.
