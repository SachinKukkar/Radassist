# 2. Use Docker Compose for local development

- **Status:** Accepted
- **Date:** <YYYY-MM-DD>

## Context

The API depends on PostgreSQL, Redis and S3-compatible object storage. Installing these
directly on each developer's machine leads to version drift and "works on my machine" bugs.
We also want anyone who clones the repository to run the whole system with one command.

## Decision

- The API is packaged as a Docker image built from `backend/Dockerfile` (multi-stage, non-root).
- `compose.yaml` at the repository root defines the local stack: `api`, `db` (PostgreSQL 18),
  `redis` (Redis 8) and `storage` (SeaweedFS, see ADR 0003).
- All image versions are pinned; Dependabot proposes upgrades.
- Published ports bind to `127.0.0.1` only, so services are not exposed to the local network.
- Development credentials have defaults so `make up` works without setup. The application
  refuses to start in `production` with those defaults.

## Consequences

- Docker Desktop (or Docker Engine) is required for development.
- CI runs the same stack, so integration tests exercise real services.
- The Compose file is for development and CI only. Production deployment is decided in a later step.
