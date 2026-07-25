# Fabric GitFlow vs. GitHub Copilot with Fabric MCP and Skills

Fabric Git-based CI/CD and GitHub Copilot with Fabric MCP servers and skills are complementary, not competing approaches.

- **Git-based CI/CD is the control system.**
- **Copilot, MCP servers, and skills are the productivity and automation layer.**

## Key differences

| Capability | Fabric with GitFlow or GitHub Flow | GitHub Copilot with Fabric MCP and skills |
|---|---|---|
| Primary purpose | Versioning, collaboration, CI/CD, and governance | AI-assisted creation, analysis, and operations |
| Source of truth | Git repository | Git and Fabric context supplied to the agent |
| Main capabilities | Branches, pull requests, approvals, history, rollback, and releases | Code generation, querying, documentation, troubleshooting, and tool execution |
| Production controls | Deterministic and auditable | Permission-dependent; generated output still requires review |
| Replaces the other approach? | No | No |

## How they work together

```text
Developer + Copilot and Fabric skills
                  |
                  v
Feature branch <-> isolated Fabric development workspace
                  |
                  v
Pull request + automated checks + human approval
                  |
                  v
Main or integration branch
                  |
                  v
Deployment pipeline -> Test -> Production
```

Fabric MCP servers give Copilot authenticated tools to inspect or modify Fabric resources. Fabric skills provide workload-specific instructions, patterns, and best practices. Neither replaces durable version history, pull-request approval, rollback, or controlled promotion between environments.

Conversely, GitFlow governs how changes are reviewed and released, but it does not intelligently generate, analyze, document, or operate those changes.

## Recommended approach

For most Fabric teams, use:

1. Git as the source of truth.
2. Short-lived feature branches.
3. An isolated Fabric development workspace for each active branch or developer.
4. Pull requests with automated checks and human approval.
5. A protected main or integration branch.
6. Fabric deployment pipelines or equivalent automation to promote changes through test and production.
7. Copilot, MCP servers, and skills to accelerate development, validation, documentation, and approved operations.

Restrict agent write access to development environments. Keep production access read-only or approval-gated, and require persistent changes to pass through Git and pull-request review.

## Should you use full GitFlow?

Traditional GitFlow uses long-lived `develop`, `release`, and `hotfix` branches. This can be appropriate when an organization has:

- Formal release trains
- Multiple supported production versions
- Strict regulatory or change-management gates
- A need to stabilize releases independently from ongoing development

For many Fabric teams, full GitFlow introduces unnecessary workspace and synchronization overhead because a Fabric workspace connects to a single branch. A lighter GitHub Flow or trunk-based model with short-lived feature branches is usually easier to operate.

## Decision summary

- **Use Git-based CI/CD alone** when AI-assisted development is unavailable or not permitted.
- **Use Copilot with Fabric MCP and skills alone** for exploration or temporary operational assistance, not as a substitute for production lifecycle management.
- **Use both together** for production development: Git provides governance and traceability, while Copilot, MCP, and skills improve speed and consistency.

## References

- [Fabric CI/CD concepts and best practices](https://learn.microsoft.com/fabric/fundamentals/understand-best-practices-fabric-cicd)
- [Microsoft Fabric Git integration](https://learn.microsoft.com/fabric/cicd/git-integration/intro-to-git-integration)
- [Skills for Microsoft Fabric](https://learn.microsoft.com/fabric/fundamentals/skills-for-fabric-overview)
- [Fabric Core MCP Server](https://learn.microsoft.com/rest/api/fabric/articles/mcp-servers/core-remote/get-started-core)
