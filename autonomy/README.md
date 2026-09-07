# autonomy — ROS 2 workspace

Flight behaviour that runs on the companion computer: the sortie state machine,
the precision-landing loop, failsafe handling, and the MAVLink bridge.

**Status:** not started. This is the second-longest pole after perception.

## What goes here

```
src/
  aegis_msgs/       ROS interfaces for domain types (Decision, Sortie, PrivacyVerdict)
  aegis_bringup/    launch files, parameters, per-site configuration
  aegis_flight/     MAVROS bridge, sortie state machine, failsafe supervision
  aegis_landing/    precision-landing loop, dock approach, retry supervision
  aegis_privacy/    30 Hz gimbal constraint enforcement (wraps aegis.domain.privacy)
```

## Constraints that already apply

- **ROS 2 Jazzy, bridged with MAVROS 2.15.x** — not AP_DDS, which documents
  Humble only. ([ADR-0007](../docs/adr/0007-ros2-jazzy-and-mavros.md))
- **ArduPilot runs unmodified.** Onboard behaviour that must survive a
  companion-computer crash goes in Lua, not a firmware patch.
  ([ADR-0005](../docs/adr/0005-ardupilot-over-px4.md))
- **A failsafe is terminal for that sortie.** Once ArduPilot changes mode on a
  failsafe it stays there until a pilot intervenes; autonomy cannot silently
  resume. The state machine must model this rather than work around it.
- **SmartRTL is RAM-bounded** (~500 points). Sortie length is capped so the
  buffer cannot fill mid-mission and disable the mode.
- **The privacy constraint is fail-closed and runs at 30 Hz.** Stale pose or
  degraded GNSS closes the shutter and stows the gimbal.
  ([ADR-0006](../docs/adr/0006-privacy-by-design-no-identifiable-data-by-default.md))

Build with `make autonomy-build`, test with `make autonomy-test`.
Background: [`docs/research/flight-stack.md`](../docs/research/flight-stack.md).
