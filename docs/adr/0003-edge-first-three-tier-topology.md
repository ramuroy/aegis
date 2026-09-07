# 0003. Edge-first three-tier topology; the cloud is never in the flight-critical loop

- **Status:** Accepted
- **Date:** 2026-09-07
- **Deciders:** Ramu Roy
- **Supersedes:** —
- **Superseded by:** —

## Context

Once [ADR-0002](0002-trigger-driven-response-not-scheduled-patrol.md) makes the
drone a response asset, the next question is where each piece of the system
runs. The tempting answer for a portfolio project is "cloud-native everything" —
it demos well and it is the architecture most job descriptions ask for.

The latency numbers make it indefensible.

**Measured:** glass-to-glass WebRTC on the India → AWS Mumbai (ap-south-1) →
India path over 4G is **~740 ms P50 / 1180 ms P95**. On the site LAN the same
pipeline measures **180–310 ms P50**.

**Required:** teleoperation research puts the usable ceiling for a human taking
manual control of a moving vehicle at **~170–300 ms**.

The cloud path misses the requirement by a factor of two to four, at the
median, on a good day. This is not an optimisation problem — it is not fixable
with a better codec, a closer region, or a faster backend, because the dominant
term is the mobile access network. Any design in which a human's manual takeover
command traverses the public internet is a design that cannot deliver manual
takeover.

Three further constraints push the same way:

- **CGNAT.** Indian mobile carriers place subscribers behind carrier-grade NAT.
  The edge node cannot be reached inbound from the internet at all. Every
  connection must be outbound-initiated (edge dials cloud). This is a property
  of the network, not a preference we can engineer around with a static-IP SIM.
- **Connectivity is not assumed.** Indian sites lose internet regularly. A
  security system that stops detecting intrusions when the fibre is cut is not a
  security system; it is a demo. Whatever the cloud does must be something the
  site can survive losing.
- **MAVLink is unauthenticated by default.** CVE-2026-1579 (CVSS 9.8, CISA
  ICSA-26-090-02, 31 Mar 2026) — anyone with link access can send
  `SERIAL_CONTROL` and obtain an interactive shell. MAVLink 2 signing is
  mandatory, but it authenticates without encrypting, and
  `HEARTBEAT`/`RADIO_STATUS`/`ADSB_VEHICLE`/`COLLISION` bypass signing entirely.
  So the link additionally has to live inside a VPN, and MAVLink UDP/TCP ports
  must never be internet-exposed.

Every mature platform in this category — FlytBase, Percepto AIM, DJI FlightHub 2,
Auterion Suite — has independently converged on the same three-tier shape.
That convergence is evidence, not coincidence.

## Options considered

### Option A — Cloud-native: thin edge, all logic in the cloud
Cleanest to build and operate, single deployment target, best story for a
backend portfolio. Fails the latency requirement for manual takeover by 2–4×,
fails outright under CGNAT without a relay, and turns every internet outage into
a total security outage. Rejected on the measurements.

### Option B — Fully on-premise: no cloud at all
Meets every latency and availability requirement trivially. But there is then no
fleet view across sites, no off-site archive (so an intruder who destroys the
edge node destroys the evidence), no central model rollout, and every software
update is a site visit. Rejected: it solves the flight-loop problem by
abandoning everything the cloud is genuinely good at.

### Option C — Three-tier: onboard / site edge / cloud, split by latency budget
Each tier owns exactly the work whose latency budget it can meet:

| Tier | Latency budget | Owns |
| --- | --- | --- |
| **Onboard** (companion computer) | 10–50 ms | Flight control, precision landing loop, safety failsafes, on-frame redaction |
| **Site edge** (Ubuntu node in the society) | 100–300 ms | Detection inference, sensor fusion, corroboration gate, dispatch decision, manual takeover console, hot video |
| **Cloud** (ap-south-1) | seconds | Fleet state, archive, analytics, multi-site coordination, model distribution, resident notifications |

More moving parts and three deployment targets. Chosen anyway.

## Decision

