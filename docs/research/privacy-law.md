# Privacy & Data Protection Law

> Research note for [AEGIS](../../README.md). Compiled 2026-09-07 from a multi-agent
> web research sweep. Every claim below is sourced; confidence levels are the
> researcher's own and are preserved verbatim.

## Summary

India's DPDP Act 2023 is now fully notified: the DPDP Rules 2025 (G.S.R. 846(E),
13 Nov 2025) commence in three phases — Rules 1,2,17-21 immediately, Rule 4 on
13 Nov 2026 (when the Data Protection Board also gets penalty powers), and the
substantive Rules 3, 5-16, 22-23 plus DPDP Sections 3-17 on 13 May 2027. The
single most consequential fact for this project is that Section 7 of the DPDP Act
is a CLOSED list of nine "legitimate uses" with no GDPR-style legitimate-interest
ground and no "security of property" ground — so a society that records
identifiable residents has, in practice, only consent, and being filmed is not
"voluntary provision" under Section 7(a). That in turn means an AGM or
general-body resolution is necessary (it is the property/governance authority to
install under society bye-laws) but is legally NOT sufficient as data-protection
consent; each resident is an independent Data Principal and Indian commentary is
consistent that a general-body approval "is not a substitute for individual
consent". Consent from visitors, delivery riders, domestic workers and passers-by
is practically unobtainable, so the only defensible architecture is one where the
drone does not produce identifiable personal data by default: on-device face and
licence-plate redaction at the encoder, class-level person/vehicle detection
instead of identification, and a two-person, ticketed, fully audited workflow to
unlock raw footage for a specific incident. Face recognition is the sharpest risk
— it is not banned in India and no state restricts private FRT, but a drone doing
FRT in an "uncontrolled environment" builds biometric templates of everyone it
sees, which the EDPB holds unlawful without an Article 9 exception for every
person captured (Guidelines 3/2019, para 84), and in India there is no Section 7
basis at all; note also that DPDP has no "sensitive data" category (a widespread
vendor error), while the still-in-force SPDI Rules 2011 do classify biometric
information as sensitive until DPDP s.44(2) omits IT Act s.43A on 13 May 2027. On
overflight: BVA 2024 Section 39 bars trespass/nuisance suits only "by reason only
of the flight of aircraft over any property at a height ... which ... is
reasonable, or by reason only of the ordinary incidents of such flight" — low
hovering to look into a neighbour's balcony is neither, and Indian courts have
already restrained residential cameras that stare into private interiors
(Calcutta HC, Shuvendra Mullick, 2025 SCC OnLine Cal 1245, SLP dismissed by SC
9 May 2025) while refusing removal where no snooping is proved (Kerala HC,
2025:KER:85261). Criminal exposure sits in BNS s.77 (voyeurism, 1-3 years first
conviction, cognizable) and IT Act s.66E, both of which are triggered by
aperture-level capture, not by patrolling as such. Operationally, CERT-In's
28 Apr 2022 Directions are the nearest-term binding obligation: Annexure I item
(xix) explicitly names **Drones** (and (xiii) IoT, (xx) AI/ML, (xi) Data Breach)
as mandatorily reportable within **6 hours**, with ICT logs kept 180 days
**within Indian jurisdiction** — this applies today, years before DPDP's May 2027
substantive obligations. The deliverable a builder should ship is a signed,
versioned 3D "privacy map" (GeoJSON polygons + altitude bands for every
registered private aperture and the society boundary) that is simultaneously the
annexure to the RWA's written policy and the runtime config that hard-slaves the
gimbal and shutter — fail-closed on stale pose or degraded GNSS.

## Hard constraints

- **No legitimate-interest basis exists in Indian law.** DPDP Section 7 is a
  closed list of nine legitimate uses and none of them covers protecting private
  property or common-area security. You cannot copy a GDPR Article 6(1)(f)
  justification into an Indian deployment.
- **Being filmed is not "voluntary provision" under Section 7(a).** For residents,
  consent is the operative basis; for visitors, delivery riders, domestic workers
  and passers-by there is no obtainable basis at all, so the system **must not**
  produce identifiable data about them.
- An AGM or general-body resolution **CANNOT** serve as data-protection consent for
  individual residents. It is still **REQUIRED** as the property/governance
  authority to install anything in common areas under the society's bye-laws. You
  need both, and they are different documents.
- **Consent withdrawal must be as easy as granting it**, and security coverage
  cannot be made conditional on consenting to non-essential processing.
  Pay-to-opt-out invalidates free consent.
- **A drone must not run 1:N face recognition over a residential society.** Every
  non-consenting person captured is templated, and there is no Section 7 ground
  and no Indian equivalent of a GDPR Article 9(2) exception available to a private
  RWA.
- **Cameras must never be pointed into private interiors, windows, balconies or
  private doors.** Indian courts have restrained specific cameras on exactly this
  basis (Calcutta HC 2025 SCC OnLine Cal 1245, SLP dismissed by the Supreme Court
  9 May 2025), and camera direction is justiciable frame by frame.
- **Notice must reach a person BEFORE they enter the monitored area**, positioned
  at roughly eye level, and must let them estimate which area is captured so they
  can avoid it or adapt their behaviour.
- **CERT-In Directions of 28 April 2022 apply NOW, not from 2027.** Qualifying
  incidents — drones (Annexure I item xix), IoT (xiii), AI/ML (xx), data breach
  (xi), data leak (xii) — must be reported within 6 hours; ICT logs must be kept
  for a rolling 180 days WITHIN Indian jurisdiction; clocks must be synced to NIC
  or NPL NTP; a Point of Contact must be filed with CERT-In. Non-compliance
  attracts action under IT Act s.70B(7).
- **From 13 May 2027 every personal data breach is notifiable with no materiality
  threshold**: intimate affected Data Principals and the Board without delay, then
  a detailed report to the Board within 72 hours. Failure carries up to Rs 200
  crore; failure of reasonable security safeguards carries up to Rs 250 crore.
- **A written contract with any Data Processor is mandatory under DPDP s.8(2).**
  The RWA cannot discharge liability by pointing at the vendor's app or VMS.
- **Contact details of the person who answers Data Principal questions must be
  published**; grievances must be answered within 90 days (one month while the
  SPDI Rules 2011 remain in force, i.e. until 13 May 2027).
- **The Drone Rules 2021 contain no privacy provision.** DGCA authorisation to fly
  is not authorisation to process personal data; the two compliance tracks are
  entirely separate.
- BVA 2024 Section 39 immunity from trespass and nuisance suits extends **ONLY** to
  flight "at a height above the ground which ... is reasonable" and to "the
  ordinary incidents of such flight". Low hovering to observe a neighbouring
  property is outside it, and the immunity never touches DPDP, BNS s.77, IT Act
  s.66E, or an Article 21 writ.
- BNS 2023 Section 77 (voyeurism) is a **COGNIZABLE** offence — police can arrest
  the operator without a warrant. Capture of a woman in a private act where she has
  a reasonable expectation of privacy carries 1-3 years on first conviction and
  3-7 years subsequently. This attaches to the individual pilot, not only to the
  society.
