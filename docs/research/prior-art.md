# Prior Art & Market Landscape

> Research note for [AEGIS](../../README.md). Compiled 2026-09-07 from a multi-agent
> web research sweep. Every claim below is sourced; confidence levels are the
> researcher's own and are preserved verbatim.

## Summary

The drone-in-a-box (DiaB) category is mature and consolidated, but every
credible system is priced and engineered for industrial/enterprise or
public-safety buyers, not residential communities: DJI Dock 3 alone lists at USD
15,890 (~₹14 lakh) before the aircraft, Percepto systems run USD 40k–250k+, and
an Asylon DroneDog+DogHouse pairing is reported above USD 150k. The only
genuinely residential product is Sunflower Labs' Beehive (Bee drone + Hive dock,
15-minute flights, 600 m radius, ~USD 10–15k equipment plus USD 400–700/month),
and it explicitly does not ship to India — its listed markets are North America,
Europe, Japan, Australia and Argentina. India's regulatory position is the
dominant hard constraint, not technology: DGFT Notification 54/2015-2020 (9 Feb
2022) prohibits import of drones in CBU/SKD/CKD form, which effectively closes
DJI and Skydio commercial hardware; DGCA's 12 Aug 2025 public notice began
cancelling UINs obtained by false Form D-2 declarations on illegally imported
drones; and the DGCA portal currently carries a live banner that "Registration
of Non-Type Certified (non-TC) UAS has been temporarily suspended until further
notice," meaning a self-built drone cannot presently be registered at all. The
most valuable Indian asset in this space is FlytBase (Pune + San Francisco,
founded 2017) — hardware-agnostic autonomy software with a real
REST/telemetry/video/geofence/precision-landing API, supporting DJI Dock 2/3
plus Hextronics, Heisha, iDrone and DBOX docks and custom PX4/ArduPilot stacks —
but it sells to mining, utilities and public safety, publishes no pricing, and
has no residential product. India's own DiaB hardware scene is essentially
non-existent: NxtQube (Nashik, AeroGravity Pvt Ltd, universal 80×85×65 cm dock
for sub-2 kg drones) reported FY25 revenue of ₹26.5 lakh, and ideaForge, Garuda,
Asteria/Jio, Aereo, Skylark and Marut all sell airframes or survey/DaaS software
with no verifiable docked-autonomy product for security. There is no complete
open-source DiaB; only building blocks exist (ArduPilot PLND precision landing
with IR-LOCK/AprilTag/MAVLink LANDING_TARGET backends, plus small GPL Python
ArUco-landing repos). The real gap for an India-first residential product is
therefore threefold — a price point roughly 10x below anything on the market
(societies pay ₹4–15 per flat per month for MyGate/NoBrokerHood/ADDA today), a
legal hardware path through a DGCA type-certified Indian OEM rather than
imports, and deep integration with the Indian society stack (gate boom barrier,
ANPR, guard app, ADDA's documented Bearer-token REST API) — all under monsoon,
45 °C-summer, unstable-power and balcony-privacy constraints that no incumbent
addresses.

## Hard constraints

- **CANNOT import a complete drone or drone kit into India.** DGFT Notification
  No. 54/2015-2020 dated 9 February 2022 prohibits drone imports in CBU, SKD and
  CKD form. Exemptions require specific DGFT authorisation and are limited to
  government entities, government-recognised educational institutions,
  government-recognised R&D entities, domestic manufacturers, and
  defence/security agencies. This makes DJI Dock 2/3 + Matrice, Skydio X10 +
  Dock, Percepto, Nightingale, Sunflower, Asylon and Hextronics hardware
  commercially unavailable in India.
- **CANNOT register a non-type-certified drone in India at present.** The DGCA
  portal carries a live notice: 'Registration of Non-Type Certified (non-TC) UAS
  has been temporarily suspended until further notice.' No UIN means no legal
  commercial operation.
- **MUST have DGCA/QCI type certification for any drone above 250 g used
  commercially.** Type certification is waived only for nano UAS (≤250 g) used
  non-commercially and for model RPAS used recreationally.
- **MUST hold a Unique Identification Number (UIN) for every drone above 250 g
  and a Remote Pilot Certificate (RPC) for commercial operation of
  micro-category and larger drones.** Registration and RPC workflows moved from
  Digital Sky to eGCA in July 2025.
- **MUST obtain flight authorisation through Digital Sky under 'No Permission,
  No Takeoff'.** Green zone permits up to 120 m AGL without prior approval;
  yellow zone requires ATC authorisation; red zone is prohibited. Most metro
  residential societies sit in yellow zones due to airport proximity.
- **MUST NOT fly over crowds, public gatherings or densely populated urban areas
  without explicit permission** — which describes an inhabited residential
  society by definition.
- **BVLOS in India is confined to three approved corridors** (Ladakh minerals
  survey, Telangana pharma delivery, Andhra Pradesh coastal monitoring). There
  is no general commercial BVLOS pathway over urban residential areas.
- **Routine commercial night operations are not yet formalised in India**; night
  FPV and BVLOS trials are running in select states with formalisation
  reportedly expected in 2026–27. A 24/7 autonomous night-patrol claim cannot be
  legally made today.
- Surveillance imagery of residents is personal data and **society CCTV norms
  already prohibit cameras capturing private homes and balconies**. Prior
  resident notification, 'CCTV Surveillance in Progress' signage, member consent
  and restricted footage access are expected; audio recording without member
  consent is treated as illegal in residential areas; retention is typically
  30–90 days followed by deletion.
- **Drones must not be flown within 10 km of the Pakistan and China borders
  without explicit Ministry of Home Affairs authorisation.**
- **RF-equipped drones require WPC Equipment Type Approval** from the Department
  of Telecommunications for their radios.
- **Physical siting is a hard limit for enterprise docks**: the Skydio Dock for
  X10 weighs 232 lbs (105 kg) and requires 12 ft clearance from obstacles, 6 ft
  between docks, and a surface level within ±3° — a spec most Indian society
  rooftops (water tanks, solar panels, dish antennas, pigeon nets, overhead
  cables, no level slab) cannot meet.
- **Aircraft weather envelopes, not dock IP ratings, are the operating limit.**
  Skydio X10 flies in only 0.25 in/hr rain while its dock survives 4 in/hr; DJI
  M4D is IP55, M3D IP54; Sunflower's Bee is rated -10 to 40 °C with 9 m/s
  sustained wind. Indian monsoon bursts and 45 °C+ summers exceed these.

## Findings

### India regulatory and legal environment

- **Drone imports into India in CBU, SKD and CKD form are PROHIBITED under DGFT
  Notification No. 54/2015-2020 dated 9 February 2022; components remain freely
  importable** — Notification moved drones from 'Restricted' to 'Prohibited'.
  Exemptions require specific DGFT authorisation and are limited to government
  entities, government-recognised educational institutions,
  government-recognised R&D entities and domestic manufacturers, and
  defence/security agencies. Motors, ESCs, flight controllers, camera modules,
  gimbals, propellers, GPS/telemetry radios (subject to WPC approval), airframes
  and batteries are all 'Free'. This asymmetry is deliberate policy to force
  domestic assembly.
  [source](https://www.sigmachambers.in/post/import-export-regulations-for-drones-in-india)
- **DGCA issued a Public Notice on 12 August 2025 initiating cancellation of UAS
  registrations obtained via false Form D-2 declarations on Digital Sky / eGCA —
  aimed at illegally imported foreign drones registered as 'Model RPAS'** —
  Affected entities had one month to submit written explanations with purchase
  invoices, DGFT import permissions and NABL-certified weight certificates.
  Failure means immediate UIN cancellation; subsequent operation attracts penal
  action under Drone Rules 2021 and the Aircraft Act 1934 / Bharatiya Vayuyan
  Adhiniyam 2024. A related enforcement data point: CISF seized 22 DJI Mini 5
  Pro drones worth ₹26.7 lakh at Hyderabad airport on 5 November 2025.
  [source](https://www.teamleaseregtech.com/updates/article/47681/dgca-initiation-of-proceedings-for-cancellation-of-registration-of-unm/)
- **DGCA's own portal currently displays a live banner: 'Registration of
  Non-Type Certified (non-TC) UAS has been temporarily suspended until further
  notice'** — Fetched directly from dgca.gov.in digigov portal in September
  2026. Practical consequence for a builder: you cannot register a custom-built
  or kit-built drone in India right now. The only legal aircraft path is a
  DGCA/QCI type-certified platform from an Indian OEM, or type-certifying your
  own design.
  [source](https://www.dgca.gov.in/digigov-portal/?page=jsp/dgca/InventoryList/dronesHome.jsp)
- **Indian drone weight categories and certification thresholds: Nano ≤250 g,
  Micro 250 g–2 kg, Small 2–25 kg, Medium 25–150 kg, Large >150 kg; type
  certification is not required only for nano UAS used non-commercially and
  model RPAS for recreation** — All micro/small/medium/large drones require type
  certification before operation. UIN registration required above 250 g. Remote
  Pilot Certificate (RPC, which replaced the Remote Pilot Licence via Drone
  (Amendment) Rules 2022) is needed for commercial operation of micro and above.
  Registration functions moved from Digital Sky to eGCA in July 2025.
  [source](https://www.kodainya.com/blogs/drone-categories) *(likely)*
- **Indian airspace zoning: green zone up to 120 m AGL without prior approval;
  yellow zone requires ATC authorisation; red zone prohibited. Most metro
  residential societies near airports fall in yellow** — Digital Sky operates a
  'No Permission, No Takeoff' protocol. Reported yellow-zone approval turnaround
  of 24–48 hours normally, up to 7 days during elections/national holidays.
  Flying over crowds, public gatherings and densely populated urban areas
  requires explicit permission.
  [source](https://theiidt.com/blog/drone-surveillance-rules-india) *(likely)*
- **The draft Civil Drone (Promotion and Regulation) Bill, 2025 was released for
  public consultation on 16 September 2025 and remains in draft as of 2026; it
  will repeal Drone Rules 2021/2022/2023** — Covers civil UAS below 500 kg MAUW.
  Makes type certification mandatory not only for operation but for
  manufacturing, assembly, sale, transfer and online distribution. Adds
  mandatory registration, insurance and safety features. Proposed penalties:
  fines up to ₹1 lakh and imprisonment up to one year for first offences.
  Comment deadline was extended to 15 October 2025. Preserves the existing
  import prohibition framework.
  [source](https://www.mondaq.com/india/aviation/1683740/summary-the-civil-drone-promotion-and-regulation-bill-2025)
  *(likely)*
- **India has only three DGCA-approved BVLOS corridors, none of them
  urban-residential** — Ladakh (minerals survey), Telangana (pharma delivery)
  and Andhra Pradesh (coastal monitoring). Night operations approval for
  specific commercial use cases (infrastructure inspection, delivery) is
  reported as expected to be formalised in 2026–27, with night FPV and BVLOS
  trials running in select states. This means a 24/7 autonomous night-patrol
  product over a residential society has no clean regulatory pathway today.
  [source](https://zbotic.in/dgca-drone-rules-india-2026-registration-license-guide/)
  *(uncertain)*
- **Indian surveillance-in-housing-society law is a patchwork with no single
  CCTV act, and cameras are already prohibited from capturing private homes and
  balconies — the exact thing an aerial camera does by default** — Governing
  instruments: IT Act 2000, Indian Penal Code provisions on unauthorised
  surveillance, and the 2017 Puttaswamy right-to-privacy judgment, plus
  state/municipal bylaws. Permitted camera areas: entrance/exit gates, lobby,
  corridors, parking, shared amenities. Prohibited: private homes and balconies,
  inside apartments, any space capturing private activities. Requirements: prior
  notification to residents, mandatory 'CCTV Surveillance in Progress' signage,
  member consent especially for directly affected residents, disclosure of who
  accesses footage. Retention typically 30–90 days then deletion. Audio
  recording without member consent is stated to be illegal in residential areas.
  [source](https://www.nobrokerhood.com/blog/cctv-rules-for-society/) *(likely)*

### Enterprise drone-in-a-box incumbents and price benchmarks

- **DJI Dock 3 lists at USD 15,890 for the dock alone (aircraft sold separately)
  at a US enterprise reseller, in stock as of the fetch** — Advexure product
  page: 'DJI Dock 3 — $15,890', 'In Stock & Ready to Ship'. Matrice 4D/4TD
  priced separately and not listed. Converts to roughly ₹14 lakh at ~₹88/USD
  before duty — and is not legally importable into India anyway.
  [source](https://advexure.com/products/dji-dock-3-for-matrice-4d-and-4td)
- **DJI Dock 3 full specs: 55 kg dock, IP56, -30 to 50 °C, 800 W max input,
  27-minute charge, >4 h backup** — From DJI's own spec page: weight 55 kg
  without aircraft; opened 1760×745×485 mm, closed 640×745×770 mm; IP56; -30° to
  50 °C; input 100-240 V AC 50/60 Hz, max 800 W, output 35 V DC; charge 15%→95%
  in 27 min; backup battery 12 Ah lead-acid giving >4 h; Ethernet 10/100/1000
  Mbps; 4G requires DJI Cellular Dongle 2 (sold separately); built-in wind,
  rainfall, ambient temp, water-immersion and cabin temp/humidity sensors.
  [source](https://enterprise.dji.com/dock-3/specs)
- **DJI Matrice 4D/4TD: 54 min max flight, 47 min hover, 1850 g, IP55, -20 to 50
  °C, 10 km radius, 12 m/s wind** — Weight 1850 g with battery/props/microSD;
  MTOW 2090 g; 377.7×416.2×212.5 mm; IP55; -20° to 50 °C; max flight 54 min at
  12 m/s forward, hover 47 min; max operating radius 10 km; max wind resistance
  12 m/s; battery 6768 mAh / 149.9 Wh, charging temp 5–45 °C. M4D cameras: 4/3
  CMOS 20 MP wide (84° FOV), 1/1.3" 48 MP medium tele (35°), 1/1.5" 48 MP tele
  (15°). M4TD adds 640×512 thermal, 45° FOV, -40 to 150 °C.
  [source](https://enterprise.dji.com/dock-3/specs)
- **DJI Dock 2 (the cheaper, smaller predecessor): 34 kg, IP55, -25 to 45 °C,
  1000 W, 32-min charge, >5 h backup; Matrice 3D/3TD 1410 g, 50 min flight** —
  Dock 2: 34 kg without aircraft; open 1228×583×412 mm, closed 570×583×465 mm;
  IP55; 100-240 V AC, 1000 W max; charge 20%→90% in 32 min at 25 °C; 12 Ah
  lead-acid backup >5 h; -25 to 45 °C; max landing wind 8 m/s; max altitude 4000
  m. M3D/3TD: 1410 g (MTOW 1610 g), IP54, 50 min max flight / 40 min hover, 10
  km radius, 12 m/s operating wind but only 8 m/s for takeoff/landing, -20 to 45
  °C, 7811 mAh / 115.2 Wh. M3TD thermal 640×512@30fps.
  [source](https://enterprise.dji.com/dock-2/specs)
- **Skydio Dock for X10 is engineered for enterprise sites and is impractical
  for a typical Indian society rooftop: 232 lbs (105 kg), needs 12 ft obstacle
  clearance and a surface level within ±3°** — 34.1" L × 37.7" W × 55.5" H with
  base; 232 lbs with base; -20 to 50 °C; airborne in 20 seconds; launch/land
  wind up to 12 m/s (27 mph); external radio rated to 160 km/h; coverage radius
  1–2 km urban, 6–12 km rural; dock withstands 4"/hr precipitation but the X10
  aircraft only flies in 0.25"/hr (light-moderate) rain. Site prep: 100–240 V AC
  (220 V recommended in cold), minimum 20 Mbps upload (100 Mbps recommended), 12
  ft from obstacles, 6 ft between docks, level within ±3°; installation 1–3
  days. Backhaul via Cat6, Starlink or 5G. Includes ADS-B receiver and weather
  sensors for BVLOS cases. [source](https://www.skydio.com/dock/technical-specs)
- **Skydio's India presence is a defence/government channel via Aeroarc, not a
  commercial route to market** — Partnership announced February 2023 for
  development, manufacture, deployment and support of small UAS for Indian
  customers, explicitly aimed at the Indian Ministry of Defence, with a stated
  later intent to branch into non-military/non-government sectors. Skydio
  established an R&D centre in Bengaluru. No verifiable commercial availability
  of X10 or Dock for X10 to Indian private buyers was found. Separately, X10,
  Dock for X10 and R10 joined the Pentagon Blue UAS Cleared List in July 2026
  and the US Army ordered 2,500+ X10Ds for over $52M in March 2026 — the
  company's centre of gravity is US defence.
  [source](https://www.businesswire.com/news/home/20240219867057/en/Skydio-and-Aeroarc-Partner-to-Advance-Support-for-Government-Customers-in-the-Region)
  *(likely)*
- **Percepto sells AIM software plus Percepto Air Max / Air Max OGI aircraft and
  Percepto Base, with third-party pricing indications of USD 40,000–250,000+** —
  Percepto Base features patented docking/charging and landing mechanisms, LTE
  connectivity, an integrated weather station, and 'base hopping' (one drone
  across multiple bases), rated for hurricane-level winds, heavy snow and rain.
  Target verticals are electric utilities, solar, mining, oil & gas and ports —
  no residential offering. The $40k–250k+ range comes from a third-party 2026
  buyer's guide, not Percepto.
  [source](https://percepto.co/drone-in-a-box/percepto-base/) *(likely)*
- **Nightingale Security Blackbird Block-5 remains in market with ~40-minute
  endurance and an unusually wide temperature envelope** — Block-5, built on 7+
  years of operations and 400,000+ missions. ~40 minutes endurance; 14.3 lbs
  (6.5 kg); 3–5 mile operational radius; thermal 640×512 at 30 mK sensitivity;
  4K camera 60° FOV with 12x zoom, starlight night vision under 10 lux; operates
  in rain, snow, sustained winds to 40 mph with gusts to 45 mph; 0–122 °F
  (extended to 140 °F, i.e. 60 °C); AES-256 encryption; under 55 dB acoustic
  signature at 100 ft altitude. No public pricing. Also partnered with
  Department 13 International to bring Blackbird to Australia.
  [source](https://www.nightingalesecurity.com/)
- **Azur Drones / Skeyetech was acquired by Tonner Drones on 27 August 2026 —
  the European DiaB incumbent has changed hands** — Binding protocol signed 27
  Aug 2026, funded entirely from cash on hand with no new equity. Skeyetech
  claims 62,000+ autonomous BVLOS flights, deployed and operational in 11
  countries, compatible with leading VMS platforms, used for
  security/surveillance, operational support, infrastructure inspection and
  gas/radioactivity detection. Latest product generation is Skeyetech E2. Tonner
  Drones and Drone Volt entered a parallel industrial and commercial
  partnership.
  [source](https://www.globenewswire.com/news-release/2026/08/27/3351786/0/en/tonner-drones-expands-defense-security-exposure-with-the-acquisition-of-azur-drones.html)
- **Asylon's model is robot hardware plus a 24/7 human-staffed Robotic Security
  Operations Center — total cost reported well above USD 150,000 for DroneDog +
  DogHouse** — Guardian aerial platform uses a patented battery-swap system (not
  contact charging), 20x optical zoom day/night, optional gun-detection computer
  vision, FAA BVLOS waivers and Operations Over People (OOP) approval, and is
  described as the first US-made platform with ASTM parachute certification.
  DroneDog pairs Boston Dynamics Spot with Asylon's PupPack payload and returns
  to a ruggedised DogHouse to charge. Electrek reports the DroneDog+DogHouse
  combo 'well over $150,000' plus ongoing payroll/subscription for human
  monitors. [source](https://asylonrobotics.com/security-robots/) *(likely)*
- **BRINC's 2026 line splits into a battery-and-payload-swapping outdoor system
  and a contact-charging one — with published endurance figures useful as a
  benchmark** — Guardian: 62 min flight, 60 mph top speed, 200 sq mi coverage,
  640x visual zoom, 64x HD thermal zoom, satellite connectivity, ships with a
  Guardian Station doing robotic battery AND payload swapping. Responder: 42 min
  flight, 28 sq mi coverage, 40x visual zoom, 640 px thermal, two-way comms with
  loudspeaker, Responder Station charges 10–90% in 20 minutes via contact
  charging. Lemur 2 indoor drone with 4K day/night, thermal, 360° position hold,
  real-time floor-plan generation, glass-breaker attachment. LiveOps web
  platform with teleoperations, livestreaming, evidence management and API
  integrations. No public pricing; customer base is US public safety.
  [source](https://www.brincdrones.com/)
- **Paladin Drones is a US drone-as-first-responder company with autonomous dock
  deployment, 47-second average aerial response and 200k+ flights — proof the
  dock-plus-dispatch model works, but only for public safety** — Products:
  Knighthawk 2.0 drone, Paladin EXT, Watchtower command system, Paladin Relay
  (LTE/RF connectivity switching), fleet management. 3–5 mile range on a single
  charge over LTE. 72% of incidents observed before ground units arrive. Targets
  police/fire departments typically with 35–150 officers. Deployments include
  Ferguson PD (MO), Forest Park PD (GA), Murrells Inlet FD (SC), Elizabeth PD
  (NJ). No pricing disclosed. [source](https://paladindrones.io/)
- **Flyby Robotics is an airframe company, not a DiaB company — no dock product
  found** — F-11 Series: F-11T with a 157 TOPS NVIDIA Jetson Orin NX, F-11S with
  dual 314 TOPS Jetson Orin NX. Max hover 56 minutes; up to 80 km/h in Sports
  Mode; dual RTK GPS at 1 cm + 1 ppm horizontal; -20 to 49 °C; 5.7 lb standard
  payload; Made in USA with NDAA-compliant variants. Markets: research/AI,
  public safety/ISR, photogrammetry. No dock or pricing shown.
  [source](https://www.flybyrobotics.com/)

### Residential prior art, low-cost docks and alternative architectures

- **Sunflower Labs Beehive is the only true residential/gated-community DiaB —
  and it does NOT ship to India** — 2026 site states availability shipping to
  'North America, Europe, Japan, Australia, and Argentina'; delivery and
  installation 8–12 weeks. Regulatory posture: FAA Part 107 waiver in the US,
  EASA SORA in Europe, case-by-case elsewhere; ISO/IEC 27001:2022 certified.
  Operating cost quoted as '$4-7/hr after it is installed for continuous
  operations', lease model rather than purchase. Up to 8 hours of daily flight
  time in 15-minute sorties, 600 m radius. Notably it still 'requires a
  pilot-in-command connection during operations' — it is not unattended
  autonomy. [source](https://sunflower-labs.com/)
- **Sunflower Bee/Hive specs expose the exact envelope an India-focused product
  must beat: 15-minute flights, 40 °C aircraft ceiling, 9 m/s wind, 1080p only**
  — Bee: 15 min operational flight time (+5 min reserve); cruise 14.5 km/h (4
  m/s); 1.56 kg with battery; 28×28×21 cm body, 48×48×21 cm with prop guards (57
  cm diagonal); camera 1920×1080 @25 fps, 50° vertical / 100° horizontal FOV,
  ~250 ms video latency; -10 °C to 40 °C; wind 9 m/s sustained, gusts 14 m/s;
  4000 mAh; 600 m max transmission radius; recharge ratio 1:2 flight-to-charge;
  needs 3 Mbps up and down. Hive: 35 kg; 86×80×80 cm closed; -20 °C to +50 °C;
  110 V or 220 V AC; 1 hour backup battery; Ethernet plus optional LTE modem.
  The Bee's 40 °C ceiling is below routine Delhi/Rajasthan/Nagpur summer highs.
  [source](https://sunflower-labs.com/specs)
- **Hextronics is the cheapest credible dock family and is explicitly
  FlytBase-integrated — the most likely hardware substrate for a cost-down
  design** — Eclipse (2026 flagship): NDAA-compliant DiaB, launch in under 20
  seconds, integrated aircraft+dock+HexAIR software, Trinity three-axis
  stabilised payload with wide+telephoto plus thermal (Trinity T) or low-light
  (Trinity V), targeted at solar fields, rail/roadside, oil & gas and urban
  rooftop surveillance. Atlas: stores 8 swappable batteries, 10–100% charge in
  45 minutes, 60-second battery swap, IP66, ~32 kg base (up to ~45 kg upgraded),
  internal regulated temperature 10–35 °C with compressor cooling and optional
  HVAC/heating, precision landing ±15 cm, for DJI M300/M350 RTK. Global: compact
  affordable nest with robotic battery swapping, under 5 minutes downtime,
  ~99.99% precision-landing reliability, -20 °F to 150 °F. No public pricing on
  any of them. [source](https://hextronics.com/)
- **Heisha DNEST is the lowest-cost dock family in the market, adapted to the
  DJI Mavic 3E class rather than the Matrice class** — DNEST5 pack reported at
  ¥29,800 for the full hardware+software package; another configuration reported
  at USD 4,880 for hardware plus software. Standard version adapted to DJI Mavic
  3E; D80 dock hardware provides remote automatic takeoff/landing and one-key
  return. Heisha also sells a luggage-style portable dock for the Mavic 3
  Enterprise series and charging landing-gear components. Pricing figures are
  from listings/resellers, not Heisha's own quote sheet, and are older than
  2026.
  [source](https://heishatech.com/solutions/dnest5-drone-dock-pack-for-multiple-scenarios/)
  *(uncertain)*
- **Easy Aerial's SAMS-T proves a tethered architecture delivering 24+ hours of
  continuous airborne endurance via data-over-power cable — a fundamentally
  different design point worth evaluating for India** — SAMS-T is a fully
  autonomous 'tethered-drone-from-a-box' that stays airborne over 24 hours while
  transmitting HD video and telemetry through the power line. Tether options
  150, 200 and 300 ft with auto-retraction inside the 'Easy Guard' enclosure.
  Aircraft options: Alpine Swift quadcopter or Albatross hexacopter. The ECTS
  variant is a rucksack-portable 40 lb Pelican-case version. 300 ft ≈ 91 m
  tether height, which is within India's 120 m green-zone ceiling.
  [source](https://easyaerial.com/) *(likely)*

### India's own drone, dock and autonomy industry

- **FlytBase (Pune + San Francisco, founded 2017) is the strongest India-origin
  asset: hardware-agnostic drone autonomy software supporting DJI Dock 2/3,
  Hextronics, Heisha, iDrone and DBOX docks plus custom PX4/ArduPilot builds** —
  Supported aircraft list: DJI Matrice 4D/4TD, Matrice 3D/3DT, Matrice 300 RTK,
  Matrice 350 RTK, Matrice 30/30T, Mavic 3E/3T/3M, Mavic 2 Enterprise, Mavic 2
  Pro/Zoom, plus 'custom PX4/ArduPilot stacks'. No Indian-manufactured drone or
  dock appears on the supported-hardware list. Features: cloud missions over
  4G/5G/LTE, centimetre-level precision landing, dock
  open/close/telemetry/charging control, failsafes on low battery / RC-link loss
  / internet loss / GPS loss, 'Visual AI agents that detect the events that
  matter in live drone video', and 'Flinks' for third-party app integration.
  Investors include Lavni Ventures and Pentathlon Ventures.
  [source](https://flytbase.com/supported-hardware)
- **FlytBase exposes eight documented API surfaces and a virtual-drone sandbox —
  a genuinely buildable substrate rather than a closed product** — APIs:
  Navigation (waypoints, geofences, altitude), Mission Planning
  (compose/validate against terrain and airspace), Command & Control (arm,
  takeoff, RTH, emergency, with audit trails), Vehicle Setup (profiles,
  calibrations, capability flags), Telemetry (position, battery, link quality,
  health streams), Video Streaming (low-latency RTSP and WebRTC), Gimbal
  Control, Payload. Plus four infrastructure capabilities: geofence
  keep-in/keep-out, collision avoidance, drone-in-a-box control (remote
  launch/land/recovery) and precision landing using machine-generated tags. API
  reference at apidocs.flytbase.com; access is gated — 'keys, docs, and a
  sandbox dock' on request. Legacy FlytOS APIs exposed ROS, C++, Python, REST
  and WebSocket (github.com/flytbase/flytsamples).
  [source](https://flytbase.com/drone-api)
- **FlytBase publishes no public pricing as of 2026 — the pricing page is a
  7-step enterprise assessment form** — Page states 'Every enterprise has unique
  requirements. FlytBase pricing reflects your specific needs', with pricing
  driven by industry/use case, integration complexity, fleet requirements and
  compliance standards. Older third-party references to 'FlytBase Pro at
  $99/month' and 'DiaB from $10,000' appear to describe the earlier FlytNow-era
  product and should be treated as stale. [source](https://flytbase.com/pricing)
- **NxtQube (Nashik) is India's only identifiable drone-in-a-box hardware
  startup, and it is sub-scale: FY25 revenue ₹26.5 lakh** — Founded 2022 by
  Nilesh Palkar and Nikhil Rajput; legal entity AEROGRAVITY PRIVATE LIMITED;
  23–31 employees; one undisclosed funding round dated 21 August 2024. FY25
  revenue ₹26.5 lakh, up 5.8% from FY24's ₹25.1 lakh. Product: 'universal
  drone-in-a-box' station sized 80×85×65 cm, integrating with nano and micro
  category drones under 2 kg, with stated DJI Mavic 2 Pro compatibility;
  supports autonomous landing, flight planning, takeoff and rapid battery
  charging. No public pricing. [source](https://inc42.com/company/nxtqube/)
- **ideaForge sells high-endurance security airframes but no verifiable
  drone-in-a-box product** — NETRA V4 PRO: over 90 minutes endurance, over 10
  miles operational range, 27x HD optical zoom, quadcopter, toolless snap-fit
  man-portable assembly. NETRA 5 (announced February 2025): under 8 kg MTOW,
  man-portable, deployable in under three minutes, for defence and security
  operations. No docking station, nest or DiaB product appears on ideaForge's
  product pages. MTOW/IP rating/wind specs for V4 PRO are not published on the
  landing page. [source](https://us.ideaforgetech.com/netra-v4-pro/)
- **Asteria Aerospace (Jio Platforms / Reliance) sells the SkyDeck cloud DaaS
  platform and the A400 EO/IR surveillance drone — but no docked-autonomy
  product** — SkyDeck is a cloud platform for drone fleet management, flight
  scheduling/execution, data processing, visualisation and AI analysis, launched
  to deliver DaaS across agriculture, survey, industrial inspection and
  surveillance/security. The A400 carries a dual optical + IR payload for
  day/night patrolling and has been used for forest-area monitoring. SkyDeck's
  launch material dates from 2022; no 2025-26 DiaB announcement was found.
  [source](https://asteria.co.in/news/asteria-aerospace-launches-skydeck-a-software-platform-for-delivering-drone-as-a-service-daas)
  *(likely)*
- **The other named Indian players are not in the security-DiaB business at
  all** — Aereo (formerly Aarav Unmanned Systems) sells end-to-end drone survey
  services for mining, infrastructure and urban/rural development plus forest
  conservation — no security, no dock, no pricing. Skylark Drones sells Spectra
  (worksite intelligence with platform integrations and API access) and Drone
  Mission Ops (project/fleet management) into mining, infrastructure,
  agriculture, solar and utilities. Marut Drones lists a 'Surveillance Drone'
  alongside Kisan, Logistics, ZAP, Cleancopter, Aquacopter, Seedcopter and
  Training drones and claims 5 DGCA-certified drone platforms, but shows no DiaB
  and no pricing. NewSpace Research raised $52M (equity $33M + $19M debt from
  SBI startup hub and SIDBI) for defence UAS, swarms, GPS-denied ops.
  [source](https://aereo.io/) *(likely)*

### Society software stack, gate integration and ARPU ceiling

- **Society management apps price at ₹3–15 per flat per month — this is the ARPU
  ceiling context an India society product must reason against** — MyGate
  ₹5–12/flat/month (used by over 25,000 societies); NoBrokerHood ₹8–15; ADDA
  ₹4–10; ApnaComplex ₹6–12; Apartment Adda ₹5–8; Societynmore ₹3–6;
  iSocietyManager ₹4–8; Neighbium ₹3–5; CommonFloor Resident free basic / ₹3+
  premium. Common integrations across these platforms: Razorpay UPI Autopay,
  Paytm, PhonePe, WATI WhatsApp API, Interakt, ZKTeco biometric devices, eSSL
  RFID readers, Tally, Zoho Books. Recommended deployment tiers put 200–500-unit
  societies on NoBrokerHood/ADDA and 500+ units on custom builds.
  [source](https://codingclave.com/blog/best-society-management-app-india-2026)
  *(likely)*
- **ADDA publishes a real, documented REST API with Bearer-token auth covering
  exactly the gate/security surfaces a drone system needs — but has NO alerts,
  notifications, SOS/panic or camera API** — Documented API groups: Units &
  Users (units by owner, units by community, members in a unit, units by member
  phone); Accounting (post invoices/receipts, account statements, defaulters,
  collection summaries); Access Control ANPR (vehicle logs, database sync —
  'maintain a log of all entry/exits happening at Gate' and sync licence-plate
  data); Access Control RFID (movement logs, database sync); Biometric Devices
  (event logging, device status); Visitor & Staff Management (staff list, staff
  check in/out, add visitors); Facility APIs; Miscellaneous (work-order updates,
  file uploads, community list, purchase requests). Auth requires a Bearer token
  approved by the ADDA API team via access request. Docs also referenced at
  indiaapi.adda.io/docs/. The absence of an alert/notification endpoint means a
  drone system cannot push an incident into ADDA today without a partnership.
  [source](https://adda.io/adda_api/adda_api.html?apt=adda-apis)

### Open-source building blocks

- **There is no complete open-source drone-in-a-box project; ArduPilot's
  precision-landing subsystem is the only production-grade open building block**
  — ArduPilot Copter supports centimetre-level precision landing/loiter through
  six backends: IR-LOCK sensor+beacon, companion computer sending MAVLink
  LANDING_TARGET messages, AprilTag/fiducial markers (e.g. via Realsense T265),
  the Landmark Precision Landing System, UAVLAS ULS-XCopter-G2 IR beacon kit,
  and a BlueOS Precision Landing Extension. Key parameters: PLND_ENABLED (1 to
  activate), PLND_TYPE (1=MAVLink, 2=IR-LOCK, 3=Gazebo, 4=SITL), PLND_YAW_ALIGN,
  PLND_ALT_MAX, PLND_STRICT (0=continue, 1=retry then land, 2=retry then hover).
  Requires a valid horizontal position estimate, steady attitude solution, a
  rangefinder for IR-LOCK, and a companion computer for vision approaches.
  Documentation explicitly warns 'Poor GPS/EKF or a noisy rangefinder will
  degrade performance.'.
  [source](https://ardupilot.org/copter/docs/precision-landing-and-loiter.html)
- **Available open-source ArUco/vision landing repos are small research
  projects, not production stacks — treat them as reference, not foundation** —
  8OL-Robotics/precision-landing: Python, GPL-3.0, 28 stars, 6 forks, only 13
  commits on main; main branch targets PX4 via mavSDK, separate ardupilot branch
  uses dronekit; decoupled/hotswappable PID controller, IO and pose estimators;
  works in Gazebo and on 3DR Solo via UDP video. Other repos found:
  Kenil16/master_project (ROS + PX4 vision landing, centimetre-order mean
  error), carlo98/precision_landing_shaping_RL (deep RL landing, Gazebo-ROS2
  dashing/foxy with PX4 RTPS), nikv96/AutonomousPrecisionLanding (OpenCV +
  dronekit-python on Pixhawk), JacopoPan/aerial-autonomy-stack (PX4/ArduPilot
  swarms with ROS2, YOLO, LiDAR, NVIDIA Jetson). FlytBase itself maintains
  public repos at github.com/flytbase (flytsamples, flytdocs) from the older
  FlytOS era. [source](https://github.com/8OL-Robotics/precision-landing)

## Recommendations

| Recommendation | Rationale | Alternatives rejected |
| --- | --- | --- |
| Do NOT design around DJI hardware, and do not plan to import any foreign drone or dock. Assume DJI Dock 2/3 + Matrice is unavailable to you in India, permanently, for the life of this project. | DGFT Notification 54/2015-2020 (9 Feb 2022) prohibits CBU/SKD/CKD drone imports; DGCA's 12 Aug 2025 public notice is actively cancelling UINs obtained on illegally imported drones; CISF seized 22 DJI Mini 5 Pro units at Hyderabad airport on 5 Nov 2025. Even if you obtained a Dock 3, the aircraft cannot be legally registered, so the system cannot be legally flown commercially. Every specification and price in the DJI ecosystem is a benchmark for you, not a bill of materials. | Grey-market import (illegal, and the UIN cancellation regime makes it operationally worthless). R&D exemption import (available only to government/recognised R&D entities and domestic manufacturers via specific DGFT authorisation — a route to a prototype, not a product). Buying pre-Feb-2022 grandfathered units (unscalable, ageing, unsupported). |
| Solve the aircraft-legality problem FIRST, before any engineering: either partner with a DGCA/QCI type-certified Indian OEM for the airframe, or budget explicitly for type-certifying your own design. Treat this as the project's critical path. | DGCA's portal currently states 'Registration of Non-Type Certified (non-TC) UAS has been temporarily suspended until further notice.' A custom-built drone cannot be registered today, so it cannot get a UIN, so it cannot fly commercially. Marut claims 5 DGCA-certified platforms; ideaForge and Garuda are certified manufacturers. The draft Civil Drone Bill 2025 hardens this further by making type certification mandatory for manufacture, assembly, sale, transfer and online distribution — not just operation. | Sub-250 g nano to dodge certification: type certification is only waived for nano used NON-commercially, and a 250 g aircraft cannot carry thermal, cannot hold position in 9 m/s wind, and cannot fly in Indian monsoon or summer thermals. It is a demo, not a product. Operating as a hobbyist/model RPAS: this is precisely the false Form D-2 declaration DGCA is prosecuting. |
| Build the software, AI and society-integration layer; buy or partner for the airframe and dock. Evaluate FlytBase (Pune) as your autonomy substrate before writing your own flight stack. | FlytBase is India-headquartered, exposes eight documented API surfaces (Navigation, Mission Planning, Command & Control, Vehicle Setup, Telemetry, Video Streaming via RTSP/WebRTC, Gimbal, Payload) plus geofence, collision avoidance, DiaB control and precision landing, supports custom PX4/ArduPilot stacks — not just DJI — and offers a virtual-drone sandbox with an identical API surface for pre-flight development. Rebuilding mission planning, failsafes, precision landing and video transport is 18–24 months of work that adds no differentiation in a residential product. | Pure ArduPilot + custom ground station: viable and cheaper in licence terms, and ArduPilot's PLND subsystem (PLND_TYPE 1/2, IR-LOCK or MAVLink LANDING_TARGET, ±cm accuracy) is genuinely production-grade — but you inherit all the dock-state-machine, failsafe, video-transport and fleet-management work. The open-source landing repos found (8OL-Robotics/precision-landing at 13 commits, Kenil16/master_project, carlo98 RL) are research artefacts, not foundations. Percepto/Skydio/Nightingale SDKs: not commercially available in India. |
| Seriously evaluate a TETHERED architecture for phase 1 instead of a free-flying DiaB. A mast/tether unit at 60–90 m over a society, always powered, always within VLOS of its anchor. | Easy Aerial's SAMS-T demonstrates 24+ hours of continuous airborne endurance via data-over-power tether with 150/200/300 ft cable and auto-retraction. For an Indian society this solves four problems at once: no battery-cycle economics, no charge-time coverage gap (versus Sunflower's 15-minute sorties and 1:2 flight-to-charge ratio), a far simpler regulatory story (permanently within visual line of sight of the anchor, under the 120 m green-zone ceiling), and dramatically better monsoon/wind survivability than a 1.5 kg free-flyer. It also sidesteps the precision-landing reliability problem entirely. | Free-flying DiaB as phase 1: every incumbent does this, and it inherits the hardest problems (precision landing in rain, battery thermal management at 45 °C, BVLOS/night approvals, obstacle avoidance among towers and overhead cables). Fixed pole-mounted PTZ cameras: cheaper still, but no repositioning, no pursuit, no deterrent presence — and societies already have these, so there is no new value to sell. |
| Set the commercial target at ₹3–5 lakh capex or ₹20,000–30,000/month as a service for a 300–500 flat society, and design the BOM backwards from there. Do not attempt to sell a ₹15 lakh+ system to an RWA. | Societies currently pay ₹4–15 per flat per month for their entire management platform (MyGate ₹5–12, NoBrokerHood ₹8–15, ADDA ₹4–10 across 25,000+ societies for MyGate alone). ₹25,000/month across 400 flats is ~₹62/flat/month — roughly 5–8x the software ARPU they already accept, but comparable to the fully loaded cost of one additional security guard, which is the budget line an RWA actually compares against. Every incumbent is 10–50x above this: DJI Dock 3 at $15,890 dock-only, Percepto at $40k–250k+, Asylon DroneDog+DogHouse reported above $150k, Sunflower at ~$10–15k equipment plus $400–700/month. | Selling capex-heavy systems to premium/luxury gated communities only: a real but tiny segment in India, and Sunflower already proves the model works there — just not at a price Indian RWAs clear. Government/municipal channel: larger budgets but 12–24 month sales cycles and a different product. |
| Design one dock to serve 3–5 nearby societies (hub-and-spoke DaaS with scheduled patrol slots), not one dock per society. | At any realistic Indian BOM, a dedicated per-society system will not clear the ₹25k/month price point. A single unit doing four 15-minute scheduled patrols across four societies within a 600 m–1 km radius amortises the hardware 4x, and matches how Indian societies actually cluster in townships and sector layouts. Sunflower's 600 m transmission radius and Skydio's 1–2 km urban radius both make this geometrically plausible; Percepto's 'base hopping' (one drone, multiple bases) shows the vendors already think in this direction for industrial sites. | One dock per society: clean product story, unaffordable BOM. On-demand-only (no scheduled patrol): removes the deterrence value that is most of what an RWA is actually buying. |
| Make privacy-by-design a shipped feature, not a disclaimer: hard geofenced no-look volumes around every balcony and window, gimbal pitch limits enforced in firmware, on-device blurring, resident-visible flight logs, and DPDP-aligned 30-day retention. | Existing Indian society CCTV norms already prohibit cameras that capture private homes and balconies, require prior resident notification, mandatory signage and member consent, and hold audio recording without consent to be illegal in residential areas. A drone at 40–60 m over an Indian apartment complex looks directly into balconies and bedrooms by default — this is the single most likely cause of deployment failure, RWA revolt or litigation, and it is a risk no incumbent product addresses because none of them fly over dense multi-storey housing. Shipping enforceable no-look geometry is both the mitigation and the differentiator. | Treating privacy as a terms-of-service problem: does not survive one angry resident, one WhatsApp group, or one Puttaswamy-grounded complaint. Manual pilot discretion: unauditable and unscalable. |
| Integrate with ADDA first (documented Bearer-token REST API), pursue MyGate and NoBrokerHood through business development, and integrate at the GATE — boom barrier, ANPR camera, guard app, intercom — not just the app. | ADDA publishes real endpoints for ANPR vehicle logs and database sync, RFID movement logs, biometric events, visitor/staff check-in-out and unit/member lookup, gated by an approved Bearer token. That is exactly the trigger surface a drone needs: an unrecognised plate at the service gate, an after-hours staff entry, a visitor who never exited. Critically, ADDA has NO alerts/notifications/SOS/camera API, so incident push-back requires partnership. MyGate (25,000+ societies) publishes no API at all — assume BD, not self-serve. No DiaB vendor worldwide integrates with any of this; it is uncontested ground. | Standalone app with no society-platform integration: makes the drone a fourth screen the guard ignores, and gives the RWA no reason to prefer it over more cameras. Building your own society management platform: competing with MyGate/ADDA/NoBrokerHood is a different, larger, worse business. |
| Engineer explicitly for the Indian physical envelope and publish a monsoon fallback: 45–50 °C ambient, 50–100 mm/hr rain bursts, 3-phase voltage swings and multi-hour outages. | Sunflower's Bee is rated only to 40 °C — below routine Delhi/Nagpur/Rajasthan summer highs — while its Hive tolerates -20 to +50 °C, showing the aircraft, not the dock, is the thermal bottleneck. Skydio's dock handles 4"/hr precipitation but the X10 aircraft only flies in 0.25"/hr; DJI M4D is IP55 and M3D only IP54. In Mumbai/Bengaluru/Kochi that means the aircraft is grounded for a large share of June–September, and no vendor sells anything for those months. Dock power draw is 800 W (Dock 3) to 1000 W (Dock 2) with only 4–5 hours of lead-acid backup, against Indian societies running DG sets and unstable mains — budget for a stabiliser/isolation transformer and a longer-duration battery that no vendor bundles. | Assuming enterprise IP ratings transfer: they describe the dock, not the aircraft, and the aircraft is what gets wet. Ignoring the monsoon and selling annual contracts anyway: guarantees churn at renewal in coastal and Western Ghats cities. |
| Target the threats a drone is actually good at, and be honest that it is bad at the ones societies complain about most. | Indian society incident reality is dominated by two-wheeler and car theft in covered basement parking, package/courier theft at doors, unauthorised entry through service and staff gates, domestic-help disputes, and stray-dog/monkey nuisance — almost all of which occur under roof, indoors, or at ground level where an aerial platform is useless or illegal. A drone genuinely wins on: large open perimeters and compound walls, plotted/villa developments and townships, construction-phase sites, terrace and open-parking sweeps, fire/water-tank/solar-panel inspection, crowd and event overwatch, and night thermal sweeps of open land. Scoping the product to those, and pairing it with existing ground CCTV for the rest, is the honest and defensible pitch. | Positioning as a general replacement for guards or CCTV: it is neither, the RWA will discover this in month two, and the reference customer is lost. |

## Open questions

- Does DGCA treat a TETHERED drone as a UAS under Drone Rules 2021, and does it
  require the same UIN, type certification and Digital Sky authorisation as a
  free-flying drone? This single answer determines whether the tethered
  architecture is a regulatory shortcut or not. Could not verify — needs a
  direct DGCA query or aviation counsel.
- When will the suspension of non-Type-Certified UAS registration be lifted, and
  is there any interim path (test permit, R&D authorisation, sandbox) for a
  startup to legally fly a self-built prototype? Not stated on the DGCA portal.
- Has the Civil Drone (Promotion and Regulation) Bill, 2025 been introduced in
  Parliament or enacted since the October 2025 consultation closed? Status as of
  September 2026 could not be confirmed beyond 'still draft'.
- What is the actual list of DGCA/QCI type-certified drone models, with
  manufacturer, model and TC number? The DGCA portal did not expose a fetchable
  list. This is the single most important procurement input and must be obtained
  directly from DGCA/QCI.
- Will FlytBase license its platform to an India residential-security reseller,
  at what per-dock/per-drone/per-month price, and does its Indian entity have
  any restriction on non-enterprise verticals? No public pricing exists.
- Can any DGCA type-certified Indian OEM drone (ideaForge, Marut, Garuda) be
  integrated with a third-party dock and a third-party autonomy platform? None
  of them publishes a cloud/OSDK equivalent to DJI's Cloud API, and none appears
  on FlytBase's supported-hardware list.
- Do MyGate and NoBrokerHood offer any partner API, and on what commercial
  terms? Neither publishes developer documentation; ADDA is the only one with a
  documented public API, and even ADDA lacks alert/notification/SOS/camera
  endpoints.
- What is the real willingness-to-pay of an Indian RWA managing committee for
  aerial security, and what is the decision process (AGM vote? managing
  committee? builder during handover?)? This needs primary field research — no
  secondary source exists.
- What third-party liability insurance is available in India for a drone
  operating over occupied dwellings, at what premium, and will insurers write it
  at all? The draft Civil Drone Bill makes insurance mandatory but the market is
  unquantified.
- How many days per year would a drone actually be grounded by weather in
  Mumbai, Bengaluru, Pune, Delhi and Chennai given a 0.25 in/hr rain limit, 9–12
  m/s wind limit and 40–50 °C thermal ceiling? Needs city-level IMD data
  modelling before any SLA is promised.
- What is the current price of the Hextronics Global and Eclipse and the Heisha
  DNEST series in 2026, landed in India including duty? All vendors are
  quote-only, and the Heisha figures found are stale and reseller-sourced.
- Is Sunflower Labs willing to enter India via a local partner, and would its
  Bee clear DGCA type certification? It ships to Argentina and Japan but not
  India, and the reason is unstated.
- Does Zuppa's indigenous autopilot have a documented API and DGCA-certified
  airframes it powers? The Zuppa site returned only a redirect and could not be
  read.
- What are Garuda Aerospace's, TSAW's and Asteria's actual security/surveillance
  DiaB roadmaps, if any? Absence of a public product is not proof of absence of
  a programme.

## Unverified or risky

The researcher could not confirm the claims below. They must not be relied on,
budgeted from, or quoted to a third party without independent verification.

- Sunflower Labs pricing tiers ($10,000–15,000 starter equipment for 4 acres,
  $400–700/month, $25,000–50,000+ for 10–30 acre estates, $5,000–10,000
  professional installation, ~$3,650/month for a 35-acre Hamptons example) come
  from a reseller/integrator blog (hteny.com), NOT from Sunflower. Sunflower's
  own site quotes only '$4-7/hr for continuous operations' on a lease model.
  Treat the tier figures as indicative only.
- The '$5,000 a month with a 24-month lease' figure for the Beehive comes from a
  reseller listing (Zions Security) that returned 403 on direct fetch and is
  inconsistent with Sunflower's own $4–7/hr framing. Do not rely on it.
- The Asylon 'DroneDog and DogHouse combo well over $150,000' figure is
  journalistic (Electrek, April 2026), not a vendor quote.
- The Percepto '$40,000–$250,000+' range comes from a third-party 2026 buyer's
  guide (thedroneu.com), not from Percepto. Percepto publishes no pricing.
- Heisha DNEST pricing (¥29,800 for the DNEST5 package; $4,880 for a
  hardware+software configuration) is from listings/blog content that predates
  2026 and could not be re-verified against Heisha's own quote sheet.
- References to 'FlytBase Pro at $99/month' and 'upgrade to low-cost
  Drone-in-a-Box systems for as little as $10,000' appear in aggregator content
  describing the older FlytNow-era product. FlytBase's own 2026 pricing page is
  a custom-quote form with no published tiers. Treat the $99 and $10,000 figures
  as STALE and do not budget from them.
- A search-result snippet described Nightingale Security as 'a Public Company'
  with 36 employees as of June 2026. This is Tracxn/aggregator data and is very
  likely a misclassification. Do not represent Nightingale as publicly listed.
- The DJI Dock 3 price of $15,890 is a US enterprise reseller (Advexure)
  listing. It is not a DJI list price, does not include the Matrice 4D/4TD
  aircraft, and is irrelevant to Indian landed cost because the hardware cannot
  legally be imported.
- Skydio Dock IP rating and backup-battery duration are NOT published on
  Skydio's technical-specs page. Do not assume an IP rating for it.
- The claim that India has exactly three DGCA-approved BVLOS corridors, and the
  24–48 hour / 7-day yellow-zone approval timelines, come from a commercial
  training-provider blog (zbotic.in), not from DGCA. Verify with DGCA before
  relying on any approval SLA.
- No verified evidence was found that ideaForge, Garuda Aerospace, Asteria
  Aerospace, Aereo, Skylark Drones, Marut Drones, NewSpace Research, TSAW or
  Zuppa sells a drone-in-a-box or autonomous docking product. This is absence of
  public evidence, not proof they have no such programme — several are
  defence-facing and may not publish.
- NxtQube's product specifications (80×85×65 cm station, nano/micro drones under
  2 kg, DJI Mavic 2 Pro compatibility) come from a directory listing and a
  YourStory article; the company's own site returned only a tagline and its
  pricing is entirely unknown. Its FY25 revenue of ₹26.5 lakh indicates a
  pre-scale company, so supply-chain and support risk is high.
- Easy Aerial SAMS-T specifications (24+ hours tethered endurance, 150/200/300
  ft cable, Alpine Swift / Albatross airframes, 40 lb ECTS) are drawn from a
  2020-era DroneDJ article, an AeroExpo listing and a 2022 brochure PDF. They
  were NOT re-verified against Easy Aerial's 2026 site and may be outdated.
- Skydio's India status is inferred from 2023–2024 partnership announcements
  with Aeroarc aimed at the Ministry of Defence. No 2025–2026 confirmation of
  Indian commercial availability, or of its absence, was obtainable.
- Society management app per-flat pricing (₹3–15/flat/month across MyGate,
  NoBrokerHood, ADDA and others) is from a single comparison blog
  (codingclave.com), which also markets a competing custom-build service. Verify
  directly with each vendor before using as a pricing anchor.
- MyGate's '25,000+ societies' figure is vendor marketing repeated by third
  parties and is not independently audited.
- Web search budget for this session was exhausted (200/200 calls) before
  Brinc/Paladin/Flyby pricing, the DGCA type-certified drone list, Zuppa, TSAW
  and Indian security-guard cost benchmarks could be fully researched. The
  Brinc, Paladin and Flyby entries above were recovered by direct site fetch;
  the remainder are genuine gaps, not omissions by judgement.
