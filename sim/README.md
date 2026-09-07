# sim — Gazebo + ArduPilot SITL

Where AEGIS is validated. Real ArduPilot firmware in the loop, not a flight model
approximation.

**Status:** not started.

## What goes here

```
worlds/    a residential-society world: perimeter, towers, parking, clubhouse,
           trees, and the dock
models/    airframe, dock, sensor nodes, actors for incident scenarios
config/    ArduPilot parameters, pinned to 4.7+ naming
scripts/   launch, and scripted incident scenarios for repeatable evaluation
```

## Constraints that already apply

- **Gazebo Harmonic**, the LTS (supported to May 2029). Not Ionic — EOL December
  2026.
- **AirSim is not an option.** Microsoft AirSim shut down 2022, Project AirSim
  end of 2023, Colosseum archived read-only 2026-07-11.
- **Isaac Sim is out of reach on the current dev machine.** Isaac Sim 6.0 needs an
  RTX 4080 with 16 GB VRAM; the dev machine is an RTX 4060 Mobile with 8 GB. If
  photorealism is needed later it is Isaac Sim 5.1.0 + Pegasus v5.1.0, pinned
  together — Pegasus has no release for Isaac 6.0.x.
- **Copter 4.7 renamed the RTL parameters** to SI units (`RTL_ALT` → `RTL_ALT_M`).
  Parameter files from 4.6 do not apply cleanly.

`make sim`, `make sim-headless`.
Background: [`docs/research/flight-stack.md`](../docs/research/flight-stack.md).