- **The SPDI Rules 2011 remain in force until 13 May 2027 and DO classify biometric
  information as sensitive personal data.** Anything shipped before that date sits
  under both regimes simultaneously. The common vendor claim that the DPDP Act
  itself treats biometrics as "sensitive personal data" is factually wrong — DPDP
  has no sensitive-data category.

## Findings

### DPDP Act 2023 and Rules 2025 — the statutory frame

- **DPDP Rules 2025 are notified and commence in three phases; the substantive
  compliance obligations bite on 13 May 2027, and the Data Protection Board's
  penalty powers on 13 Nov 2026.** — Gazette Notification G.S.R. 846(E) dated
  13 November 2025 (published 14 Nov 2025) under s.40 of the DPDP Act 2023;
  23 rules and 7 schedules. Phase 1 (13 Nov 2025): Rules 1, 2, 17-21 + DPDP
  ss.1, 2, 18-26, 35, 38-43, 44(1), 44(3). Phase 2 (13 Nov 2026): Rule 4 (Consent
  Manager registration) + ss.27-28 (Board enforcement), ss.29-34
  (penalties/appeals), ss.36, 37, 1(3). Phase 3 (13 May 2027): Rules 3, 5-16,
  22-23 + ss.3-17 (notice, consent, Data Fiduciary duties, Data Principal rights)
  and s.44(2). No grace period after Phase 3.
  [source](https://www.vratex.com/dpdp-act/dpdp-rules-2025-timeline)
- **DPDP Act Section 7 is a closed list of legitimate uses containing NO
  legitimate-interest ground and NO security-of-property ground. Consent is the
  only realistic lawful basis for filming residents.** — Section 7 clauses:
  (a) purpose for which the Data Principal voluntarily provided her personal data
  and has not indicated non-consent; (b) State subsidies/benefits/services;
  (c) State functions / sovereignty / security of the State; (d) statutory
  disclosure obligations; (e) court orders/decrees; (f) medical emergency;
  (g) epidemic/public-health threat; (h) disaster or breakdown of public order
  (Disaster Management Act 2005); (i) employment purposes or safeguarding the
  employer from loss/liability incl. trade secrets. Nothing covers protecting
  private property or common-area security. Clause (i) can arguably cover the
  society's OWN employees (guards, housekeeping), never residents or visitors.
  Being recorded by a camera is not "voluntarily provided" under 7(a).
  [source](https://www.dpdpa.com/dpdpa2023/chapter-2/section7.html)
- **Linklaters confirms India adopts a consent-centric model with no standalone
  legitimate-interest ground, and confirms the penalty schedule and phased
  dates.** — Consent must be "free, specific, informed, unconditional and
  unambiguous" with "clear affirmative action". Notices must be offered in English
  or an Eighth Schedule language. Breach notification: notify Board and affected
  individuals without delay + 72-hour detailed report to the Board (extensible),
  with NO materiality threshold — every breach is notifiable. Non-SDFs need not
  appoint a DPO but must designate a person to answer Data Principal questions and
  publish contact details; only SDFs need an India-based DPO. No right to data
  portability; no right to be forgotten (only erasure post-May 2027).
  [source](https://www.linklaters.com/en/insights/data-protected/data-protected---india)
- **Penalty Schedule to DPDP s.33: up to Rs 250 crore for failure to take
  reasonable security safeguards; Rs 200 crore for failure to notify a breach;
  Rs 50 crore residual.** — Schedule entries: s.8(5) reasonable security
  safeguards breach - Rs 250 crore; s.8(6) failure to notify Board/affected Data
  Principals - Rs 200 crore; s.9 children's data - Rs 200 crore; s.10 SDF
  obligations - Rs 150 crore; s.15 Data Principal duties - Rs 10,000; breach of
  voluntary undertaking (s.32) - amount of the original breach; any other
  contravention - Rs 50 crore. Board weighs six factors under s.33(2) and may
  escalate under s.33(3). Penalties are fixed-rupee, not turnover-linked.
  Enforceable from 13 Nov 2026. [source](https://www.dpdpa.com/theschedule.html)
- **DPDP Rules 2025 prescribe concrete technical controls (Rule 6), a two-tier
  breach process (Rule 7), a 1-year log floor, and a 90-day grievance outer limit
  (Rule 14).** — Rule 6 reasonable security safeguards: encryption / obfuscation /
  masking / virtual tokens; access control; logging, monitoring and review to
  detect unauthorised access; retention of logs and personal data for at least one
  year; business continuity and backups; contractual security obligations flowed
  down to Data Processors. Rule 7: intimate affected Data Principals and the Board
  "without delay" with a description, then a detailed report to the Board within
  72 hours covering nature, extent, timing, location, likely impact, remedial
  measures and the intimations given. Rule 8(3): retain personal data, associated
  traffic data and other logs for at least one year from processing before
  erasure. Rule 13(3): SDFs must verify that algorithmic software poses no risk to
  Data Principals; Rule 13(4): SDFs may not transfer specified traffic data
  outside India; SDFs owe annual DPIA + audit. Rule 14(3): respond to Data
  Principal requests / grievances within 90 days. Board investigations: 6 months,
  extendable by 3.
  [source](https://ssrana.in/articles/meity-notifies-final-digital-personal-data-protection-rules-2025/)
  *(likely)*
- **DPDP has no "sensitive personal data" category, but the SPDI Rules 2011 (which
  DO classify biometric information as sensitive) remain in force until 13 May
  2027.** — "The 2011 SPDI Rules defined sensitive personal data or information
  including passwords, financial information, health data and biometrics. The DPDP
  Act does not replicate that category; all personal data carries the same base
  obligations." The SPDI Rules die only when DPDP s.44(2) omits IT Act s.43A —
  scheduled for 13 May 2027. Until then both regimes co-exist, so a
  face-recognition deployment launched in 2026 is simultaneously exposed to
  SPDI-style written-consent/ISO-27001-grade-security expectations AND the
  incoming DPDP regime. Vendor marketing claiming "facial biometrics are sensitive
  personal data under the DPDP Act" is wrong on the statute.
  [source](https://opsiocloud.com/in/knowledge-base/are-spdi-rules-still-in-force/)

### Who carries the obligation: the RWA as Data Fiduciary

- **The RWA / Managing Committee is the Data Fiduciary; the drone vendor and the
  community app are Data Processors, and a general-body resolution does NOT
  constitute individual consent.** — "Under the DPDP Act, such approvals are not a
  substitute for individual consent. Each resident is a data principal with an
  independent right to decide whether their personal data can be used for
  non-essential purposes." Separately: "An AGM resolution does not count as consent
  from individual residents" — consent must be clear, specific, documented and
  freely given. "Pay-to-opt-out" models invalidate free consent. Responsibility
  stays with the RWA even when a vendor's app/VMS does the processing; DPDP s.8(2)
  requires a valid contract with any Data Processor.
  [source](https://www.outlookindia.com/brand-studio/realty-mirror/torbit-regulation-monitor-what-dpdp-act-changes-for-rwas-and-housing-societies)
  *(likely)*
- **Section 3(c)(ii) "publicly available data" exemption does not save common-area
  surveillance, and the personal/domestic exemption is unavailable to an
  association.** — DPDP does not apply to personal data "made publicly available by
  data principals voluntarily or made available by any other person who is under an
  obligation under Indian law to make such personal data publicly available" —
  walking through a lobby is neither. The Act also does not apply to processing
  "for any personal or domestic use", but that is framed around an individual; an
  RWA/managing committee acting for the society is an organisation determining
  purpose and means, i.e. a Data Fiduciary. This mirrors CJEU Ryneš, where the
  household exemption was read narrowly and did not cover a camera partially
  covering public space or neighbouring property.
  [source](https://cms-induslaw.com/en/ind/publication/faqs-on-the-digital-personal-data-protection-act-and-rules)
  *(likely)*
- **Grievance response outer limit is 90 days, and contact details of the person
  answering Data Principal questions must be published prominently.** — Rule 14(3)
  / DPDP: "respond to grievances within a reasonable period not exceeding 90
  (ninety) days". Organisations "may designate a grievance officer" — the Rules do
  not mandate qualifications or a full-time role for non-SDFs, but contact details
  must be "prominently displayed". Under the still-in-force SPDI Rules 2011 a
  grievance officer must redress discrepancies within one month, so until 13 May
  2027 the shorter one-month clock is the safer internal SLA.
  [source](https://cms-induslaw.com/en/ind/publication/faqs-on-the-digital-personal-data-protection-act-and-rules)
  *(likely)*

### Facial recognition and biometrics

- **There is no Indian statute authorising or restricting private facial
  recognition, and no state-level ban was found. Regulation rests on
  constitutional privacy doctrine and DPDP consent.** — "There is no Act of
  parliament which allows the police, railways, or temple trusts to operate live
  facial recognition on the public" — regulation relies on scattered executive
  orders and court directives. IFF's Project Panoptic (started 2020) had recorded
  120+ government FRT contracts by 2024; an IFF CIC second appeal established there
  is no rule governing FRT use, no privacy impact assessment was ever done, and an
  80% similarity score was treated as a positive match. Puttaswamy four-part test:
  (1) legality — action must rest on valid law, not executive order; (2) legitimate
  aim; (3) proportionality / rational nexus; (4) procedural safeguards against
  misuse. DPDP s.17(2)(a) lets the Centre exempt State instrumentalities — that
  exemption is unavailable to a private RWA, which therefore has NO carve-out.
  [source](https://www.barandbench.com/columns/surveillance-without-statute-the-constitutional-void-in-indias-facial-recognition-policy)
- **EDPB para 84: a facial-recognition system running in an "uncontrolled
  environment" needs a lawful exception for EVERY person it captures, not just for
  the enrolled ones — which makes drone-borne FRT over a society effectively
  unlawful.** — Para 84: "the system involves capturing on the fly the faces of any
  individual passing in the range of the camera, including persons who have not
  consented to the biometric device, and thereby creating biometric templates ...
  Since the purpose is to uniquely identify natural persons, an exception under
  Article 9(2) GDPR is still needed for anyone captured by the camera." The
  concert-hall example requires "clearly separated entrances; one with a biometric
  system and one without ... installed and made accessible in a way that prevents
  the system from capturing biometric templates of non-consenting spectators."
  Para 86: an alternative non-biometric route must be offered without cost or
  restraint. Para 87-90: templates must be minimal and non-transferable across
  systems, stored on a device under the user's control or encrypted with a
  user-held key, biometric templates and raw/identity data kept in distinct
  databases, external access to biometric data prohibited, and raw face images
  deleted once there is no lawful basis. Direct India read-across: because DPDP s.7
  has no equivalent of Art 9(2) grounds and no legitimate interest, a drone doing
  1:N face matching against a resident gallery has NO available lawful basis for
  the non-consenting people it templates.
  [source](https://www.edpb.europa.eu/system/files/documents/files/file1/edpb_guidelines_201903_video_devices_en_0.pdf)

### Case law: camera direction is justiciable

- **Kerala High Court 2025: a neighbour's CCTV will not be ordered removed absent
  proof of actual snooping; privacy and the security limb of Article 21 must be
  "balanced delicately".** — Sivasankaran @ Sankarankutty & Anr v State of Kerala &
  Ors, 2025:KER:85261, W.P.(C) No. 8754 of 2025, N. Nagaresh J. Judgment text:
  "Right to privacy can only be validly abridged if the test of proportionality is
  satisfied, as has been held by the Hon'ble Apex Court in ... K.S. Puttaswamy
  (Retired) and another v. Union of India and another [(2019) 1 SCC 1]." And:
  "Right to privacy of one and the right to security which is an element of right
  to life of another, are to be balanced delicately when they are in conflict with
  each other." Operative: "unless there is an established case of snooping into the
  affairs of the petitioners, there cannot be a direction to respondents 5 to 7 to
  remove the CCTV Cameras. The writ petition fails and it is hence dismissed."
  Petitioners had filed photographs of the camera taken from their dining room and
  bedroom (Exhibit P2) and it still failed.
  [source](https://images.assettype.com/barandbench-kannada/2025-11-16/h0lrtrpn/Sivasankaran___Sankarankutty_vs_State_of_Kerala___ors.pdf)
- **Calcutta High Court 2025 restrained cameras that covered a co-occupant's
  residential portion; the Supreme Court declined to interfere.** — Shuvendra
  Mullick v. Indranil Mullick, 2025 SCC OnLine Cal 1245, DB (Sabyasachi
  Bhattacharyya and Uday Kumar JJ), 10 February 2025. Nine dome cameras with motion
  detection installed in 2022 across common and residential areas; five (nos. 5,
  10, 11, 12, 13) focused on the appellant's allocated portion including his
  bedroom. Held: "Continuous recording of activities of appellant in the internal
  area of his dwelling house is violating his privacy. The dignity, autonomy and
  identity of an individual shall be respected and cannot be violated." Those five
  cameras were restrained. SLP(C) 12384/2025 dismissed by the Supreme Court on
  9 May 2025 (Dipankar Datta and Manmohan JJ). Practical rule for the drone build:
  the direction and coverage of individual cameras is separately justiciable — a
  system can be lawful in aggregate and unlawful camera-by-camera / frame-by-frame.
  [source](https://www.scconline.com/blog/post/2025/02/12/installing-cctv-private-residential-space-without-cooccupant-consent-violates-privacy-calcutta-high-court-legal-news/)
  *(likely)*
- **CJEU C-708/18 (TK) is the closest EU analogue: apartment-block common-area CCTV
  must rest on a "present and effective" interest, be "strictly necessary", and
  survive a less-intrusive-alternatives test.** — Three cameras in the common areas
  of a residential building against vandalism/burglary; one flat owner objected.
  Court held the interest must be present and effective, not hypothetical (prior
  thefts and vandalism sufficed); processing must be "strictly necessary" and not
  "reasonably ... as effectively achieved by other means less restrictive of
  fundamental freedoms"; proportionality assessment must consider data minimisation
  and operational alternatives such as limiting operating hours or obscuring
  images. Consent of the data subject was not required because Art 7(f) (legitimate
  interest) applied — which is precisely the ground India does NOT have. Judgment
  11 December 2019. Companion precedent: C-212/13 Ryneš (11 Dec 2014) — the
  household exemption is narrow and does not cover a camera that even partially
  covers public space or neighbouring property.
  [source](http://eulawanalysis.blogspot.com/2019/12/video-surveillance-in-flats-and-data.html)

### Aviation, drone-specific and criminal law

- **Bharatiya Vayuyan Adhiniyam 2024 s.39 bars trespass/nuisance suits ONLY for
  flight at a reasonable height and the ordinary incidents of flight — it does not
  immunise surveillance or low hovering.** — Verbatim s.39 (Bar of certain suits):
  "No suit shall be brought in any civil court in respect of trespass or in respect
  of nuisance by reason only of the flight of aircraft over any property at a
  height above the ground which having regard to wind, weather and all the
  circumstances of the case is reasonable, or by reason only of the ordinary
  incidents of such flight." This re-enacts Aircraft Act 1934 s.17. BVA 2024
  s.2(3): "'aircraft' means any machine that can derive support in the atmosphere
  from reactions of the air, other than reactions of the air against the earth's
  surface" — a multirotor is an aircraft, so the bar can apply. BVA 2024 (Act 16 of
  2024) received assent 11 Dec 2024, commenced 1 Jan 2025. Two limits matter: "by
  reason only of the flight" excludes a nuisance claim founded on deliberate
  observation, and hovering at low altitude over a neighbour is not flight "at a
  reasonable height".
  [source](https://www.linkinglaws.com/assets/pdf/bareacts/604.pdf)
- **The Drone Rules 2021 contain no privacy provision at all — the predecessor UAS
  Rules 2021 (revoked) did, and it was dropped.** — Academic analysis: "'privacy'
  is absent in the amended 2021 Rules"; the earlier UAS Rules 2021 required
  operators to "protect the privacy of a person and their property by adopting
  suitable procedures" but lacked specifications. Consequence: a DGCA-legal flight
  is not a DPDP-legal processing operation. As one Indian firm puts it, "A lawful
  flight authorization doesn't equate to compliant data processing."
  Recommendations in the literature: adopt Puttaswamy
  legality/necessity/proportionality, mandate DPIAs and privacy-by-design, define
  storage limits and consent mechanisms.
  [source](https://ijpiel.com/index.php/2022/10/07/drone-laws-of-india-off-to-a-flying-start/)
  *(likely)*
- **Criminal exposure: BNS 2023 s.77 (voyeurism) and IT Act s.66E are triggered by
  aperture-level capture, and both are individually chargeable against the
  pilot/operator, not just the society.** — BNS s.77 criminalises watching or
  capturing the image of a woman engaged in a private act in a place where she
  would reasonably expect privacy, without consent, and dissemination of such
  images. First conviction: 1-3 years + fine; subsequent: 3-7 years + fine.
  Cognizable — police may arrest without warrant and investigate without
  magistrate's permission. It is gender-specific. BNS s.78 covers stalking
  including monitoring a woman. IT Act s.66E is gender-neutral and covers
  intentional capture/publication of an image of a "private area" without consent
  under circumstances violating privacy. A drone-specific legal analysis notes
  these operate on intent, circumstances and effect rather than creating any
  blanket aerial-recording ban.
  [source](https://www.sigmachambers.in/post/privacy-laws-drone-companies-india-dpdp)
  *(likely)*

### Incident reporting: CERT-In binds today

- **CERT-In Directions of 28 April 2022 expressly list DRONES as a mandatorily
  reportable incident category within 6 hours, and require 180-day ICT log
  retention inside India. This binds today, years before DPDP's May 2027
  obligations.** — Direction (ii): "shall mandatorily report cyber incidents as
  mentioned in Annexure I to CERT-In within 6 hours of noticing such incidents"
  (incident@cert-in.org.in; 1800-11-4949). Annexure I item (xix) covers "Attacks
  or malicious/suspicious activities affecting
  systems/servers/networks/software/applications related to Big Data, Block chain,
  virtual assets ... Robotics, 3D and 4D Printing, additive manufacturing,
  Drones"; item (xiii) IoT devices; item
  (xx) AI and Machine Learning systems; items (xi) Data Breach and (xii) Data Leak.
  Direction (i): sync all ICT clocks to NIC or NPL NTP servers. Direction (iii):
  designate a Point of Contact (Annexure II format) to interface with CERT-In.
  Direction (iv): "mandatorily enable logs of all their ICT systems and maintain
  them securely for a rolling period of 180 days and the same shall be maintained
  within the Indian jurisdiction." Non-compliance attracts punitive action under IT
  Act s.70B(7).
  [source](https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf)

### Design bar: redaction, retention, policy and what vendors ship

- **Drone footage is personal data only where an individual is identifiable — which
  makes resolution, angle and repeated observation design levers, and makes
  "filming in public" NOT a Section 3(c)(ii) exemption.** — "Drone footage is
  personal data only where an individual is identifiable by or in relation to it
  ... Resolution, angle, and repeated observation all factor into this
  determination." Critically: "filming in public doesn't automatically qualify
  footage as 'publicly available' under the law's exclusions." The EDPB reaches the
  same conclusion for special-category data at para 70 of Guidelines 3/2019: "The
  mere fact of entering into the range of the camera does not imply that the data
  subject intends to make public special categories of data relating to him or
  her." There is no bystander-consent exemption in DPDP; the recommended
  mitigations are field-of-view restrictions, altitude limits, resolution controls,
  geofenced camera restrictions and early-stage blurring of faces and plates.
  [source](https://www.sigmachambers.in/post/privacy-laws-drone-companies-india-dpdp)
  *(likely)*
- **EDPB Guidelines 3/2019 give the concrete design bar: erase footage after a few
  days (beyond 72 hours needs justification), mask irrelevant areas, and DEACTIVATE
  unnecessary camera functions such as unlimited movement, zoom and audio.** —
  Para 121: "the personal data should in most cases (e.g. for the purpose of
  detecting vandalism) be erased, ideally automatically, after a few days. The
  longer the storage period set (especially when beyond 72 hours), the more
  argumentation for the legitimacy of the purpose and the necessity of storage has
  to be provided." Example given: 24 hours sufficient for a small shop. Para 129:
  "systems that allow masking or scrambling areas that are not relevant for the
  surveillance ... On the other hand, the selected solutions should not provide
  functions that are not necessary (e.g., unlimited movement of cameras, zoom
  capability, radio transmission, analysis and audio recordings). Functions
  provided, but not necessary, must be deactivated." Para 113: signage positioned
  so the data subject recognises the surveillance before entering the monitored
  area, approximately at eye level, and "must be able to estimate which area is
  captured by a camera so that he or she is able to avoid surveillance or adapt his
  or her behaviour". Para 103: irreversible blurring counts as erasure. Para 28
  example: "cameras should only be filming the premises itself because it is not
  necessary to watch neighbouring premises or public areas".
  [source](https://www.edpb.europa.eu/system/files/documents/files/file1/edpb_guidelines_201903_video_devices_en_0.pdf)
- **Typical Indian housing-society CCTV retention practice is 30-90 days; the only
  hard Indian judicial retention figure (18 months) comes from a police-station
  case and does not bind societies.** — Industry norm: "Standard retention is
  between 30 and 90 days, depending on the society's policy." Signage practice:
  "CCTV Surveillance in Progress" boards at entrances, lobbies, parking, monitored
  common spaces. Audio capture discouraged/illegal without consent. Cameras must
  not record inside private homes. Paramvir Singh Saini v Baljit Singh (2020)
  directed police stations to retain CCTV footage for 18 months (or one year if
  longer storage is unavailable) — a useful benchmark for an incident-flagged tier
  but not a legal requirement for an RWA. Some state overlays exist, e.g. Karnataka
  Public Safety (Measures) Enforcement Act, 2017 mandating CCTV in specified
  public-facing places, and some Maharashtra municipal corporations requiring CCTV
  in new societies.
  [source](https://www.nobrokerhood.com/blog/cctv-rules-for-society/) *(likely)*
- **A twelve-section written CCTV/surveillance policy adopted by resolution, with
  facial recognition and audio defaulting to OFF, is the accepted Indian
  practitioner template for an RWA.** — Sections: (1) purpose and lawful basis;
  (2) coverage map listing monitored zones AND deliberately unmonitored areas
  (balconies, private interiors, bathrooms); (3) signage and notice; (4) a single
  named accountable custodian; (5) named-personnel access control with casual
  viewing prohibited; (6) written footage-request procedure; (7) finite retention
  with automatic secure deletion; (8) system security (locked recorders, access
  logs, changed passwords); (9) data-processing contract with any cloud/app vendor;
  (10) resident rights and grievance route with a named handler; (11) explicit
  audio and AI stance — "Microphones and facial recognition defaulting to OFF";
  (12) review date. Hard restrictions: no WhatsApp forwarding of footage, no
  targeting individuals, least-intrusive-option principle. Adoption path: draft,
  circulate to residents, committee and general-body approval, publish to all
  residents, with legal/DPO review before sign-off. On camera direction: "Never a
  neighbour's window, balcony, or private door, and never a bathroom or any private
  interior."
  [source](https://www.studiomatrx.org/guides/housing-society-cctv-policy-india)
  *(likely)*
- **A production-grade, MIT-licensed on-device redaction component already exists
  and can be embedded in the companion-computer video pipeline.** — ORB-HD/deface:
  CenterFace detector (trained on WIDER FACE) run under ONNX Runtime with OpenCV
  fallback; five anonymisation modes (blur, solid, mosaic with configurable tile
  size, custom image replacement, none); `--scale` downsamples for detection (e.g.
  640x360) while preserving output resolution; execution providers include CUDA
  (onnxruntime-gpu), OpenVINO (onnxruntime-openvino) and DirectML; MIT licence;
  `python3 -m pip install deface`. This is the right shape for an edge pipeline on
  a Jetson-class companion computer: detect at reduced scale, composite the blur at
  full resolution, and make the blur irreversible before the frame reaches the
  encoder (EDPB para 103 treats irreversible blurring as erasure).
  [source](https://github.com/ORB-HD/deface)
- **There is published research specifically on privacy-preserving drone patrol
  that anonymises faces while preserving robot perception (SLAM).** —
  "Privacy-Protection Drone Patrol System based on Face Anonymization", Harim Lee,
  Myeung Un Kim, Yeongjun Kim, Hyeonsu Lyu, Hyun Jong Yang, arXiv:2005.14390,
  submitted 29 May 2020. A GAN with modified loss functions transforms a person's
  face into a different face while maintaining facial components, so simultaneous
  localisation and mapping still works; evaluated on public face and video datasets
  and on a custom drone with a high-resolution camera and companion computer.
  Useful as the citation for "anonymise at the sensor, not in the cloud" in a DPIA.
  Marked as pre-2025 — re-verify current SOTA before selecting a model.
  [source](https://arxiv.org/abs/2005.14390)
- **Commercial drone-security platforms market geofencing, RBAC, audit logs and
  encryption — but none of the major vendors markets on-device face or plate
  redaction. That gap is the differentiator for an India-first product.** —
  FlytBase: "set operational boundaries with geofences and define restricted areas
  with no-fly zones"; "role-based access"; "encrypted transmission"; SOC 2;
  "complete audit trails"; timestamped geo-referenced records; in-country data
  residency. Skydio site security: "Role-based access, audit logs, and tenant-level
  isolation"; data "encrypted in transit and at rest"; SOC 2, ISO 27001 alignment,
  NIST adherence; drones avoid terrain, buildings and geofences. Neither product
  page names privacy masking, camera-frustum lockouts, on-device redaction, or
  retention controls. Existing geofences constrain where the AIRCRAFT goes; nothing
  constrains where the CAMERA LOOKS — which is the actual legal exposure.
  [source](https://www.skydio.com/solutions/site-security)

## Recommendations

| Recommendation | Rationale | Alternatives rejected |
| --- | --- | --- |
| Architect for "no identifiable personal data by default". Redact faces and licence plates ON THE COMPANION COMPUTER, before the H.264/H.265 encoder, and treat the redacted stream as the only stream that exists. Raw frames must never touch persistent storage, the RF downlink, or the cloud unless an incident is flagged. | Section 7 gives no lawful basis for processing identifiable data about visitors, delivery riders, domestic workers or passers-by, and consent from them is unobtainable. If the artefact the system produces is not identifiable, most of the DPDP surface disappears — the Sigma Chambers analysis is explicit that footage is personal data only where an individual is identifiable, and EDPB para 103 treats irreversible blurring as erasure. This is also the only control that survives the Calcutta HC camera-by-camera scrutiny. Concretely: deface/CenterFace under ONNX Runtime with the CUDA or TensorRT provider on a Jetson-class board, detection at 640x360, composite at full res, irreversible Gaussian or mosaic. Budget the pipeline so redaction never drops below the encoder frame rate; if the redactor stalls, blank the frame rather than pass it through. | Cloud-side redaction (raw data has already left the aircraft and been stored — the breach and the unlawful processing both already happened); redaction only at export time (the stored object is still identifiable personal data at rest); relying on low resolution alone (zoom and super-resolution defeat it, and it degrades the security utility). |
| Do NOT put face recognition on the drone. Ship class-level detection (person / vehicle / unknown-vs-registered-vehicle) on the patrol path, and confine any 1:1 biometric verification to an opt-in, signed, fixed gate kiosk with a non-biometric alternative lane. | EDPB Guidelines 3/2019 para 84 holds that a biometric system in an uncontrolled environment needs a lawful exception for EVERY person it templates, and para 86 requires a free, unconditional non-biometric alternative. India is stricter, not looser: there is no Section 7 ground at all, so 1:N matching from a drone has no lawful basis for the non-consenting majority it captures, and no state-level authorisation exists to lean on. Puttaswamy's proportionality and procedural-safeguards limbs would be very hard to satisfy for an RWA with no statutory backing. If the society insists on FRT, implement it exactly as the EDPB concert-hall example: separated lanes, templates on a resident-held credential or encrypted with a resident-held key, templates and identity data in distinct stores, raw face images deleted after enrolment, and external access to biometric data prohibited. | Drone-borne 1:N face matching against a resident gallery (no lawful basis for bystanders; highest-penalty exposure at Rs 250 crore under s.8(5) if the template store leaks); "we delete templates within milliseconds" (EDPB expressly rejects this — temporary templates are still biometric data); gait or re-identification embeddings as an FRT workaround (same uniqueness purpose, same legal analysis, worse defensibility because it is covert). |
| Build a signed, versioned 3D privacy map (GeoJSON polygons + min/max altitude AGL) that is simultaneously the legal annexure to the RWA policy and the runtime config that hard-slaves the shutter and gimbal. Compute the camera frustum every frame from GNSS + IMU + gimbal angles + FOV, intersect it against no-look volumes, and force shutter-closed on intersection. Fail CLOSED. | This is the single control that makes the whole system defensible, because it converts a policy promise into an enforced invariant and produces machine evidence that no aperture was ever observed. Volumes to encode: (a) every registered private aperture — window, balcony, terrace, private door — as a polygon plus a lateral buffer; (b) the society's external boundary, extruded, so the frustum can never intersect anything outside the plot above a set height; (c) sensitive interiors near glazing. Fail-closed triggers: gimbal/IMU pose older than ~200 ms, GNSS horizontal accuracy worse than the map's buffer, RTK fix lost, map signature verification failure, or redactor watchdog timeout. Every shutter-close event is written to the append-only audit log — that log is what you hand a court to defeat a "you were looking into my bedroom" allegation, which is exactly the allegation the Calcutta HC acted on and the Kerala HC demanded proof of. | Aircraft-only geofencing as sold by FlytBase and Skydio (constrains where the drone flies, not where the camera looks — legally the wrong invariant); operator discipline and SOPs (unauditable, and the Calcutta HC restrained specific cameras, not operators); post-hoc masking in the VMS (the unmasked frame was already captured, transmitted and stored). |
| Adopt an explicit altitude, standoff and ground-sample-distance discipline, and write the numbers into the policy so they become enforceable commitments rather than aspirations. Suggested starting envelope: patrol legs at 30-40 m AGL over open common areas; minimum 15 m horizontal standoff from any external boundary and from any residential facade carrying windows; no hover within 10 m lateral of any registered aperture; optical zoom hard-capped on patrol; patrol GSD floored so that faces are not resolvable at the ground plane. | BVA 2024 s.39 protects only flight "at a height above the ground which ... is reasonable" and "the ordinary incidents of such flight". Low hovering over or beside a dwelling to observe it is outside both limbs, so the standoff discipline is what keeps you inside the statutory bar on trespass/nuisance suits, and what keeps you clear of BNS s.77 and IT Act s.66E. EDPB para 129 independently requires that unnecessary functions — "unlimited movement of cameras, zoom capability ... and audio recordings" — be DEACTIVATED, so the zoom cap and a hard audio-disable are not optional extras. Use the DORI framework from IEC 62676-4 to set the GSD floor: size the patrol optics so the ground plane sits at "observe/detect" pixel density, not "identify", and require a deliberate, logged, incident-authorised descent or zoom to cross into identification density. India has NO statutory standoff number, so these are engineering commitments you choose and then honour — which is precisely why they must be in the signed policy. | Flying at maximum permitted 400 ft AGL for everything (loses the security utility and does not address camera angle, which is the real exposure); relying on the s.39 bar alone (it is a bar on "flight" suits only — it does not touch DPDP, BNS 77, IT Act 66E, or a writ petition framed on Article 21); leaving altitude to pilot judgement (unauditable). |
| Implement a tiered retention schedule with automatic, verifiable deletion, and separate the DPDP/CERT-In LOG clocks from the FOOTAGE clock. Suggested: redacted patrol video 7 days; incident-flagged raw video 30 days (extendable only by a logged legal hold); ANPR plate ciphertext 7 days, plaintext plate only on a rule hit and only 7 days; audit and system logs 365 days stored in India. | EDPB para 121 says footage should be erased automatically after a few days and that "especially when beyond 72 hours" the controller must argue the necessity — that is the international design bar. Indian society practice of 30-90 days is the local norm, so a 7-day default with a 30-day incident tier is defensible at both ends and is far easier to justify than a blanket 90 days. The log clocks are separate and both are floors, not ceilings: CERT-In direction (iv) requires ICT logs for a rolling 180 days WITHIN Indian jurisdiction, and DPDP Rule 6 / Rule 8(3) push a one-year floor for logs — so 365 days in an India region satisfies both. Deletion must be verifiable: crypto-shred by destroying the per-object key, and write the deletion event to the audit log. | A single uniform retention period (over-retains footage and under-retains logs, failing both CERT-In and Rule 6); 90 days for everything by default (needs justification you cannot give and multiplies breach severity under s.8(5), which carries the Rs 250 crore cap); indefinite retention pending "possible investigations" (no lawful basis, and DPDP requires erasure once the specified purpose no longer applies). |
| Store licence plates as a salted HMAC keyed per society for allow-list matching, and write plaintext plate text only when an alert rule actually fires. | A plate is personal data in this deployment because the RWA holds the resident vehicle register and can trivially link plate to person — so the identifiability test is satisfied and the DPDP obligations attach. HMAC(plate, society_key) supports the only operation you actually need on the patrol path — "is this vehicle on the registered list?" — without ever persisting an identifier. It also collapses the blast radius of a breach: a leaked hash table of unknown plates is far less damaging than a leaked movement log of named residents. Rotate the key on committee turnover and on any suspected compromise. | Plaintext plate logging for all detections (creates a resident movement-history database with no lawful basis and enormous s.8(5) exposure); no ANPR at all (loses the highest-value, lowest-intrusion security signal — vehicles are less privacy-sensitive than people). |
| Gate every de-redaction, export and download behind a two-person, ticketed, purpose-bound workflow written to an append-only audit log. No single account — including the RWA president or the vendor's admin — may unblur a frame alone. | Rule 6 requires access control plus "logging, monitoring and review to detect unauthorised access", and EDPB para 135 requires that "User performed actions (both to the system and data) are recorded and regularly reviewed". The realistic failure mode for an Indian society is not a hacker — it is a committee member pulling footage of a neighbour and forwarding it on WhatsApp, which is exactly the abuse the practitioner template bans outright. Make the log immutable (hash chain or WORM object storage with an object-lock retention of 365 days), record actor, timestamp, reason code, ticket reference, exact frame range and the second approver, and surface a monthly access report to the general body. This log is also your s.8(5)/s.8(6) defence file if the Board ever asks. | Role-based access alone (the vendor default; it authorises but does not deter or evidence); logging only exports (the harm is in viewing, and the Calcutta HC case turned on continuous observation, not on distribution); trusting the vendor's SOC 2 (SOC 2 attests the vendor's controls, not the society's use). |
| Build consent as a first-class, versioned data object per resident, with withdrawal at least as easy as granting, and propagate withdrawal into the privacy map within a published SLA. Keep the RWA general-body resolution as the PROPERTY authority, not as the consent artefact. | The consistent Indian commentary is that a general-body approval "is not a substitute for individual consent" and that each resident is an independent Data Principal; DPDP also requires withdrawal to be as easy as giving. But the resolution is still required — the society's bye-laws are what authorise installing anything in common areas, and the practitioner guidance is that the decision must be "a formally minuted vote of the managing committee or the general body, as your bye-laws require, at a properly convened meeting with proper notice". So you need BOTH, and you must not let anyone conflate them. Data model: consent record {principal_id, policy_version, purposes[], granted_at, channel, evidence_hash, withdrawn_at}. On withdrawal, (a) register that flat's apertures as no-look volumes, (b) delete any biometric template and derived data, (c) confirm in writing, (d) re-issue the signed privacy map to every aircraft before the next sortie. Note the trap: you cannot make security coverage conditional on consenting to non-essential processing, and a pay-to-opt-out model invalidates free consent. | Treating the AGM vote as consent (the specific error every Indian commentator warns against); bundling drone-surveillance consent into the community-app terms of use (fails "specific" and "unconditional"); allowing opt-out only by moving out (not free consent). |
| Ship a one-button incident pipeline that emits BOTH regulatory notifications from a single event: a CERT-In report within 6 hours and the DPDP two-tier notice (Data Principals and Board without delay, detailed report to the Board within 72 hours). | This is the nearest-term binding obligation and it is routinely missed. CERT-In Annexure I explicitly names Drones (item xix), IoT devices (xiii), AI/ML systems (xx), Data Breach (xi) and Data Leak (xii) — a compromised drone, a leaked VMS bucket, or a hijacked control link is all squarely reportable within 6 hours, TODAY, with punitive action available under IT Act s.70B(7). From 13 May 2027 the DPDP layer stacks on top with no materiality threshold: every breach is notifiable, and failure to notify carries up to Rs 200 crore. Pre-build the templates and the affected-principal enumeration query now; you cannot assemble either inside 6 hours. Also do the prerequisites: designate the CERT-In Point of Contact in the Annexure II format, and sync all system clocks to NIC or NPL NTP servers so your logs are admissible and correlatable. | Treating CERT-In as a large-enterprise obligation (the Directions apply to "body corporate" generally, and drones are named); waiting for May 2027 (CERT-In already applies); ad hoc email notification (no evidentiary trail of timeliness, which is exactly what the Board will assess under s.33(2)). |
| Do a DPIA even though Indian law does not require one for a non-SDF RWA, and publish its conclusions in redacted form to residents. | Under the DPDP Rules the annual DPIA and audit obligation attaches only to Significant Data Fiduciaries notified by the Central Government (Rule 13), so an ordinary RWA is not legally required to do one — be honest with the client about that. Do it anyway, because it is the cheapest defence available. Under GDPR this processing would trigger a mandatory DPIA twice over (Art 35(3)(c) systematic monitoring of a publicly accessible area on a large scale, and Art 35(3)(b) if special-category data is processed at scale), and EDPB para 137 says "it is reasonable to assume that many cases of video surveillance will require a DPIA". In an Indian dispute the DPIA is what converts "we bought a drone" into documented evidence of the proportionality and less-intrusive-alternatives analysis that the Kerala HC's Puttaswamy framing and CJEU C-708/18's "strictly necessary" test both demand. Include the honest comparison against fixed CCTV — if fixed cameras achieve the same purpose, the drone may fail the necessity limb, and you need to have addressed that in writing rather than have opposing counsel raise it first. | Skipping it because it is not mandatory (leaves the necessity question undocumented, which is the weakest point of the whole deployment); a vendor-supplied generic DPIA (fails the "analysing the area in question" standard EDPB applies to legitimate-interest evidence). |
| Deliver signage and layered notice as a build artefact, not a policy afterthought: first-layer boards at every pedestrian and vehicle entrance and at each patrol-zone boundary, second-layer full notice on the society app, noticeboard and a QR-addressed page, in English plus the relevant Eighth Schedule language. | EDPB para 113 requires the notice to be positioned so a person recognises the surveillance BEFORE entering the monitored area, at roughly eye level, and — critically for drones — "The data subject must be able to estimate which area is captured by a camera so that he or she is able to avoid surveillance or adapt his or her behaviour if necessary." For an aerial system that means the signage must publish the patrol footprint and schedule, not just the fact of cameras. First-layer content per para 114: purposes, identity of the fiduciary, existence of Data Principal rights, contact details of the responsible person, and a pointer to the second layer. DPDP requires notices to be available in English or an Eighth Schedule language of the principal's choice, and the contact details of the person answering questions must be prominently displayed. Practically: publish the redacted coverage map itself — the same GeoJSON that drives the shutter lockout, rendered — which is a strong trust signal and costs nothing. | A single "CCTV in operation" board at the gate (does not let a person estimate the captured area, and says nothing about aerial coverage); notice buried in the community app's privacy policy (fails the before-entry and eye-level positioning tests, and does not reach visitors at all). |
| Ship the governance pack as a numbered deliverable alongside the hardware, and make the machine-readable privacy map an annexure to it so policy and code cannot drift apart. | The documents an Indian RWA needs, in order: (1) General-body/managing-committee RESOLUTION authorising the system under the society's registered bye-laws, naming the custodian and the budget — check your state's cooperative-society or apartment-ownership law for the required majority and do not assume it; (2) Aerial Surveillance and Data Protection POLICY on the twelve-section practitioner template, with FRT and audio explicitly defaulting to OFF; (3) COVERAGE AND NO-LOOK MAP annexure — the signed, versioned GeoJSON, both rendered and machine-readable; (4) PRIVACY NOTICE meeting Rule 3 (itemised data description, specified purpose, how to withdraw consent, how to exercise rights, how to complain to the Board), in English plus an Eighth Schedule language; (5) CONSENT ARTEFACT and consent register, versioned and withdrawable; (6) DPIA (voluntary but do it); (7) RETENTION AND ERASURE SCHEDULE with the separate footage/log clocks; (8) DATA PROCESSING AGREEMENT between the RWA and the drone vendor/operator, required by DPDP s.8(2), flowing down Rule 6 security obligations; (9) ACCESS CONTROL MATRIX plus named custodian and published grievance contact with the 90-day (or one-month, pre-2027) SLA; (10) BREACH RUNBOOK covering CERT-In 6h and DPDP without-delay + 72h; (11) SIGNAGE PLAN; (12) POLICE DISCLOSURE REGISTER requiring a written requisition before any footage leaves the society; (13) staff and guard CONFIDENTIALITY UNDERTAKINGS and training records; (14) third-party drone INSURANCE; (15) annual review record including the periodic re-justification of necessity that EDPB expects. | Selling the drone and leaving governance to the society (the RWA is the Data Fiduciary and will carry the penalty, but the vendor is the Data Processor and carries its own s.8(2) contractual and Rule 6 flow-down exposure — and reputationally the vendor is who gets named); a generic template pack (state bye-laws and the society's actual geometry differ, and the no-look map is site-specific by definition). |

## Open questions

- Would a court find drone patrol PROPORTIONATE under Puttaswamy where fixed CCTV
  would achieve the same security purpose more cheaply and less intrusively? CJEU
  C-708/18 requires that the processing not be "reasonably ... as effectively
  achieved by other means less restrictive of fundamental freedoms". This is the
  weakest limb of the entire deployment and must be answered in writing in the DPIA
  before the first flight.
- Does Rule 8(3)'s one-year retention floor apply to an ordinary Data Fiduciary
  like an RWA, or only to the Schedule-listed classes (e-commerce, social media,
  online gaming)? Readings in the law-firm commentary conflict, and the answer
  decides whether you are legally required to retain footage you would rather
  delete in 7 days. Needs the gazette text and counsel.
- Do the SPDI Rules 2011 bind a non-profit RWA at all? IT Act s.43A defines "body
  corporate" to include an association of individuals "engaged in commercial or
  professional activities" — a registered cooperative housing society arguably is
  not. The drone VENDOR is unambiguously covered either way.
- Could the RWA or the vendor ever be notified as a Significant Data Fiduciary
  under DPDP s.10, pulling in mandatory annual DPIA, independent audit, algorithmic
  due diligence (Rule 13(3)) and traffic-data localisation (Rule 13(4))? No
  criteria have been notified.
- What majority does the target state's cooperative-society or apartment-ownership
  law require for a general-body resolution authorising a surveillance system, and
  does the society's registered bye-law text impose more? The practitioner guidance
  is explicit: "Your bye-laws set that threshold - do not guess it."
- Does the local police commissionerate in the target city require an NOC or
  advance intimation for routine drone flights over a residential society, over and
  above DigitalSky? Local police can and do stop authorised flights.
- What is the correct statutory vehicle for police requisition of society footage
  under the BNSS 2023 (successor to CrPC s.91)? Fix the section number before the
  disclosure register template goes out.
- No GDPR enforcement action specifically against residential DRONE surveillance
  was located. Video surveillance is a top DPA fine category overall, but the
  drone-specific precedent that would set the sharpest design bar does not appear
  to exist yet.
- Is there any Indian judicial precedent on drone overflight of a private
  residence, as distinct from fixed CCTV? None was found. The BVA s.39 / BNS 77 /
  IT Act 66E analysis is therefore constructed from first principles and analogous
  CCTV cases.
- How should the system handle a resident who withdraws consent but whose flat's
  apertures face the ONLY viable patrol corridor? The technical answer (no-look
  volume) may make part of the patrol route useless; the governance answer needs to
  be settled with the committee in advance.

## Unverified or risky

The researcher could not confirm the items below in this session. Do not rely on
any of them — in code, in a specification, or in a document handed to a client or
a regulator — without checking the primary source first.

- RULE NUMBERING RISK: the DPDP Rules 2025 rule numbers used above (Rule 3 notice,
  Rule 6 security safeguards, Rule 7 breach, Rule 8 erasure, Rule 13 SDF, Rule 14
  rights/grievance) come from law-firm secondary sources. The gazette PDF for
  G.S.R. 846(E) could not be retrieved in this session (MeitY and PIB both returned
  HTTP 403). Verify every rule number against the gazette before it appears in any
  document handed to a client or a regulator.
- The claim that facial/biometric data is "sensitive personal data under the DPDP
  Act" appears in vendor marketing (e.g. hyperverge) and is WRONG. DPDP has no
  sensitive-data category; Linklaters is explicit that "The DPDP Act does not
  replicate that category; all personal data carries the same base obligations." Do
  not repeat the vendor framing.
- IEC 62676-4 DORI pixel-density figures (detect / observe / recognise / identify)
  are cited from memory as the basis for the GSD floor and were NOT verified in
  this session. Confirm the exact px/m thresholds against the standard before
  writing them into a specification.
- IT Act Section 66E penalty (up to 3 years and/or Rs 2 lakh) and the full text of
  its "private area" and "circumstances violating privacy" Explanations were not
  re-verified — the indiankanoon document ID fetched turned out to be an unrelated
  Kerala property judgment.
- SPDI Rules 2011 internal rule numbers (privacy policy, written consent, grievance
  officer, ISO 27001 security standard) were not verified in this session — the
  MeitY PDF returned 403. The substance (biometrics are SPDI; the Rules survive
  until 13 May 2027) is well corroborated.
- BNSS 2023 section number for police requisition of documents was not verified. Do
  not put a section number in the disclosure-register template until confirmed.
- Karnataka Public Safety (Measures) Enforcement Act, 2017 and the reported
  Maharashtra municipal CCTV requirements for new societies come from a single
  industry blog. Verify scope and applicability to residential societies before
  relying on them as a lawful-obligation argument under DPDP s.7(d).
- DATE DISCREPANCY in the Kerala HC judgment: the primary PDF header reads "MONDAY,
  THE 11TH DAY OF AUGUST 2025" while carrying a registry stamp "aks/10.11.2025",
  and LiveLaw reported it as 15 November 2025. Cite by the neutral citation
  2025:KER:85261 / W.P.(C) No. 8754 of 2025 rather than by date.
- "The Drone Rules 2021 contain no privacy provision" rests on two secondary
  sources (an IJPIEL academic analysis and a legal commentary). The official DGCA
  PDF is a scanned image with no extractable text, so a keyword search of the
  primary instrument could not be performed. Confirm before asserting it in a legal
  document.
- The Supreme Court order in SLP(C) 12384/2025 (9 May 2025) was a DISMISSAL of a
  special leave petition. A dismissal in limine is not a merits precedent and
  should not be cited as "the Supreme Court held that CCTV requires consent of all
  occupants", which is how several secondary sources report it. The binding
  reasoning lives in the Calcutta HC division bench judgment.
- The suggested altitude (30-40 m AGL), standoff (15 m boundary / 10 m aperture)
  and retention (7 / 30 / 365 day) numbers are ENGINEERING RECOMMENDATIONS, not
  statutory figures. India prescribes no standoff distance and no retention period
  for private surveillance. They become binding only because you write them into
  the signed policy — which is the point, but do not present them as legal
  requirements.
- Claims that FlytBase and Skydio lack on-device face/plate redaction are based on
  their public marketing pages only. Confirm against current product documentation
  or a sales engineer before relying on it as a competitive differentiator.
- The arXiv face-anonymisation drone paper (2005.14390) is from May 2020 and is
  PRE-2025. Treat its GAN approach as a citation for the architectural principle,
  not as a current model recommendation; re-verify state of the art before
  selection.
