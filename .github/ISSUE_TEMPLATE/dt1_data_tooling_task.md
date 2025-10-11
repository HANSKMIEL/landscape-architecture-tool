---
name: DT1 Data Ingestion & Tooling Task
about: Coordinate data import/tooling improvements with MCP guardrails
title: "[DT1] <concise summary>"
labels: ["scope:DT1", "needs-triage"]
assignees: ""
---

## Summary

Summarize the data pipeline/tooling change and expected outcomes.

## MCP Agent Coordination

- **Primary Agent**: <!-- e.g., MCP Data Tooling Agent -->
- **Secondary Guardrails Needed**: <!-- e.g., B1, T1, DOC1 -->
- **Coordination Notes**: <!-- Note downstream consumers or follow-on agents -->

## Scope Checklist

- [ ] Reviewed `.github/copilot-instructions/data_tooling.md` and related guardrails
- [ ] Documented input formats, column mappings, and validation rules
- [ ] Planned fixture updates and deduplication handling
- [ ] Assessed performance/memory considerations for large files

## Validation Plan

List every command/output that must be produced before completion:

- [ ] `python -m pytest tests/test_excel_import.py tests/fixtures/test_stability.py`
- [ ] Sample import dry-run with representative data attached
- [ ] Cleanup verification for temporary files and artifacts

## Testing & Evidence

Attach run logs, fixture diffs, and sample data outputs.

## Documentation & Logging

- [ ] Updated `dev_log.md` with guardrail IDs, validations, and links
- [ ] Updated operator docs in `docs/development/` if processes changed
- [ ] Logged MCP handoff or follow-up tasks for downstream agents

## Open Questions / Risks

Capture schema dependencies, legacy data concerns, or operational risks.

---
Use the [MCP Agent Handoff Playbook](../../docs/development/mcp_agent_handoff.md) when coordinating with other guardrails.
