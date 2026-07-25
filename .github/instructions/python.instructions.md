---
applyTo: "**/*.py"
---

- Target clear, typed, testable Python suitable for validation scripts, dataset generation, and deployment helpers.
- Prefer explicit function boundaries, small helpers, standard library usage, and deterministic behavior.
- Never log tokens, secrets, or raw authentication headers.
- Use pathlib-friendly paths, descriptive error messages, and exit behavior that works well in CI.
- Add or update focused tests whenever Python behavior changes.
