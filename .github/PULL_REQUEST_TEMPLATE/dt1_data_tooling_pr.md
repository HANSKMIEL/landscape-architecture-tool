# DT1 Data Ingestion & Tooling PR Template

## Summary

- [ ] Linked issue: `Fixes #`
- [ ] Data/tooling change description:
- [ ] Affected import routes/services/fixtures:

## Guardrail Acknowledgement

- [ ] Reviewed `.github/copilot-instructions/data_tooling.md`
- [ ] Coordinated with secondary guardrails: <!-- e.g., B1, T1, DOC1 -->
- [ ] Consulted [MCP Agent Handoff Playbook](../../docs/development/mcp_agent_handoff.md) for multi-agent work

## Validation & Evidence

- [ ] `python -m pytest tests/test_excel_import.py tests/fixtures/test_stability.py`
- [ ] Sample import dry-run attached (representative dataset)
- [ ] Deduplication/sanitization results documented
- [ ] Cleanup of temporary artifacts confirmed

## Documentation & Logging

- [ ] Updated `dev_log.md` with guardrail IDs, validations, and links
- [ ] Updated operator docs in `docs/development/`
- [ ] Logged handoff tasks for downstream consumers

## Risk & Data Integrity

- [ ] Impact on existing datasets evaluated
- [ ] Rollback or data restoration plan documented
- [ ] Outstanding risks noted here:

---

## Reviewer Checklist

- [ ] Guardrail alignment confirmed
- [ ] Test and sample outputs verified
- [ ] Documentation updates reviewed
- [ ] Data integrity considerations assessed
