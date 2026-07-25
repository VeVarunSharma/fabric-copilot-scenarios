# Scenario 09 - Copilot Coding Agent for late-arriving retail data

## Business problem
A retail analytics team reruns its daily Silver load whenever stores resend files. The current Python transformation only keeps transactions whose business date exactly matches the batch date, so late-arriving transactions are dropped and replayed files can double count revenue. The team wants a clear issue that a human can assign to GitHub Copilot Coding Agent so the first pull request already includes code, tests, and a small documentation update.

## Target personas and prerequisites
- Data engineer maintaining Python-based retail ingestion logic
- GitHub repository administrator or maintainer configuring Copilot Coding Agent access
- Reviewer who understands the Fabric retail medallion flow

Prerequisites:
- GitHub Copilot with Coding Agent available for the repository plan and region
- A repository administrator has enabled the feature where required
- Required pull request checks are defined before anyone assigns the issue

## Manual baseline or starting state
The starter implementation under [starter/](starter/) only keeps same-day business records. It does not preserve late-arriving transactions that land within an allowed grace window, and it does not deduplicate replayed transaction IDs idempotently.

## Copilot-assisted workflow
1. A human files or refines [issue/late-arriving-data.md](issue/late-arriving-data.md) until the acceptance criteria and test plan are specific.
2. A repository admin confirms that Copilot Coding Agent is enabled for the org or repo if that setting is required in the customer's tenant. This scenario documents the flow but does not invoke an agent.
3. A maintainer assigns the issue to Copilot from GitHub. Copilot opens a branch and a pull request against the starter files.
4. Required checks run against the generated changes. For this scenario, the expected Python target is shown in [expected/](expected/).
5. A human reviewer compares the PR to the issue, validates the tests, checks naming and edge cases, and decides whether to merge.
6. If the PR is acceptable, the human merges it and closes the issue. If not, the human leaves review comments and asks Copilot or another engineer to revise the change.

This is the customer-facing flow to explain in workshops: assign to Copilot -> PR opens -> checks run -> human review decides. The scenario intentionally stops at documentation and sample code.

## Scenario artifacts
- Structured issue: [issue/late-arriving-data.md](issue/late-arriving-data.md)
- Baseline files for the agent to modify: [starter/retail_transactions.py](starter/retail_transactions.py) and [starter/test_retail_transactions.py](starter/test_retail_transactions.py)
- Expected post-PR result: [expected/retail_transactions.py](expected/retail_transactions.py) and [expected/test_retail_transactions.py](expected/test_retail_transactions.py)
- Ready-to-copy prompt: [sample-prompt.md](sample-prompt.md)
- Human review guidance: [expected-output.md](expected-output.md)
- Stretch work: [extension-exercises.md](extension-exercises.md)

## Validation
Run the starter and expected tests separately so reviewers can see the current baseline and the intended enhanced state.

```bash
python3 -m unittest discover -s scenarios/09-copilot-coding-agent/starter -p 'test_*.py'
python3 -m unittest discover -s scenarios/09-copilot-coding-agent/expected -p 'test_*.py'
```

## Learning objectives
- Write issue descriptions that are specific enough for a coding agent to execute safely.
- Turn data engineering acceptance criteria into deterministic unit tests.
- Explain when humans still own approvals, reviews, and merge decisions.
- Recognize the admin enablement and repository policy caveats around Coding Agent rollout.

## Review checklist
- The issue states the problem, scope, acceptance criteria, and non-goals clearly.
- The starter files are small, deterministic, and stdlib-only.
- The expected files include late-arrival handling and idempotent deduplication.
- Validation commands are copyable and run locally.
- The documentation explains assign-to-Copilot -> PR -> checks -> human review without claiming the scenario actually invoked an agent.

## What work did Copilot eliminate?
Copilot removes the repetitive first draft work: translating the issue into code changes, updating tests for the new behavior, writing the initial PR summary, and narrating which acceptance criteria were met. Humans still decide the scope, review the generated diff, and control merge approval.
