# services — edge and cloud

## Continuation boundary: 2026-09-08

No backend service or regulator integration was implemented or deployed here.
The [regulatory checkpoint](../docs/research/drone-regulation.md) distinguishes
administrative eGCA services from Digital Sky operational airspace services.
That source description is not a supported public API contract; no authenticated
workflow was exercised. Future dispatch must distinguish a corroborated event
from current aircraft launch eligibility. See the [handoff](../docs/HANDOFF-2026-09-08.md).


Two deployment targets with genuinely different jobs, split by latency budget
([ADR-0003](../docs/adr/0003-edge-first-three-tier-topology.md)).

**Status:** not started.

## What goes here

```
edge/       detection worker, sensor fusion, corroboration gate, dispatch,
            MediaMTX, NATS JetStream leaf, takeover console backend
cloud/      fleet state, archive, analytics, resident notifications, model
            distribution
```

## Constraints that already apply

- **The edge must survive total uplink loss.** With the internet severed it still
  detects, dispatches, records and alarms locally. Any feature that only works
  when the cloud is reachable is a feature that does not work.
- **All connections are outbound-initiated.** Indian carriers use CGNAT, so the
  edge cannot be reached inbound at all. No inbound ports, no static-IP SIM.
- **The cloud can abort, never pilot.** Manual takeover is on-site/LAN only.
- **Store-and-forward is the default**, not a fallback. Losing the uplink must
  never lose an event.
- **MAVLink 2 signing inside WireGuard**, ports never internet-exposed
  (CVE-2026-1579). Signing keys are escrowed — they cannot be recovered remotely.
- **Alerting is DLT- and template-gated.** No SMS to an Indian number without
  TRAI DLT registration; WhatsApp outside a 24-hour window needs a pre-approved
  Utility template. FCM push is free and is the primary channel.

`make up`, `make down`, `make logs`.
Background: [`docs/research/architecture.md`](../docs/research/architecture.md).
