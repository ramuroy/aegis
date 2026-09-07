# Project state

**As of 2026-09-07.** Read this first when picking the project back up. It records
what exists, what was decided and why, what changed along the way, and what to do
next — in that order.

The [ADRs](adr/) hold the *reasoning* behind each decision. This document holds
the *state*: it tells you where you are, and points at the ADR when you need to
know why.

---

## 1. What AEGIS is

An autonomous aerial security system for Indian gated residential communities
(RWAs / co-operative housing societies).

The design was inverted early by a costing exercise. The obvious build — a drone
flying a scheduled perimeter patrol — loses to fixed CCTV by roughly **12:1 on
temporal coverage per rupee** at the size of society that would actually buy one.
So AEGIS is not a patrol system:

- **Fixed AI cameras + an ESP32 perimeter-sensor grid** are the always-on layer.
  This is what the customer is mostly buying and what provides 24/7 coverage.
- **The drone is a response asset.** It launches only on a *corroborated*
  trigger, to do what cameras cannot: reach a blind spot, follow a subject across
  the property, and put a steerable view on an incident for a human to judge.

Full reasoning: [ADR-0002](adr/0002-trigger-driven-response-not-scheduled-patrol.md).

### Validation scope

Validation is in high-fidelity simulation: real ArduPilot firmware, real ROS 2,
real models trained on real aerial datasets, benchmarked on real hardware. The
airframe and dock are specified and costed as an engineering design; no physical
aircraft has been fabricated. **Every number in this repository is reproducible
from this repository.**

---

## 2. Decisions locked in

Six ADRs, all `Accepted`. Each was a genuine fork with a cost.

| ADR | Decision | Decided by | Revisit when |
| --- | --- | --- | --- |
| [0001](adr/0001-record-architecture-decisions.md) | Record ADRs | Four disciplines pull shared choices in opposite directions; code shows the outcome and hides the trade | ADR count > ~50 |
| [0002](adr/0002-trigger-driven-response-not-scheduled-patrol.md) | Dispatch on corroborated triggers, no patrol schedule | Scheduled patrol loses to CCTV 12:1 on coverage/rupee; CPCB 45 dB(A) night limit; ~400 battery cycles | Sites above 20–30 acres, where the arithmetic inverts |
| [0003](adr/0003-edge-first-three-tier-topology.md) | Edge-first; cloud never in the flight loop | 740 ms P50 measured India→ap-south-1→India vs a 170–300 ms teleop ceiling | Indian mobile latency to ap-south-1 drops below ~150 ms P95 |
| [0004](adr/0004-rf-detr-over-ultralytics-yolo.md) | RF-DETR (Apache-2.0), no AGPL in the inference path | Every Ultralytics generation is AGPL-3.0 and names "edge devices, robotics, cameras" as an Enterprise trigger | A better Apache/MIT small-object detector appears, or commercial intent is dropped |
| [0005](adr/0005-ardupilot-over-px4.md) | ArduPilot Copter 4.7.x, run **unmodified** | It ships a precision-landing *retry* state machine in firmware; PX4 does not | PX4 ships comparable retry (watch each minor release) |
| [0006](adr/0006-privacy-by-design-no-identifiable-data-by-default.md) | Emit no identifiable personal data by default | DPDP Act §7 is a **closed list** — no legitimate-interest ground exists in Indian law | DPDP is amended, or 13 May 2027 lands and SPDI 2011 falls away |

### The three findings that shaped everything

1. **A scheduled patrol drone loses to fixed CCTV.** A 5-acre society is ~600 m
   of perimeter; a drone at 12 sorties/day is airborne 8.3% of the day (≈6.5%
   after weather and kite-season groundings). Cameras for the same capex cover
   100%, in rain, at 03:00, silently. → the trigger-driven design.
2. **The cloud cannot be in the flight-critical loop.** Measured 740 ms P50 /
   1180 ms P95 vs a 170–300 ms human-takeover ceiling, and the dominant term is
   the mobile access network — unfixable in the backend. → edge-first, and manual
   takeover is an on-site capability.
3. **DPDP Act §7 is a closed list of nine legitimate uses** with no
   legitimate-interest and no security-of-property ground. Visitors, delivery
   riders and passers-by cannot realistically consent, so a meaningful fraction
   of the people the system sees can never lawfully be identified by it. → the
   system must be *incapable* of emitting identifiable data by default, not
   merely configured not to.

### Binding rules that follow

These are commitments, not preferences. Breaking one invalidates an ADR's
analysis and requires redoing it before anything ships.

- **No patches to ArduPilot C++.** Upstream PR, or work around it. This is what
  keeps GPLv3 off our code (ADR-0005).
