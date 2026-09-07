# Architecture Decision Records

This directory records the *reasoning* behind AEGIS's significant technical
decisions, not just their outcome. Each record is immutable once accepted: if a
decision is revisited, a new ADR supersedes the old one and the old one is
marked `Superseded` with a forward link.

Why bother: AEGIS spans four disciplines (flight autonomy, computer vision,
distributed backend, web) and a decision that looks arbitrary from inside one
discipline is usually load-bearing for another. The ADRs are where that
cross-discipline reasoning lives.

## Index

| ADR | Title | Status |
| --- | ----- | ------ |
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-trigger-driven-response-not-scheduled-patrol.md) | Dispatch on corroborated triggers, not a patrol schedule | Accepted |

## Format

We use a lightly-trimmed [Nygard-style](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
template — see [`_template.md`](_template.md).

## Conventions

- Filename: `NNNN-kebab-case-title.md`, zero-padded, monotonically increasing.
- Status: `Proposed` → `Accepted` | `Rejected`, later possibly `Superseded by NNNN`.
- Keep each ADR under roughly one page. If it needs more, the decision is
  probably two decisions.
