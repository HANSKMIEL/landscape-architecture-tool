---
name: F1 Frontend Development Task
about: Manage frontend/UI work with MCP guardrails
title: "[F1] <concise summary>"
labels: ["scope:F1", "needs-triage"]
assignees: ""
---

## Summary

Describe the UI/UX change, affected components, and goals.

## MCP Agent Coordination

- **Primary Agent**: <!-- e.g., MCP Frontend Agent -->
- **Secondary Guardrails Needed**: <!-- e.g., B1, DOC1, T1 -->
- **Coordination Notes**: <!-- Outline collaboration with backend or docs agents -->

## Scope Checklist

- [ ] Reviewed `.github/copilot-instructions/frontend.md` and linked guardrails
- [ ] Audited `frontend/src/services/api.js` contracts for compatibility
- [ ] Identified affected components/pages/layouts and localization files
- [ ] Planned accessibility and responsive design validations

## Validation Plan

List every command/output that must be produced before completion:

- [ ] `cd frontend` then `npm run test:run`
- [ ] `cd frontend` then `npm run build`
- [ ] Visual regression or manual UI verification notes attached

## Testing & Evidence

Attach screenshots, recordings, or test logs demonstrating the change.

## Documentation & Logging

- [ ] Updated `dev_log.md` with guardrail IDs, validations, and links
- [ ] Updated relevant docs or product briefs in `docs/development/`
- [ ] Captured MCP handoff details if backend or QA agents participate

## Open Questions / Risks

List API dependencies, design approvals, or launch-blocking issues.

---
Use the [MCP Agent Handoff Playbook](../../docs/development/mcp_agent_handoff.md) for cross-category collaboration.