- **`ultralytics` is not an allowed dependency anywhere**, including notebooks
  and comparison scripts (ADR-0004).
- **Licence review is per-artefact, not per-repo.** A permissive repo can ship
  non-permissive weights — RF-DETR XL/2XL are PML 1.0; D-FINE's Objects365
  checkpoints are not commercially cleared.
- **Identification is never a default, a toggle, or a "pro tier"** (ADR-0006).
- **Every degradation must reduce capability**, never leave it unchanged.

---

## 3. What is built

~1,800 lines of library code, 132 tests, ruff-clean. All under `aegis/`, which is
the shared library every tier imports.

### `aegis/domain/ids.py` — typed ULID identifiers
ULID rather than UUIDv4 because IDs here are written in time order and read in
time ranges, so the primary-key index gets locality instead of scattering every
insert. `NewType` wrappers make `dispatch(site_id, drone_id)` with the arguments
swapped a type error. Randomness is `os.urandom` — these IDs appear in URLs and
the audit log, and a predictable sequence would let someone enumerate incidents.

### `aegis/domain/geo.py` — datum-safe geodesy
The module exists to enforce one idea: **an altitude is meaningless without its
datum.** Four are in play (AGL, AMSL, HAE, AHL) and over India the HAE↔AMSL gap
is −65 to −100 m — one of the largest geoid anomalies on Earth, and more than the
entire legal altitude envelope. `Altitude` carries its datum and refuses
cross-datum arithmetic.

`LocalFrame` is an ENU tangent plane using both radii of curvature; sub-millimetre
at society scale, so it sidesteps the projected-CRS question. `AltitudeBand`
models a privacy constraint as a vertical slice rather than a column — without
which transiting at 40 m trips every balcony beneath and the constraint becomes
unenforceable in practice.

### `aegis/domain/privacy.py` — the privacy map
The load-bearing idea from ADR-0006, and the piece most worth reading.

One signed, versioned artefact — society boundary plus altitude-banded apertures —
is *simultaneously* the annexure to the RWA's approved privacy policy and the
config that constrains the gimbal at 30 Hz. Deployed behaviour cannot drift from
approved policy because they are the same file. The HMAC covers the site origin
too, since moving it would silently move every aperture.

Enforcement is **angular, not volumetric**. Asking "does the frustum intersect a
protected volume" detects a violation but offers no corrective action, so the only
response is closing the shutter and losing the sortie because one balcony clipped
a frame corner. Instead each aperture is projected from the aircraft's current
position into (azimuth, elevation), inflated by half-FOV *and by pose
uncertainty*, yielding forbidden boresight directions — cheap enough for 30 Hz and
producing a clamp rather than a verdict. Because uncertainty inflates the
exclusions, a degraded GNSS fix mechanically widens the no-look cones.

### `aegis/domain/sensing.py` — the always-on layer
`SensorClass` maps onto `ModalityFamily`, which encodes the physical principle and
therefore **which failure modes correlate**. `SensorNode` carries `clock_skew_s`
because ESP32 nodes without an RTC drift seconds per day; uncorrected, a node 8 s
fast never corroborates with anything and the failure is completely silent.

### `aegis/domain/dispatch.py` — the corroboration gate
The only thing in AEGIS that launches an aircraft. Dispatch requires either ≥2
modality families from ≥2 distinct **nodes** within a time and distance window, or
one high-confidence detection in a society-designated high-value zone. Everything
else raises a ticket — the normal outcome, not a failure.

Distinct *nodes* as well as distinct *families* is deliberate: one ESP32 carrying
a PIR and a camera shares power, link and firmware with itself, so a brownout
trips both, and correlated failures are exactly what corroboration excludes.

Corroboration ("is it real?") and admission ("may we fly?") are separate stages,
because a resident disputing a 23:00 launch is entitled to know which one applied.
Hence `Decision.corroborated` alongside `Decision.should_launch`.

### `aegis/vision/camera.py` + `georef.py` — pixels to world
Three things here are not the obvious implementation:

- **Foot point, not box centre.** A person's centroid is ~1 m above their feet; at
  30° depression that is 1.73 m of extra ground range. It is a bias, not noise, so
  it never averages out.
- **The error budget is the product.** A position without an uncertainty cannot be
  correlated. Three terms propagated analytically, dominant one reported — which
  is actionable: with RTK fitted, *attitude* dominates, so the next money goes on
  the gimbal, not the GNSS. Computed CEP is 3.1 m on baro, 0.51 m on RTK,
  matching the independently-researched 2–5 m and 0.5–1.5 m ranges.
- **Damped Newton undistortion**, not the textbook fixed-point iteration.

---

## 4. What changed along the way

