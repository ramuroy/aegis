# Changelog

## 2026-09-08 documentation handoff

- Added [regulatory research](docs/research/drone-regulation.md) and a
  [resumable handoff](docs/HANDOFF-2026-09-08.md), including decisions, rationale,
  source-retrieval limits and the distinction between R&D and commercial flight.
- Recovered DGCA's nano/model registration instructions and visually read the
  2024 amendment through Brave; retained project-specific approval gates.
- Reconciled the README, STATE, older research notes, subsystem plans, setup
  guidance and ADR index with this checkpoint. Historical source snapshots and
  accepted ADRs remain intact; dated corrections qualify older broad claims.
- Clarified planned versus implemented licence/CI enforcement and historical
  test/setup evidence. Next work is perception provenance and dataset preparation.
- No runtime, firmware, dependencies or accepted ADR bodies changed. No tests,
  lint, training, deployment or physical-flight validation ran in this session.


Notable changes to AEGIS. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning will follow [Semantic Versioning](https://semver.org/) from the first
release.

For *why* a decision was made, see [`docs/adr/`](docs/adr/). For where the project
currently stands, see [`docs/STATE.md`](docs/STATE.md).

## [Unreleased]

Nothing released yet. The project is pre-`0.1.0`; everything below is the initial
build-out.

### Decided

- **ADR-0001** — Record architecture decisions. Four disciplines pull shared
  choices in opposite directions and the code shows only the outcome.
- **ADR-0002** — Dispatch on corroborated triggers, no patrol schedule. A
  scheduled patrol loses to fixed CCTV ~12:1 on temporal coverage per rupee at
  the society size that would buy one; CPCB's 45 dB(A) night limit and ~400
  battery cycles to 80% SoH both penalise the schedule specifically.
- **ADR-0003** — Edge-first three-tier topology; the cloud is never in the
  flight-critical loop. Measured 740 ms P50 India→ap-south-1→India against a
  170–300 ms human-takeover ceiling.
- **ADR-0004** — RF-DETR as the detector; no AGPL in the inference path. Every
  Ultralytics generation is AGPL-3.0 and names edge/robotics/camera deployment as
  an Enterprise-licence trigger.
- **ADR-0005** — ArduPilot Copter 4.7.x, run unmodified. It ships a
  precision-landing *retry* state machine in firmware; PX4 does not. Running stock
  and integrating over MAVLink keeps GPLv3 off our code.
- **ADR-0006** — Emit no identifiable personal data by default. DPDP Act §7 is a
  closed list with no legitimate-interest and no security-of-property ground.
- **ADR-0007** — ROS 2 Jazzy, bridged with MAVROS rather than AP_DDS. No JetPack
  exists for the Ubuntu the newer ROS 2 LTS requires, and AP_DDS documents Humble
  only.

### Added

- **Domain model** (`aegis/domain/`)
  - Typed ULID identifiers, minted per tier, with `NewType` wrappers so swapped
    arguments are a type error.
  - Datum-safe geodesy: `Altitude` carries its reference datum and refuses
    cross-datum arithmetic; `LocalFrame` is an ellipsoidal ENU tangent plane;
    `AltitudeBand` models a vertical slice so overflight does not trip every
    balcony beneath it.
  - **Privacy map** — one signed, versioned artefact that is simultaneously the
    RWA's approved-policy annexure and the runtime gimbal constraint. Enforcement
    is angular rather than volumetric, so it yields a corrective clamp instead of
    a bare verdict, and pose uncertainty inflates the exclusion regions so a
    degraded fix mechanically widens them. Fail-closed throughout.
  - **Sensing layer** keyed on `ModalityFamily`, which encodes which failure modes
    correlate. `SensorNode` carries measured clock skew, because ESP32 nodes
    without an RTC drift seconds per day and fail to corroborate silently.
  - **Corroboration gate** — the only thing that launches an aircraft. Requires
    ≥2 modality families from ≥2 distinct nodes, or one high-confidence detection
    in a high-value zone. Corroboration and admission are separate audited stages.
- **Vision** (`aegis/vision/`)
  - Pinhole camera model with Brown-Conrady distortion and a damped-Newton
    inverse.
  - Georeferencing with a propagated error budget that reports the *dominant*
    term. Uses the bounding-box foot point, not its centre.
- **Tests** — 132, property-based (Hypothesis) wherever the maths warrants it.
- **Documentation** — seven ADRs; seven sourced research notes carrying 212
  findings, 89 hard constraints and 212 source URLs with confidence markers
  preserved; project state and handoff document; environment setup guide;
  contributor guide; a README for every planned subsystem stating the constraints
  that already bind it.
- **Tooling** — `make` as the single entry point across four toolchains, a
  toolchain doctor that names the exact remedy for each missing tool, and lint /
  format / test runners that skip absent toolchains but report what they skipped.

### Fixed

Three defects, all surfaced by property tests rather than example tests, all
pinned by regression tests.

- `haversine_m` used the WGS-84 **semi-major axis** as a sphere radius, biasing
  every distance high near the equator by up to 0.67%. Now the IUGG mean radius;
  the residual 0.56% is the irreducible sphere-vs-ellipsoid difference.
- `bearing_deg` could return exactly **360.0** — `-1e-148 % 360.0` evaluates to
  360.0 in IEEE-754 because `360.0 - 1e-148` is not representable. Code bucketing
  bearings into sectors would have indexed past the end of its array.
- Fixed-point undistortion **diverged at wide-lens corners** (r² ≈ 1.16 on an
  ordinary 90° action-camera calibration) — precisely where perimeter detections
  sit. Replaced with damped Newton plus a backtracking line search.

Investigating the third established that **Brown-Conrady has a maximum
representable radius**: `r_d = r·R(r²)` is not monotonic under barrel distortion,
so for that calibration it peaks near 1.03 while the 16:9 frame corner needs
1.077. Those pixels correspond to no ray at all, and the solver now says so
rather than returning the nearest reachable point as though it were an answer.

Also fixed, in documentation and tooling:

- Five ADRs and the README linked to `docs/research/*.md` files that did not
  exist; ADR-0005 referred forward to an ADR-0007 that had not been written.
- `make lint`, `make fmt` and `make paper` invoked scripts that did not exist.
- The repository layout described eight directories that git was not tracking,
  because git does not track empty directories.
- The mypy configuration carried an `ignore_missing_imports` override for
  `ultralytics`, which ADR-0004 forbids outright — a rule that would have quietly
  permitted the import it bans.
- Two research citations leaked local `file://` paths to cached PDFs; a DGFT URL
  containing literal parentheses is now percent-encoded.

### Known gaps

- **DGCA research follow-up (2026-09-08):** added the sourced
  [drone-regulation checkpoint](docs/research/drone-regulation.md) and updated the
  handoff. Distinguishes conditional R&D from commercial operation, separate
  TC/UIN/RPC requirements, registration suspension and the recovered nano/model
  application instructions, import exceptions,
  amendment/source limits and the unresolved preflight/offline-dispatch contract.
  Legal coverage and physical-flight approval remain PARTIAL. Next software work
  is perception licence provenance, dataset preparation and an RF-DETR baseline;
  accepted ADRs and runtime code are unchanged.
- No CI pipeline. `tools/check_licences.py`, promised by ADR-0004, is specified
  but not written.
- Perception, autonomy, simulation, services, web, firmware, hardware spec, paper
  and deck are all not started.
