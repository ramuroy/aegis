# paper — IEEE-format write-up

**Status:** not started.

## Intended contribution

The defensible claim is not "we built a drone security system" — that exists
commercially. It is the design inversion and the mechanism that makes it work:

1. A costing analysis showing that scheduled aerial patrol is dominated by fixed
   CCTV at residential scale, with the crossover identified (~20–30 acres).
2. **Corroboration keyed on modality family**, so agreement is required between
   sensors whose failure modes do not correlate — with an evaluation against
   nuisance sources.
3. **The privacy map**: a single signed artefact that is simultaneously an
   approved-policy annexure and a runtime gimbal constraint, making
   policy-to-implementation drift structurally impossible; motivated by DPDP §7
   being a closed list with no legitimate-interest ground.
4. A georeferencing error budget that identifies the dominant term rather than
   reporting one aggregate number.

## Rules

- Every number must be reproducible from this repository by a named command.
- Validation is in simulation and must be described as such. The hardware is a
  costed design, not a build.
- Related work draws on [`docs/research/`](../docs/research/), where each claim
  keeps its source URL and confidence marker.
