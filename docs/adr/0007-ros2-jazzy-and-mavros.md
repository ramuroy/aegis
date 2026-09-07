# 0007. ROS 2 Jazzy, bridged with MAVROS rather than AP_DDS

- **Status:** Accepted
- **Date:** 2026-09-07
- **Deciders:** Ramu Roy
- **Supersedes:** —
- **Superseded by:** —

## Context

[ADR-0005](0005-ardupilot-over-px4.md) settled the firmware — ArduPilot Copter
4.7.x, run unmodified, integrated over MAVLink 2. It deferred two questions that
follow from it: which ROS 2 distribution, and which bridge.

Both look like free choices and neither is.

### The distribution is forced by the companion computer

ROS 2's current LTS is **Lyrical Luth** (released 2026-05-22, supported to May
2031). It is the obvious pick for a project starting now — five years of support
against Jazzy's remaining runway.

It is also unusable here. Lyrical Luth's Tier-1 Linux platform is **Ubuntu 26.04**.
JetPack 7 — the only supported software stack for the Jetson Orin Nano Super
chosen in ADR-0005 — is built on **Ubuntu 24.04 LTS**. There is no JetPack for
26.04. So the current LTS cannot run on a supported image of the deployment
target's own hardware.

**ROS 2 Jazzy Jalisco** is Tier-1 on Ubuntu 24.04, which is exactly what JetPack 7
provides. It is the only LTS that fits.

This is a constraint chain, not a preference, and it propagates: the dev machine
matches the target, so the whole project sits on 24.04.

### The bridge is forced by ArduPilot's own support statement

ArduPilot ships a native ROS 2 interface, `AP_DDS`, which speaks DDS directly from
the flight controller with no translation layer. Architecturally it is the nicer
option — one less process, one less protocol hop, native ROS types end to end.

Two facts rule it out:

1. **ArduPilot's own ROS 2 documentation states that Humble is the only supported
   version.** Humble is Ubuntu 22.04. Using AP_DDS would mean either running an
   unsupported combination on Jazzy or dropping back to 22.04 — which reopens the
   JetPack problem from the other side.
2. **On STM32, AP_DDS requires an H7-class board.** F4 and F7 autopilots lack the
   CPU headroom to run DDS at all. That does not bite the Pixhawk 6C in the
   current BOM, but it does eliminate every cheaper flight controller from the
   Tier B build, which is a real constraint on the hardware design rather than a
   theoretical one.

**MAVROS** translates MAVLink to ROS topics in a separate process on the companion
computer. It is a translation layer we would rather not have, but `mavros 2.15.1`
was released into Jazzy on 2026-08-22, so it is current and maintained on exactly
the distribution we are pinned to.

## Options considered

### Option A — Lyrical Luth + AP_DDS
The architecturally cleanest and longest-supported combination. Impossible: no
JetPack for Ubuntu 26.04, and AP_DDS documents Humble only. Rejected on facts, not
on judgement.

### Option B — Humble + AP_DDS
Matches ArduPilot's stated support. Costs Ubuntu 22.04, which is off the JetPack 7
path and puts us on a distribution whose support window is shorter than Jazzy's.
Buys a cleaner bridge at the price of an unsupported companion-computer image —
the wrong trade, since the companion computer is where our code actually runs.

### Option C — Jazzy + MAVROS
Jazzy matches JetPack 7. MAVROS is current on Jazzy and speaks the MAVLink 2 that
ADR-0005 already committed to. The cost is a translation process and a second
protocol in the stack.

## Decision

**ROS 2 Jazzy Jalisco, bridged to ArduPilot with MAVROS 2.15.x.**

Supporting choices:

1. **MAVSDK-Python 3.17.x for the ground and dock orchestrator**, not for the
   onboard flight loop. It is a pleasant async API for mission upload and dock
   sequencing, and it does not belong in a real-time path.
2. **DroneKit is treated as dead.** It is unmaintained and must not appear in any
   dependency list, including examples.
3. **The MAVROS geoid datasets are part of setup, not an optional extra.** Without
   `install_geographiclib_datasets.sh`, MAVROS cannot convert between AMSL and
   ellipsoidal height — which is precisely the datum confusion
   `aegis/domain/geo.py` exists to prevent, reintroduced at the bridge. This is
   recorded in [`docs/ops/setup.md`](../ops/setup.md) because it fails silently.
4. **The bridge is a boundary, not a pass-through.** MAVLink messages are
   translated into AEGIS domain types at the edge of the autonomy package rather
   than propagated raw. This keeps the Vehicle Abstraction Layer of ADR-0003
   meaningful and means a future DJI adapter does not require rewriting every node.

## Consequences

**Easier:** everything runs on a supported JetPack image. MAVROS is
well-documented with a large user base, so integration problems are usually
someone else's already-solved problem.

**Harder:** an extra process and an extra protocol hop in the autonomy stack, with
its own failure modes (MAVROS silently not reconnecting after a link drop is a
known class of problem, and needs an explicit watchdog). We also carry translation
code that AP_DDS would have made unnecessary.

**Committed to:** Ubuntu 24.04 / Jazzy / JetPack 7 as one unit. Changing any one
of the three breaks the chain and requires re-deriving this decision.

**Revisit if:** ArduPilot documents AP_DDS support on Jazzy or later — worth
checking at each ArduPilot minor release, since it would remove a whole process
from the stack — or if the companion computer changes away from Jetson, which
would free the distribution choice entirely.

## References

- ROS 2 Jazzy Jalisco (Tier-1: Ubuntu 24.04); Lyrical Luth, 2026-05-22, supported to May 2031 (Tier-1: Ubuntu 26.04).
- JetPack 7 — built on Ubuntu 24.04 LTS.
- ArduPilot ROS 2 documentation: AP_DDS supported on Humble only; H7-class board required on STM32.
- `mavros` 2.15.1 released into Jazzy, 2026-08-22. MAVSDK-Python 3.17.2.
- Full comparison: [`docs/research/flight-stack.md`](../research/flight-stack.md).
