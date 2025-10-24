# D1 Deployment & Infrastructure PR Template

## Summary

- [ ] Linked issue: `Fixes #`
- [ ] Deployment objective:
- [ ] Impacted environments/scripts/workflows:

## Guardrail Acknowledgement

- [ ] Reviewed `.github/copilot-instructions/deployment.md`
- [ ] Coordinated with secondary guardrails: <!-- e.g., T1, DOC1 -->
- [ ] Consulted [MCP Agent Handoff Playbook](../../docs/development/mcp_agent_handoff.md) for multi-agent work

## Validation & Evidence

- [ ] `python -m pytest tests/test_dependency_validator_import.py`
- [ ] `cd frontend` then `npm run build`
- [ ] Manual smoke test against `http://72.60.176.200:8080` and `/health`
- [ ] Attach deployment logs or validation artifacts:

## Documentation & Logging

- [ ] Updated `dev_log.md` with guardrail IDs, validations, and links
- [ ] Updated relevant runbooks in `docs/deployment/`
- [ ] Added post-deployment verification steps to the PR description or comments

## Risk & Rollback Plan

- [ ] Rollback command/script documented
- [ ] Monitoring plan in place
- [ ] Remaining risks or follow-ups listed here:

---

## Reviewer Checklist

- [ ] Guardrail alignment confirmed
- [ ] Validation outputs verified
- [ ] Documentation updates reviewed
- [ ] Deployment/rollback steps understood
