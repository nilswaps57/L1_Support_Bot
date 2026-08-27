# Dependency, Licence, and Vulnerability Review

**Review date:** 2026-08-27
**Scope:** backend and frontend direct runtime/development dependencies in the locked local workspace
**Policy:** no automatic dependency upgrades were applied; especially no breaking major upgrade

## Inventory and reproducibility

- Backend dependencies are resolved by `backend/uv.lock`; `uv lock --check` passed.
- Frontend dependencies are resolved by `frontend/package-lock.json`; `npm ls --depth=0` completed successfully.
- Backend resolved versions were inspected with `uv tree --depth 1`.
- Frontend resolved versions were inspected with `npm ls --depth=0`.

## Vulnerability results

| Area | Command/result | Interpretation | Action |
|---|---|---|---|
| Frontend runtime | `npm audit --omit=dev --json`: 0 vulnerabilities across 14 production dependencies | No runtime advisory was reported for the shipped dependency graph | Recheck before release |
| Frontend all dependencies | 5 findings: 1 critical, 1 high, 3 moderate | Findings are in direct `vitest` and its Vite/esbuild test-tool tree; they are development-only in this application | Keep the current lockfile for this phase; schedule a tested Vitest/Vite major upgrade before exposing test tooling or dev server outside localhost |
| Backend | `pip-audit` is not installed in the project environment, so no scanner result is claimed | The backend dependency graph was not vulnerability-certified by a Python advisory scanner | Install a reviewed scanner in the audit environment and rerun against `backend/uv.lock` before production approval |
| Backend lock | `uv lock --check` passed | Lock metadata is internally consistent | Preserve the lockfile |

The npm findings were not fixed automatically because npm reported the available fix as
`vitest@4.1.11`, a major upgrade from the pinned Vitest 2 line. The affected packages are
Vite/Vitest/esbuild development tooling, not the production frontend bundle. The local Vite
development server remains localhost-only by convention and must not be treated as a production
service.

## Licence suitability

The direct dependency metadata and upstream project licences were reviewed at a high level.
The intended permissive set is suitable for an internal prototype and requires legal review for
production distribution:

- FastAPI, Pydantic Settings, SQLAlchemy, Alembic, aiosqlite, Docling, python-docx, qdrant-client,
  rank-bm25, structlog, React, React DOM, React Router, TanStack Query, React Hook Form, Vite,
  Vitest, TypeScript, Testing Library, and jsdom are reported as MIT/BSD-family or similarly
  permissive by their project metadata.
- HTTPX and pytest-family packages are BSD/MIT-family.
- Qdrant client is Apache-2.0; Playwright is Apache-2.0; FlashRank is Apache-2.0.
- PyMuPDF is AGPL-3.0 or commercial licensing. This is an unresolved production licensing
  risk and must be replaced, commercially licensed, or approved by counsel before distribution.
- Transitive dependency licences were not certified by a dedicated SBOM/licence scanner in this
  environment. A release review must generate an SBOM and retain licence notices.

## Unresolved risks

1. Backend advisory scanning is pending because `pip-audit` is unavailable.
2. The frontend test-tool critical/high findings remain documented, not silently accepted for a
   production-exposed dev server.
3. PyMuPDF licensing is unresolved for any deployment that distributes the backend.
4. Licence metadata should be verified from the exact locked distributions, including transitive
   packages, before external distribution.

## Follow-up gate

Before production deployment, run a Python advisory scan and an SBOM/licence scan against the
locked files, remediate or formally accept every runtime advisory, resolve PyMuPDF licensing,
and retest the frontend after a planned Vite/Vitest upgrade. This review does not introduce CI/CD.
