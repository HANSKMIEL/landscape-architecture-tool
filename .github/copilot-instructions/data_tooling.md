# Data Ingestion & Tooling Guardrails (DT1)

> Reference the [MCP Agent Triage Map](README.md#quick-links) for cross-category workflow steps and required secondary guardrails.
> Confirm sub-workflow obligations in [subworkflows.md](subworkflows.md) before starting work.

1. Review the ingest route (`src/routes/excel_import.py`), supporting services, and existing fixtures before changing behavior.
2. Preserve data validation and sanitization—extend current checks instead of bypassing them. Pay special attention to duplicate detection and transaction handling.
3. Update tests and fixtures when accepted columns or formats change. Required commands:

   ```powershell
   python -m pytest tests/test_excel_import.py tests/fixtures/test_stability.py
   ```

4. Log format or workflow changes in `dev_log.md` and, if needed, update operator documentation under `docs/development/`.
5. Clean up temporary files and ensure large file uploads are handled efficiently (streaming or chunking where applicable).
