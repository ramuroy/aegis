# web — operations dashboard

## Continuation boundary: 2026-09-08

No dashboard/UI code or deployment changed in this session. Future operator views
should distinguish sensor corroboration, privacy-policy status and aviation launch
eligibility instead of presenting a trigger as flight approval. This is a planning
implication, not an implemented UI or accepted new ADR. The existing privacy
boundary remains in force. See the [regulatory checkpoint](../docs/research/drone-regulation.md)
and [handoff](../docs/HANDOFF-2026-09-08.md) before making readiness claims.


The console an operator actually watches. Its job is to make one alert out of
many events legible fast enough to act on.

**Status:** not started.

## What goes here

Map-first layout: live site map with sensor and aircraft state, alert triage
queue, live video with the manual-takeover control, sortie review with the
decision trail, and the privacy-map editor where residents' apertures are
registered.

## Constraints that already apply

- **React 19 + MapLibre GL + deck.gl.**
- **The takeover console is an on-site capability.** Its latency budget is
  100–300 ms on the LAN; the same UI served from the cloud must visibly *not*
  offer manual control, because 740 ms cannot deliver it.
- **Every dispatch must be explainable in the UI.** A resident disputing a launch
  is entitled to see which sensors corroborated, and whether the system did not
  believe an alarm or believed it and was not permitted to fly — the two are
  distinct outcomes and must not be collapsed into one badge.
- **Unlocking raw footage is a two-person, ticketed, audited flow.** It is not a
  button.

`make setup-web`, `make web`.
