# GitHub Dev Day runbook

## Goals

- Show how GitHub Copilot improves day-to-day analytics delivery work.
- Connect prompt engineering with pull request review, automation, and security signals.
- Demonstrate that developer speed and enterprise governance can reinforce each other.

## Best fit

Use this runbook for developer audiences that want a repository-centric story with a strong GitHub workflow angle.

## Flow

1. Frame the repository as the delivery system for Fabric artifacts, prompts, and documentation.
2. Show one builder-focused scenario such as pipeline generation or notebook generation.
3. Show one governance-focused scenario such as Fabric DevOps or GitHub Advanced Security.
4. Discuss how rulesets, reviews, checks, and alerts create safe acceleration.
5. End with a practical prompt pattern that the audience can reuse in their own repositories.

## Roles

- GitHub platform presenter
- Fabric delivery presenter
- Reviewer who critiques generated output live

## Setup

- Review [GitHub Enterprise guidance](../governance/github-enterprise.md).
- Review [GHAS guidance](../governance/github-advanced-security.md).
- Pick prompt examples from [scenario prompts](../../prompts/scenarios/README.md).
- Keep [repository rulesets guidance](../governance/repository-rulesets.md) available for policy questions.

## Checkpoints

- The audience can see how prompts become reviewable repository artifacts.
- The audience understands that rulesets and security features are configured in GitHub settings and validated by process.
- The audience can distinguish draft generation from approved production change.

## Exit criteria

- The customer identifies one GitHub workflow improvement and one Fabric delivery improvement.
- Review owners know which checks or controls must be enabled outside the repository.
- The session produces at least one reusable prompt or checklist for internal adoption.
