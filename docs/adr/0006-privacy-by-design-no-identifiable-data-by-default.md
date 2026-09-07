# 0006. Produce no identifiable personal data by default; the privacy map is both policy and runtime config

- **Status:** Accepted
- **Date:** 2026-09-07
- **Deciders:** Ramu Roy
- **Supersedes:** —
- **Superseded by:** —

## Context

Most surveillance products treat privacy as a policy layer bolted on after the
system works: a retention setting, a role check, a consent form in a drawer.
Indian law does not permit that here, for a specific and unusual reason.

**DPDP Act 2023 Section 7 is a closed list of nine "legitimate uses". There is no
legitimate-interest ground and no security-of-property ground.** This is the
single most consequential legal fact in the project, and it is where designs
copied from GDPR deployments break: a European system can process footage under
Article 6(1)(f) legitimate interest, balance it against data-subject rights, and
document the balancing test. India has no such provision. There is nothing to
balance, because there is no ground to balance with.

What remains is consent. And consent decomposes badly:

- **Residents** can consent — but being filmed is *not* "voluntary provision"
  under s.7(a), so it must be actual, informed, withdrawable consent.
- **An AGM or general-body resolution is necessary but not sufficient.** It is
  the property-governance authority to install anything in common areas under
  the society bye-laws. It is *not* data-protection consent, because each
  resident is an independent Data Principal. Both documents are required and
  they are different documents.
- **Visitors, delivery riders, domestic workers and passers-by cannot
  realistically consent at all.** There is no obtainable lawful ground for
  processing their identifiable data.

That last point is decisive. Since a meaningful fraction of the people a
security system sees can never lawfully be identified by it, **the only
defensible architecture is one that does not produce identifiable personal data
in the first place.** Privacy cannot be a setting; it has to be a property of
what the system is capable of emitting.

The surrounding exposure sharpens it further:

- **Overflight immunity is narrow.** BVA 2024 s.39 bars trespass and nuisance
  suits only "by reason only of the flight of aircraft over any property at a
  height which is reasonable" and for "the ordinary incidents of such flight".
  Low hovering to observe a neighbour's balcony is neither. The immunity never
  touches DPDP, BNS s.77, IT Act s.66E, or an Article 21 writ.
- **Camera direction is justiciable frame by frame.** The Calcutta High Court
  restrained residential cameras pointed into private interiors (*Shuvendra
  Mullick*, 2025 SCC OnLine Cal 1245; SLP dismissed by the Supreme Court on
  9 May 2025), while the Kerala High Court declined removal where no snooping
  was proved (2025:KER:85261). The distinction the courts draw is what the
  camera *looks at*, not whether surveillance in general is permitted.
- **Criminal exposure attaches to the individual pilot.** BNS 2023 s.77
  (voyeurism) is a **cognizable** offence — arrest without warrant — carrying
  1–3 years on first conviction and 3–7 subsequently. An FIR under IPC s.447
  (criminal trespass) was registered against a licensed *research* drone that
  merely drifted, with no damage, no injury and no landowner complaint (Crime
  No. 24/2026, PS Doddaballapura Rural; stayed and allowed, Karnataka HC W.P.
  No. 3862/2026).
- **CERT-In's 28 April 2022 Directions bind today**, years before DPDP's
  substantive obligations. Annexure I explicitly names **Drones (xix)**, IoT
  (xiii), AI/ML (xx) and data breach (xi) as reportable within **six hours**,
  with ICT logs retained 180 days **within Indian jurisdiction**, clocks synced
  to NIC or NPL NTP, and a Point of Contact filed. Non-compliance is actionable
  under IT Act s.70B(7).
- **The Drone Rules 2021 contain no privacy provision at all.** DGCA
  authorisation to fly is not authorisation to process personal data. These are
  two entirely separate compliance tracks and clearing one says nothing about
  the other.

One widespread vendor claim is simply wrong and worth recording so we do not
repeat it: **DPDP has no "sensitive personal data" category.** The SPDI Rules
2011 do classify biometric information as sensitive, and they remain in force
until 13 May 2027, when DPDP s.44(2) omits IT Act s.43A. Anything shipped before
that date sits under both regimes at once.

## Options considered

### Option A — Record everything, restrict access by role
The industry default. Full-fidelity footage retained, RBAC on playback,
retention timer. Under Indian law this produces identifiable personal data about
people who cannot consent, from the moment the encoder runs. Access control does
not cure the absence of a processing ground. Rejected.

### Option B — Redact at rest, on ingest to the edge node
Better: identifiable frames exist only transiently. But they still exist, on the
aircraft and on the wire, and the aircraft is the component most likely to be
lost, stolen or physically recovered by an adversary. Rejected as insufficient.

### Option C — Redact on-device at the encoder; identifiable data is never produced
Face and licence-plate regions are blurred in the encode path on the companion
computer, before any frame is written to storage or transmitted. Detection is
**class-level** (person / vehicle / animal) rather than identity-level. Raw
footage is unlocked only per-incident through a two-person, ticketed, fully
audited workflow.

Costs compute in the tightest budget in the system and means the default
recording is genuinely less useful for after-the-fact investigation. Accepted
anyway — it is the only option where the system's normal operating output is
lawful for every person it sees.

## Decision

**The system produces no identifiable personal data by default. Identification is
an exceptional, audited, per-incident unlock — never an operating mode.**

