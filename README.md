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
| Quality | Ruff (lint + format), mypy (strict), pytest, coverage |
| Workflow | uv, pre-commit, GitHub Actions, Dependabot |
| Planned | PostgreSQL, Redis, Celery, MinIO/S3, ONNX Runtime, React + TypeScript, Docker, Prometheus, Grafana |

## Quick start

**Prerequisites:** [uv](https://docs.astral.sh/uv/), `git`, `make`

```bash
git clone https://github.com/<your-username>/radassist.git
cd radassist
cp backend/.env.example backend/.env
make install
make run
```

Then open:

- http://127.0.0.1:8000/docs for interactive API docs
- http://127.0.0.1:8000/health/live for the liveness check

## Commands

| Command | Description |
|---|---|
| `make install` | Install dependencies and git hooks |
| `make run` | Start the API with auto-reload |
| `make check` | Lint, type-check and test (same as CI) |
| `make format` | Auto-format and fix lint issues |
| `make hooks` | Run all pre-commit hooks on every file |

## Configuration

All settings are environment variables prefixed with `RADASSIST_`. See [`backend/.env.example`](backend/.env.example).

| Variable | Default | Description |
|---|---|---|
| `RADASSIST_ENVIRONMENT` | `development` | `development`, `test` or `production` |
| `RADASSIST_DEBUG` | `false` | FastAPI debug mode (never in production) |
| `RADASSIST_LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING` or `ERROR` |
| `RADASSIST_LOG_JSON` | `false` | JSON log lines (use in production) |

## Project structure

```
backend/
  app/
    api/routes/   HTTP endpoints
    core/         configuration and logging
    schemas/      request/response models
    main.py       application factory
  tests/          automated tests
.github/          CI workflow, Dependabot, PR template
```

## Development workflow

1. Create a branch from an up-to-date `main`: `git switch -c feat/<name>`
2. Commit using [Conventional Commits](https://www.conventionalcommits.org/)
3. Push and open a pull request. CI must pass before merging.
4. Squash-merge, then `git switch main && git pull`

## Roadmap

- [x] 1. Project skeleton, tooling, CI
- [ ] 2. Docker & local infrastructure
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
