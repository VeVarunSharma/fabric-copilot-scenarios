---
description: Create or improve DAX measures using repository conventions for readability and safe calculations.
mode: edit
tools:
  - codebase
---

Improve the selected semantic-model or DAX file.

Requirements:
- Use readable `VAR` blocks and `RETURN`.
- Prefer `DIVIDE` for ratio math.
- Keep business names, descriptions, format strings, and display folders consistent.
- Make time-intelligence assumptions explicit.
- Avoid unnecessary model churn outside the requested measure changes.

Summarize the business meaning of each changed measure.
