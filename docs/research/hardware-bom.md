# Hardware Bill of Materials

> Research note for [AEGIS](../../README.md). Compiled 2026-09-07 from a multi-agent
> web research sweep. Every claim below is sourced; confidence levels are the
> researcher's own and are preserved verbatim.

## Summary

Two Indian legal facts dominate every hardware choice and must be settled before a
single part is bought. First, DGFT Notification No. 54/2015-20 dated 09.02.2022 makes
import of drones in CBU, SKD or CKD form **Prohibited** (exceptions only for
government entities, government-recognised educational/R&D bodies, domestic
manufacturers and defence, each needing a DGFT authorisation), while "Import of drone
components shall be 'Free'" — so DJI Dock 3, Skydio, Sunflower, Hextronics and Heisha
are simply not buyable, but every frame, FC, motor, ESC and companion computer in this
BOM is. Second, dgca.gov.in carries a live banner today (7 Sep 2026): "Registration of
Non-Type Certified (non-TC) UAS has been temporarily suspended until further notice" —
a self-built S500/Pixhawk airframe cannot presently obtain a UIN, so Tier B is legally
an R&D/indoor/nano article and Tier C's aircraft must come from a DGCA type-certified
Indian OEM. On radio, the one notification I read in full is G.S.R. 853(E) of 10 Dec
2021 (MoC, WPC Wing; F. No. R-11018/06/2020-PP), the 865–868 MHz Short Range Devices
exemption rules: Table-I, which explicitly covers "Telemetry, Telecommand, Alarms and
Data in general", allows only **25 mW e.r.p. at 1% duty cycle**, and Table-II
(tracking/sensors) only 500 mW e.r.p. with Adaptive Power Control and ≤2.5% duty cycle
— which means an 868 MHz LoRa link can carry heartbeats and alarms but can never
legally carry continuous MAVLink telemetry, let alone video. Rule 5 of the same
notification makes WPC Equipment Type Approval mandatory for such equipment, and the
ETA portal (saralsanchar.gov.in/wpc_eta_report.php) has an explicit "Drones" equipment
category gated on the two questions "working in License exempted/Delicensed bands?"
and "free from EXIM Policy of DGFT?". I could not reach any WPC notification
de-licensing 433 MHz, and India sits in ITU Region 3 where 433.05–434.79 MHz is not an
ISM band — yet 433 MHz SiK radios are sold openly here (Simplifly 100 mW ₹4,015;
Holybro V3 ₹8,661; a 500 mW 3DR clone ₹6,683), so treat them as legally unverified and
design the C2 link on 2.4 GHz (FlySky AFHDS2A / ExpressLRS) instead; 915 MHz SiK radios
are unambiguously wrong for India because 890–915 / 925–960 MHz is licensed GSM/E-GSM
cellular. On the BOM itself, robu.in and flyrobo.in are Cloudflare-blocked to automated
retrieval but robocraze.com, quartzcomponents.com, thinkrobotics.com and makerbazar.in
all quote current INR stock and prices: a complete Tier A demo (four ESP32-CAM +
LD2410 mmWave perimeter nodes, an ESP32-S3 gate node, an actuator-driven scale dock,
and an Indian-made LiteWing ESP32-S3 flyer) lands at ₹25,000–36,000; a genuine Tier B
PX4 prototype (Holybro S500 V2 kit ₹26,026 + Pixhawk 6C/PM02/M9N ₹33,263 + Pi 5 +
Hailo AI HAT+ ₹23,193 + radios, batteries, charger, gimbal) lands at ~₹1.15 lakh;
Tier C is ~₹2.6–3.5 lakh of dock and site infrastructure *before* an aircraft you must
source from an Indian OEM at ₹3.5–8 lakh. The costliest engineering mistakes are
thermal, not electronic: LiPo charging is out of spec above 45 °C and a sealed rooftop
enclosure in an Indian summer runs 60–70 °C internally, so the dock's battery bay needs
active refrigeration (₹18,000–30,000), not fans; and the aircraft, not the dock's IP
rating, sets the weather envelope — an open-frame S500 with exposed ESCs has no ingress
rating at all and a practical wind ceiling near 8–10 m/s, well below routine Indian
pre-monsoon squalls.

## Hard constraints

- **CANNOT import a complete drone or drone kit.** DGFT Notification No. 54/2015-20
  dated 09.02.2022, ITC(HS) 2022 Chapter-88 Policy Condition 03: import of drones in
  CBU, SKD or CKD form is Prohibited; exceptions require a DGFT import authorisation
  and are limited to government entities, government-recognised educational
  institutions, government-recognised R&D entities, drone manufacturers for R&D, and
  defence/security. Import of drone COMPONENTS is 'Free'.
- **CANNOT register a self-built drone today.** Live banner on dgca.gov.in (retrieved
  2026-09-07): 'Registration of Non-Type Certified (non-TC) UAS has been temporarily
  suspended until further notice.' No UIN means no legal commercial operation for
  anything above 250 g.
- **MUST keep any Tier A flyer at or below 250 g** (Nano class per Drone Rules 2021,
  gazette CG-DL-E-26082021-229221, 25 Aug 2021) to avoid type certification and UIN.
- **865-868 MHz telemetry is capped at 25 mW e.r.p. with a 1% duty cycle** for
  non-specific SRD (Table-I, G.S.R. 853(E), 10.12.2021) — that is 36 seconds of
  transmit per hour. Tracking/data-acquisition class (Table-II) allows 500 mW e.r.p.
  but requires Adaptive Power Control and caps duty cycle at 2.5% (10% for network
  access points), bandwidth <=200 kHz. Continuous MAVLink or any video over 868 MHz is
  not lawful.
- **MUST obtain WPC Equipment Type Approval for exempt-band radio equipment** — Rule
  5(1) of G.S.R. 853(E): 'such equipment shall be type approved'. The Saral Sanchar ETA
  self-declaration portal has an explicit 'Drones' equipment category and requires the
  equipment to be both in a de-licensed band and free from DGFT EXIM restrictions.
- **The 865-868 MHz exemption is granted on a non-interference, non-protection, shared
  and non-exclusive basis** (Rule 3). Under Rule 4 a licensed user who reports
  interference can have the Authority order you to relocate, reduce power, change
  antennas, or discontinue operation entirely.
