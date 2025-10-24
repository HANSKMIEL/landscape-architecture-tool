# B1 Backend Development PR Template

## Summary

- [ ] Linked issue: `Fixes #`
- [ ] Backend change description:
- [ ] Impacted routes/services/models/schemas:

## Guardrail Acknowledgement

- [ ] Reviewed `.github/copilot-instructions/backend.md`
- [ ] Coordinated with secondary guardrails: <!-- e.g., F1, DT1, T1 -->
- [ ] Consulted [MCP Agent Handoff Playbook](../../docs/development/mcp_agent_handoff.md) for multi-agent work

## Validation & Evidence

- [ ] `python -m pytest tests/routes tests/services`
- [ ] `python -m pytest tests/test_dependency_validator_import.py`
- [ ] Alembic migration generated and reviewed (if applicable)
- [ ] API contract synced with `frontend/src/services/api.js`

## Documentation & Logging

- [ ] Updated `dev_log.md` with guardrail IDs, validations, and links
- [ ] Updated relevant API docs or schemas
- [ ] Recorded handoff notes for secondary guardrails

## Risk & Rollout

- [ ] Database migration rollback plan documented
- [ ] Performance & load impact assessed
- [ ] Outstanding risks noted here:

---

## Reviewer Checklist

- [ ] Guardrail alignment confirmed
- [ ] Tests and migrations verified
- [ ] Contract and documentation updates reviewed
- [ ] Risk/rollback plans evaluated
