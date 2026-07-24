---
description: Review a Fabric pipeline definition for orchestration quality, resiliency, and safe parameterization.
mode: ask
tools:
  - codebase
---

Review the selected Fabric pipeline definition.

Check for:
- explicit dependencies and failure paths
- retry and timeout coverage where failures are realistic
- parameterized environment-specific values
- separation between orchestration logic and transformation logic
- readability, unnecessary churn, and customer-demo safety

Return prioritized findings and recommended edits only.
