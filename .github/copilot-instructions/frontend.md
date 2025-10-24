# Frontend Development Guardrails (F1)

> Reference the [MCP Agent Triage Map](README.md#quick-links) for cross-category workflow steps and required secondary guardrails.
> Confirm sub-workflow obligations in [subworkflows.md](subworkflows.md) before starting work.

1. Sync with backend contracts: read the relevant API helper in `frontend/src/services/api.js` and confirm response shapes against backend schemas.
2. Follow the established UI system (shadcn + Tailwind). Reuse existing utility classes and components from `frontend/src/components/ui` before introducing new patterns.
3. Keep text and labels centralized; update locale/resources files where necessary rather than hard-coding strings.
4. Maintain routing and state guards to match backend permissions.
5. Run validation commands after changes:

   ```powershell
   cd frontend
   npm run test:run
   npm run build
   ```

6. Document notable UX changes or new flows in `docs/development/` or the product brief, and note any API adjustments in `dev_log.md`.
