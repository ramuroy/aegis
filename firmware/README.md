# firmware — ESP32 sensor nodes

## Continuation boundary: 2026-09-08

No ESP32 firmware was implemented, flashed or bench-validated in this session.
Fixed sensing remains the always-on layer in the accepted event-driven design.
A corroborated trigger is not itself permission to launch an aircraft; the
[regulatory checkpoint](../docs/research/drone-regulation.md) records those separate
open gates. See the [handoff](../docs/HANDOFF-2026-09-08.md) for the current task order.


The always-on layer. Under [ADR-0002](../docs/adr/0002-trigger-driven-response-not-scheduled-patrol.md)
this — not the drone — is what provides 24/7 coverage, and it is most of what the
customer is buying.

**Status:** not started.

## What goes here

```
perimeter-node/   fence vibration, PIR, tamper. Battery, long sleep, LoRa or WiFi
gate-node/        boom-barrier contact, gate camera trigger, ANPR handoff
dock-controller/  roof actuation, charge contactor, weather interlocks, telemetry
```

## Constraints that already apply

- **A node reports its own health honestly.** `DEGRADED` still corroborates;
  `STALE` and `TAMPERED` do not. A node that cannot tell the edge it is unwell is
  worse than one that is absent.
- **Clock skew is expected and must be measurable.** ESP32 without an RTC drifts
  seconds per day and reboots with no wall time. The edge measures skew from
  heartbeats; uncorrected, a node 8 s fast never corroborates and fails silently.
- **868 MHz is duty-cycle limited to 1%** under India's SRD exemption — 36 seconds
  of transmit per hour. Continuous 1 Hz telemetry over 868 MHz LoRa is not lawful;
  use it for heartbeat and alarm only.
- **Two sensors on one board do not corroborate each other.** They share power,
  link and firmware, so their failure modes correlate. Multi-sensor nodes are
  fine; they just cannot self-corroborate.

`make firmware`.
Background: [`docs/research/hardware-bom.md`](../docs/research/hardware-bom.md).
