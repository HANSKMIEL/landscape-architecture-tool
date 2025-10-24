---
name: T1 Testing & Quality Task
about: Drive test coverage, linting, and quality gates with MCP guardrails
title: "[T1] <concise summary>"
labels: ["scope:T1", "needs-triage"]
assignees: ""
---

## Summary

Explain the testing/quality objective and areas of focus.

## MCP Agent Coordination

- **Primary Agent**: <!-- e.g., MCP QA Agent -->
- **Secondary Guardrails Needed**: <!-- e.g., B1, F1, D1 -->
- **Coordination Notes**: <!-- Note coordination with feature owners or deployment teams -->

## Scope Checklist

- [ ] Reviewed `.github/copilot-instructions/testing.md` and related guardrails
- [ ] Identified impacted fixtures, factories, or shared helpers
- [ ] Catalogued target flaky tests or coverage gaps
- [ ] Planned reporting format for results (issue comments, reports/, etc.)

## Validation Plan

List every command/output that must be produced before completion:

- [ ] `make backend-test`
- [ ] `make lint`
- [ ] `cd frontend` then `npm run test:run`

## Testing & Evidence

Attach logs, screenshots, or generated reports.

## Documentation & Logging

- [ ] Updated `dev_log.md` with guardrail IDs, validations, and links
- [ ] Added quality findings to `reports/` if substantial
- [ ] Logged MCP handoff notes if fixes route back to other guardrails

## Open Questions / Risks

Document persistent flakes, environment blockers, or follow-up work.

---
Use the [MCP Agent Handoff Playbook](../../docs/development/mcp_agent_handoff.md) to coordinate cross-category fixes.
