# FLEXCUBE L1 Support Bot

Internal RAG support assistant for Oracle FLEXCUBE 11.11 documentation.

## Project Layout

- `backend/`: Python, FastAPI, and Clean Architecture backend
- `frontend/`: React and TypeScript SPA
- `docs/`: architecture, ADR, development, and evaluation notes
- `data/`: local development data, excluded from source control
- `specs/002-flexcube-support-chatbot/`: feature specification and implementation plan

## Local Development

Phase 1 establishes the project foundations. See [docs/development/local-setup.md](docs/development/local-setup.md) for prerequisites and commands.

Backend dependencies are managed with uv. Frontend dependencies are managed with npm.
The initial runtime is local and does not require containers or CI/CD infrastructure.

## Architecture

See [docs/architecture/README.md](docs/architecture/README.md) and [docs/adr/README.md](docs/adr/README.md).