### 1. On-device redaction at the encoder
Face and plate regions are blurred on the companion computer in the encode path,
before storage or transmission. Detection classes are person / vehicle / animal.
No identity is computed, stored or transmitted in normal operation.

### 2. No face recognition in v1
FRT is not banned in India and no state restricts private use, but a drone doing
1:N recognition over a society builds biometric templates of everyone it sees,
with no s.7 ground for any of them and no Indian equivalent of GDPR Art. 9(2).
(The EDPB reaches the same conclusion on the European side — Guidelines 3/2019,
para 84.) This is independently required by the licence position in
[ADR-0004](0004-rf-detr-over-ultralytics-yolo.md); two independent arguments,
same answer.

### 3. The privacy map is a single artefact that is simultaneously the legal
### annexure and the runtime configuration

This is the load-bearing engineering idea in this ADR.

A **signed, versioned 3D privacy map** — GeoJSON polygons plus altitude bands
for the society boundary and for every registered private aperture (window,
balcony, private door, terrace) — is:

- the **annexure to the RWA's written privacy policy**, the document residents
  are shown and the general body approves; and
- the **runtime configuration** that hard-slaves the gimbal and the shutter.

One artefact, one version number, one signature. It is therefore impossible for
the deployed behaviour to drift from the approved policy, because they are the
same file. When a resident registers a new balcony, the policy annexure and the
gimbal constraint update in the same commit, signed, with an audit trail.

The runtime enforcement is **fail-closed**: on stale pose, degraded GNSS, or a
signature that does not verify, the shutter closes and the gimbal returns to a
safe stow attitude. Degraded state means *less* capability, never more.

### 4. Two-person incident unlock
Raw, unredacted footage for a specific incident is released only via a ticketed
workflow requiring two distinct authenticated approvers, with the reason,
requester, approver, time window and exported artefact recorded in an
append-only audit log.

### 5. Compliance obligations wired into the system, not a checklist
- **CERT-In:** six-hour incident reporting path for drone / IoT / AI / breach
  categories; 180-day ICT log retention **inside Indian jurisdiction**; NTP
  synced to NIC or NPL; Point of Contact on file. These are live obligations
  today, not 2027 obligations.
- **DPDP s.8(2):** a written Data Processor contract is mandatory. The RWA
  cannot discharge liability by pointing at our software.
- **Grievances:** published contact for Data Principal queries; 90-day response
  (one month while the SPDI Rules 2011 remain in force to 13 May 2027).
- **Consent withdrawal must be as easy as granting it**, and security coverage
  must never be made conditional on consenting to non-essential processing —
  pay-to-opt-out invalidates free consent.
- **Notice before entry:** signage reaching a person *before* they enter the
  monitored area, at roughly eye level, describing the area covered well enough
  that they can avoid it.
- **Any analytics feature defaults OFF** and is enabled only by a separate,
  knowingly taken general-body resolution with its own documented safeguards —
  never bundled with a hardware upgrade.

### 6. Compliance timeline is tracked, because it moves
DPDP Rules 2025 (G.S.R. 846(E), 13 Nov 2025) commence in phases: Rules 1, 2 and
17–21 immediately; Rule 4 on **13 Nov 2026**, when the Data Protection Board
gains penalty powers; the substantive Rules 3, 5–16, 22–23 and DPDP ss. 3–17 on
**13 May 2027**. From that date every personal data breach is notifiable with no
materiality threshold — affected Data Principals and the Board without delay,
detailed report within 72 hours, up to ₹200 crore, and up to ₹250 crore for
failure of reasonable security safeguards.

## Consequences

**Easier:** the system's normal output is lawful with respect to every person it
observes, including the ones who could never have consented. The privacy map
collapses a whole class of policy-versus-implementation drift bugs into a
non-problem. Audit and DPIA are largely a matter of exporting artefacts the
system already maintains.

**Harder:** on-device redaction costs compute in the tightest budget in the
system, and the default recording is genuinely less useful for investigation —
which is a real product cost we are choosing to pay. The two-person unlock adds
operational friction at exactly the moment a customer is most stressed. The
privacy map needs a maintenance workflow (residents move, balconies get
enclosed) that is now a product surface rather than a config file.

**Committed to:** identification is never a default, a toggle, or a "pro tier".
Any feature request that would have the system routinely emit identifiable data
is out of scope under this ADR, not a backlog item.

**Revisit if:** DPDP is amended to add a legitimate-interest or property-security
ground (this would be a substantial change and is not currently proposed), or
when the 13 May 2027 phase lands and the SPDI Rules 2011 fall away — at which
point the dual-regime analysis simplifies and this ADR should be re-read rather
than assumed still accurate.

## References

- DPDP Act 2023, s. 7 (closed list of legitimate uses), s. 8(2), s. 44(2).
- DPDP Rules 2025, G.S.R. 846(E), notified 13 Nov 2025 — phased commencement.
- CERT-In Directions, 28 April 2022, Annexure I items (xi), (xiii), (xix), (xx); IT Act s. 70B(7).
- BVA 2024, s. 39; BNS 2023, s. 77; IT Act 2000, s. 66E.
- *Shuvendra Mullick*, 2025 SCC OnLine Cal 1245 (SLP dismissed, SC, 9 May 2025); Kerala HC 2025:KER:85261.
- Karnataka HC W.P. No. 3862/2026 (Crime No. 24/2026, PS Doddaballapura Rural).
- EDPB Guidelines 3/2019, para 84.
- Full analysis: `docs/research/privacy-law.md`.
