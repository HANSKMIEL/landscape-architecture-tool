---
name: DOC1 Documentation & Ops Task
about: Maintain documentation, runbooks, and ops notes with MCP guardrails
title: "[DOC1] <concise summary>"
labels: ["scope:DOC1", "needs-triage"]
assignees: ""
---

## Summary

Describe the documentation or operations update and target audience.

## MCP Agent Coordination

- **Primary Agent**: <!-- e.g., MCP Documentation Agent -->
- **Secondary Guardrails Needed**: <!-- e.g., D1, B1, T1 -->
- **Coordination Notes**: <!-- Outline fact-checking or review steps with other agents -->

## Scope Checklist

- [ ] Reviewed `.github/copilot-instructions/documentation.md` and linked guardrails
- [ ] Identified affected guides (`docs/deployment/`, `docs/architecture/`, `_internal/`)
- [ ] Synced documentation with current branch context (V1.00D vs. main)
- [ ] Planned screenshots/diagrams and storage locations if needed

## Validation Plan

List every check required (spellcheck, linting, validation scripts, etc.):

- [ ] Markdown lint/spellcheck (if configured)
- [ ] Cross-reference with latest automation/scripts
- [ ] Stakeholder review notes captured (if applicable)

## Evidence & Artifacts

Link to PRs, rendered docs, or attachments demonstrating updates.

## Logging & Follow-up

- [ ] Updated `dev_log.md` with guardrail IDs, validations, and links
- [ ] Notified downstream teams of documentation changes
- [ ] Recorded MCP handoff notes if other guardrails must implement follow-on work

## Open Questions / Risks

List outstanding approvals, consistency checks, or conflicting sources.

---
Use the [MCP Agent Handoff Playbook](../../docs/development/mcp_agent_handoff.md) for multi-guardrail coordination.