Three real defects, all surfaced by property tests, all fixed and pinned by
regression tests. Recorded because the reasoning is worth keeping.

| What | How it was found | Fix |
| --- | --- | --- |
| `haversine_m` used the WGS-84 **semi-major axis** as a sphere radius, biasing every distance high near the equator by 0.67% | Property test comparing it against the ellipsoidal `LocalFrame` | IUGG mean radius (6 371 008.8 m); residual 0.56% is irreducible sphere-vs-ellipsoid difference |
| `bearing_deg` could return exactly **360.0** — `-1e-148 % 360.0` rounds up in IEEE-754 | Hypothesis, range invariant | Explicit upper-bound check; code bucketing bearings into sectors would have indexed off the end |
| Fixed-point undistortion **diverges at wide-lens corners** (r² ≈ 1.16 on an ordinary 90° action-camera calibration) — exactly where perimeter detections sit | Property round-trip test | Damped Newton with backtracking line search |

Investigating the third surfaced something worth knowing on its own:
**Brown-Conrady has a maximum representable radius.** `r_d = r·R(r²)` is not
monotonic under barrel distortion — for these coefficients it peaks near 1.03
around r ≈ 1.7, while the 16:9 frame corner needs 1.077. Those pixels correspond
to *no ray at all*. The solver detects the stalled residual and raises rather than
returning the nearest reachable point as if it were an answer. The test that
caught it was also wrong: it round-tripped pixel → ideal → pixel, which is the
ill-defined direction. It now starts from an ideal coordinate, where the target is
reachable by construction.

---

## 5. What is not built yet

In rough dependency order.

- [ ] **Perception pipeline** — VisDrone/UAVDT dataset prep, RF-DETR fine-tune,
      SAHI sweep mode, ONNX/TensorRT export, benchmark harness
- [ ] **Autonomy** — ROS 2 Jazzy workspace, MAVROS bridge, sortie state machine,
      precision-landing loop, SITL test harness
- [ ] **Simulation** — Gazebo Harmonic residential-society world, ArduPilot SITL
      integration, scripted incident scenarios
- [ ] **Backend services** — edge node (detection, fusion, MediaMTX, NATS leaf) and
      cloud (FastAPI, Postgres + PostGIS, NATS hub)
- [ ] **Ops dashboard** — React 19 + MapLibre GL, live map, alert triage, mission
      planner
- [ ] **ESP32 firmware** — perimeter node, gate node, dock controller
- [ ] **Hardware design spec** — BOM at three tiers, wiring, dock mechanical design
- [ ] **IEEE paper** and **presentation deck**

### Known gaps

- **DGCA regulation research is incomplete.** Seven of eight research topics
  landed; the Indian drone-regulation sweep failed on a rate limit and its re-run
  was stopped mid-flight. This is the highest-value gap — it determines what is
  legally claimable — and should be the first thing re-run. What *is* known from
  adjacent topics is captured in [prior-art](research/prior-art.md) and
  [unit-economics](research/unit-economics.md), including the DGFT import
  prohibition and the non-TC registration suspension.
- `docs/ops/setup.md` is written but the toolchains it describes (ROS 2, Gazebo,
  Docker, PlatformIO) are **not yet installed** on the dev machine. `make doctor`
  reports current state.
- No CI pipeline yet. The licence check promised in ADR-0004
  (`tools/check_licences.py`) is specified but not written.

---

## 6. How to pick this up

```bash
cd /home/sena/ESPworkspace/aegis
make doctor          # what is installed, and the exact fix for what is not
make setup           # bootstrap Python and web dependencies
make test            # 132 tests, should be green
make help            # everything else
```

Then read, in this order: this file → [`docs/adr/`](adr/) (0002, 0003, 0006 are
the important ones) → `aegis/domain/privacy.py` and `aegis/domain/dispatch.py`,
which are where the design actually lives.

### Suggested next step

Re-run the DGCA regulation research, then build the perception pipeline. The
perception work is the longest pole and it is fully unblocked — the detector
choice, licence position and error budget are all settled, and the georeferencing
it feeds is already written and tested.

---

## 7. Conventions

- **Commits** are small, atomic, and explain *why* rather than what. The diff
  already says what.
- **ADRs are immutable** once `Accepted`. Changing a decision means writing ADR
  *N+1* that supersedes it, never editing the original.
- **Every reported number must be reproducible** from this repository.
- Python is `ruff`-formatted and linted; `mypy` is strict on the domain model and
  services, lenient on training scripts where the numeric stack is poorly typed.
- Research notes under [`docs/research/`](research/) are compiled from a
  multi-agent web sweep and preserve the original confidence markers. Anything
  marked *(unverified)* has not been confirmed and must be checked before it is
  relied on.
