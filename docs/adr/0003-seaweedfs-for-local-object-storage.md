# 3. Use SeaweedFS as the local S3-compatible object store

- **Status:** Accepted
- **Date:** 2026-09-28

## Context

X-ray images and heatmaps will be stored in object storage accessed through the S3 API.
Locally and in CI we need a self-hosted S3-compatible server.

MinIO was the usual choice, but its community edition stopped publishing Docker images in
October 2025, entered maintenance mode in December 2025, and its repository was archived in 2026.
Depending on it would mean running unmaintained software with no security updates.

Alternatives considered:

| Option | License | Notes |
|---|---|---|
| SeaweedFS | Apache-2.0 | Actively maintained; `weed mini` runs a full S3 server in one container and can pre-create a bucket |
| Garage | AGPL-3.0 | Lightweight, but needs extra initialisation (cluster layout, key creation) |
| RustFS | Apache-2.0 | MinIO-like, but a younger project |
| LocalStack | Mixed | Emulates many AWS services; heavier than we need |

## Decision

Use SeaweedFS (pinned version) in `compose.yaml`. The application talks only to the standard
S3 API through `boto3`, configured by `RADASSIST_S3_*` settings, with path-style addressing.

## Consequences

- Swapping the storage product (for example, to AWS S3 in production) is a configuration change, not a code change.
- SeaweedFS-specific features are not used, so the application stays portable.
- We must keep the SeaweedFS image version updated (Dependabot).
