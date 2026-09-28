# RadAssist

[![CI](https://github.com/<your-username>/radassist/actions/workflows/ci.yml/badge.svg)](https://github.com/<your-username>/radassist/actions/workflows/ci.yml)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

AI-assisted X-ray triage platform. Upload chest and musculoskeletal radiographs, get model predictions with visual explanations, and work through an urgency-ranked worklist.

> **Disclaimer:** RadAssist is an educational portfolio project. It is **not a medical device** and must not be used for clinical diagnosis or patient care.

> **Status:** under active development. See the [roadmap](#roadmap).

## Tech stack

| Area | Tools |
|---|---|
| Backend | Python 3.12, FastAPI, Pydantic, Uvicorn |
| Data services | PostgreSQL 18, Redis 8, SeaweedFS (S3-compatible) |
| Clients | psycopg 3, redis-py, boto3 |
| Containers | Docker (multi-stage, non-root), Docker Compose |
| Quality | Ruff, mypy (strict), pytest (unit + integration), coverage, hadolint |
| Workflow | uv, pre-commit, GitHub Actions, Dependabot |
| Planned | SQLAlchemy, Celery, ONNX Runtime, React + TypeScript, Prometheus, Grafana |
| ML data | numpy, Pillow, pydicom, click |


## Quick start (Docker, recommended)


## Quick start (Docker, recommended)

**Prerequisites:** [Docker](https://docs.docker.com/get-docker/) with Compose, `git`, `make`

```bash
git clone https://github.com/<your-username>/radassist.git
cd radassist
make up
```

Then open:

- http://127.0.0.1:8000/docs for interactive API docs
- http://127.0.0.1:8000/health/ready for the readiness check (all dependencies should be `ok`)

Stop with `make down`. Your data is kept in Docker volumes; `make reset` deletes it.

## Local development (API on your laptop)

## ML data pipeline

The `ml/` package (`radassist-ml`) turns the raw datasets into validated manifests with
patient-level splits and preprocessed images. See [`ml/README.md`](ml/README.md) and the
[dataset cards](docs/datasets/README.md). Datasets are licensed and are never committed.


**Extra prerequisite:** [uv](https://docs.astral.sh/uv/)

```bash
cp backend/.env.example backend/.env
make install        # dependencies + git hooks
make deps           # start db, redis and storage in Docker
make run            # API with auto-reload on http://127.0.0.1:8000
```

## Services

| Service | Image | Host address | Purpose |
|---|---|---|---|
| `api` | built from `backend/Dockerfile` | http://127.0.0.1:8000 | FastAPI application |
| `db` | `postgres:18` | 127.0.0.1:5432 | Relational database |
| `redis` | `redis:8.8-alpine` | 127.0.0.1:6379 | Cache and task queue broker |
| `storage` | `chrislusf/seaweedfs:4.47` | http://127.0.0.1:8333 | S3-compatible object storage |

All ports bind to `127.0.0.1` only. The credentials are for local development only.

## Commands

| Command | Description |
|---|---|
| `make up` / `make down` | Start / stop the full stack in Docker |
| `make deps` | Start only the dependencies |
| `make run` | Run the API locally with auto-reload |
| `make check` | Lint, type-check and unit tests (as in CI) |
| `make test-integration` | Integration tests against the running services |
| `make logs` / `make ps` | Follow logs / show container health |
| `make reset` | Stop and **delete** all local data |
| `make ml-check` | ML lint, type-check and tests |


Run `make` to see every command.

## Configuration

The API reads environment variables prefixed with `RADASSIST_`. See [`backend/.env.example`](backend/.env.example) for the full list.
Docker Compose accepts optional overrides in a root `.env` file. See [`.env.example`](.env.example).

With `RADASSIST_ENVIRONMENT=production`, the API refuses to start with the development credentials.

## Health checks

| Endpoint | Meaning | Used by |
|---|---|---|
| `GET /health/live` | The process is running | Docker `HEALTHCHECK` |
| `GET /health/ready` | Database, Redis and object storage are reachable (200), otherwise 503 | Load balancers, CI |

## Architecture decisions

Significant decisions are recorded in [`docs/adr/`](docs/adr/README.md).

## Development workflow

1. Create a branch from an up-to-date `main`: `git switch -c feat/<name>`
2. Commit using [Conventional Commits](https://www.conventionalcommits.org/)
3. Push and open a pull request. Both CI jobs must pass.
4. Squash-merge, then `git switch main && git pull`

## Roadmap

- [x] 1. Project skeleton, tooling, CI
- [x] 2. Docker & local infrastructure
- [ ] 3. Datasets & preprocessing
- [ ] 4. Training pipeline with MLflow
- [ ] 5. Inference package (ONNX, heatmaps, DICOM)
- [ ] 6. Database layer
- [ ] 7. Authentication & roles
- [ ] 8. Studies API & object storage
- [ ] 9. Async inference worker
- [ ] 10. Frontend setup & auth
- [ ] 11. Worklist, viewer & feedback UI
- [ ] 12. Production Docker & one-command demo
- [ ] 13. CI/CD & container registry
- [ ] 14. Cloud deployment
- [ ] 15. Observability
- [ ] 16. MLOps: registry, drift, feedback loop
- [ ] 17. Documentation & v1.0.0

## License

MIT. See [LICENSE](LICENSE).
