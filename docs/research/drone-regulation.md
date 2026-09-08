# Indian drone regulation: research checkpoint

**As of 2026-09-08. Status: PARTIAL, not deployment clearance.**

This closes the interrupted first-pass research task, not the legal or physical
flight gates. It separates simulation, conditional prototype testing, and a
commercial residential-security service. AEGIS has not demonstrated an eligible
operator, approved aircraft/configuration, lawful site-specific operating envelope,
or permission for unattended/BVLOS operation.

Where older research notes make broader drone-regulation claims, use the
qualifications below. Accepted ADRs are unchanged. Proposed implementation
constraints here are not implemented features or newly accepted decisions.

## 1. Findings that change the plan

- Continue software, recorded-data perception and simulation work. Do not present
  simulation success as permission for a residential deployment.
- Investigate Rule 42 for prototype research, rather than assuming every custom
  aircraft must first obtain a type certificate. Eligibility and site control
  must be evidenced; calling a commercial service a pilot does not make it R&D.
- Keep type certification, aircraft registration, pilot certification, airspace
  permission and import authorization as separate gates. An exemption from one
  does not automatically exempt the others.
- Preserve event-driven dispatch and the project restriction on night launches.
  Neither corroboration nor society consent establishes aviation permission.
- Resolve preflight airspace freshness before connecting dispatch to live arming.
  Local sensing can remain operational when an aircraft cannot lawfully launch.

These are project implications of the sources below, not an opinion that the
proposed service is approved. Obtain qualified Indian aviation advice and the
applicable authority's written position before physical operations.

## 2. Applicable instruments and evidence quality

| Instrument | Finding | Evidence boundary |
| --- | --- | --- |
| Drone Rules, 2021, G.S.R. 589(E), 25 August 2021 | Base rules for this analysis. | Relevant clauses visually read from a government-hosted reproduction; direct original-gazette download failed. |
| Drone (Amendment) Rules, 2022, G.S.R. 108(E), 11 February 2022 | Remote pilot terminology becomes certificate; authorized RPTO issuance replaces the additional licence step. The legacy registration deadline becomes 31 March 2022. | Official MoCA publication and indexed text consulted. |
| Drone (Amendment) Rules, 2023, G.S.R. 715(E), notification dated 27 September 2023 | Form D-4 permits specified government identity/address evidence as an alternative to a passport. | Official MoCA publication and appended gazette text consulted. |
| Drone (Amendment) Rules, 2024, G.S.R. 515(E), notification dated 21 August 2024 | Similar identity/address alternatives added to registration/transfer Forms D-2 and D-3. | Original gazette loaded in Brave after direct-download failure; English identification and operative amendments visually read on pp. 2-3. Not archived in the repository. |

Sources: [2021 original gazette][rules-original], [government-hosted rules
reproduction][rules-copy], [2022 amendment][amendment-2022], [2023
amendment][amendment-2023], [2024 amendment][amendment-2024].

The reproduction's filename says `with_2023_amendment`, but the main rules retain
older licence wording, with the 2023 amendment appended. It is **not** a reliable
fully consolidated current text. Apply amendments separately. PDF page references
below are one-based pages of that reproduction, not the original gazette.