- **MUST NOT use 915 MHz radios in India:** 890-915 MHz (GSM/E-GSM uplink) and 925-960
  MHz (downlink) are licensed cellular spectrum. A 915 MHz SiK radio transmits directly
  into a mobile operator's uplink.
- **LiPo charging is out of specification above 45 C ambient.** A sealed rooftop
  enclosure in Indian summer reaches 60-70 C internally; passive fans cannot cool below
  ambient. Active refrigeration of the battery bay plus a thermistor charge-inhibit is
  mandatory, not optional.
- **The airframe, not the dock, sets the weather envelope.** A Holybro S500 V2 or F450
  has NO ingress protection rating (open carbon plate, exposed ESCs) and a practical
  sustained-wind ceiling around 8-10 m/s. No dock IP rating changes this.
- **A Jetson Orin Nano Super Developer Kit cannot be flown on a Tier B airframe:** over
  1 kg with shell and PSU, and ~25 W. Airborne inference must be Raspberry Pi 5 +
  Hailo class (~180 g, ~12 W) or an integrated OAK-D.

## Findings

### Indian regulatory gates: import, registration, spectrum

- **Importing a complete drone or drone kit into India is prohibited; importing drone
  components is free** — Annexure-I to DGFT Notification No. 54/2015-20 dated
  09.02.2022 (ITC (HS) 2022), Chapter-88 Schedule-I Policy Condition No. 03, revised
  text: '1. Import of drones in Completely-Built-Up (CBU), Semi-knocked-down (SKD) or
  Completely-Knocked-down (CKD) form is Prohibited, with following exceptions: i.
  Import of drones by Government entities, educational institutions recognized by
  central or state government, government recognized R&D entities and drone
  manufacturers for R&D purpose shall be allowed in CBU, SKD or CKD form subject to
  import authorisation issued by DGFT in consultation with concerned line ministries.
  ii. Import of drones for defence & security purposes shall be allowed in CBU, SKD or
  CKD form subject to import authorisation issued by DGFT in consultation with
  concerned line ministries. 2. Import of drone components shall be "Free".' BOM
  CONSEQUENCE: every line item in Tiers A and B below is a component and is
  importable/stockable; a DJI Dock 3 + Matrice, a Skydio X10 + Dock, a Sunflower
  Beehive or a Hextronics/Heisha dock with aircraft is not. It also means Indian
  distributors stock components deeply (robocraze, quartzcomponents, thinkrobotics all
  show live stock) but almost nobody stocks a finished imported airframe.
  Source: DGFT Notification 54/2015-20, 09.02.2022, Annexure-I (primary document, fetched as PDF).

