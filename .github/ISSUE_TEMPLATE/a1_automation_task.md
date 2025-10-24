---
name: A1 Automation & Integration Task
about: Coordinate n8n and webhook work with MCP agents and guardrails
title: "[A1] <concise summary>"
labels: ["scope:A1", "needs-triage"]
assignees: ""
---

## Summary

Outline the automation or integration change, including impacted workflows or receivers.

## MCP Agent Coordination

- **Primary Agent**: <!-- e.g., MCP Automation Agent -->
- **Secondary Guardrails Needed**: <!-- e.g., B1, T1 -->
- **Coordination Notes**: <!-- Describe sync points with other agents -->

## Scope Checklist

- [ ] Reviewed `.github/copilot-instructions/automation.md` and referenced guardrails
- [ ] Identified affected n8n workflows (`n8n-workflows/`) and export requirements
- [ ] Mapped payload/contracts to Flask receivers (`src/routes/n8n_receivers.py`)
- [ ] Planned background/offline processing for long-running tasks

## Validation Plan

List every command/output that must be produced before completion:

- [ ] `python -m pytest tests/routes/test_n8n_receivers.py`
- [ ] Contract validation against sample payloads
- [ ] Updated documentation in `_internal/n8n-workflows/`

## Testing & Evidence

Attach workflow exports, contract diffs, and test logs.

## Documentation & Logging

- [ ] Updated `dev_log.md` with guardrail IDs, validations, and links
- [ ] Documented integration touchpoints and operator notes
- [ ] Captured handoff steps in MCP handoff log if work transfers

## Open Questions / Risks

List remaining integration gaps, secrets, or performance concerns that need follow-up.

---
Use the [MCP Agent Handoff Playbook](../../docs/development/mcp_agent_handoff.md) when routing work to another specialty.
