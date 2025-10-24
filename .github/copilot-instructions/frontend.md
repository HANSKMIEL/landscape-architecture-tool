# Frontend Development Guardrails (F1)

> Reference the [MCP Agent Triage Map](README.md#quick-links) for cross-category workflow steps and required secondary guardrails.
> Confirm sub-workflow obligations in [subworkflows.md](subworkflows.md) before starting work.

## Core Best Practices
**Follow the comprehensive framework:**
- **Architecture**: [DEVELOPMENT_GUIDE.md - Frontend Architecture](../../docs/DEVELOPMENT_GUIDE.md#frontend-architecture) - Component separation, hooks, context
- **API Integration**: [API_DOCUMENTATION.md](../../docs/API_DOCUMENTATION.md) - REST API reference
- **Debugging**: [DEBUGGING_GUIDE.md - Frontend](../../docs/DEBUGGING_GUIDE.md#frontend-debugging) - Browser DevTools, React DevTools

## Development Workflow

1. **Sync with Backend Contracts**: Read the relevant API helper in `frontend/src/services/api.js` and confirm response shapes against backend schemas from [API_DOCUMENTATION.md](../../docs/API_DOCUMENTATION.md).

2. **UI System**: Follow the established UI system (shadcn + Tailwind). Reuse existing utility classes and components from `frontend/src/components/ui` before introducing new patterns.

3. **Localization**: Keep text and labels centralized; update locale/resources files where necessary rather than hard-coding strings.

4. **Routing and Guards**: Maintain routing and state guards to match backend permissions.

5. **Component Structure**: Follow separation of concerns from [DEVELOPMENT_GUIDE.md - Frontend](../../docs/DEVELOPMENT_GUIDE.md#separation-of-concerns):
   - UI components in `frontend/src/components/`
   - API calls in `frontend/src/services/api.js` (never fetch directly in components)
   - Custom hooks in `frontend/src/hooks/`
   - Context providers in `frontend/src/context/`

6. **Validation**: Run validation commands after changes:

   ```powershell
   cd frontend
   npm run test:run
   npm run build
   ```

7. **Documentation**: Document notable UX changes or new flows in `docs/development/` or the product brief, and note any API adjustments in `dev_log.md`.

## Debugging Frontend Issues
Use systematic process from [DEBUGGING_GUIDE.md - Frontend](../../docs/DEBUGGING_GUIDE.md#frontend-debugging):
- **Console Tab**: Check for JavaScript errors and console.log output
- **Network Tab**: Inspect API calls (request/response, status codes)
- **React DevTools**: Inspect component props, state, and hierarchy
- **Breakpoints**: Use Sources tab debugger for step-by-step debugging

## Common Patterns
- **API Integration**: All API calls through `frontend/src/services/api.js`
- **Error Handling**: Display user-friendly messages from API error responses
- **Loading States**: Show loading indicators during async operations
- **Form Validation**: Validate on frontend, handle errors from backend (422 status)
