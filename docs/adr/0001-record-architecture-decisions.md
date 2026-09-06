# 0001. Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-09-07
- **Deciders:** Ramu Roy
- **Supersedes:** —
- **Superseded by:** —

## Context

AEGIS is a single system that has to be coherent across four normally-separate
engineering domains:

1. **Flight autonomy** — PX4/ROS 2, hard real-time-ish, safety-critical, where a
   bad decision ends in a crash.
2. **Computer vision** — throughput- and accuracy-bound, GPU-constrained,
   where a bad decision ends in missed intrusions or alert fatigue.
3. **Distributed backend** — availability- and consistency-bound, where a bad
   decision ends in lost telemetry or a security incident.
4. **Web/product** — latency- and clarity-bound, where a bad decision ends in an
   operator missing the one alert that mattered.

These domains impose contradictory pressures on shared choices. The message
transport is the clearest example: flight autonomy wants microsecond-jitter
local IPC, the backend wants durable replayable streams, and the web tier wants
a firewall-friendly push channel. There is no single correct answer, only a
correct *trade*, and the trade is invisible in the resulting code.

Without a written record, the six-months-later reader — including the author —
sees only the outcome and reasonably concludes it was arbitrary.

## Options considered

### Option A — No formal record; rely on commit messages
Zero ceremony, and commit messages do carry some rationale. But they are
scattered, keyed to implementation moments rather than decisions, and
effectively unsearchable once the tree grows past a few hundred commits. A
decision that spans five commits across three directories has no home.

### Option B — A single long `DESIGN.md`
One file, easy to find. But it is mutable: when a decision changes, the previous
reasoning is overwritten and the *history* of the thinking — often the most
valuable part — is lost to `git log -p` archaeology.

### Option C — Nygard-style ADRs
One immutable file per decision, superseded rather than edited. Slightly more
ceremony per decision; preserves the full decision history; makes it obvious
when something was decided and by what reasoning.

## Decision

We will record every significant architectural decision as an ADR in
`docs/adr/`, using the Nygard-style template in `_template.md`.

"Significant" means the decision satisfies at least one of:

- it is expensive to reverse later (data model, wire protocol, framework);
- it trades one discipline's interest against another's;
- a reasonable engineer would ask "why on earth did they do it that way?";
- it is a deliberate *non*-decision — something we chose to defer, and why.

Routine choices (which HTTP status code, which lint rule) do not get an ADR.

## Consequences

**Easier:** onboarding, design review, and writing the paper's methodology
section — the ADRs are already the argument, in order.

**Harder:** every significant decision now costs ~20 minutes of writing. This is
intentional friction: a decision that cannot be justified in a page probably has
not been thought through.

**Committed to:** ADRs are immutable once `Accepted`. Changing our mind means
writing ADR *N+1* that supersedes it, not editing the original.

**Revisit if:** the ADR count exceeds ~50 and the index stops being navigable,
at which point we add topic grouping rather than abandoning the practice.
