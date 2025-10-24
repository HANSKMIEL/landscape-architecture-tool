# MCP Agent Handoff Playbook

This guide standardizes how we brief MCP agents, move work between specialty categories, and track progress across the V1.00D branch. Pair it with the guardrail files under `.github/copilot-instructions/`.

## 1. Prepare the Handoff Package

1. Identify the primary guardrail ID (see the triage map) and any secondary IDs. Run `python scripts/devops/triage_helper.py <files...>` if you need help mapping changed files to guardrails.
2. Collect the following snippets into the issue or MCP prompt:
   - Relevant guardrail sections (copy-paste the numbered requirements).
   - Direct links to the source files that will be touched.
   - Validation commands that must be run before completion.
3. Attach recent context (logs, screenshots, n8n exports, etc.) so the agent starts with the latest signal.

### Template

```markdown
### Scope
- Primary Guardrail: B1 – Backend Development
- Secondary Guardrails: T1 – Testing & Quality

### Objectives
- [ ] Implement new supplier filter endpoint
- [ ] Update frontend client to consume the endpoint

### References
- Route: src/routes/suppliers.py
- Service: src/services/supplier_service.py
- Guardrails: .github/copilot-instructions/backend.md, .github/copilot-instructions/testing.md

### Validation
- python -m pytest tests/routes/test_suppliers.py
- make backend-test
```

## 2. Track Ownership and Progress

- Mention the acting agent in the issue (e.g., “Assigned to MCP backend agent”).
- If the work hops to another agent, add a comment describing the remaining tasks and the guardrail IDs still open.
- Update checkboxes in the handoff template as steps finish; link to the validation output or report.

## 3. Validate and Record

- Run every validation command listed in the participating guardrails. Attach logs or summaries in the issue.
- Add an entry in `dev_log.md` including:
  - Guardrail IDs touched.
  - Validation commands executed.
  - Issue or PR reference for traceability.

## 4. Close-Out Checklist

Before closing the issue or merging a PR:

- [ ] All guardrail validations executed without failures.
- [ ] Secondary guardrail owners (if any) acknowledged the results.
- [ ] Documentation updates landed where required (docs/, _internal/, reports/).
- [ ] Dev log entry created and linked.
- [ ] Deployment or smoke checks run when D1 is involved.

## 5. Best Practices

- Prefer short, iterative handoffs (one guardrail per agent) when uncertainty is high.
- Use GitHub Draft PRs to collect validation logs while work is in progress.
- Label issues with guardrail IDs (e.g., `scope:B1`) to build historical reporting on effort distribution.
- For repeat workflows, store your prompt packages under `docs/development/agent_prompts/` so the next handoff is copy/paste ready.

Following this playbook keeps cross-category development efficient, auditable, and aligned with the guardrail expectations.