The Bharatiya Vayuyan Adhiniyam, 2024 commenced on 1 January 2025 according to
[PIB's official explanation][bva-commencement]. Section 43 repeals the Aircraft
Act, 1934 but saves existing rules/actions insofar as consistent with the new
Act. Repeal alone does not establish that the Drone Rules disappeared. The
[India Code record][bva-record] and [indexed Act text][bva-text] were located;
full Act-PDF retrieval failed, so complete statutory reconciliation remains open.

MoCA published a [draft Civil Drone (Promotion and Regulation) Bill,
2025][draft-bill] and a [consultation extension][draft-consultation]. A draft is
not an operative permission. This bounded search did not locate a subsequent
enactment/commencement instrument; that is **not proof that none exists**. Refresh
the legislation and directions search before live-flight approval.

## 3. Operating requirements: clause map

The following is a navigation aid to the [base rules][rules-copy], with the
[2022 terminology amendment][amendment-2022] applied. It is not an exhaustive
compliance checklist.

| Subject | Rule and reproduction page | AEGIS consequence |
| --- | --- | --- |
| Aircraft class | Rule 5, p. 7: nano <=250 g; micro >250 g to 2 kg; small >2 to 25 kg, measured by maximum all-up weight including payload. | Classify the complete flight configuration, not the empty frame. |
| Type certificate (TC) | Rules 6 and 13, pp. 8-9. Manufacturing/importing does not itself require a TC under Rule 13(1); operation has its own requirements and exemptions. | Do not describe certification as universally required before building a prototype. Import policy is separate. |
| Registration/UIN | Rules 14-16, pp. 9-10. General registration obligation; exemptions must have their own basis. Rule 16 concerns legacy aircraft. | A TC exemption is not a blanket UIN exemption or an open new-build registration channel. |
| Remote pilot certificate (RPC) | Rules 31-36, pp. 12-13; 2022 amendment. Rule 36 distinguishes nano from micro used for non-commercial purposes. | A micro commercial service cannot rely on the non-commercial micro exemption. |
| Airspace | Rules 19-24, p. 11. Preflight restrictions check; green-zone permission relief is conditional. Temporary restrictions can apply. | A residential boundary or yesterday's green map is not sufficient launch evidence. |
| Safety and incidents | Rules 26, 29-30, p. 12. Avoid endangerment, yield to manned aircraft, report accidents within 48 hours. | Include operating safety and a distinct aviation incident procedure; do not substitute a cyber-incident reporting clock. |
| Insurance | Rule 44, p. 15; nano exception. | Obtain applicable third-party cover and confirm scope for the actual operation. |

Rule 3's model-RPAS definition includes a <=25 kg limit, specified
educational/research/design/testing/recreational purposes and VLOS. A self-built
commercial security aircraft does not become a model RPAS merely because it is
small. Rule 13's nano TC exemption also does not establish a nano registration
exemption. A separate current exemption/direction would need to be identified.
[Rules 3, 13-14][rules-copy].

Rule 12 lists safety features that government may require through notification,
including NPNT, tracking and geofencing. Do not turn that enabling clause alone
into a claim that a particular NPNT or Remote ID implementation is universally
mandatory today. Applicable notifications and the certification scheme still need
to be collected for the selected aircraft. [Rule 12][rules-copy].

## 4. Conditional R&D path, not commercial authorization

Rule 42 exempts specified persons from TC, UIN, prior permission and RPC
requirements **for research, development and testing**. The listed categories are
recognized/government-controlled R&D entities or educational institutions,
DPIIT-recognized startups, authorized testing entities, and UAS manufacturers
with a GST identification number. Operations must satisfy the green-zone and
premises/controlled-open-area conditions. [Rule 42, reproduction p. 14][rules-copy].

Before using this route, assemble an evidence packet:

1. Identify the actual operating legal entity and the exact eligibility limb;
   retain recognition or manufacturer/GSTIN evidence, as applicable.
2. Define the experiment and its research purpose. Separate it from routine
   resident-facing security operations and commercial service claims.
3. Document the premises or controlled open area and current airspace status.
4. Have the proposed aircraft, pilot/supervisor, safety envelope and exemption
   interpretation reviewed before approving a flight.
5. Retain the approval basis with each experiment; stop when its scope or
   conditions no longer match.

This is a proposed project review process. AEGIS eligibility, a qualifying site,
and any needed additional directions or permissions are **not established**.
Rule 42 does not say that every other legal obligation is waived.

## 5. Registration status and current portals

The live [DGCA homepage][dgca] displayed the non-TC registration suspension on
8 September 2026. Following its link in Brave recovered the
[underlying one-page instructions][non-tc-instructions]. They are undated and
refer to a separate public notice dated 12 August 2025.

Despite the general suspension, the instructions offer a contact-and-document
route for locally manufactured nano/model UAS under Rule 13, not automatic
approval. Requested evidence includes eGCA identity, intended use, tracking and
geofencing details, specifications, calibrated weighing evidence, component
identifiers, photographs and import authorization where applicable.

The declarations cover non-commercial model use; VLOS R&D in controlled green
areas; restricted-zone permissions; R&D reports at least every two months or
earlier when requested; data retention; immediate accident/incident reporting;
and concurrent TC initiation for future commercial operations.

These are registration-route commitments, not a replacement text for Rule 42.
AEGIS eligibility and approval are unestablished. Inference for an applicant:
the immediate-reporting commitment must not be reduced to the base Rule 30
48-hour deadline. The suspension alone does not establish cancellation of all
existing registrations or repeal of R&D exemptions.

A [February 2026 PIB account][portal-migration] states that registration, RPC,
TC and RPTO authorization services moved to eGCA, while flight-plan and airspace
map services remain with Digital Sky. Portal names in the 2021 rules are not a
current integration specification. No authenticated eGCA workflow, aircraft list,
or supported machine-readable airspace API was exercised in this research.

## 6. Imports: prohibition with authorization exceptions

[DGFT Notification 54/2015-2020, 9 February 2022][dgft], Annexure I, sets a
prohibited policy for complete/SKD/CKD drones, with DGFT-authorization exceptions
for the specified R&D route and for defence/security purposes; components have a
free import policy in that notification.

The security-purpose exception is not evidence that AEGIS has authorization, but
the text also does not justify a blanket assertion that every private security
import is categorically impossible. Conversely, a commercial foreign drone or
dock bundle cannot be budgeted as freely importable. Classification of a dock
alone, current policy amendments, licensing eligibility, duties and other
equipment approvals require separate confirmation. "Free" import policy does
not mean duty-free or exemption from all other controls.

This pass establishes the cited notification's text, not a complete current
customs classification or import-law opinion for a proposed purchase.

## 7. Autonomy, BVLOS, night and offline dispatch

Rule 4 explicitly recognizes autonomous UAS as a subcategory. That is neither a
blanket ban on autonomy nor a blanket permission for unattended BVLOS service.
The reviewed base rules alone do not resolve the full operating conditions for
AEGIS's proposed residential missions. [Rules 3-4][rules-copy].

Historical experimental guidance and an entity-specific [2021 NAL conditional
BVLOS exemption][nal-exemption] are not transferable AEGIS permissions. This
research did not establish a current general authorization covering the proposed
unattended, night or BVLOS service. Keep those deployment claims on hold. Do not
present the project's night-disable default as proof of a nationwide statutory
night-flight ban.

**Design implication, not implemented:** Rules 21-24 require resolving airspace
restrictions before flight, including temporary restrictions. This creates an
open question for ADR-0003's offline-dispatch promise. A locally cached green
zone and a signed privacy map serve different purposes; neither alone proves
current aviation permission. [Rules 21-24][rules-copy].

Proposed behavior for a future launch gate:

- Require evidence identifying the operating basis, aircraft/configuration,
  operator/pilot, site, applicable restrictions and validity period.
- Refuse a new launch when required evidence is missing, expired or cannot be
  established. Continue local sensing, privacy-filtered review and ground alerts.
- Treat an aircraft already airborne under its flight-controller failsafe and
  approved contingency plan; do not confuse a prelaunch refusal with an arbitrary
  airborne shutdown.
- Model these states in simulation before connecting a real arming command.

Do not invent a legal cache lifetime or assume a public API exists. If the
offline-dispatch contract changes, record the accepted resolution in a new ADR;
do not rewrite an accepted ADR to hide the conflict.

## 8. Open gates and next work

| Gate | Current state | Evidence required to close |
| --- | --- | --- |
| Complete current legal chain | PARTIAL | Original 2021 gazette reconciliation, durable source archive, full 2024 Act reconciliation, and subsequent rules/directions/commencement search. |
| Non-TC registration | OPEN | Instructions recovered; authority-confirmed applicability and approval for the proposed aircraft/path remain outstanding. |
| Prototype R&D eligibility | OPEN | Operating entity, eligibility evidence, experiment scope and controlled green-zone site. |
| Commercial aircraft and pilot | OPEN | Actual configuration's TC/UIN or precise exemptions, pilot qualification and applicable insurance. |
| Unattended/BVLOS/night envelope | OPEN | Current applicable directions and written basis covering this operation, not another entity's historical experiment. |
| Site and operational safety | OPEN | Current restrictions, site rights, contingency plan, people/property risk controls and local requirements. |
| Certification safety features | OPEN | Applicable scheme and notifications for the chosen hardware/software configuration. |
| Imports | OPEN if foreign equipment is proposed | Current classification, policy and any required authorization for the exact shipment. |
| Preflight/offline contract | OPEN | Accepted design decision, supported restriction-check workflow and refusal behavior. |

The next software task is the perception pipeline: first establish dataset,
model-weight and transitive-dependency licence provenance, then implement dataset
preparation and an RF-DETR inference baseline feeding existing georeferencing.
Preserve the no-AGPL/no-ultralytics boundary. Training results, ONNX/TensorRT
performance and hardware compatibility must be measured separately; none was
demonstrated in this research pass. Physical-flight work remains gated above.

Related context: [handoff](../STATE.md), [flight stack](flight-stack.md),
[prior art](prior-art.md), [hardware BOM](hardware-bom.md),
[unit economics](unit-economics.md), [privacy law](privacy-law.md).

## 9. Retrieval limits

- Official websites, indexed official publications and the government-hosted
  scanned rules reproduction were consulted. The relevant scanned clauses were
  rendered and read rather than trusting incomplete text extraction.
- Direct eGazette retrieval encountered timeout/certificate failures. No TLS
  verification bypass was used. A subsequent user-authorized Brave pass loaded
  the original 2024 gazette and enabled visual reading of its English amendments.
- Brave exposed the DGCA banner's underlying public PDF URL; its instructions
  were then read as text and visually. The referenced separate 12 August 2025
  cancellation-proceedings notice was not reviewed. No authenticated registration
  or supported airspace-API workflow was exercised.
- This is a dated, bounded source pass, not proof of exhaustive legal coverage.
  No authority was contacted, application submitted, purchase made, or flight
  authorized. No code, tests or aircraft behavior were validated.

[rules-original]: https://egazette.gov.in/WriteReadData/2021/229221.pdf
[rules-copy]: https://indiacinehub.gov.in/sites/default/files/2024-04/drone_rules_2021_with_2023_amendment_1.pdf
[amendment-2022]: https://www.civilaviation.gov.in/sites/default/files/2025-11/drone-amendment-rules-2022-dated-11-feb-2022.pdf
[amendment-2023]: https://www.civilaviation.gov.in/sites/default/files/2023-10/Drone%20%28Amendment%29%20Rules%2C%202023.pdf
[amendment-2024]: https://egazette.gov.in/WriteReadData/2024/256584.pdf
[bva-record]: https://www.indiacode.nic.in/indiacode/handle/123456789/20589?view_type=browse
[bva-text]: https://upload.indiacode.nic.in/view-casepdf?id=AC_CEN_36_0_000010_202416_1738131525716&type=act
[bva-commencement]: https://www.pib.gov.in/PressNoteDetails.aspx?ModuleId=3&NoteId=154274&lang=2&reg=3
[draft-bill]: https://www.civilaviation.gov.in/sites/default/files/2025-09/Draft%20Civil%20Drone%20%28Promotion%20and%20Regulation%29%20Bill%202025.pdf
[draft-consultation]: https://www.civilaviation.gov.in/in-focus/extension-timelines-commentssuggestions-draft-civil-drone-promotion-and-regulation-bill
[dgca]: https://www.dgca.gov.in/digigov-portal/
[non-tc-instructions]: https://public-prd-dgca.s3.ap-south-1.amazonaws.com/topHeader/drone/Registration%20of%20Non-Type%20Certified%20UAS.pdf
[portal-migration]: https://www.pib.gov.in/PressNoteDetails.aspx?ModuleId=3&NoteId=157407&lang=2&reg=3
[dgft]: https://content.dgft.gov.in/Website/dgftprod/7d5fd1eb-ad39-4c99-b760-014223657469/Eng-Notification%2054%20dated%209%20Feb%202022%20ITC%28HS%29%202022%20_with%20Annexures.pdf
[nal-exemption]: https://www.civilaviation.gov.in/sites/default/files/migration/Conditional_exemption_to_NAL_for_BVLOS_drone_operations_13_Sep_2021.pdf
