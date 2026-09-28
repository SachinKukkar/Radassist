# 1. Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-09-28

## Context

RadAssist is built incrementally over many steps. Decisions made early (tools, services,
structure) shape everything later, and the reasons behind them are easily forgotten.

## Decision

We record every architecturally significant decision as an Architecture Decision Record (ADR)
in `docs/adr/`, following Michael Nygard's format: Title, Status, Context, Decision, Consequences.

## Consequences

- Reviewers and future contributors can see *why* the system looks the way it does.
- Changing a decision requires writing a new ADR that supersedes the old one, which keeps history honest.
- Writing an ADR takes a few minutes per significant decision.
