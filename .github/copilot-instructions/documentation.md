# Documentation & Ops Guardrails (DOC1)

> Reference the [MCP Agent Triage Map](README.md#quick-links) for cross-category workflow steps and required secondary guardrails.
> Confirm sub-workflow obligations in [subworkflows.md](subworkflows.md) before starting work.

## Core Documentation Framework
**All documentation must align with the comprehensive best practices guides:**
- **[DEVELOPMENT_GUIDE.md](../../docs/DEVELOPMENT_GUIDE.md)** - 5 pillars of engineering velocity
- **[API_DOCUMENTATION.md](../../docs/API_DOCUMENTATION.md)** - REST API reference (update when endpoints change)
- **[DEBUGGING_GUIDE.md](../../docs/DEBUGGING_GUIDE.md)** - Systematic debugging process
- **[BRANCHING_STRATEGY.md](../../docs/BRANCHING_STRATEGY.md)** - Git workflow documentation
- **[BEST_PRACTICES_OVERVIEW.md](../../docs/BEST_PRACTICES_OVERVIEW.md)** - Framework adherence summary

## Documentation Guidelines

1. **Keep Core Guides Updated**: When code changes affect documented practices:
   - Update `docs/DEVELOPMENT_GUIDE.md` if changing environment setup, architecture patterns, or workflows
   - Update `docs/API_DOCUMENTATION.md` when adding/modifying API endpoints
   - Update `docs/DEBUGGING_GUIDE.md` when discovering new common issues or solutions
   - Update `docs/BRANCHING_STRATEGY.md` if workflow changes

2. **Keep deployment, architecture, and operations documentation accurate**—update `docs/deployment/`, `docs/architecture/`, or `_internal/` guides alongside code changes.

3. **Summarize significant updates in `dev_log.md`**, including references to instructions used or validation performed.

4. **When instructions diverge from `main`, call that out explicitly** and note the branch context (V1.00D).

5. **Run spellcheck or linting tools if available**; ensure Markdown formatting passes project standards (tables, headings, fenced code).

6. **Attach screenshots or diagrams when they improve clarity**; store large assets in the appropriate docs subdirectory.

## API Documentation Standards
- **All new endpoints** must be documented in `docs/API_DOCUMENTATION.md`
- Include: endpoint URL, HTTP method, request/response examples, status codes, validation rules
- Follow RESTful conventions documented in [DEVELOPMENT_GUIDE.md - RESTful API](../../docs/DEVELOPMENT_GUIDE.md#restful-api-design)

## Debugging Documentation
- **Add new common issues** to `docs/DEBUGGING_GUIDE.md` when discovered
- Include: symptom, diagnosis steps, solution, prevention strategy
- Follow the 5-step debugging framework structure

## Workflow Documentation
- **Document any workflow changes** in `docs/BRANCHING_STRATEGY.md`
- Maintain alignment with GitHub Flow variant (main → V1.00D → feature branches)
- Update PR templates if workflow expectations change
