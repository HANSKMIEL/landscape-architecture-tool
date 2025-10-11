# Documentation & Ops Guardrails (DOC1)

> Reference the [MCP Agent Triage Map](README.md#quick-links) for cross-category workflow steps and required secondary guardrails.
> Confirm sub-workflow obligations in [subworkflows.md](subworkflows.md) before starting work.

1. Keep deployment, architecture, and operations documentation accurate—update `docs/deployment/`, `docs/architecture/`, or `_internal/` guides alongside code changes.
2. Summarize significant updates in `dev_log.md`, including references to instructions used or validation performed.
3. When instructions diverge from `main`, call that out explicitly and note the branch context (V1.00D).
4. Run spellcheck or linting tools if available; ensure Markdown formatting passes project standards (tables, headings, fenced code).
5. Attach screenshots or diagrams when they improve clarity; store large assets in the appropriate docs subdirectory.
