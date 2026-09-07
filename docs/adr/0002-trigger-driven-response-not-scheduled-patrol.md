# 0002. Dispatch the drone on corroborated triggers, not on a patrol schedule

- **Status:** Accepted
- **Date:** 2026-09-07
- **Deciders:** Ramu Roy
- **Supersedes:** —
- **Superseded by:** —

## Context

The obvious design for "AI drone security for residential societies" is a drone
that flies a scheduled perimeter patrol — every 30 minutes, say — streaming video
to a detector. Every demo video in this category shows exactly that. It is also,
on the numbers, the wrong product.

**The coverage arithmetic.** A 5-acre society is ~20,234 m² with only ~600 m of
perimeter. A drone flying 12 sorties/day at 10 minutes each is airborne 8.3% of
the day, and ~6.5% after weather and kite-season groundings. Fixed cameras
bought for the same ₹5–7 lakh of capex cover 100% of the day — in rain, at
03:00, silently, without overflying anyone's balcony and without a single
regulatory approval. Per rupee of capex, the scheduled drone loses roughly
**12:1 on temporal coverage** at this site size.

The crossover where a drone starts winning is around **20–30 acres / 1.5+ km of
perimeter**, where trenching and PoE civils for an equivalent camera line run
₹25–45 lakh and the drone's marginal cost of covering more ground is near zero.

**The regulatory arithmetic makes it worse.** Three independent limits each bite
a *scheduled* patrol specifically:

- **Noise.** CPCB Noise Pollution (Regulation and Control) Rules 2000 set 55 dB(A)
  day and **45 dB(A) night (22:00–06:00)** in residential zones. Published
  measurements put a 0.74 kg Mavic at 46 dB at 30 m and a 2.85 kg Inspire at
  52 dB at 15 m. A 2 kg quad hovering near an occupied façade at night exceeds
  the night limit. A routine night patrol is not merely unpopular, it is
  non-compliant.
- **Battery physics.** At ~400 cycles to 80% state-of-health, 12 sorties/day
  consumes ~11 battery sets per year. Patrol frequency and battery opex are
  the same number.
- **Privacy.** Every scheduled overflight of a resident who has not consented is
  processing without a lawful ground (see [ADR-0006](0006-privacy-by-design-no-identifiable-data-by-default.md)).
  A patrol maximises exposure while the 91.7%-of-the-day gap means it is
  statistically unlikely to be airborne when anything actually happens.

**The willingness-to-pay arithmetic closes it.** A 300-flat society already
spends ₹3.3–3.9 lakh/month on security (~14 guards at ₹20,000–24,800 all-in
each, ≈₹1,100/flat/month), but its ceiling for a *new* technology line item is
₹20,000–60,000/month. Modelled cost-to-serve for a vendor-owned patrol service
is ₹4.7 lakh/year — ₹1,938 per flight hour against ₹96 per guard-hour. A
scheduled-patrol DaaS business is structurally unprofitable at the price the
buyer will actually pay.

So the honest conclusion is: **the drone is not a surveillance platform. It is a
response asset.** Its unique capability is not seeing continuously — cameras do
that better and cheaper — it is arriving somewhere in 40 seconds with a
steerable camera, over walls, at an angle no fixed mount can achieve.

## Options considered

### Option A — Scheduled perimeter patrol
The category default. Simple to build, easy to demo, immediately legible to a
buyer. Loses 12:1 on coverage economics, breaches night noise limits, maximises
privacy exposure, burns batteries proportional to schedule, and is airborne for
none of the 91.7% of the day when an incident is most likely.

### Option B — Drone only, dispatched on a single sensor trigger
Fixes the duty-cycle problem: the drone is idle until something happens. But a
single PIR or fence sensor in an Indian society fires constantly — cats, monkeys,
falling branches, wind on a gate. Launching on every one produces a drone that
is airborne more than a scheduled patrol, with worse noise timing (random, at
night) and a society that unplugs it in a week.

### Option C — Fixed AI cameras as the always-on layer; drone as verification and pursuit
Fixed cameras and a fence-sensor grid form the sensing layer that is always on
and legally uncontroversial. The drone launches only on a **corroborated**
trigger — two independent sensor classes agreeing, or one high-confidence
detection in a high-value zone — to do the things cameras cannot: get eyes on a
spot with no camera coverage, follow a moving subject across the property,
and put a steerable, well-lit view on an incident for a human to adjudicate.

Costs more to build (three subsystems, not one) and is harder to demo in a
30-second clip. But it is the configuration in which the drone's marginal
contribution is positive.

## Decision

**The drone dispatches on corroborated triggers. There is no patrol schedule.**

Concretely:

1. **Always-on layer** — fixed AI cameras plus a ₹60,000–1 lakh perimeter
   fence-sensor grid (ESP32 nodes; see `firmware/`). This layer, not the drone,
   is what provides 24/7 coverage and is what the customer is mostly buying.
2. **Corroboration gate** — a dispatch requires either (a) two independent
   sensor classes agreeing within a time window, or (b) one detection above a
   high confidence threshold inside a zone marked high-value. Single-sensor
   events raise a ticket; they do not launch an aircraft.
3. **Drone as response asset** — launches to a georeferenced point of interest,
   establishes a view, streams to the on-site console for human adjudication,
   and returns. Median expected dispatches: single digits per day, not 12
   scheduled sorties.
4. **Night dispatch is opt-in per society and off by default**, because of the
   45 dB(A) night limit. When enabled it is gated on a genuine corroborated
   alarm, which is defensible in a way a routine 02:00 patrol is not.
5. **One exception to "no schedule":** a single daily *dock self-test* sortie
   — a 90-second hop to verify the aircraft, the link, the camera and the
   precision-landing loop still work. This is maintenance, not surveillance,
   and it flies at a fixed daytime slot over the dock itself.

## Consequences

**Easier:** the noise, privacy, battery-life and unit-economics objections all
soften at once, because they are all functions of airborne time and this design
minimises airborne time by construction. The system also degrades gracefully —
if the drone is grounded by weather, the always-on layer is untouched and the
customer still has a working product. That is not true of a drone-only design.

**Harder:** we now build and integrate three subsystems instead of one, and the
demo is less immediately spectacular than a drone flying a lap. The corroboration
logic becomes a first-class piece of engineering with its own failure modes
(see the fusion service) rather than a `cron` entry.

**Committed to:** the sensing layer is the product's spine and the drone is a
peripheral. If a future decision reverses that — making the drone primary — the
economics above have to be re-derived, not assumed away.

**Revisit if:** we target sites above ~20–30 acres (townships, plotted
developments, industrial parks), where the coverage arithmetic inverts and a
scheduled patrol may genuinely beat trenching a camera line. The beachhead
segment named in the go-to-market is exactly those sites, so this is a likely
future ADR, not a hypothetical one.

## References

- CPCB Noise Pollution (Regulation and Control) Rules, 2000 — residential limits
  55 dB(A) day / 45 dB(A) night.
- Drone Rules 2021, Rule 44 (mandatory third-party insurance, Motor Vehicles Act
  1988 applied *mutatis mutandis*).
- Cost-to-serve and guard-cost modelling: `docs/research/unit-economics.md`.
