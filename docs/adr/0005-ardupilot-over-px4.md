# 0005. ArduPilot Copter as the flight firmware, run unmodified

- **Status:** Accepted
- **Date:** 2026-09-07
- **Deciders:** Ramu Roy
- **Supersedes:** —
- **Superseded by:** —

## Context

For a dock-based system, the single capability that decides whether the product
works unattended is **precision landing that recovers from its own failures**.
Everything else — waypoint navigation, geofencing, failsafes — both candidate
firmwares do competently. But a drone that misses the pad once and gives up is a
drone that needs a human on site, and a system that needs a human on site is not
an autonomous system.

As of September 2026 the two viable firmwares are:

- **ArduPilot Copter 4.7.1** (released 2026-09-03)
- **PX4 v1.17.0** (released 2026-05-13; v1.18.0-beta2 in flight test since 2026-08-09)

The relevant difference is not general quality, it is that ArduPilot ships a
complete precision-landing **retry state machine in firmware**:

| Parameter | Role |
| --- | --- |
| `PLND_STRICT` | whether to insist on a target lock before committing to descent |
| `PLND_RET_MAX` (4) | how many retry attempts before falling through |
| `PLND_TIMEOUT` (4 s) | how long a lost target is tolerated before a retry |
| `PLND_RET_BEHAVE` | what a retry does — climb and re-acquire, or go around |
| `PLND_ALT_MIN` (0.75 m) | floor below which retry is abandoned (committed to land) |
| `PLND_ALT_MAX` (8 m) | ceiling above which the target is not trusted |

PX4's precision landing is a thinner search-then-descend-then-give-up design.
ArduPilot additionally has onboard **Lua scripting** (so dock-specific behaviour
lives on the aircraft and survives a companion-computer crash), **Rally points**,
and a **SmartRTL → RTL → Land** fence ladder.

The counterweight is licensing, and it is real: **ArduPilot is GPLv3; PX4 is
BSD-3-Clause.** For a product intended for commercial sale that difference
normally decides the question outright.

It does not decide it here, because of *how* we intend to use the firmware.

## Options considered

### Option A — PX4, on the licence
BSD-3-Clause, no copyleft obligation under any usage pattern, and the cleaner
default for a commercial product. Costs us the retry state machine, which we
would then have to reimplement in the companion computer — off-board, across a
MAVLink link, in the one loop where link loss is most likely and least
tolerable. Rejected: it moves safety-critical recovery logic to the wrong side
of the least reliable link in the system.

### Option B — ArduPilot with modified firmware
Gets the retry machine and lets us patch behaviour into the autopilot. Triggers
GPLv3 distribution obligations on the modified firmware: shipping a unit means
publishing that source. Rejected — not because publishing is unacceptable, but
because it makes a licence commitment in exchange for patches we have not shown
we need.

### Option C — ArduPilot, run **unmodified**, integrated over MAVLink
The aircraft runs a stock, unmodified upstream build. All AEGIS logic lives in
separate processes on the companion computer, communicating over MAVLink 2 — a
documented wire protocol, not a linked library. Behaviour that must run onboard
is expressed as ArduPilot **Lua scripts**, which are interpreted data loaded at
runtime, not compiled into the firmware image.

Under this pattern GPLv3's distribution obligation attaches to the firmware we
distribute — which is unmodified upstream ArduPilot, already publicly available
under the same licence. Our own code is not a derivative work of it.

## Decision

**ArduPilot Copter 4.7.x, run unmodified, integrated over MAVLink 2 and
extended only through Lua scripts.**

Binding rules:

1. **No patches to ArduPilot C++ source.** If a change genuinely requires one,
   it goes upstream as a PR, and until it lands we work around it. This is not
   licence theatre — it is what keeps us on a supportable upstream and what
   keeps the licence analysis above true.
2. **Precision landing targets 10–15 cm 2σ**, not better. PX4 documents ~10 cm
   with IR-LOCK and published AprilTag work shows <10 cm in final descent, so
   this is achievable — but the remaining error is absorbed **mechanically**, by
   a self-centering conductive charging pad. We explicitly do not design a pad
   that requires <5 cm accuracy; funnels are cheaper and more reliable than
   control loops.
3. **A downward rangefinder is mandatory hardware**, not an option:
   `PLND_ALT_MIN`/`PLND_ALT_MAX` are inoperative without one, which means no
   retry behaviour at all. This propagates into the BOM as a hard line item.
4. **Contact charging, not inductive.** Every real dock uses contacts — DJI
   Dock 3 does 800 W and 15→95% in 27 minutes; Heisha's DPAD uses gold-plated
   dual electrodes at up to 10 A. Published inductive docking achieves only
   **56.6% transfer efficiency at 96.5 W**, which is both a thermal problem and
   an availability problem in a system whose whole point is being ready.
5. **Failsafe latch is designed for, not around.** Once an ArduPilot radio,
   battery, GCS or terrain failsafe changes mode, the vehicle stays in that mode
   until a pilot changes it directly — autonomy cannot silently resume the
   mission. The dispatch state machine treats a failsafe as a terminal state for
   that sortie requiring explicit operator clearance, which is the correct
   behaviour anyway.
6. **Parameter files are pinned to 4.7+ naming.** Copter 4.7 converted RTL
   parameters to SI units and renamed them (`RTL_ALT` → `RTL_ALT_M`); files
   written for 4.6 or earlier will not apply cleanly. Rally point altitudes
   override `RTL_ALT_M`, so the two are configured together or not at all.
7. **SmartRTL is bounded, and we bound it.** Its buffer is ~3 KB per 100 points
   (~500 points typical); when it fills, the mode disables itself and cannot be
   selected. Sortie length is capped so this cannot happen mid-mission.

## Consequences

**Easier:** the hardest part of unattended operation — landing reliably, again
and again, including after a failed attempt — is upstream's problem, tested by a
large community, running on the aircraft where it belongs. We inherit Rally
points and the fence ladder for free.

**Harder:** we accept a constraint on ourselves (no firmware patches) that will
occasionally be inconvenient, and we take on ArduPilot's parameter surface,
which is large and version-sensitive. ArduPilot's native ROS 2 bridge (`AP_DDS`)
documents support for **ROS 2 Humble only** and requires an H7-class autopilot,
so we bridge with MAVROS instead — a separate decision, recorded in ADR-0007.

**Committed to:** stock upstream firmware. The moment someone patches
ArduPilot's C++ for a "quick fix", the licence analysis in this ADR is void and
must be redone before anything ships.

**Revisit if:** PX4 ships a comparable precision-landing retry state machine —
worth re-checking at each minor release, since v1.18 is in flight test — or if
the project abandons commercial distribution, at which point Option B's
obligations cost nothing and firmware patching becomes available.

## References

- ArduPilot Copter 4.7.1 release notes (2026-09-03); `PLND_*` parameter documentation.
- PX4 v1.17.0 release (2026-05-13); PX4 precision landing documentation (~10 cm with IR-LOCK).
- DJI Dock 3 charging specification (800 W, 15→95% in 27 min); Heisha DPAD electrode rating.
- Inductive docking efficiency measurement (56.6% at 96.5 W).
- Full comparison: `docs/research/flight-stack.md`.
