# Flight & Autonomy Stack

## Applicability update: 2026-09-08

Accepted ADRs retain stock ArduPilot, the no-C++-fork boundary, permitted Lua and
the ROS 2 Jazzy/MAVROS integration direction. This session did not requalify the
version/hardware matrix, run SITL or approve a real aircraft configuration.
Autopilot capability and an autonomous-UAS category are not proof of permission
for unattended/BVLOS/night service. The [regulatory checkpoint](drone-regulation.md)
supersedes broader legal assumptions below and identifies the open offline-launch
question without changing accepted ADRs. See the [handoff](../HANDOFF-2026-09-08.md).


> Research note for [AEGIS](../../README.md). Compiled 2026-09-07 from a multi-agent
> web research sweep. Every claim below is sourced; confidence levels are the
> researcher's own and are preserved verbatim.

## Summary

As of Sept 2026 the two viable firmwares are ArduPilot Copter 4.7.1 (released
2026-09-03) and PX4 v1.17.0 (released 2026-05-13, with v1.18.0-beta2 in flight test
since 2026-08-09). For a dock-based patrol system ArduPilot wins on the one thing
that actually decides the product — it ships a complete precision-landing retry state
machine in firmware (PLND_STRICT / PLND_RET_MAX=4 / PLND_TIMEOUT=4 s /
PLND_RET_BEHAVE / PLND_ALT_MIN=0.75 m / PLND_ALT_MAX=8 m) plus onboard Lua scripting,
Rally points and a SmartRTL→RTL→Land fence ladder, whereas PX4's precision landing is
a thinner search-then-give-up design and PX4 has no onboard scripting. The
counterweight is licensing: ArduPilot is GPLv3, PX4 is BSD-3-Clause — if you intend
to ship modified autopilot firmware in a commercial RWA product, that is a business
decision, not a technical one. On the companion side the Jetson Orin Nano Super 8GB
(67 TOPS, 7–25 W, ₹36,882 dev kit) is the only board that comfortably runs YOLO26
detection *and* a 30 Hz vision-landing loop concurrently; Ultralytics measures YOLO26n
at 640 px in 3.80 ms INT8 (~263 FPS, inference-only) on it. Raspberry Pi 5 + AI HAT+
26 TOPS (₹10,670) is a third the price but its published 431 FPS is a hardware-only
benchmark — real end-to-end pipelines land near 30 FPS, which is tight once you add
the landing loop. Middleware: use ROS 2 Jazzy Jalisco because it is the distro that
matches JetPack 7 (Ubuntu 24.04); the new LTS, Lyrical Luth (2026-05-22, supported to
May 2031), is Tier-1 on Ubuntu 26.04 and therefore has no JetPack, and ArduPilot's own
ROS 2 docs still say "Humble is the only version supported" for AP_DDS. Bridge with
MAVROS 2.15.1 (released into jazzy on 2026-08-22), keep MAVSDK-Python 3.17.2 for the
ground/dock orchestrator, and treat DroneKit as dead. Precision landing should target
10–15 cm 2σ (PX4 documents ~10 cm with IR-LOCK; published AprilTag work shows <10 cm
in final descent) and the remaining error must be absorbed by a mechanically
self-centering conductive charging pad — do not design a pad that needs <5 cm. Contact
charging is what every real dock uses (DJI Dock 3: 800 W, 15%→95% in 27 min; Heisha
DPAD: gold-plated dual electrodes up to 10 A); published inductive docking hits only
56.6% transfer efficiency at 96.5 W, so reject it for v1. For simulation, Gazebo
Harmonic (LTS to May 2029) + ArduPilot SITL + ardupilot_gazebo is the working loop;
AirSim is dead and its Colosseum fork was archived 2026-07-11, so photorealism must
come from Isaac Sim — and specifically Isaac Sim 5.1.0 + Pegasus Simulator v5.1.0,
because Pegasus has no release for Isaac Sim 6.0.1 yet.

## Hard constraints

- ArduPilot is GPLv3. If you distribute a product containing modified ArduPilot
  firmware, you **must make that modified source available**. PX4 is BSD-3-Clause and
  carries no such obligation. Decide this before you write firmware patches, not
  after.
- ROS 2 Lyrical Luth's Tier-1 Linux platform is Ubuntu 26.04; JetPack 7 is built on
  Ubuntu 24.04 LTS. **You cannot run the current ROS 2 LTS on a supported Jetson
  image** — Jazzy (Ubuntu 24.04) is the only LTS that fits.
- ArduPilot's native ROS 2 (AP_DDS) is documented as **supporting ROS 2 Humble only**,
  and on STM32 it **requires an H7-class board** — F4 and F7 autopilots lack the CPU
  to run DDS.
- ArduPilot precision-landing retry (PLND_ALT_MIN / PLND_ALT_MAX) **requires a
  downward rangefinder**. Without one you get no retry behaviour at all.
- Copter 4.7 converted RTL parameters to SI units and renamed them (RTL_ALT →
  RTL_ALT_M). Parameter files written for 4.6 or earlier **will not apply cleanly**.
- **Rally point altitudes override RTL_ALT_M** — ArduPilot docs state
  RTL_ALTITUDE/RTL_ALT_M are NOT used when a Rally Point is selected.
- The Raspberry Pi AI HAT+ **requires a Raspberry Pi 5** (PCIe Gen 3). **It does not
  work on Pi 4 or CM4 at full bandwidth**, and the Pi 5 needs the official 27 W
  (5V/5A) supply or it throttles.
- Isaac Sim 6.0 minimum spec is an RTX 4080 with 16 GB VRAM plus 32 GB system RAM.
  **A100 and H100 are explicitly unsupported** (no RT Cores).
- Pegasus Simulator v5.1.0 **works only with Isaac Sim 5.1.0** and is explicitly
  incompatible with other Isaac versions. There is no Pegasus release for Isaac Sim
  6.0.x as of 2026-09-07.
- Qualcomm Flight RB5 is **end-of-life at ModalAI and cannot be designed into a new
  product**.
- CodexLabsLLC/Colosseum was archived read-only on 2026-07-11; Microsoft AirSim (2022)
  and Project AirSim (end of 2023) are both shut down. **None can be a project
  dependency.**
- Gazebo Ionic reaches EOL in December 2026 — **do not start a new project on it**.
- India: **BVLOS operation is restricted to designated corridors and
  government-approved entities/select delivery operators.** A fully autonomous BVLOS
  patrol over a private residential society is not covered by any general permission
  and **requires specific DGCA authorisation**. (Secondary sources — confirm with DGCA
  directly.)
- India: **DGCA type certification is mandatory for commercial drones before
  manufacture, sale or operation.** (Secondary sources — confirm with DGCA directly.)
