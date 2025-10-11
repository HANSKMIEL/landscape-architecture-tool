# Automation & Integrations Guardrails (A1)

> Reference the [MCP Agent Triage Map](README.md#quick-links) for cross-category workflow steps and required secondary guardrails.
> Confirm sub-workflow obligations in [subworkflows.md](subworkflows.md) before starting work.

1. Mirror any n8n workflow adjustments by exporting JSON into `n8n-workflows/` and documenting the change.
2. Keep webhook payload shapes synchronized between n8n flows and Flask receivers (`src/routes/n8n_receivers.py`).
3. Avoid long-running or blocking work inside webhook handlers; delegate to async/background tasks where possible.
4. Validate payloads and signatures before processing; update tests under `tests/routes/` or create new fixtures for automation cases.
5. Recommended checks:

   ```powershell
   python -m pytest tests/routes/test_n8n_receivers.py
   ```

6. Record integration touchpoints and deployment considerations in `_internal/n8n-workflows/README.md` and `dev_log.md`.
