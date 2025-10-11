# T1 Testing & Quality PR Template

## Summary

- [ ] Linked issue: `Fixes #`
- [ ] Testing/quality objective:
- [ ] Impacted suites/fixtures/tools:

## Guardrail Acknowledgement

- [ ] Reviewed `.github/copilot-instructions/testing.md`
- [ ] Coordinated with secondary guardrails: <!-- e.g., B1, F1, D1 -->
- [ ] Consulted [MCP Agent Handoff Playbook](../../docs/development/mcp_agent_handoff.md) for multi-agent work

## Validation & Evidence

- [ ] `make backend-test`
- [ ] `make lint`
- [ ] `cd frontend` then `npm run test:run`
- [ ] Additional targeted tests (list):
- [ ] Attach logs or reports (link to `reports/` if applicable)

## Documentation & Logging

- [ ] Updated `dev_log.md` with guardrail IDs, validations, and links
- [ ] Documented test findings and follow-up actions
- [ ] Added or updated quality reports under `reports/`

## Risk & Follow-up

- [ ] Identified flaky tests and owners
- [ ] Noted environment or tooling issues
- [ ] Outstanding risks captured here:

---

## Reviewer Checklist

- [ ] Guardrail alignment confirmed
- [ ] Test outputs verified
- [ ] Follow-up actions documented
- [ ] Quality reports reviewed
