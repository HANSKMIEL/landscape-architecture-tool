# A1 Automation & Integrations PR Template

## Summary

- [ ] Linked issue: `Fixes #`
- [ ] Automation objective:
- [ ] Affected n8n workflows / webhook endpoints:

## Guardrail Acknowledgement

- [ ] Reviewed `.github/copilot-instructions/automation.md`
- [ ] Coordinated with secondary guardrails: <!-- e.g., B1, T1 -->
- [ ] Consulted [MCP Agent Handoff Playbook](../../docs/development/mcp_agent_handoff.md) for multi-agent work

## Validation & Evidence

- [ ] `python -m pytest tests/routes/test_n8n_receivers.py`
- [ ] Workflow export attached/linked
- [ ] Payload contract verification documented
- [ ] Background/offline processing validated (if applicable)

## Documentation & Logging

- [ ] Updated `_internal/n8n-workflows/` documentation
- [ ] Updated `dev_log.md` with guardrail IDs, validations, and links
- [ ] Added follow-up tasks for downstream agents (if needed)

## Risk & Monitoring

- [ ] Failure handling and retries documented
- [ ] Alerting/monitoring impacts assessed
- [ ] Outstanding risks noted here:

---

## Reviewer Checklist

- [ ] Guardrail alignment confirmed
- [ ] Payload/contracts validated
- [ ] Tests and exports reviewed
- [ ] Documentation/logging updates verified
