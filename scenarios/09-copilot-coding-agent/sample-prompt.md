# Sample prompt

## Ready-to-copy prompt
```text
I am preparing a GitHub issue for Copilot Coding Agent. Read scenarios/09-copilot-coding-agent/issue/late-arriving-data.md plus the starter files under scenarios/09-copilot-coding-agent/starter/. Summarize the implementation plan, call out risky edge cases, and draft the pull request checks and review notes I should require before assigning the issue.
```

## Context supplied to Copilot
- The retail Silver load runs once per arrival date.
- Transactions can arrive up to two days late.
- Replayed files must not double count the same transaction ID.
- The example must stay deterministic and use Python stdlib only.

## Constraints and acceptance criteria
- Do not invent new infrastructure or external packages.
- Keep the change set small enough for a workshop review.
- Ensure the resulting PR updates tests with the behavior in the issue.
- Preserve a human review gate after the PR is opened.

## Follow-up prompts
```text
Turn the issue into a concise reviewer checklist that maps each acceptance criterion to a file and test.
```

```text
What repository settings or admin enablement caveats should I mention before telling a customer to assign this issue to Copilot?
```