**Three tiers, split strictly by latency budget. The cloud is "supervise, abort,
review" — never "fly".**

Binding rules that fall out of this:

1. **No cloud round-trip may sit between a human and a flight control input.**
   Manual takeover is an on-site/LAN capability. The cloud console can *abort*
   (a single idempotent command whose worst case is a safe RTL) but cannot pilot.
2. **The site edge is autonomous.** Detection, fusion, corroboration and dispatch
   run entirely on the edge node. With the uplink severed the system still
   detects, still dispatches, still records, still alarms locally. It loses
   remote visibility and off-site archive, nothing else.
3. **All connections are outbound-initiated** (edge dials cloud). No inbound
   ports, no static-IP SIM, no port forwarding. CGNAT is treated as a given.
4. **Store-and-forward is the default, not a fallback.** A NATS JetStream leaf
   node on the edge buffers everything destined for the cloud and drains when
   connectivity returns. Losing the uplink must never lose an event.
5. **MAVLink 2 signing on every non-USB link, inside WireGuard, ports never
   internet-exposed.** Signing keys are escrowed — they cannot be recovered
   remotely, and losing them on all GCS devices means physically pulling the SD
   card or reflashing over SWD.
6. **A Vehicle Abstraction Layer with two adapters** — MAVLink 2 /
   `MISSION_ITEM_INT` for PX4/ArduPilot, and DJI Cloud API over MQTT
   (`thing/product/{sn}/{osd,state,services,events}` + KMZ/WPML) — so the
   airframe decision stays reversible. Given the India import position
   ([ADR-0005](0005-ardupilot-over-px4.md)), the MAVLink adapter is the one we
   build first and the DJI adapter is a documented interface, not a shipped one.

```
              ┌──────────────────────────────────────────────┐
              │  CLOUD  (AWS ap-south-1)          seconds     │
              │  fleet state · archive · analytics · models   │
              │  resident notifications · multi-site          │
              └───────────────▲──────────────────────────────┘
                              │ outbound-initiated only (CGNAT)
                              │ NATS JetStream leaf → hub, store-and-forward
              ┌───────────────┴──────────────────────────────┐
              │  SITE EDGE  (Ubuntu node)      100–300 ms    │
              │  detection · fusion · corroboration gate     │
              │  dispatch · takeover console · hot video     │
              │  ── survives total uplink loss ──            │
              └───────▲───────────────────▲──────────────────┘
                      │ WireGuard          │ MQTT / LoRa
                      │ MAVLink 2 (signed) │
              ┌───────┴────────┐   ┌───────┴──────────────────┐
              │  ONBOARD       │   │  PERIMETER SENSOR GRID   │
              │  10–50 ms      │   │  ESP32 nodes · gate node │
              │  flight ctrl   │   │  fixed AI cameras        │
              │  prec. landing │   └──────────────────────────┘
              │  failsafes     │
              │  on-frame redaction (ADR-0006)                │
              └────────────────┘
```

## Consequences

**Easier:** the system has a defensible answer to "what happens when the internet
goes down" — the most common question an Indian buyer asks and the one most
cloud-native architectures answer badly. Manual takeover actually works. Video
does not pay a WAN round-trip to reach the operator who needs it.

**Harder:** three deployment targets, three upgrade paths, and a genuine
distributed-systems problem in reconciling edge and cloud state after a
partition. Store-and-forward means the cloud's view is eventually consistent and
every cloud-side feature must tolerate that.

**Committed to:** the edge node is not optional and not a cache. Any feature
proposal that only works when the cloud is reachable is, by this ADR, a feature
that does not work.

**Revisit if:** Indian mobile latency to ap-south-1 drops below ~150 ms P95 at
the median site — which would require access-network change, not backend change.
5G SA deployment is the thing to watch; measure before assuming.

## References

- CVE-2026-1579 / CISA ICSA-26-090-02 (31 Mar 2026) — unsigned MAVLink shell access.
- PX4 hardening guidance: MAVLink UDP/TCP ports must never be internet-exposed.
- Measured latency figures and stack selection: `docs/research/architecture.md`.
