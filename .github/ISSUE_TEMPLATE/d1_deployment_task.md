---
name: D1 Deployment & Infrastructure Task
about: Plan and track deployment/infrastructure work with MCP agents and guardrails
title: "[D1] <concise summary>"
labels: ["scope:D1", "needs-triage"]
assignees: ""
---

## Summary
Provide a short description of the deployment or infrastructure change and its objective.

## MCP Agent Coordination

- **Primary Agent**: <!-- e.g., MCP Deployment Agent -->
- **Secondary Guardrails Needed**: <!-- e.g., T1, DOC1 -->
- **Coordination Notes**: <!-- Outline planned touchpoints with secondary agents -->

## Scope Checklist

- [ ] Reviewed `.github/copilot-instructions/deployment.md` and linked guardrails
- [ ] Determined required secrets (`VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, etc.)
- [ ] Identified affected scripts/workflows (`scripts/deployment/`, `.github/workflows/`)
- [ ] Documented fallback/rollback steps if deployment fails

## Validation Plan

List every command/output that must be produced before completion (copy from guardrails as needed):

- [ ] `python -m pytest tests/test_dependency_validator_import.py`
- [ ] `cd frontend` then `npm run build`
- [ ] Manual smoke test for `http://72.60.176.200:8080` and `/health`

## Testing & Evidence

Paste links, logs, or attach files showing each validation result.

## Documentation & Logging

- [ ] Updated `dev_log.md` with guardrail IDs, validations, and links
- [ ] Updated relevant runbooks under `docs/deployment/`
- [ ] Added/updated MCP handoff notes if work transfers to another agent

## Open Questions / Risks

Enumerate blockers, approvals, or risk items. Tag owners where collaboration is needed.

---
Use the [MCP Agent Handoff Playbook](../../docs/development/mcp_agent_handoff.md) when handing over to another specialty.