- **A self-built (non-type-certified) drone cannot currently be registered in India —
  DGCA has suspended non-TC UAS registration** — Live banner on the DGCA portal
  homepage, retrieved 2026-09-07: 'Registration of Non-Type Certified (non-TC) UAS has
  been temporarily suspended until further notice. For more information click here.'
  (links to jsp/dgca/topHeader/drone/Registration of Non-Type Certified UAS.pdf).
  Combined with Drone Rules 2021 classification (gazette CG-DL-E-26082021-229221 dated
  25 Aug 2021): Nano ≤250 g; Micro >250 g to ≤2 kg; Small >2 kg to ≤25 kg; Medium >25
  to ≤150 kg; Large >150 kg. A Holybro S500-class build is ~1.6–2.2 kg AUW, i.e.
  Micro/Small, needing a UIN that cannot presently be issued. Only the Nano class
  (≤250 g) escapes type certification for non-commercial use. PROJECT CONSEQUENCE:
  Tier A's flyer must be ≤250 g (LiteWing ~90 g, Pluto X ~65 g) and indoor/private;
  Tier B is an R&D bench article, not a deployable patrol drone; Tier C's aircraft must
  be bought from a type-certified Indian OEM, not built.
  [source](https://www.dgca.gov.in/digigov-portal/)

- **India's 865–868 MHz Short Range Device exemption caps telemetry at 25 mW e.r.p. and
  1% duty cycle, and mandates WPC type approval** — G.S.R. 853(E), New Delhi 10
  December 2021, Ministry of Communications (Wireless Planning and Coordination Wing),
  issued under ss. 4 & 7 Indian Telegraph Act 1885 and ss. 4 & 10 Indian Wireless
  Telegraphy Act 1933; [F. No. R-11018/06/2020-PP], signed ASHIM DUTTA, Dy. Wireless
  Adviser. Short title: 'Use of Low Power Equipment in the Frequency Band 865-868 MHz
  for Short Range Devices (Exemption from Licence) Rules, 2021'. Supersedes the 2005
  865-867 MHz RFID rules. Rule 3 exempts licensing on a non-interference,
  non-protection, shared and non-exclusive basis for equipment meeting Tables I–IV.
  TABLE-I Non-Specific SRD (note: 'primarily include devices for Telemetry,
  Telecommand, Alarms and Data in general'): 865–868 MHz, 25 mW e.r.p., duty cycle
  limit 1%, FHSS with max occupied bandwidth ≤50 kHz for 58 or more hop channels, EN
  300 220; the duty cycle applies to the entire transmission, not per hop channel.
  TABLE-II Tracking/Tracing/Data Acquisition (includes sensors, actuators, wireless
  industrial applications): 865–868 MHz, 500 mW e.r.p., Adaptive Power Control
  REQUIRED, duty cycle ≤10% for network access points and ≤2.5% otherwise, ≤200 kHz.
  TABLE-III Wideband Data Transmission: 25 mW e.r.p., >600 kHz to ≤1 MHz, duty ≤10%
  network access points / ≤2.8% otherwise, EN 300 220. TABLE-IV RFID: 2 W e.r.p.
  permitted only on four 200 kHz channels centred at 865.7, 866.3, 866.9 and 867.5 MHz;
  interrogator continuous transmission ≤4 s with ≥100 ms gap; tags respond at −20 dBm
  e.r.p.; EN 302 208. Rule 4: a licensed user suffering interference can have the
  Authority order you to relocate, reduce power, change antenna, or discontinue. Rule
  5(1): 'such equipment shall be type approved', application in the Annexure format.
  ENGINEERING CONSEQUENCE: 1% duty cycle = 36 seconds of transmit per hour. Continuous
  1 Hz MAVLink telemetry over 868 MHz LoRa is not lawful under Table-I; even Table-II's
  2.5% is 90 s/hour. Use 868 MHz for heartbeat/alarm only.
  Source: Gazette of India Extraordinary Part II Sec 3(i), G.S.R. 853(E) dated 10.12.2021 (primary document, fetched as PDF).

- **WPC Equipment Type Approval is a per-model self-declaration on the Saral Sanchar
  portal and has an explicit 'Drones' equipment category** —
  saralsanchar.gov.in/wpc_eta_report.php ('ETA (Self-Declaration)') offers: List of
  Issued ETA (Self-Declaration), Search Import Undertaking By Id, Apply For New ETA
  (Self-Declaration). Equipment Category dropdown includes Mobile Handsets, Smart
  Phones, Laptops, Smart Watches, Accessories, Microphones, Speakers, Headphones,
  Earphones, Printers, Scanners, Cameras, Other, **Radar**, **Drones**, Receivers. Two
  gating questions are shown on the page: 'Whether the equipment is working in License
  exempted/Delicensed bands?' and 'Whether the equipment is free from EXIM Policy of
  DGFT?'. Note the portal's own regulations pointer
  (http://wpc.dot.gov.in/content/10_1_Regulations.aspx) is dead as of 2026-09-07 —
  wpc.dot.gov.in does not resolve; WPC content has migrated under dot.gov.in, which now
  serves a client-rendered Next.js SPA with no fetchable HTML for the de-licensed-bands
  page. Separately, the same Saral Sanchar site now advertises 'Telecommunication
  Authorisation Rules 2026' and a new 'Radio Equipment Possession Authorisation'
  covering 'authorisation, possession, testing, demonstration, renewal, surrender,
  disposal, and compliance of Radio Equipment' — the WPC regime is being restructured
  under the Telecommunications Act 2023, so confirm the current instrument before
  filing. [source](https://saralsanchar.gov.in/wpc_eta_report.php)

### Tier BOMs

- **TIER A BOM — simulation + minimal hardware, ₹25,206 lean / ₹36,228 with edge node
  (target ₹15,000–40,000)** — All prices retrieved live 2026-09-07, INR, Indian stock.

  A1 PERIMETER SENSOR NODES ×4 — ESP32 Camera Development Board (OV2640/OV3660) ₹675 ×4
  = ₹2,700 [quartzcomponents.com/products/esp32-camera-development-board-wifi-bluetooth-with-ov2640-camera-module;
  robocraze ₹689 for the 3MP OV3660 variant]; HLK-LD2410 24 GHz human-presence radar
  ₹376 ×4 = ₹1,504 [quartzcomponents.com/products/hi-link-hlk-ld2410-24ghz-...]; IP65
  plastic enclosure 90×90×60 mm ₹458 ×4 = ₹1,832; 12 V 2 A SMPS ₹249 ×4 = ₹996; XY-3606
  24/12→5 V 5 A buck ₹137 ×4 = ₹548; PG7 IP68 cable glands ₹6 ×12 = ₹72. Subtotal
  ₹7,652. (Cheaper LD2420 micro-motion radar ₹222 if budget-bound; LD2410B 6 m test kit
  ₹814 for bench work.)

  A2 GATE NODE — ESP32-S3-WROOM-N16R8 dual-USB devkit ₹684 [quartzcomponents]; ESP32
  Camera board ₹675 (vehicle presence only — NOT plate OCR); RC522 13.56 MHz RFID
  reader ₹78 + RFID tags ₹14 ×10 = ₹140; 2-ch optocoupled relay ₹62 (boom-barrier dry
  contact); HC-SR04 ₹72; 12 V square siren SQR117 ₹194; IP65 enclosure ₹458; 12 V 2 A
  SMPS ₹249. Subtotal ₹2,612.

  A3 SCALE-MODEL DOCK (1:3) — Linear Actuator 12 V 100 mm 7 mm/s ₹2,748 ×2 = ₹5,496
  [quartzcomponents.com/products/linear-actuator-stroke-length-12v-100mm-7mm-s];
  BTS7960B 43 A H-bridge ₹318 ×2 = ₹636; MG996R metal-gear servo ₹254 ×2 = ₹508
  (centering arms); V-15-1C25 micro limit switches ₹36 ×4 = ₹144; ESP32S 38-pin devkit
  ₹358; 12 V 10 A 120 W SMPS ₹639; 4-ch 12 V relay module ₹142; DHT22 ₹108 + rain-drop
  sensor ₹39 (weather interlock); charging contacts (brass/pogo, improvised) ~₹500;
  acrylic/ply/3D-printed shell ~₹2,500. Subtotal ₹11,070.

  A4 FLYER (≤250 g, legal without UIN) — LiteWing ESP32-S3 programmable drone with
  battery ₹3,290
  [quartzcomponents.com/products/litewing-esp32-based-programmable-drone-with-battery-ready-to-fly];
  kit-without-battery ₹3,090; robocraze lists v1.2 ₹3,586. Optional LiteWing
  Positioning Module (PMW3901 optical flow + VL53L1X ToF) ₹2,095 — this is what makes
  an indoor autonomous-hold demo actually work. Indian-designed (CircuitDigest).
  Alternative: Drona Aviation Pluto X ₹15,999 [makerbazar.in] / ₹21,799 [robocraze];
  Pluto DIY Nano 1.2 ₹8,199.

  A5 OPTIONAL EDGE NODE — Raspberry Pi 5 ₹7,799.99 [thinkrobotics.com] + official 27 W
  USB-C PSU ₹1,204 [robocraze] + Active Cooler ₹529 + SanDisk 32 GB A1 ₹1,489 =
  ₹11,022.

  TOTALS: lean (A1+A2+A3+A4) = ₹24,624; +positioning module = ₹26,719; +Pi 5 edge node
  = ₹35,646. Comfortably inside the ₹15k–40k envelope.
  [source](https://quartzcomponents.com/products/litewing-esp32-based-programmable-drone-with-battery-ready-to-fly)

- **TIER B BOM — working PX4 prototype drone, ₹1,14,590 as specced (target
  ₹60,000–1,50,000)** — All prices live 2026-09-07 from robocraze.com unless noted; all
  in stock.

  AIRFRAME+POWERTRAIN — Holybro S500 V2 DIY Drone Kit, includes frame, motors, props
  and ESCs, SKU TIFKT0350, ₹26,026
  [robocraze.com/products/holybro-s500-v2-diy-drone-kit-included-motor-prop-and-esc].
  This is the single best value line in the whole BOM: it removes thrust-matching
  guesswork and is the reference PX4 airframe.

  AUTOPILOT — Holybro Pixhawk 6C + PM02 power module + M9N GPS bundle ₹33,263
  [robocraze.com/products/holybro-pixhawk-6c-flight-controller-with-pm02-power-module-and-m9n-gps].
  Without GPS: ₹30,046. Separates: PM02 ₹2,269; Holybro M9N standard-connector GPS
  ₹8,609; Micro M9N with case ₹7,111; Holybro M10 GPS ₹5,846. Anti-vibration damper
  ₹170.

  RTK (optional, for 0.5–1.5 m landing accuracy) — SmartElex GPS-RTK ZED-F9P-04B UFL
  ₹17,067; 7Semi u-blox ZED-F9P dual-band RTK SMA modem ₹20,475. Note you need TWO
  (base + rover) or an NTRIP/CORS subscription.

  C2 RADIO — FlySky FS-i6X 2.4 GHz 6CH AFHDS-2A TX + FS-iA10B RX ₹6,357 (2.4 GHz, the
  defensible band). ExpressLRS alternative: RadioMaster Boxer 2.4 GHz ELRS ₹18,196 +
  RP1 V2 nano RX ₹2,556; HGLRC ELRS 2.4G RX ₹1,586.

  TELEMETRY — Simplifly SiK Telemetry Radio 100 mW 433 MHz ₹4,015; Holybro SiK V3 100
  mW 433 MHz ₹8,661; 3DR 433 MHz 500 mW ₹6,683. ⚠ SEE THE 433 MHz LEGALITY CAVEAT —
  budget for it but plan to replace with a Wi-Fi/4G MAVLink bridge on the companion
  computer.

  ENERGY — Bonka 14.8 V 4S 4200 mAh 35C LiPo ₹4,529 ×2 = ₹9,058; iMax B6AC 80 W balance
  charger ₹2,280 (B6 non-AC ₹1,899); LiPo-safe bag + sand bucket ~₹800.

  COMPANION COMPUTER (airborne) — Raspberry Pi 5 ₹7,799.99 [thinkrobotics] + Raspberry
  Pi AI HAT+ (Hailo-8L) ₹7,249.99 [thinkrobotics, showing sold out] or Raspberry Pi AI
  Kit (M.2 HAT + Hailo) ₹6,999 [makerbazar, sold out] + official M.2 HAT+ ₹1,203
  [robocraze] + IMX708 12 MP camera ₹4,249 [thinkrobotics] + 27 W PSU ₹1,204 + 64 GB
  card ₹1,489 ≈ ₹23,193. Total airborne mass ~180 g.

  PAYLOAD — 3-axis FPV brushless gimbal with control board ₹7,499; T-MOTOR GB4106
  gimbal motor ₹4,683 if building your own.

  CONSUMABLES — prop guards F450/F550 4-pc set ₹329; spare 1045 CF props ₹77/pair ×4 =
  ₹308 (Holybro 1045 2-pair ₹2,135); XT60/silicone wire/heatshrink/buzzer/safety switch
  ~₹1,500.

  SUBTOTAL AS SPECCED: 26,026+33,263+4,015+6,357+9,058+2,280+800+329+308+23,193+7,499+1,500+170
  = ₹1,14,598.

  BUDGET VARIANT (~₹48,000): F450 frame with integrated PCB ₹824; A2212 1000KV motors
  ₹395 ×4 = ₹1,580; SimonK 30A ESC ₹371 ×4 = ₹1,484; 1045 props ₹49 ×4 = ₹196; Matek
  PDB-XT60 ₹381; FS-i6X ₹6,357; Bonka 3S 5200 mAh ₹4,522 ×2; iMax B6 ₹1,899; Pi 5 +
  camera ₹9,300; SpeedyBee F7 V3 FC ₹7,028 (see 'do not buy' on Pixhawk 2.4.8 clones);
  misc ₹3,000.

  GROUND STATION (separate line, do NOT fly it) — NVIDIA Jetson Orin Nano Super
  Developer Kit ₹49,999.99 [thinkrobotics.com]; 'Made in India' deployment kit variant
  ₹65,049.99; bare Orin Nano module ₹45,649.99; Orin NX 8GB devkit ₹1,09,399
  [robocraze]; Seeed reComputer J3011 (Orin Nano 8GB) ₹96,772 [robocraze].
  [source](https://robocraze.com/products/holybro-s500-v2-diy-drone-kit-included-motor-prop-and-esc)

- **TIER C — the aircraft cannot be bought as COTS in India, so Tier C is dock + site
  infrastructure at ₹2.6–3.5 lakh, plus ₹3.5–8 lakh for an OEM aircraft** — Because
  DGFT 54/2015-20 blocks imported airframes and DGCA has suspended non-TC
  registration, Tier C decomposes into (a) an aircraft procured from a DGCA
  type-certified Indian OEM under a partnership (ideaForge, Garuda Aerospace, Marut
  Drones, Asteria, Sagar Defence all have live Indian sites; none publish list prices —
  expect ₹3.5–8 lakh for a sub-25 kg security multirotor with thermal), and (b) dock +
  ground infrastructure you build. DOCK BOM (engineering estimate built from live
  Indian component prices):

  • IP66 fabricated enclosure ~800×800×600 mm, GRP or powder-coated SS304/316:
  ₹35,000–60,000 (fabrication; off-the-shelf plastic IP65 boxes top out at 90×90×60 mm
  / ₹458 and are useless at this size)
  • 2× industrial 12/24 V linear actuators, 200–300 mm stroke, ≥1000 N, IP65 for the
  split roof: ₹8,000–15,000 (the ₹2,748 100 mm 7 mm/s hobby actuator and the ₹3,375
  50 mm 100 N unit are Tier A parts only)
  • Roof rails, bearings, hinges, gas struts: ₹8,000
  • 2-axis centering arms + drives + limit switches: ₹12,000
  • Spring-loaded gold-plated charging contacts: ₹6,000 (do NOT use inductive — see 'do
  not buy')
  • EPDM weather seals, IP68 glands, drip edges: ₹3,000
  • THERMAL: 2× filtered 24 V fans ₹2,000; 100 W anti-condensation heater + hygrostat
  ₹4,000; active refrigeration for the battery bay (Peltier bank TEC1-12715 ₹296 ea, or
  a 300 W panel A/C) ₹18,000–30,000
  • Weather station (cup anemometer + rain + T/RH, fixed-mount industrial):
  ₹8,000–15,000
  • Precision landing: IR-LOCK/AprilTag beacon + downward camera + ArduPilot PLND:
  ₹8,000
  • Dock controller: Waveshare industrial 6-ch ESP32-S3 WiFi/BT/RS485 relay module
  ₹3,199 [thinkrobotics] or a small PLC ₹15,000
  • Site edge computer: Jetson Orin Nano Super Dev Kit ₹49,999 in a fanless IP-rated box
  ₹8,000
  • Networking: Waveshare/SmartElex industrial 5-port gigabit switch ₹2,032–2,564;
  Waveshare SIM7600G-H 4G HAT ₹9,499 or a 4G failover router ₹8,000
  • Power: 24 V 500 W industrial PSU ₹4,000; surge/lightning arrestor + earthing ₹12,000
  • Structure: galvanised base frame, roof anchoring for wind uplift, vibration
  isolation: ₹25,000
  • UPS: 1 kVA pure-sine inverter + 24 V 100 Ah LiFePO4 (~2.5 kWh): ₹60,000–80,000

  DOCK SUBTOTAL ≈ ₹2,60,000–3,50,000 excluding aircraft. PAYLOAD REALITY CHECK: a real
  thermal security payload is the budget killer — a 640×512 AI-tracking 19 mm thermal
  gimbal is listed at ₹7,61,999.99 and a Q30TIRM Pro 3-axis gimbal with 3 km IR
  rangefinder at ₹38,39,999.99 on thinkrobotics.com. MLX90640 32×24 arrays
  (₹4,451–7,349) are thermometers, not thermal cameras, and will not detect a person at
  30 m. [source](https://www.thinkrobotics.com/search?q=thermal+camera) *(likely)*

### Dock power, thermal and weather engineering

- **Dock power draw, solar viability and UPS sizing for Indian conditions** — Load
  model: edge computer (Jetson Orin Nano Super) 7–25 W; dock controller + sensors
  + network 10 W; actuators 60–120 W but only ~20 s per cycle; battery charging
  150–350 W for 40–60 min per sortie; ACTIVE COOLING is the dominant continuous load —
  a 300 W Peltier bank or panel A/C running most of an Indian summer day. Realistic
  budget: 60–90 W continuous idle, 250–450 W while charging, 400–700 W peak with
  cooling. Daily energy ≈ 2.5–4.5 kWh. SOLAR: at an Indian average ~4.5 kWh/kWp/day,
  covering 3 kWh/day after conversion losses needs ~0.9–1.0 kWp of panel plus ~5 kWh of
  storage. A 5 W 12 V panel is ₹759 and a 30 A charge controller ₹372 at
  quartzcomponents — i.e. hobby scale; a real 1 kWp array plus MPPT plus 5 kWh LiFePO4
  is ₹1.8–2.5 lakh, which is not competitive with grid + UPS. Recommendation:
  grid-primary, solar only if the society already has a rooftop array you can tap. UPS:
  size for outage ride-through, not off-grid. Indian society outages are typically
  1–4 h; a 1 kVA/800 W pure-sine inverter with 24 V 100 Ah LiFePO4 (~2.5 kWh usable)
  carries an 80–150 W idle dock for 8–16 h, or one charge cycle plus idle. Budget
  ₹60,000–80,000 for LiFePO4, ₹35,000–45,000 for tubular lead-acid (2× 150 Ah) with a
  3–5 year replacement cycle. CRITICAL INTERLOCK: on mains failure the dock must refuse
  to launch and must suspend charging above the LiPo thermal limit — a UPS that keeps
  the charger alive while the cooling dies is how you get a rooftop LiPo fire.
  [source](https://quartzcomponents.com/products/12v-5w-solar-panel) *(likely)*

- **Monsoon and 45 °C heat: the airframe, not the dock, sets the operating envelope, and
  LiPo charging is the binding thermal constraint** — IP RATING: the dock
  needs IP65 minimum and IP66 in practice (driving monsoon rain, not just splash). But
  the aircraft in Tiers A and B has NO ingress rating — a Holybro S500 V2 is an open
  carbon plate frame with exposed ESCs, motor windings and an unsealed FC. Even
  enterprise machines are limited (peer research on this project recorded DJI M4D at
  IP55, M3D at IP54, and Skydio X10 rated for only 0.25 in/hr rain against a dock that
  survives 4 in/hr). So the system will be weather-grounded through much of the monsoon
  regardless of what you spend on the box. HEAT: standard LiPo charge temperature range
  is 0–45 °C and most balance chargers (iMax B6AC ₹2,280) enforce nothing — a sealed
  rooftop enclosure in Indian summer reaches 60–70 °C internally with only passive
  venting, so a fan can never get you below ambient and you must actively refrigerate
  the battery bay. Add a thermistor on the pack and a hard charge-inhibit above 45 °C.
  Discharge (flight) is more tolerant but cell IR rises and usable capacity falls
  sharply at pack temperatures above 50 °C, cutting an already short endurance. WIND: a
  1.6–2.2 kg S500-class quad on 1045 props has a practical sustained-wind ceiling around
  8–10 m/s with very little margin; Indian pre-monsoon squalls routinely exceed 15 m/s,
  and a rooftop adds local acceleration and rotor-wake recirculation off parapets and
  water tanks. Wire a real anemometer into the launch interlock — do not rely on a
  forecast API. CORROSION: for Mumbai/Chennai/Kochi, conformal-coat every PCB and use
  SS316 fasteners; salt fog will kill uncoated ESCs in a season. UV: cheap ABS/PC
  junction boxes chalk and crack in 12–18 months of Indian sun; specify UV-stabilised
  polycarbonate or GRP.
  [source](https://robocraze.com/products/holybro-s500-v2-diy-drone-kit-included-motor-prop-and-esc)
  *(likely)*

### Sourcing in India: vendors and consolidated unit prices

- **Indian vendor landscape: which stores are actually usable, and the GST/price
  caveat** — VERIFIED REACHABLE AND QUOTING LIVE STOCK (2026-09-07): robocraze.com
  (best drone-parts depth — Holybro, Bonka, FlySky, RadioMaster, SimplyFly, u-blox);
  quartzcomponents.com (best passive/sensor/enclosure depth and the cheapest ESP32
  line); thinkrobotics.com (best AI-accelerator and Jetson depth, plus thermal);
  makerbazar.in (Pluto/Drona Aviation, Raspberry Pi AI Kit). VERIFIED BLOCKED to
  automated retrieval (Cloudflare 403 — they are still fine to buy from manually):
  robu.in, www.flyrobo.in, www.zbotic.in, sharvielectronics.com search,
  electronicscomp/quartz Magento search, rcbazaar.com. Amazon.in and Flipkart return
  bot-challenge pages. PRICING CAVEAT: robocraze.com and quartzcomponents.com list
  GST-inclusive INR retail. thinkrobotics.com prices end in .99 and I could not confirm
  from the storefront whether they are inclusive or exclusive of 18% GST — a peer
  researcher on this project recorded the Jetson Orin Nano Super at '₹31,959 + 18% GST'
  from another channel versus thinkrobotics' ₹49,999.99, a large enough spread that you
  should get a written quote before committing. IMPORT-DUTY CAVEAT: because DGFT makes
  drone COMPONENTS 'Free', direct import from AliExpress/Banggood is lawful for parts,
  but you pay BCD + Social Welfare Surcharge + IGST + courier clearance on landed value,
  typically adding 30–45% and 2–6 weeks, and lithium batteries are effectively
  un-shippable by air courier. For every part in this BOM the Indian-stocked price beats
  the landed import price once duty and time are counted — buy domestically.
  [source](https://robocraze.com)

- **Key Tier A/B unit prices, consolidated, all live 2026-09-07** — ESP32 Camera Dev
  Board (OV2640/OV3660) ₹675 quartz / ₹689 robocraze · ESP32-S 38-pin devkit ₹358
  quartz / ₹395 robocraze · ESP32 30-pin CP2102 ₹375 · ESP32-S3-WROOM-N16R8 devkit ₹684
  · ESP32-C3 Super Mini ₹274 · ESP32-C6-WROOM-1-N8 ₹955 · XIAO ESP32S3 Sense (OV3660 +
  mic + 8 MB PSRAM) ₹1,849 thinkrobotics · HLK-LD2410 ₹376 · HLK-LD2420 ₹222 · HC-SR501
  PIR ₹69 · MH-SR602 mini PIR ₹84 · HC-SR04 ₹72 · RC522 RFID ₹78 · SX1278 433 MHz LoRa
  ₹295 / Ra-02 ₹355 · nRF24L01+PA+LNA ₹165 · Heltec V3 ESP32 + SX1262 + OLED ₹2,299
  robocraze · TP4056 Type-C ₹16 · 18650 2600 mAh original ₹170 · 12 V 7.2 Ah Li-ion pack
  (Wattnine, 3 yr warranty) ₹1,652 · 12 V 10 A 120 W SMPS ₹639 · XY-3606 5 V 5 A buck
  ₹137 · IP65 box 90×90×60 ₹458 · PG7/PG13.5 glands ₹6/₹9 · 12 V siren SQR117 ₹194 ·
  MG996R ₹254 · SG90 ₹86 · TEC1-12715 Peltier ₹296 · 12 V 80×25 fan ₹94 · 5 W 12 V solar
  panel ₹759 · 30 A solar charge controller ₹372 · DHT22 ₹108 · BME680 ₹829 · rain
  sensor ₹39 · SanDisk 32 GB A1 ₹1,489 · Raspberry Pi 5 ₹7,799.99 · Pi 5 27 W PSU ₹1,204
  · Pi 5 Active Cooler ₹529 · Pi M.2 HAT+ ₹1,203 · Pi AI HAT+ (Hailo) ₹7,249.99 · Pi AI
  Kit ₹6,999 · Pi AI Camera IMX500 ₹8,359 · IMX708 12 MP ₹4,249 · Pi NoIR V2 ₹1,660 ·
  SmartElex 5-port industrial gigabit switch ₹2,032 · Waveshare SIM7600G-H 4G HAT ₹9,499
  · SmartElex SIM7600E 4G dongle+board ₹5,432 · OAK-D-Lite ₹31,649.99 · Intel RealSense
  D435 ₹41,279.99 / D455 ₹55,039.99 · MLX90640 55° ₹4,451 · Holybro S500 V2 kit ₹26,026
  · S500 CF frame alone ₹3,608 · F450 frame ₹668 / with PCB ₹824 · Tarot TL65B01 650
  folding CF frame ₹13,204 · A2212 1000KV ₹395 · 2212 920KV ₹707 · Emax MT2213 935KV +
  1045 prop ₹1,279 · SimonK 30 A ESC ₹371 · BLHeli 30 A ₹609 · 1045 props ₹49–77/pair ·
  Matek PDB-XT60 ₹381 · Holybro PM07 (14S) ₹5,769 · Pixhawk 6C+PM02+M9N ₹33,263 ·
  SpeedyBee F7 V3 ₹7,028 · Holybro Kakute H7 V1.3 ₹9,311 · Radiolink CrossFlight ₹6,034
  · Holybro M9N ₹8,609 / Micro M9N ₹7,111 / M10 ₹5,846 · ZED-F9P (SmartElex) ₹17,067 /
  7Semi ₹20,475 · SiK 433 MHz 100 mW ₹4,015 (Simplifly) / ₹8,661 (Holybro V3) · FS-i6X +
  iA10B ₹6,357 · RadioMaster Boxer ELRS ₹18,196 · RP1 V2 ELRS RX ₹2,556 · Bonka 4S
  4200 mAh 35C ₹4,529 · Bonka 4S 10000 mAh ₹11,874 · Tattu 4S 10000 mAh ₹13,999.99 ·
  iMax B6AC ₹2,280 · 3-axis brushless gimbal ₹7,499 · Jetson Orin Nano Super Dev Kit
  ₹49,999.99. [source](https://quartzcomponents.com)

## Recommendations

| Recommendation | Rationale | Alternatives rejected |
| --- | --- | --- |
| Put the entire C2 and telemetry link on 2.4 GHz (FlySky AFHDS-2A FS-i6X ₹6,357, or ExpressLRS RadioMaster Boxer ₹18,196 + RP1 V2 RX ₹2,556) and carry MAVLink over Wi-Fi or 4G from the companion computer. Buy at most one 433 MHz SiK pair (Simplifly 100 mW, ₹4,015) as a bench fallback and never the 500 mW unit. | The only Indian SRD exemption I could read in full is G.S.R. 853(E) for 865–868 MHz, and it caps non-specific SRD telemetry at 25 mW e.r.p. / 1% duty cycle — arithmetically incompatible with continuous MAVLink. I could not find any WPC notification de-licensing 433 MHz, and India is in ITU Region 3 where 433.05–434.79 MHz is not an ISM allocation. 2.4 GHz is the one band where every consumer device in the country is already type-approved, so an ETA filing there is routine rather than novel. | 915 MHz SiK radios (the default in US tutorials) are wrong for India — 890–915 / 925–960 MHz is licensed GSM/E-GSM cellular. 868 MHz LoRa is lawful but only for heartbeat/alarm traffic at 1–2.5% duty cycle. Analogue 5.8 GHz FPV is unencrypted, so anyone with a ₹3,000 receiver watches the society's video. |
| For Tier A, buy the Indian-made LiteWing ESP32-S3 drone (₹3,290 with battery, ₹5,230 with the optical-flow/ToF positioning combo) rather than a Pluto X (₹15,999–21,799) or any imported micro quad. | It is under 250 g (Nano class, no UIN and no type certification needed), it is ESP32-based so it shares a toolchain with the perimeter and gate nodes, it is domestically stocked, and the ₹2,095 PMW3901 + VL53L1X module is what actually makes an indoor position-hold demo work. It also sidesteps DGFT 54/2015-20 entirely because it is manufactured in India. | Pluto X is a good product but 5× the price for the same demo value. Seeed ESP-FLY (₹10,749.99) is 3× the price. Any imported ready-to-fly micro drone is a CBU import and is prohibited. |
| For Tier B, buy the Holybro S500 V2 DIY kit (₹26,026, SKU TIFKT0350) plus the Pixhawk 6C + PM02 + M9N bundle (₹33,263) rather than assembling an F450 from discrete parts. | The kit is thrust-matched, is the reference PX4 airframe with published tuning, and eliminates the single most common failure mode in student drone builds — mismatched motor/ESC/prop/battery combinations that either can't lift the companion computer or brown out the FC on a hard yaw. At ₹59,289 for the two lines it still leaves ~₹55,000 of the ₹1.5 lakh envelope for compute, energy and payload. | An F450 build from discrete parts saves ~₹22,000 but costs weeks of debugging and cannot comfortably lift a Pi 5 + AI HAT + gimbal. A Tarot 650 folding frame (₹13,204) is the right long-term airframe but needs 15-inch props and a 6S powertrain you would then have to source separately. |
| Fly a Raspberry Pi 5 + AI HAT+ (₹23,193 all-in with camera and storage) and keep the Jetson Orin Nano Super Dev Kit (₹49,999.99) firmly on the ground as the dock/site edge node. | The Pi 5 + Hailo stack is ~180 g and ~12 W, which an S500 can carry; the Jetson dev kit with its shell and PSU is over a kilogram and 25 W, which it cannot. Splitting inference this way also matches the correct architecture — light onboard detection for flight safety, heavy inference and archival at the site node. | OAK-D-Lite (₹31,649.99) puts a depth camera and inference in one airborne package but costs more than the Pi+Hailo and has weaker model support. Intel RealSense D435 (₹41,279.99) is a depth sensor, not an accelerator. Note also that a peer researcher measured Pi 5's PCIe Gen3 ×1 link roughly halving Hailo model-zoo throughput — size your model budget from measured, not published, FPS. |
| Budget ₹18,000–30,000 of the dock for active refrigeration of the battery bay, and hard-wire a thermistor charge-inhibit above 45 °C. | LiPo charging is out of spec above 45 °C and a sealed rooftop enclosure in an Indian summer runs 60–70 °C internally. Fans cannot go below ambient. This is the single line item most DIY dock designs omit and the one that turns a rooftop dock into a fire on the society's terrace — a liability no RWA will accept twice. | Passive venting and filtered fans (₹2,000) are adequate only for the electronics bay, not the battery bay. Peltier modules (TEC1-12715, ₹296 each) are cheap but ~30% efficient and dump their waste heat back into the same enclosure unless you get the hot side genuinely outside. |
| Use physical spring-loaded contacts (~₹6,000) for dock charging, never inductive/wireless charging. | Published measurement on a three-module wireless drone docking station reached 96.5 W output at 56.6% transfer efficiency — meaning roughly 75 W of loss dumped as heat, inside exactly the enclosure you are already fighting to keep below 45 °C, while nearly doubling turnaround time. | Qi-style modules are available in India for ₹384–613 but are 5 V/2 A class — three orders of magnitude short of what a 4S 4200 mAh pack needs for a sensible recharge. |
| Treat Tier C's aircraft as a partner-supplied item from a DGCA type-certified Indian OEM and spend your own Tier C money on the dock, edge node, power and site integration (₹2.6–3.5 lakh). | DGFT 54/2015-20 blocks importing a finished platform and DGCA has suspended non-TC UAS registration, so there is currently no legal path from a self-built airframe to a registered, commercially operable society drone. The dock and ground stack, by contrast, are entirely buildable now from domestically stocked components and are where your differentiation lives anyway. | Buying a DJI Dock 3 + Matrice (~₹14 lakh for the dock alone before the aircraft) is not merely expensive, it is unavailable — a prohibited CBU import. Applying for a DGFT R&D import authorisation is possible only through a recognised educational or R&D entity and adds months. |
| File WPC ETA per radio model through saralsanchar.gov.in before any deployment, and check whether the new Telecommunication Authorisation Rules 2026 / 'Radio Equipment Possession Authorisation' has superseded the process you are following. | Rule 5(1) of G.S.R. 853(E) makes type approval mandatory for exempt-band equipment, the ETA portal has a dedicated 'Drones' category, and the exemption itself is explicitly non-interference and non-protection — a licensed operator can have you ordered off air. The Saral Sanchar site now advertises a 2026 authorisation regime and a new Radio Equipment Possession Authorisation, so the instrument may have changed under the Telecommunications Act 2023. | Relying on 'the module already has an ETA' is unsafe — ETA is granted per make/model to a specific applicant, and the portal's own regulations link (wpc.dot.gov.in) is now dead, so vendor claims cannot be checked against a public register without going through the portal's ETA search. |

## Open questions

- What are the exact GSR notification numbers, dates and EIRP limits for India's 2.4 GHz
  and 5.15-5.35 / 5.725-5.875 GHz de-licensing? dot.gov.in now serves a client-rendered
  Next.js SPA with no fetchable HTML and no discoverable public API, wpc.dot.gov.in no
  longer resolves, and egazette.nic.in was unreachable. Someone must open dot.gov.in in
  a browser and download the 'Exemption from licensing requirement' PDFs directly.
- Is there ANY WPC notification de-licensing 433 MHz (or 433.05-434.79 MHz) in India for
  telemetry or SRD use? I found none and could not rule one out. This single answer
  decides whether the ~4,000-8,700 rupee SiK radios every Indian drone shop sells are
  legal.
- Was 5925-6425 MHz de-licensed for low-power indoor use in 2025, and does it help here?
  Relevant if the site link moves to Wi-Fi 6E.
- Has the 'Telecommunication Authorisation Rules 2026' and the new 'Radio Equipment
  Possession Authorisation' advertised on saralsanchar.gov.in superseded the ETA
  self-declaration process under the Telecommunications Act 2023? The portal advertises
  both simultaneously.
- When will DGCA lift the non-TC UAS registration suspension, and what will the
  replacement pathway require? This gates the entire Tier B-to-Tier C transition.
- Are thinkrobotics.com's listed prices inclusive or exclusive of 18% GST? A peer
  researcher recorded the Jetson Orin Nano Super at 'Rs 31,959 + 18% GST' from another
  channel against thinkrobotics' Rs 49,999.99 — get a written quote before committing to
  the Tier C edge node.
- What are the current BCD + SWS rates on drone components under ITC(HS) Chapter 88 and
  8806 after the 2025-26 budget? 'Free' in the DGFT import policy sense does not mean
  zero duty.
- Which Indian OEMs currently hold a DGCA Type Certificate for a sub-25 kg security
  multirotor, and will any of them sell single units to a startup rather than to
  government buyers? None publish list prices.
- Is the Raspberry Pi AI HAT+ / AI Kit actually obtainable in India right now? Both
  thinkrobotics (Rs 7,249.99) and makerbazar (Rs 6,999) showed it sold out on
  2026-09-07.
- What does IP66 sheet-metal or GRP enclosure fabrication in the 800x800x600 mm class
  actually cost from an Indian fabricator? The Rs 35,000-60,000 figure is an engineering
  estimate, not a quote.

## Unverified or risky

The researcher could not confirm the claims below. Do not rely on any of them without
independently checking the underlying source first.

- 433 MHz telemetry legality in India is UNVERIFIED. I could not reach any WPC
  notification de-licensing 433 MHz, and India is in ITU Region 3 where 433.05-434.79
  MHz is not an ISM allocation (it is a Region 1 band) and 430-440 MHz is used by
  amateur and government services. Yet Indian retailers openly stock Simplifly SiK
  100 mW 433 MHz at Rs 4,015, Holybro SiK V3 100 mW at Rs 8,661 and a 500 mW 3DR clone
  at Rs 6,683. Treat all of these as legally unverified — being on sale in India is not
  evidence of lawful operation. Do not build the architecture on this link.
- The exact FHSS occupied-bandwidth figure in Table-I of G.S.R. 853(E) is OCR-ambiguous
  in the gazette PDF's merged columns; I read it as '<=50 kHz for 58 or more hop
  channels' but the neighbouring 'EN 300 220' reference interleaved with it. The 25 mW
  e.r.p. and 1% duty-cycle figures are unambiguous; verify the bandwidth against the
  original before certifying.
- 2.4 GHz and 5.8 GHz de-licensing in India is stated here WITHOUT clause numbers
  because I could not open the DoT source. I have deliberately not cited any GSR number
  for these bands. Do not let anyone insert one from memory.
- Analogue 5.8 GHz FPV VTX (e.g. the Rs 2,987 25 mW 40CH AIO unit) is doubly risky: the
  band's exact Indian status is unverified above, and analogue FPV is unencrypted, so a
  security product broadcasting a society's video in the clear is a DPDP Act problem as
  well as a possible spectrum problem.
- All Tier C dock costs (enclosure fabrication, industrial actuators, refrigeration,
  UPS, structure) are ENGINEERING ESTIMATES built up from component-level Indian prices,
  not vendor quotes. Treat the Rs 2.6-3.5 lakh figure as a planning number with +/-40%
  uncertainty.
- Tier C aircraft pricing (Rs 3.5-8 lakh from an Indian OEM) is an estimate. ideaForge,
  Garuda Aerospace, Marut Drones and Sagar Defence all have live websites but none
  publishes a price list; several are primarily government/defence channel.
- Thermal payload pricing is verified as listed but should be sanity-checked with the
  vendor: thinkrobotics.com lists an 'AT19 Lightweight 19mm 640x512 Thermal Camera with
  AI Tracking' at Rs 7,61,999.99 and a 'Q30TIRM pro 3-axis Gimbal Camera 3KM IR Laser
  Rangefinder' at Rs 38,39,999.99. A peer researcher also flagged that Teledyne FLIR
  cores are US export-controlled and that the main maker channel will not ship Lepton to
  India.
- The 56.6% wireless-charging efficiency figure at 96.5 W comes from a 2023 IEEE paper
  ('Design and Validation of a Wireless Drone Docking Station', Stuhne et al.,
  arXiv:2309.05433), not from a 2026 commercial product. The direction of the conclusion
  (contacts beat coils in a hot sealed box) is robust; the exact number is a 2023
  research result.
- Stock status changes fast. Raspberry Pi AI HAT+ / AI Kit, Holybro Radio Telemetry Kit
  (makerbazar Rs 10,999), ESP32-CAM-MB (thinkrobotics Rs 899.99) and several ESP32-S3
  boards were all showing sold out on 2026-09-07. Re-check availability before
  committing a BOM.
- robu.in and flyrobo.in — two of the largest Indian drone-parts retailers and the ones
  named in the brief — could not be retrieved (Cloudflare 403 to every automated
  request). Their pricing is likely comparable to or slightly below robocraze; a human
  should price-check the Tier B list against robu.in manually before purchase.
- This BOM does not price the DPDP Act 2023 / DPDP Rules 2025 compliance surface
  (consent, retention, erasure, breach notification) that a resident-facing video system
  incurs, nor the CVE-2026-1579 MAVLink-signing and WireGuard requirements identified by
  peer researchers on this project. Both add engineering cost that is not hardware.
