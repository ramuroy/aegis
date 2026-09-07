<div align="center">

# AEGIS

**Autonomous aerial security for gated residential communities.**

*A drone that stays on its pad until something actually happens.*

[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
[![ADRs](https://img.shields.io/badge/decisions-documented-informational)](docs/adr/)
[![Firmware](https://img.shields.io/badge/firmware-ArduPilot%204.7-orange)](docs/adr/0005-ardupilot-over-px4.md)
[![Detector](https://img.shields.io/badge/detector-RF--DETR%20(Apache--2.0)-green)](docs/adr/0004-rf-detr-over-ultralytics-yolo.md)

</div>

---

## The finding that shaped this project

The obvious build is a drone that flies a scheduled perimeter patrol. Every
product demo in this category shows exactly that.

I costed it, and it loses.

A 5-acre society is ~20,234 m² with only ~600 m of perimeter. A drone flying 12
sorties a day at 10 minutes each is airborne **8.3% of the day** — about 6.5%
once you subtract monsoon and kite-season groundings. Fixed cameras bought with
the same ₹5–7 lakh of capex cover **100%** of it: in rain, at 03:00, silently,
without overflying anyone's balcony, and without a single regulatory approval.

Per rupee of capex, a scheduled patrol drone loses to fixed CCTV roughly
**12:1 on temporal coverage** at the size of society that would actually buy one.

Three regulations independently punish the *schedule* specifically:

| Constraint | Effect on a scheduled patrol |
| --- | --- |
| CPCB Noise Rules 2000 — **45 dB(A)** night limit in residential zones | A 2 kg quad near an occupied façade at night is non-compliant. Night patrol is out. |
| ~400 battery cycles to 80% SoH | 12 sorties/day burns ~11 battery sets a year. Patrol frequency *is* the opex line. |
| DPDP Act 2023 §7 — closed list, no legitimate-interest ground | Every scheduled overflight processes a resident with no lawful basis. |

So AEGIS inverts the design. **The drone is not a surveillance platform — it is a
response asset.** Fixed AI cameras and an ESP32 perimeter-sensor grid provide the
always-on layer. The aircraft launches only on a *corroborated* trigger, to do
the things cameras cannot: reach a blind spot, follow a subject across the
property, and put a steerable view on an incident for a human to adjudicate.

Full reasoning: [ADR-0002](docs/adr/0002-trigger-driven-response-not-scheduled-patrol.md).

> The crossover where a patrol *does* win is around 20–30 acres / 1.5 km of
> perimeter, where trenching a camera line costs ₹25–45 lakh. That is recorded
> as the revisit condition, not hand-waved away.

---

## Architecture

Split strictly by latency budget. The cloud is *supervise, abort, review* —
never *fly*.

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
              │  on-frame redaction                          │
              └────────────────┘
```

**Why not cloud-native?** Measured glass-to-glass WebRTC on India → AWS
ap-south-1 → India over 4G is **740 ms P50 / 1180 ms P95**. Teleoperation
research puts the human-takeover ceiling at **170–300 ms**. The cloud path misses
by 2–4× at the median, and the dominant term is the mobile access network — no
amount of backend engineering fixes it. Manual takeover is therefore an on-site
capability, and the edge node keeps detecting, dispatching and recording with the
uplink completely severed. ([ADR-0003](docs/adr/0003-edge-first-three-tier-topology.md))

---

## Decisions worth reading

This repo documents *why*, not just *what*. Each of these was a real fork with a
real cost:

| ADR | Decision | The thing that decided it |
| --- | --- | --- |
| [0002](docs/adr/0002-trigger-driven-response-not-scheduled-patrol.md) | Dispatch on corroborated triggers, no patrol schedule | Scheduled patrol loses to CCTV 12:1 on coverage per rupee |
| [0003](docs/adr/0003-edge-first-three-tier-topology.md) | Edge-first; cloud never in the flight loop | 740 ms measured vs a 170–300 ms requirement |
| [0004](docs/adr/0004-rf-detr-over-ultralytics-yolo.md) | RF-DETR, not YOLO | Every Ultralytics generation is AGPL-3.0; "edge devices, robotics, cameras" is a named Enterprise trigger |
| [0005](docs/adr/0005-ardupilot-over-px4.md) | ArduPilot, run **unmodified** | It ships a precision-landing *retry* state machine; PX4 doesn't. Running stock keeps GPLv3 off our code |
| [0006](docs/adr/0006-privacy-by-design-no-identifiable-data-by-default.md) | Emit no identifiable data by default | DPDP §7 is a **closed list** — no legitimate-interest ground exists in Indian law |
| [0007](docs/adr/0007-ros2-jazzy-and-mavros.md) | ROS 2 Jazzy, bridged with MAVROS | No JetPack exists for the Ubuntu the current ROS 2 LTS needs; AP_DDS documents Humble only |

### The idea I'm most pleased with

The **privacy map** is one signed, versioned GeoJSON artefact — society boundary
plus altitude bands for every registered private aperture — that is
simultaneously:

- the **annexure to the RWA's approved privacy policy**, and
- the **runtime config** that hard-slaves the gimbal and shutter.

Deployed behaviour cannot drift from approved policy, because they are the same
file. Enforcement is fail-closed: on stale pose, degraded GNSS, or a signature
that does not verify, the shutter closes and the gimbal stows. Degraded state
means *less* capability, never more.

---

## Stack

| Layer | Choice | Note |
| --- | --- | --- |
| Flight firmware | ArduPilot Copter 4.7.x, unmodified | `PLND_*` retry state machine; Lua for onboard behaviour |
| Middleware | ROS 2 Jazzy + MAVROS 2.15 | Jazzy is the only LTS matching JetPack 7 (Ubuntu 24.04) |
| Companion | Jetson Orin Nano Super 8 GB | 67 TOPS; runs detection *and* a 30 Hz landing loop concurrently |
| Detector | RF-DETR (Apache-2.0) | RF-DETR-S: 53.0 COCO AP @ 512 px, 3.5 ms T4-FP16 |
| Small objects | SAHI sliced inference (MIT) | +5–7 AP at 4–6× compute — sweep mode, not every frame |
| Tracking | Roboflow `trackers` + `supervision` | Apache-2.0 / MIT; **not** BoxMOT (AGPL) |
| Simulation | Gazebo Harmonic + ArduPilot SITL | AirSim is dead; Colosseum archived 2026-07-11 |
| Edge | Docker Compose, MediaMTX, NATS JetStream leaf | Store-and-forward through partitions |
| Cloud | FastAPI, Postgres 17 + PostGIS, NATS hub | Partitioned Postgres beats a TSDB below ~10k pts/sec |
| Web | React 19 + MapLibre GL + deck.gl | |
| Sensor nodes | ESP32-S3 | Perimeter, gate, dock controller |

Rejected alternatives and the reasons are in the ADRs — including the licence
traps that a `pip install` does not surface (RF-DETR XL is PML 1.0, not
Apache-2.0; D-FINE's Objects365 checkpoints are not commercially cleared even
though the repo is Apache-2.0).

---

## Documentation

| Document | What it is for |
| --- | --- |
| [`docs/STATE.md`](docs/STATE.md) | **Start here.** Where the project is, what changed, what to do next |
| [`docs/adr/`](docs/adr/) | Why each decision was made, and what would make us revisit it |
| [`docs/research/`](docs/research/) | The sourced research the decisions rest on — every claim carries a URL and a confidence level |
| [`docs/ops/setup.md`](docs/ops/setup.md) | Environment setup; says which toolchains you actually need |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Conventions, and the six rules that are not negotiable |

### Research notes

| Note | Covers |
| --- | --- |
| [architecture](docs/research/architecture.md) | Edge/cloud split, transport, video, alerting, Indian carrier constraints |
| [cv-models](docs/research/cv-models.md) | Detector licensing, small-object detection, edge accelerators, georeferencing |
| [flight-stack](docs/research/flight-stack.md) | ArduPilot vs PX4, ROS 2, precision landing, docking, simulation |
| [privacy-law](docs/research/privacy-law.md) | DPDP Act, consent, overflight, CERT-In, case law |
| [prior-art](docs/research/prior-art.md) | Commercial drone-in-a-box landscape and the India gap |
| [unit-economics](docs/research/unit-economics.md) | What societies pay today, cost to serve, noise, insurance, risk register |
| [hardware-bom](docs/research/hardware-bom.md) | Priced BOM at three tiers, and the RF licensing trap |

---

## Status

Early and honest. This section tracks reality, not intent.

- [x] Architecture decided and documented — 7 ADRs
- [x] Domain model: typed ULID identifiers, datum-safe geodesy
- [x] Privacy map: schema, HMAC signing, 30 Hz gimbal constraint solver
- [x] Corroboration gate: modality-family fusion, admission gates, audit trail
- [x] Georeferencing: camera model, damped-Newton undistortion, error budget
- [ ] Perception: dataset pipeline, RF-DETR fine-tune, ONNX/TensorRT export
- [ ] Autonomy: ROS 2 nodes, sortie state machine, SITL harness
- [ ] Simulation: residential-society world
- [ ] Backend services and ops dashboard
- [ ] ESP32 sensor-node firmware
- [ ] Hardware design spec and BOM
- [ ] Paper and deck

**Scope note.** Validation is in high-fidelity simulation — real ArduPilot
firmware, real ROS 2, real models trained on real aerial datasets, benchmarked on
real hardware. The airframe and dock are specified and costed as an engineering
design; no physical aircraft has been fabricated. Every number quoted in this
repository is reproducible from this repository.

---

## Getting started

```bash
make doctor     # check which toolchains you have, and how to get the rest
make setup      # bootstrap Python and web dependencies
make test       # run the suites
make help       # everything else
```

The repo spans four toolchains that share no package manager (colcon, pip, pnpm,
PlatformIO), so `make` is the single entry point regardless of which corner of
the tree you are standing in.

---

## Repository layout

```
aegis/            shared library — domain model, privacy map, dispatch, vision
  domain/         ids, geodesy, privacy map, sensing, corroboration gate
  vision/         camera model, georeferencing
autonomy/         ROS 2 workspace: flight, sortie state machine, SITL harness
perception/       dataset pipeline, training, evaluation, export
services/         edge and cloud backend services
web/              operations dashboard
firmware/         ESP32 perimeter, gate and dock-controller firmware
sim/              Gazebo worlds, ArduPilot SITL configuration
infra/            compose, k8s, observability
tests/            132 tests, property-based where the maths warrants it
docs/
  STATE.md        where the project is, and what to do next — read this first
  adr/            architecture decision records — the reasoning
  research/       sourced research notes behind every decision
  ops/setup.md    environment setup for all four toolchains
paper/            IEEE-format paper
```

---

## Licence

Apache-2.0. See [LICENSE](LICENSE).

No AGPL-licensed code enters the inference or training path — this is enforced in
CI, not by memory. ([ADR-0004](docs/adr/0004-rf-detr-over-ultralytics-yolo.md))