- Once an ArduPilot radio, battery, GCS or terrain-data-loss failsafe triggers a mode
  change, the vehicle remains in that mode until a pilot changes it directly.
  **Autonomy software cannot silently resume the mission.**
- SmartRTL is RAM-bounded (~3 KB per 100 points, ~500 points typical); **when the
  buffer fills the mode disables itself and cannot be selected**.

## Findings

### Firmware and flight-controller hardware

- **ArduPilot Copter 4.7.1 is the current stable Copter firmware, released
  2026-09-03** — GitHub release tag Copter-4.7.1 published 2026-09-03T23:50:43Z;
  announced on Discourse as 'the stable/official version for multicopters and
  traditional helicopters'. Copter-4.7.0 preceded it on 2026-07-21/22. 4.7.1 adds
  board support (ARKV6S, CORVON_V5, ORBITH743v2) and fixes to circle/simple/auto
  modes, GPS corrections and gimbal comms.
  [source](https://discuss.ardupilot.org/t/copter-4-7-1-released/145385)
- **PX4 v1.17.0 is the current stable PX4 release (2026-05-13); v1.18.0-beta2 is in
  flight test since 2026-08-09** — Zenodo record 10.5281/zenodo.20168996 'Published
  May 13, 2026 | Version v1.17.0'. GitHub API shows v1.18.0-beta2 published
  2026-08-09T04:44:58Z, prerelease=true. v1.17 headline features: new multicopter
  Altitude Cruise mode, FwLateralLongitudinalSetpointType and RoverSetpointTypes for
  ROS 2 control, rmw_zenoh compatibility, on-device TensorFlow Lite Micro neural
  control (research only), 3 new INS drivers (MicroStrain, sbgECom, EULER-NAV).
  [source](https://zenodo.org/records/20168996)
- **Copter 4.7 renamed RTL altitude parameters to SI units — RTL_ALT_M replaces
  RTL_ALT — which breaks existing parameter files** — Copter-4.7.0 release notes:
  'RTL parameters underwent major conversion to SI units with new naming conventions
  (e.g., RTL_ALT_M replacing RTL_ALT)', plus a fix to RTL final altitude behaviour
  when RTL_ALT_FINAL is non-zero. The Rally Points doc confirms the new name: 'The
  RTL_ALTITUDE or RTL_ALT_M parameters are NOT used with Rally Points!'.
  [source](https://discuss.ardupilot.org/t/copter-4-7-0-released/144650)
- **Pixhawk 6C (STM32H743) is a $166 H7 board that satisfies the AP_DDS CPU
  requirement and runs both firmwares** — Holybro Pixhawk 6C: STM32H743 main
  processor, redundant IMUs ICM-42688-P and BMI088, plus magnetometer and barometer.
  From $165.99 (plastic case, no power module); bundles $184.98–$219.98. Ships with
  PX4 pre-installed and supports ArduPilot 4.3+.
  [source](https://holybro.com/products/pixhawk-6c)

### Precision landing, dock and charging

- **ArduPilot ships a full precision-landing retry state machine in firmware; PX4 does
  not** — AC_PrecLand.cpp AP_GROUPINFO defaults: PLND_ENABLED=0, PLND_TYPE=0 (0:None
  1:MAVLink 2:IRLock 3:SITL_Gazebo 4:SITL), PLND_YAW_ALIGN=0 cdeg, PLND_LAND_OFS_X/Y=0
  cm (range ±20 cm), PLND_EST_TYPE=1 (KalmanFilter), PLND_ACC_P_NSE=2.5 (0.5–5),
  PLND_CAM_POS=0.0 m, PLND_BUS=-1, PLND_LAG=0.02 s (range 0.02–0.250),
  PLND_XY_DIST_MAX=2.5 m, PLND_STRICT=1 (0:Land Vertically 1:Retry Landing 2:Hover),
  PLND_RET_MAX=4, PLND_TIMEOUT=4 s, PLND_RET_BEHAVE=0, PLND_ALT_MIN=0.75 m,
  PLND_ALT_MAX=8 m, PLND_OPTIONS bitmask (0:Moving Target 1:Allow after reposition
  2:High speed descent), PLND_ORIENT.
  [source](https://raw.githubusercontent.com/ArduPilot/ardupilot/master/libraries/AC_PrecLand/AC_PrecLand.cpp)
- **PX4 precision landing achieves roughly 10 cm with IR-LOCK and supports arbitrary
  vision via MAVLink LANDING_TARGET** — PX4 docs: IR-LOCK sensor + IR beacon +
  downward distance sensor gives 'roughly 10 cm' precision. Params: PLD_HACC_RAD=0.2 m
  (horizontal acceptance radius), PLD_BTOUT=5 s, PLD_FAPPR_ALT=0.1 m, plus
  PLD_SRCH_ALT / PLD_SRCH_TOUT / PLD_MAX_SRCH / PLD_YAW_EN, SENS_EN_IRLOCK, LTEST_MODE
  (0:moving 1:stationary), RTL_PLD_MD (0:disabled 1:opportunistic 2:required). Three
  phases: horizontal approach → descent over target → final approach. Two Kalman
  filters (x, y) in landing_target_estimator.
  [source](https://docs.px4.io/main/en/advanced_features/precland.html)
- **ArduPilot supports five precision-landing backends including a BlueOS extension
  and AprilTag over MAVLink** — Documented backends: BlueOS Precision Landing Extension
  (companion-computer), IR-LOCK sensor+beacon, Landmark Precision Landing System,
  UAVLAS ULS-XCopter-G2 IR beacon kit, and MAVLink LANDING_TARGET messages from a
  companion computer using fiducial markers such as AprilTag. Copter 4.7.0 added
  LOCAL_FRD frame support to the precision-landing MAVLink backend.
  [source](https://ardupilot.org/copter/docs/precision-landing-and-loiter.html)
- **IR-LOCK sensor is $349 / 21.5 g with 15 m beacon detection; ArduPilot setup is two
  parameters** — IR-LOCK Sensor (modified Pixy camera, IR filter and 3.6 mm lens
  pre-installed): $349.00, 21.5 g, I2C to autopilot, mounted lens-down on the underside
  of the frame with the white button pointing forward. MarkOne Beacon V3.0 detection
  range 15 m in all lighting conditions. ArduPilot config: PLND_ENABLED=1, PLND_TYPE=2.
  ArduPilot documents testing at approximately 10 m above the target and publishes no
  cm accuracy figure.
  [source](https://ardupilot.org/copter/docs/precision-landing-irlock.html)
- **Published AprilTag landing work reports sub-10 cm terminal accuracy** —
  Long-Duration Autonomy for Small Rotorcraft UAS including Recharging: 48 cm AprilTag
  from a 4 m approach height, expected 2σ height estimation error 4.5 cm, error below
  0.1 m in the final stage of descent; simulated 2σ landing error 0.09 m major
  half-axis / 0.08 m minor half-axis. Note this is a 2018 paper — treat as the design
  floor, not the 2026 state of the art. [source](https://arxiv.org/pdf/1810.05683)
  *(likely)*
- **Every production dock uses conductive contact charging with mechanical centering,
  not induction** — DJI Dock 3: 55 kg, 640×745×770 mm closed / 1760×745×485 mm open,
  100–240 VAC 50/60 Hz, max 800 W, 15%→95% aircraft charge in 27 minutes, IP56, −30 to
  50 °C, 12 Ah lead-acid backup giving >4 h (without charging/climate), 1 aircraft per
  dock, max landing wind 12 m/s, multi-constellation RTK. Supports Matrice 4D / 4TD
  (47 min endurance at 15 m/s, IP55, 48 MP tele + 640×512 thermal + 1800 m laser
  rangefinder). [source](https://enterprise.dji.com/dock-3/specs)
- **Heisha publishes the concrete electrical envelope for a DIY contact charging pad**
  — DPAD line: gold-plated dual electrodes passing up to 10 A; models operate at 17.5 V
  or 52.8 V with max charging currents 6–10 A depending on drone size; 'Smoother
  Centering' via optimised PCB wiring; infrared sensors with sun-blocking shade for
  positioning; compatible with DJI series and open-source platforms. The C200 pad is
  80×80 cm, max 6 A, 17.5 V DC input. The C300 claims 'vision-based precision landing
  centimeter-level accuracy' plus a locking structure.
  [source](https://heishatech.com/for-developers/dpad-c500-drone-charging-pad/)
- **Published inductive drone docking achieves only 56.6% power transfer efficiency at
  96.5 W** — Design and Validation of a Wireless Drone Docking Station (arXiv
  2309.05433): maximum output power 96.5 W with power transfer efficiency of 56.6%
  using three wireless charging modules connected in series; series beat parallel. For
  comparison, commercial WiBotic products are 150 W / 250 W / 300 W with a 1 kW unit
  announced, using GaN plus Vicor modules and 'Adaptive Matching'.
  [source](https://arxiv.org/abs/2309.05433)

### Failsafes, geofence, return-to-dock and India regulation

- **ArduPilot Rally Points give you a dock-first RTL that ignores home** — On RTL the
  vehicle flies to the nearest Rally Point rather than home. RALLY_TOTAL
  (GCS-managed, do not edit), RALLY_LIMIT_KM (max distance for a rally point to be
  eligible; 0 disables the limit), RALLY_INCL_HOME (allow home to compete as a rally
  point). Each rally point carries its own altitude relative to home, and RTL_ALT_M is
  not applied. [source](https://ardupilot.org/copter/docs/common-rally-points.html)
- **ArduPilot geofencing supports layered inclusion/exclusion polygons with an
  escalating action ladder** — FENCE_ENABLE=1; FENCE_TYPE bitmask bit0=global max
  altitude, bit1=cylindrical 'TinCan' centred on home, bit2=inclusion/exclusion polygon
  or circle zones, bit3=global min altitude. FENCE_ACTION options include 0=Report
  Only, 1=RTL/LAND, 2=LAND/HOLD, 3=SmartRTL/RTL/LAND. FENCE_ALT_MAX, FENCE_ALT_MIN,
  FENCE_MARGIN. On breach the system erodes backup fences outward in 20 m increments
  and forces LAND/HOLD at 100 m beyond the configured boundary, with RC-switch pilot
  override.
  [source](https://ardupilot.org/copter/docs/common-geofencing-landing-page.html)
- **ArduPilot SmartRTL retraces the flown path but is RAM-limited** — Points captured
  at max 3 per second, only when the vehicle has moved SRTL_ACCURACY metres from the
  last point; path is then simplified (curves→straight lines) and pruned (loops
  removed). SRTL_POINTS sets the buffer; each additional 100 points costs ~3 KB RAM and
  most autopilots handle 500 points. SRTL_POINTS=0 disables SmartRTL. SRTL_OPTIONS bit
  2 (value 4) suppresses pilot yaw input. When the buffer fills, the mode disables
  itself and cannot be selected.
  [source](https://ardupilot.org/copter/docs/smartrtl-mode.html)
- **ArduPilot Copter documents ten distinct failsafe subsystems** — Radio, Battery,
  GCS, EKF, Dead Reckoning, Vibration, Terrain Data Loss, Crash Check, Parachute, and
  an independent hardware Watchdog. Important behavioural note: once a Radio, Battery,
  GCS or Terrain Data Loss failsafe triggers a mode change, the vehicle stays in that
  mode until the pilot changes it directly.
  [source](https://ardupilot.org/copter/docs/failsafe-landing-page.html)
- **PX4 failsafe parameter set for an equivalent safety configuration** — Battery:
  COM_LOW_BAT_ACT (warn / land / return-then-land / return-then-terminate), BAT_LOW_THR,
  BAT_CRIT_THR, BAT_EMERGEN_THR. RC loss: COM_RC_LOSS_T, NAV_RCL_ACT
  (loiter/return/land/disarm/terminate), COM_RCL_EXCEPT. Datalink: COM_DL_LOSS_T,
  NAV_DLL_ACT, COM_DLL_EXCEPT. Geofence: GF_ACTION (hold/return/land/terminate),
  GF_MAX_HOR_DIST, GF_MAX_VER_DIST. Position: COM_POS_FS_EPH, EKF2_NOAID_TOUT.
  [source](https://docs.px4.io/main/en/config/safety.html)
- **ParaZero now has an Indian channel partner, but published prices are for
  DJI-specific kits** — ParaZero signed a strategic cooperation agreement with India's
  BonV Aero in March 2026 (framed as a counter-drone deal). US retail: SafeAir Mavic 3
  with RC parachute $1,757; SafeAir Anzu Raptor $1,852; SafeAir DJI Matrice 350 Pro
  $3,999. No India-specific pricing or a custom-multirotor kit price could be verified.
  [source](https://www.stocktitan.net/news/PRZO/para-zero-signed-a-strategic-cooperation-agreement-with-india-s-bon-jz9kkeri7l5g.html)
  *(likely)*
- **India permits BVLOS only in designated corridors / for approved entities, and a new
  drone Bill is pending** — DGCA has approved three BVLOS corridors — Ladakh (minerals
  survey), Telangana (pharma delivery), Andhra Pradesh (coastal monitoring) — plus
  delivery/logistics corridors in Telangana, Uttarakhand and Gujarat. BVLOS
  authorisation is 'currently restricted to government-approved entities and select
  drone delivery operators'. The draft Civil Drone (Promotion and Regulation) Bill,
  2025 was introduced by MoCA in September 2025 and would replace the existing Drone
  Rules entirely. DGCA type certification is mandatory for commercial drones before
  manufacture, sale or operation. Sources are secondary Indian industry blogs, not the
  DGCA gazette — verify directly before committing.
  [source](https://www.kodainya.com/blogs/drone-laws-in-india) *(uncertain)*

### Middleware: ROS 2, MAVROS, MAVSDK

- **ROS 2 Lyrical Luth is the new LTS (2026-05-22, supported to May 2031) but its
  Tier-1 Linux platform is Ubuntu 26.04** — Tier 1: Ubuntu 26.04 (Resolute)
  amd64+arm64, Windows 11/VS2022 amd64. Features: Callback Group Events Executor using
  10–15% less CPU than Single/Multithreaded executors; AsyncNode for rclpy (asyncio +
  rclpy together); zero-copy GPU data transfer via rosidl::Buffer improvements with
  rmw_fastrtps_cpp; new CLI parameter commands and multi-topic bandwidth monitoring;
  remote-controllable and circular bag recording.
  [source](https://discourse.openrobotics.org/t/ros-2-lyrical-luth-released/55021)
- **JetPack 7 is built on Ubuntu 24.04 LTS and Linux kernel 6.8 — which pins a Jetson
  companion to ROS 2 Jazzy, not Lyrical Luth** — NVIDIA: JetPack 7 is 'Built on Linux
  Kernel 6.8 and Ubuntu 24.04 LTS' with full support for the Jetson Orin and Thor
  platforms. Ubuntu 24.04 is the Tier-1 platform for ROS 2 Jazzy and Kilted, not for
  Lyrical Luth (26.04). [source](https://developer.nvidia.com/embedded/jetpack)
- **MAVROS is actively released and is the only MAVLink↔ROS 2 bridge with binaries
  across every current distro** — mavros 2.15.1 released 2026-08-22 simultaneously into
  Humble, Jazzy, Kilted, Lyrical and Rolling. ROS Index marks it 'RECOMMENDED', status
  DEVELOPED / RELEASED. Latest changelog fixes namespace handling in launch files and
  ROS 2 deprecations. [source](https://index.ros.org/p/mavros/)
- **ArduPilot's native ROS 2 (AP_DDS) is officially Humble-only and requires an STM32H7
  autopilot** — ArduPilot dev docs: 'Currently, ROS 2 Humble is the only version
  supported.' Install via `vcs import --recursive --input
  https://raw.githubusercontent.com/ArduPilot/ardupilot/master/Tools/ros2/ros2.repos
  src` then `colcon build --packages-up-to ardupilot_dds_tests`, with micro-ROS-Agent.
  AP_DDS is native from ArduPilot 4.5+ over XRCE-DDS; on STM32 boards it should only be
  used on H7-based boards because F4 and F7 lack the CPU headroom. Topics/services and
  publish rates are individually enabled at compile time.
  [source](https://ardupilot.org/dev/docs/ros2-install.html)
- **MAVSDK-Python is alive and current at 3.17.2 (2026-07-22); DroneKit-Python is not
  maintained** — MAVSDK-Python GitHub releases: 3.17.2 published 2026-07-22, preceded
  by 3.15.0–3.15.3 on 2026-02-11. DroneKit-Python 'has not been maintained for some
  years'; PX4 docs steer new projects to ROS 2 instead.
  [source](https://github.com/mavlink/MAVSDK-Python/releases)
- **PX4's ROS 2 path is uXRCE-DDS by default with the px4_ros2 C++/Python interface
  library at 2.2.1** — uXRCE-DDS is 'more tested and included by default in most PX4
  builds' and exposes uORB messages as ROS 2 messages; Zenoh must be manually added and
  enabled. The PX4 ROS 2 Interface Library lets you write flight modes in ROS 2
  'indistinguishable from internal PX4 modes'. Auterion/px4-ros2-interface-lib releases:
  2.2.1 (2026-08-03, px4_msgs 3.5), 2.2.0 (2026-08-03), 2.1.1 (2026-05-19), 2.1.0
  (2026-03-23, added Python bindings), 2.0.0 (2025-12-15). px4_msgs carries release/1.17
  and release/1.18 branches for version pinning.
  [source](https://docs.px4.io/main/en/ros2/)

### Companion compute and perception

- **Jetson Orin Nano Super 8GB dev kit is ₹36,882 in India; 67 TOPS at 7–25 W** —
  Fab.to.Lab (India): ₹36,882.11. Specs: 67 TOPS, 8 GB 128-bit LPDDR5 at 102 GB/s,
  7 W–25 W, 1024 CUDA cores + 32 tensor cores @ 1020 MHz, 6-core Arm Cortex-A78AE @
  1.7 GHz, 4K60 H.265 decode. NVIDIA MSRP $249. Bare module (Orin Nano 8GB) listed at
  ₹43,109 by Tanna TechBiz; Orin NX 16GB module ₹105,509.
  [source](https://www.fabtolab.com/seeed-nvidia-jetson-orin-nano-super-developer-kit)
- **YOLO26n on Orin Nano Super runs at 3.80 ms INT8 / 4.57 ms FP16 per 640 px image —
  but these figures exclude pre- and post-processing** — Ultralytics Jetson benchmarks,
  YOLO26n @ 640×640: Orin Nano Super (JetPack 6.1+) TensorRT FP16 4.57 ms (~219 FPS),
  INT8 3.80 ms (~263 FPS). Orin NX 16GB (JetPack 6.0/6.1+) FP16 4.13 ms (~242 FPS),
  INT8 3.49 ms (~287 FPS). Ultralytics explicitly notes the measurements exclude
  preprocessing and postprocessing.
  [source](https://docs.ultralytics.com/guides/nvidia-jetson/)
- **YOLO26 (Jan 2026) is NMS-free end-to-end, which materially simplifies edge
  deployment** — Five scales reaching 40.9–57.5 mAP on COCO at 1.7–11.8 ms T4 TensorRT
  latency. Removes NMS natively and drops Distribution Focal Loss, reducing model
  complexity. Nano variant up to 43% faster CPU inference vs YOLO11. Exports to
  TensorRT, ONNX, CoreML, TFLite, OpenVINO.
  [source](https://www.ultralytics.com/yolo/yolo26)
- **Raspberry Pi AI HAT+ 26 TOPS (Hailo-8) is ₹10,670 in India but its headline FPS
  numbers are hardware-only benchmarks** — CrazyPi India: ₹10,670.00; $110 MSRP (13
  TOPS Hailo-8L version $70). Requires Raspberry Pi 5 exclusively via PCIe Gen 3;
  official 27 W (5V/5A) USB-C PSU recommended or the board throttles. Runs 3–5
  concurrent models. Benchmarks vary by two orders of magnitude depending on
  methodology: 431 FPS YOLOv8n / 491 FPS YOLOv8s at batch 1, 640 px (hardware
  benchmark); 136.7 FPS at batch 8; ~29.5 FPS for a full 640×640 detection pipeline.
  Pi 5 PCIe Gen3 gives roughly double the Gen2 frame rate.
  [source](https://www.crazypi.com/raspberry-pi-ai-hat-plus-26-tops-hailo-8-india)
- **Luxonis RVC2 (OAK-D family) delivers 4 TOPS total / 1.4 TOPS AI at ~4.5 W and runs
  YOLO at ~30 FPS only at 416 px** — RVC2 measured: YOLOv8n @416×416 = 31.3 FPS,
  YOLO11n @416 = 28.08 FPS, YOLOv10n @416 = 27.07 FPS; larger models drop to 3–6 FPS.
  Max power ~4.5 W. Encoding H.264/H.265/MJPEG up to 4K30 or 1080p60. Prices: OAK-D
  Lite $269, OAK-D $329, OAK-D Pro $429 (adds IR illumination + IR dot projector),
  OAK-D Pro W $529, OAK-D Pro PoE $579.
  [source](https://docs.luxonis.com/hardware/platform/rvc/rvc2)
- **Luxonis OAK-4 (RVC4, Qualcomm QCS8550) reaches 48 TOPS INT8 but costs $949–$1,149**
  — RVC4: 6-core ARMv8 CPU, 8 GB RAM, 128 GB onboard storage, up to 48 TOPS INT8 and 12
  TOPS FP16 NPU plus 4 TOPS FP16 GPU (~52 TOPS aggregate marketing figure). Sensors:
  48 MP rolling-shutter IMX586 or 5 MP global-shutter OG05B10. Hardware-accelerated
  stereo depth, warping, optical flow, feature detection; 4K encode/decode. Shop prices:
  OAK 4 S $949, OAK 4 D $1,049, OAK 4 D Pro $1,149, OAK 4 CS $1,099 (prototype).
  [source](https://shop.luxonis.com/collections/oak-cameras-col)
- **Qualcomm Flight RB5 is end-of-life; ModalAI VOXL 2 is the surviving successor at 15
  TOPS / 16 g / 0.1–7 W** — ModalAI lists Qualcomm Flight RB5 among legacy development
  drone products that are End of Life and no longer for sale. VOXL 2: Qualcomm QRB5165,
  8 cores up to 3.091 GHz, 15 TOPS NPU, 16 g, 0.1–7 W, $1,299.99 board / $1,399.99 dev
  kit, embedded flight controller running PX4 or ArduPilot on the sensors DSP with
  integrated IMU and barometer, 6 concurrent MIPI camera inputs, up to 8K30 encode,
  NDAA '20 Sec. 848 compliant. [source](https://www.modalai.com/products/voxl-2)

### Simulation and test

- **Gazebo Jetty is the newest LTS (Sep 2025 → May 2031); Harmonic (→ May 2029) remains
  PX4's and ArduPilot's default** — Gazebo release table: Jetty Sep 2025 / EOL May 2031
  / LTS; Ionic Sep 2024 / EOL Dec 2026; Harmonic Sep 2023 / EOL May 2029 / LTS;
  Fortress EOL May 2027; Garden EOL Nov 2024. PX4 main supports Harmonic, Ionic and
  Jetty on Ubuntu 24.04 with Harmonic as default. ardupilot_gazebo supports Garden,
  Harmonic, Ionic and Jetty via `GZ_VERSION={harmonic|garden|ionic}`; Harmonic needs
  libgz-sim8-dev + rapidjson-dev + OpenCV/GStreamer dev packages.
  [source](https://gazebosim.org/docs/latest/releases/)
- **PX4 SITL ships an 'aruco' world and a moving_platform world — directly relevant to
  precision-landing development** — Targets use the gz_ prefix: `make px4_sitl gz_x500`,
  plus gz_x500_depth (front depth camera), gz_x500_vision (visual odometry),
  gz_x500_lidar_down (downward 1D lidar), gz_x500_lidar_2d, gz_x500_lidar_front,
  gz_x500_gimbal. Worlds: default, windy, aruco, baylands, lawn, rover, ridge, walls,
  moving_platform. Combine as e.g. gz_x500_windy.
  [source](https://docs.px4.io/main/en/sim_gazebo_gz/)
- **AirSim is dead and the Colosseum fork was archived 2026-07-11 — neither can be
  designed in** — Microsoft shut down AirSim in July 2022; Project AirSim was shut down
  at the end of 2023. CodexLabsLLC/Colosseum was archived by its owner on 2026-07-11
  and is now read-only. An xcloudplatform/Colosseum fork exists but is not an official
  successor. [source](https://github.com/CodexLabsLLC/Colosseum)
- **Isaac Sim 6.0.1 (2026-06-22) is current, but Pegasus Simulator has no Isaac Sim 6
  release — ArduPilot+Isaac requires pinning Isaac Sim 5.1.0** — Isaac Sim releases:
  v6.0.1 2026-06-22, v6.0.0 2026-06-04, v6.0.0-dev2 2026-03-16, v5.1.0 2025-10-21,
  v5.0.0 2025-08-08. Pegasus Simulator releases: v5.1.0 (2025-10-26, for Isaac 5.1.0,
  explicitly not compatible with older Isaac), v4.5.1 (2025-10-25, patch to allow
  ArduPilot SITL with Isaac Sim 4.5.0), v4.5.0 (2025-07-20, ArduPilot multiagent). Repo
  is actively committed (latest commits 2026-07-24) but no Isaac 6 tag exists.
  [source](https://github.com/PegasusSimulator/PegasusSimulator/releases)
- **Isaac Sim 6.0 minimum hardware is an RTX 4080 with 16 GB VRAM and 32 GB system RAM**
  — Minimum (x86_64): Ubuntu 22.04/24.04 or Windows 11, Intel Core i7 7th gen / AMD
  Ryzen 5, 32 GB RAM, GeForce RTX 4080, 16 GB VRAM, driver Linux 580.95.05 / Windows
  581.42. Recommended: Ryzen 7 / i7 9th gen, 64 GB RAM, RTX 5080. GPUs without RT Cores
  (A100, H100) are explicitly unsupported. Under 16 GB VRAM may be insufficient for
  scenes rendering more than 16 MP per frame.
  [source](https://docs.isaacsim.omniverse.nvidia.com/6.0.0/installation/requirements.html)
- **Webots has had no tagged stable release since R2025a (2025-02-04)** — GitHub
  releases for cyberbotics/webots show R2025a published 2025-02-04T12:36:33Z as the most
  recent non-nightly tag; everything since is nightly builds (nightly_4_9_2026 published
  2026-09-04). Treat Webots as maintained-but-unreleased for an 18-month-plus window.
  [source](https://github.com/cyberbotics/webots/releases)

## Recommendations

| Recommendation | Rationale | Alternatives rejected |
| --- | --- | --- |
| **Flight controller firmware:** ArduPilot Copter 4.7.1 on an STM32H743 board (Holybro Pixhawk 6C, ~$166, or CubePilot Cube Orange+). Pin the exact tag Copter-4.7.1 and freeze it; do not track master. | The dock is the hard part, and ArduPilot is the only firmware that puts the dock logic in the autopilot rather than in your Python. PLND_STRICT=1 + PLND_RET_MAX=4 + PLND_TIMEOUT=4 + PLND_RET_BEHAVE + PLND_ALT_MIN/MAX give you "climb, re-acquire, try again, up to 4 times, then hover or land" for free — PX4's precision landing only has a single search-at-altitude behaviour. On top of that: Lua scripting runs dock-specific abort/e-stop logic on the FC so it survives a companion-computer crash (PX4 has no onboard scripting at all); Rally points let RTL default to the dock instead of home; the fence action ladder (FENCE_ACTION=3 → SmartRTL/RTL/Land) plus inclusion/exclusion polygons maps one-to-one onto "stay inside the society, never over the pool or the clubhouse terrace"; and PLND_LAND_OFS_X/Y (±20 cm) lets you bias touchdown so the charging contacts, not the airframe centre, land on the electrodes. H7 is mandatory if you ever want AP_DDS — F4/F7 lack the CPU. | PX4 v1.17.0 — genuinely better ROS 2 integration (uXRCE-DDS by default, px4_ros2 lets you author flight modes in ROS 2 that are indistinguishable from internal modes) and BSD-3-Clause instead of GPLv3. Reject for v1 because its precision landing and RTL/rally feature set is thinner exactly where a dock needs depth, and because you will spend the ROS 2 advantage on rewriting the retry state machine you got free from ArduPilot. Revisit if legal insists on proprietary firmware modifications. Betaflight/INAV: no mission, no precision landing, not candidates. |
| **Companion computer:** NVIDIA Jetson Orin Nano Super 8GB on JetPack 7 (Ubuntu 24.04, kernel 6.8). ₹36,882 dev kit, ₹43,109 bare module. Budget 15–25 W and design the power system for the 25 W MAXN mode, not the 7 W figure. | You need two concurrent vision workloads — patrol detection (person/vehicle/intrusion) and the 20–30 Hz downward fiducial-landing loop — and only the Jetson class runs both without contention. YOLO26n at 640 px is 3.80 ms INT8 on this board, leaving real headroom after pre/post-processing. CUDA means the landing pipeline (undistort, threshold, tag decode, PnP) can be GPU-accelerated too, and TensorRT INT8 is a first-class export target for YOLO26. JetPack 7's Ubuntu 24.04 base is also what makes the ROS 2 Jazzy decision clean. | Raspberry Pi 5 + AI HAT+ 26 TOPS (₹10,670, Hailo-8) — a third of the price and tempting, but the quoted 431 FPS is a hardware benchmark; real end-to-end 640×640 pipelines measure ~29.5 FPS, and the Hailo NPU cannot help the landing loop's non-NN CV stages, which fall back to the Pi's CPU. Viable for a static/ground camera, not for the airborne dual-workload. Jetson Orin NX 16GB (157 TOPS) — ₹105,509 for the module alone and 10–25 W; over-specified and over-priced for one 640 px detector. Luxonis OAK-D Pro ($429, RVC2) — only 1.4 TOPS AI at ~4.5 W and ~30 FPS at 416 px; excellent as a *sensor* (its IR dot projector is genuinely useful for night stereo) but not as the compute. OAK-4/RVC4 ($949–$1,149) — 48 TOPS but 4–5× the Jetson's price for less flexibility. Qualcomm Flight RB5 — hard reject, it is EOL at ModalAI. ModalAI VOXL 2 ($1,300, 15 TOPS, 16 g, NDAA-compliant, integrated FC) — the most elegant single-board answer and worth revisiting for a productised v2, but at ~₹1.15 lakh landed plus import friction it is wrong for an India-first first build. |
| **Middleware:** ROS 2 Jazzy Jalisco on the drone + MAVROS 2.15.1 as the single MAVLink bridge, with MAVSDK-Python 3.17.2 confined to the dock/ground orchestrator. Do not put DroneKit or AP_DDS anywhere. | Jazzy is the only distro that is simultaneously LTS, Tier-1 on Ubuntu 24.04 (= JetPack 7), and carries a current mavros binary (2.15.1, released 2026-08-22 into jazzy alongside every other distro). One bridge process owning the MAVLink link avoids the classic failure where two clients fight over MAVLink stream rates and command ACKs. MAVSDK-Python is the right tool for the dock controller (open/close lid, verify pad clear, arm the mission, monitor telemetry) because it is a clean async Python API and it lives off-board where its extra latency does not matter. | ROS 2 Lyrical Luth (2026-05-22, LTS to 2031) — reject on the drone: Tier-1 Linux is Ubuntu 26.04 and there is no JetPack on 26.04, so you would be building ROS from source on an unsupported base. Use it on the ground station if you want. ROS 2 Humble — ArduPilot's AP_DDS docs still say "Humble is the only version supported", but Humble means Ubuntu 22.04, which means JetPack 6 and giving up JetPack 7; not worth it when MAVROS gives you the same data on Jazzy. ROS 2 Kilted — non-LTS, Ionic-era, EOL too soon. AP_DDS/uXRCE-DDS on ArduPilot — Humble-only, H7-only, and topic/rate selection is a compile-time decision; too rigid and too new for a first build. DroneKit-Python — unmaintained for years, PX4 itself points people away from it; hard reject. PX4 uXRCE-DDS + px4_ros2 — the technically superior middleware, but it comes bundled with the PX4 firmware decision you already rejected. |
| **Precision landing:** nested AprilTag (36h11) markers on the pad, decoded on the Jetson, published as MAVLink LANDING_TARGET with PLND_TYPE=1. Add a downward rangefinder. Add an IR-LOCK sensor ($349, 21.5 g) as a redundant night channel only after the vision path works. | Design target is 10–15 cm 2σ, not 3 cm. PX4 documents ~10 cm with IR-LOCK; published AprilTag work shows sub-10 cm in the final descent stage. Nesting matters: a single large tag leaves the camera's FOV in the last metre, so use e.g. a ~40 cm outer tag for the 10 m→1.5 m phase and an ~8 cm inner tag for 1.5 m→touchdown, switching on rangefinder altitude. The rangefinder is not optional — PLND_ALT_MIN=0.75 / PLND_ALT_MAX=8 retry logic requires it. The single highest-value tuning parameter is PLND_LAG: its default of 0.02 s assumes an I2C sensor, and a Jetson capture→detect→PnP→MAVLink pipeline is realistically 80–150 ms. Measure it with a timestamped LED flash and set PLND_LAG accordingly; leaving it at default is the most common cause of oscillating, never-converging precision landings. Set PLND_EST_TYPE=1 (Kalman) and tune PLND_ACC_P_NSE (default 2.5, range 0.5–5) upward to trust the camera more once latency is correct. | IR-LOCK as the primary — $349 and 21.5 g for a modified Pixy with a 15 m beacon range; it is robust in all lighting but gives you a single blob, no orientation, and no yaw alignment for contact-plate registration. Good redundancy, poor primary. UAVLAS ULS-XCopter-G2 and the commercial "Landmark" system — supported by ArduPilot but closed, priced on request, and unverifiable for India import. BlueOS Precision Landing Extension — attractive if you were already on a BlueOS-based companion, but it adds a whole runtime you do not otherwise need. Pure GPS/RTK landing — RTK gives you 2–3 cm horizontally but says nothing about where the *pad* is; the pad moves (thermal expansion, mount settling, someone bumps it), so vision-relative is the correct reference frame. Use RTK to get within a metre, then hand off to vision. |
| **Dock and charging:** conductive contact pad with passive mechanical self-centering (V-funnel skid guides or DJI-style powered centering arms), gold-plated electrode plates rated ≥10 A, sized to your pack (6S ≈ 25.2 V; 8 A ≈ 200 W). Build the pad so it tolerates ±10 cm of landing error. | This is the single decision that de-risks the whole project: every metre of precision-landing accuracy you fail to achieve can be bought back with a sloped funnel. Every real dock does exactly this — DJI Dock 3 charges 15%→95% in 27 minutes at up to 800 W with mechanical centering; Heisha's DPAD line uses gold-plated dual electrodes passing up to 10 A at 17.5 V or 52.8 V, with their C200 pad at 80×80 cm / 6 A / 17.5 V DC as a concrete DIY-scale reference. Put the electrodes as concentric rings or long parallel bars rather than points so yaw error is irrelevant, use spring-loaded contacts on the skids, and add a current-sense confirmation step ("charging detected within 5 s of touchdown, else disarm-and-retry") as a Lua script on the FC. | Inductive/wireless charging — reject for v1. The published academic docking design achieves 56.6% power transfer efficiency at 96.5 W, meaning ~40 W dumped as heat in a sealed enclosure in Indian summer, plus receiver-coil mass on an endurance-critical airframe. WiBotic's commercial 150/250/300 W and 1 kW products are real but are a supplier relationship and a cost centre, not a shortcut. The one honest argument for induction — no exposed contacts to corrode in monsoon humidity — is better solved with gold plating plus a closing lid. Battery swap robots — Heisha ships auto-swap docks for the DJI M400 and they work, but a swap mechanism is a second robot with its own failure modes, and 27-minute contact charging already supports a several-patrols-per-day duty cycle. Revisit only if you need >80% dock availability. |
| **Simulation:** Gazebo Harmonic + ArduPilot SITL + ardupilot_gazebo (GZ_VERSION=harmonic, libgz-sim8-dev) on Ubuntu 24.04 as the everyday loop. For the photorealistic society demo, use Isaac Sim 5.1.0 + Pegasus Simulator v5.1.0 — not Isaac Sim 6.0.1. | Harmonic is LTS to May 2029, is the default for both PX4 and ArduPilot, runs headless in CI, and is what you will actually iterate the precision-landing controller in a thousand times. Borrow PX4's world list for ideas — it ships an `aruco` world and a `moving_platform` world that are precisely the docking test cases. For the demo video, Isaac gives real photorealism (PBR, ray-traced sun angles, correct shadows on a society compound) and Pegasus provides the PX4/ArduPilot SITL bridge — but Pegasus's newest tag is v5.1.0 for Isaac Sim 5.1.0 (2025-10-26) and its README states it is not compatible with other Isaac versions. Isaac Sim 6.0.1 shipped 2026-06-22 with no matching Pegasus release, so pinning 6.0.1 will strand you. Check hardware first: Isaac Sim 6.0 needs an RTX 4080 / 16 GB VRAM / 32 GB RAM minimum and will not run on A100/H100. | Microsoft AirSim — shut down July 2022, Project AirSim shut down end of 2023; hard reject. Colosseum — the community fork, archived read-only on 2026-07-11; hard reject despite still ranking well in search. Webots — no tagged stable release since R2025a (Feb 2025), nightlies only; not a base to build a demo on. Flightmare — no 2025/2026 activity found; treat as abandoned. Gazebo Jetty (LTS to May 2031) — the future default and worth migrating to, but ardupilot_gazebo's documented apt path is still Harmonic's libgz-sim8-dev; take Jetty on the next refresh, not on day one. Gazebo Ionic — EOL Dec 2026, pointless to start on. |
| **Safety case:** layer the failsafes in firmware, not in Python, and do not buy a parachute before checking its minimum deployment altitude against your patrol altitude. Concrete config: FENCE_ENABLE=1, FENCE_TYPE=15 (max alt + circle + polygon + min alt), FENCE_ACTION=3, inclusion polygon on the society boundary, exclusion polygons over pools/clubhouse/playground; Rally point on the dock with RALLY_INCL_HOME=1; RTL_ALT_M set above the tallest tower; BATT_FS_LOW_ACT=RTL and BATT_FS_CRT_ACT=Land; GCS and radio failsafes both to SmartRTL; EKF/vibration/dead-reckoning failsafes enabled. | ArduPilot documents ten failsafe subsystems (radio, battery, GCS, EKF, dead reckoning, vibration, terrain data loss, crash check, parachute, hardware watchdog) and they run in the autopilot at 400 Hz with no dependence on the Jetson, the Wi-Fi, or your code. Two behaviours you must design around: (1) once a radio/battery/GCS/terrain failsafe changes mode, the vehicle stays in that mode until a pilot changes it — your autonomy stack cannot silently resume; (2) SmartRTL is RAM-bounded (SRTL_POINTS, ~3 KB per 100 points, ~500 typical) and when the buffer fills the mode disables itself, so a long patrol can silently lose its best failsafe — either cap patrol length or fall back to RTL. The min-altitude fence (FENCE_TYPE bit 3) is the underused one here: it stops a confused vehicle descending into a courtyard. On parachutes, the honest engineering answer is that a patrol at 20–30 m AGL over occupied ground may be below the minimum safe deployment altitude of most systems, in which case prop guards, a rooftop-height corridor that avoids overflight of people, and a hard geofence are the real mitigations — verify the specific canister's minimum altitude with the vendor before spending on it. | Implementing geofence/RTL logic in ROS 2 on the companion — reject outright: it fails exactly when the companion fails. Companion-side logic should only ever *request* modes, never be the last line of defence. Relying on RTL alone without Rally points — sends the drone to arming home, which after a dock relocation or a GPS glitch may not be the dock. Buying a ParaZero SafeAir kit up front — India channel now exists via BonV Aero (agreement March 2026) and US prices run $1,757–$3,999 for DJI-specific kits, but there is no verifiable India price or custom-multirotor SKU; get a quote and a minimum-deployment-altitude figure in writing first. |

## Open questions

- Verified mass budget: NVIDIA does not publish a weight for the Orin Nano module, and
  Luxonis does not publish OAK-D Pro weight on its shop page. Weigh the actual Jetson
  module + carrier + heatsink/fan + cameras + wiring before committing to an airframe
  and endurance target.
- Actual sustained power draw of the Jetson at your workload. The 7–25 W envelope is a
  mode range, not a measurement; instrument it with both YOLO26 and the landing loop
  running before sizing the battery and the charging pad current.
- End-to-end latency of the vision→LANDING_TARGET pipeline, which sets PLND_LAG. This
  must be measured (timestamped LED flash into the camera, log the MAVLink arrival) —
  it cannot be estimated, and getting it wrong is the dominant cause of
  precision-landing oscillation.
- Whether ArduPilot's Copter 4.7 documentation now publishes any cm accuracy figure for
  IR-LOCK — the wiki still gives none, only a 15 m MarkOne detection range. Get a real
  number from bench tests, not from vendor marketing.
- Landed India cost of imported parts (IR-LOCK $349, Luxonis, Holybro, ParaZero) after
  customs duty, IGST and freight. The USD sticker prices in this report are ex-vendor;
  Indian landed cost is typically materially higher.
- DGCA's actual position on an unmanned, dock-launched autonomous patrol inside a
  private gated community — is it VLOS (remote pilot on site) or BVLOS? This determines
  whether the project is buildable at all and must be answered by DGCA/Digital Sky, not
  by industry blogs.
- Whether DJI enterprise hardware (Dock 3 / Matrice 4D) can be procured and legally
  operated in India for security applications, given procurement restrictions on
  Chinese-origin drones. Assumed not — verify before using DJI as anything more than a
  design reference.
- Minimum safe deployment altitude of any candidate parachute system versus your
  intended 20–30 m patrol altitude. If the parachute needs more altitude than you fly,
  it is dead weight.
- Timeline for a Pegasus Simulator release supporting Isaac Sim 6.0.x — the repo is
  actively committed (July 2026) but no tag exists. Affects whether you pin Isaac 5.1.0
  long-term.
- Night operation: whether IR illumination over residential balconies raises
  privacy/nuisance objections from the RWA, and whether a thermal payload (adding cost
  and mass) is required for useful after-dark detection.
- Whether YOLO26's NMS-free architecture holds its accuracy after INT8 quantisation on
  the Orin Nano Super for small, distant human targets at patrol altitude — benchmark on
  your own annotated society footage, not COCO.

## Unverified or risky

These are claims the researcher could not confirm. Do not rely on any of them without
checking the primary source yourself first.

- An IR-LOCK 'Mark Two' sensor could not be found. The current product is the 'IR-LOCK
  Sensor' at $349 paired with the MarkOne Beacon (V1.1 / V2.0 / V3.0). Do not cite a
  Mark II part number — it may not exist.
- Heisha 'DPAD-C500' as a distinct SKU could not be confirmed. The documented DPAD
  models are DPad 60, DPad 80 and DPad 135; the charging-pad line includes a C200
  (80×80 cm, 6 A, 17.5 V DC) and a C300. Confirm the actual SKU with Heisha before
  quoting.
- OAK-4 pricing is inconsistent across sources: a Dec 2025 press write-up quoted OAK 4 S
  from $749 / OAK 4 D $849 / OAK 4 D Pro $949, while the Luxonis shop currently shows
  $949 / $1,049 / $1,149. Treat the shop page as authoritative and re-check.
- Jetson Orin NX 16GB India pricing spans ₹48,999 (an IndiaMART listing) to ₹105,509
  (Tanna TechBiz). The IndiaMART figure is not credible against the module's global MSRP
  and should not be used for budgeting.
- Jetson Orin NX 'Super' 157 TOPS versus base 100 TOPS: the Super figure is a
  JetPack-enabled power-mode uplift, not different silicon. Confirm which figure applies
  at your chosen power budget.
- Hailo-8 YOLOv8 benchmark figures range from 29.5 FPS to 491 FPS across sources
  depending on whether pre/post-processing and PCIe generation are included. Only the
  ~30 FPS end-to-end figure is meaningful for a real pipeline. Similarly, the
  Ultralytics Jetson figures explicitly exclude pre/post-processing.
- The 2018 arXiv AprilTag landing accuracy numbers (2σ 0.09 m / 0.08 m; <0.1 m in final
  descent) are eight years old and could not be re-verified against a 2025/2026
  replication. The MDPI 2026 fiducial-marker landing paper (Electronics 15(8):1582)
  exists but MDPI returned HTTP 403 — its GPS-vs-optical touchdown precision numbers are
  unread.
- Isaac Sim 5.1.0 is reported in one NVIDIA forum thread as 'no longer supported' while
  it remains the only version Pegasus Simulator targets. This is a live tension —
  confirm support status before building a demo on it.
- ROS 2 Jazzy's exact EOL (commonly stated as May 2029) could not be re-verified
  directly: docs.ros.org is behind an Anubis challenge that blocks automated fetching.
  Its LTS status and Ubuntu 24.04 Tier-1 platform are corroborated indirectly via mavros
  release channels and the Kilted/Lyrical announcements.
- All India drone-regulation findings (BVLOS corridors, type certification mandate,
  draft Civil Drone Bill 2025) come from Indian industry blogs, not from DGCA gazette
  notifications or the Drone Rules text. No clause numbers are quoted because none could
  be verified. Do not rely on these for compliance decisions.
- ParaZero's India relationship with BonV Aero was reported in a counter-drone context
  (drone interception units), which is not the same as parachute recovery distribution.
  Whether SafeAir parachute kits are actually purchasable in India through this channel
  is unconfirmed.
- No India-based drone-dock manufacturer with a verified contact-charging product could
  be confirmed. TechEagle references in-house 'droneports' and Garuda Aerospace markets
  autonomous patrol services, but neither publishes dock specifications or pricing.
- DJI Dock 3 India availability and pricing could not be established. Given Indian
  procurement sensitivities around Chinese-origin drones, treat DJI Dock 3 purely as a
  design benchmark, not a procurement option.
- No maintained open-source reference implementation of an autonomous charging dock (pad
  + precision landing + charge state machine) was located. Assume this integration is
  original work and budget accordingly.
