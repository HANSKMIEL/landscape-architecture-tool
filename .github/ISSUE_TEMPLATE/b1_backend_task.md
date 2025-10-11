---
name: B1 Backend Development Task
about: Guide backend-focused work using MCP guardrails
title: "[B1] <concise summary>"
labels: ["scope:B1", "needs-triage"]
assignees: ""
---

## Summary

Describe the backend change and affected routes/services/models.

## MCP Agent Coordination

- **Primary Agent**: <!-- e.g., MCP Backend Agent -->
- **Secondary Guardrails Needed**: <!-- e.g., F1, DT1, T1 -->
- **Coordination Notes**: <!-- Note alignment steps with other agents -->

## Scope Checklist

- [ ] Reviewed `.github/copilot-instructions/backend.md` and linked guardrails
- [ ] Identified affected routes, services, schemas, and models
- [ ] Planned migrations/fixtures updates if schema changes occur
- [ ] Synced response shape expectations with `frontend/src/services/api.js`

## Validation Plan

List every command/output that must be produced before completion:

- [ ] `python -m pytest tests/routes tests/services`
- [ ] `python -m pytest tests/test_dependency_validator_import.py`
- [ ] Alembic migration scripts tested (`flask --app src.main db migrate`, `db upgrade --sql`)

## Testing & Evidence

Attach test logs, migration previews, and contract confirmations.

## Documentation & Logging

- [ ] Updated `dev_log.md` with guardrail IDs, validations, and links
- [ ] Updated API documentation or schemas if response shapes changed
- [ ] Recorded MCP handoff details when sharing work across agents

## Open Questions / Risks

Track blockers, dependency updates, or rollout considerations.

---
Use the [MCP Agent Handoff Playbook](../../docs/development/mcp_agent_handoff.md) for multi-guardrail work.
