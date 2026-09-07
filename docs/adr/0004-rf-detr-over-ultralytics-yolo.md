# 0004. RF-DETR as the detector; no AGPL in the inference path

- **Status:** Accepted
- **Date:** 2026-09-07
- **Deciders:** Ramu Roy
- **Supersedes:** —
- **Superseded by:** —

## Context

The default choice for object detection is Ultralytics YOLO. It has the best
documentation, the largest community, and `pip install ultralytics` gets you a
working detector in four lines. Nearly every drone-vision project uses it.

It is also **AGPL-3.0**, and AEGIS is a system intended to be sold to housing
societies. Ultralytics explicitly names, as triggers requiring a commercial
Enterprise License:

- "embedded deployments in hardware, edge devices, robotics, cameras, or
  appliances" — which is exactly a companion computer on an airframe;
- SaaS and API products — which is exactly the cloud tier;
- internal business tools;
- "custom-trained or fine-tuned YOLO models in a proprietary or commercial
  setting" — which is exactly a detector fine-tuned on aerial data.

AGPL-3.0's network clause means the obligation is not avoided by never shipping
a binary: serving inference over a network is conveying. Complying would require
publishing the complete corresponding source of the entire derivative work
**including the model weights**. The alternative is an Enterprise License (one
publicly reported quote ~USD 5,000/year).

This is a decision that is nearly free to make now and extremely expensive to
reverse later, because by the time it matters the detector is entangled with the
training pipeline, the export path, the tracker, and every benchmark number in
the paper.

The trap is wider than Ultralytics itself. Auditing the obvious dependencies:

| Component | Licence | Verdict |
| --- | --- | --- |
| Ultralytics YOLOv5/v8/v11/v12/YOLO26 | AGPL-3.0 | Excluded |
| YOLOv13 (iMoonLab) | AGPL-3.0 (Ultralytics fork) | Excluded — same obligations |
| BoxMOT (tracking) | AGPL-3.0 | Excluded |
| DEIMv2 | bespoke "DEIMv2 License", commercial contact required; DINOv3 backbone terms | Excluded |
| InsightFace pretrained weights (`buffalo_*`, `antelopev2`) | non-commercial research only (code is MIT) | Excluded |
| RF-DETR **XL / 2XL**, Seg-XL/2XL (via `rfdetr[plus]`) | PML 1.0 | Excluded |
| RF-DETR **Nano → Large** | Apache-2.0 | **Usable** |
| D-FINE (COCO-only checkpoints) | Apache-2.0 | Usable |
| D-FINE `*_obj365` / `*_obj2coco` checkpoints | authors flag possible Objects365 dataset terms | Excluded — not commercially cleared |
| DEIM | Apache-2.0 | Usable (fallback) |
| SAHI (sliced inference) | MIT | Usable |
| Roboflow `trackers` | Apache-2.0 | Usable |
| `supervision` | MIT | Usable |

Note the two subtleties that a licence scan misses: a permissively-licensed
*repository* can ship *checkpoints* under different terms (D-FINE's Objects365
weights, InsightFace's face models), and a permissive model family can have
non-permissive members (RF-DETR XL/2XL). Licence compliance here is per-artefact,
not per-repo.

Separately, the accuracy story is not what picks the architecture. On aerial
imagery the binding constraint is object size, not model capacity: **68% of
VisDrone objects are under 32×32 px**, and a stock YOLO11s reaches only ~32–39.5%
mAP50 on VisDrone regardless of how good the architecture is. The fix is input
resolution and sliced inference, which is available to any detector.

## Options considered

### Option A — Ultralytics YOLO, accept AGPL
Fastest to build, best ecosystem. Forces open-sourcing the whole stack including
weights, or a recurring licence fee. For a system whose commercial thesis is a
price point 10× below incumbents, a per-seat model licence is a meaningful
margin line. Rejected.

### Option B — Ultralytics YOLO, buy the Enterprise Licence
Removes the obligation cleanly. But it makes the single most replaceable
component in the system a permanent recurring cost and a vendor dependency,
to buy accuracy that resolution and slicing provide for free. Rejected on
value, not on principle.

### Option C — RF-DETR (Apache-2.0), sizes Nano through Large
Real numbers: RF-DETR-S reaches **53.0 COCO AP at 512 px / 3.5 ms** (T4, FP16);
RF-DETR-M reaches **54.7 AP at 576 px / 4.4 ms**. That is competitive with or
ahead of the AGPL alternatives at comparable latency, under Apache-2.0, with
no per-artefact carve-outs inside the Nano–Large range.

DETR-family models converge more slowly than YOLO and are fussier to fine-tune,
so training cost is higher. Accepted as the price of the licence position.

## Decision

**RF-DETR (Nano–Large, Apache-2.0) is the detector. No AGPL-licensed code enters
the inference or training path.**

Supporting choices that follow:

1. **Tracking:** Roboflow `trackers` (Apache-2.0) + `supervision` (MIT), running
   ByteTrack/BoT-SORT with camera-motion compensation — not BoxMOT (AGPL).
2. **Small objects:** solve with resolution and **SAHI** (MIT) sliced inference,
   which buys **+5–7 AP at ~4–6× the compute**. Because that multiplier is real,
   SAHI runs in a periodic *sweep* mode over a static scene, not on every frame
   of a tracking loop.
3. **Checkpoints are audited individually.** D-FINE is a permitted fallback but
   only its COCO-only checkpoints; the Objects365-pretrained variants are
   excluded. This rule is enforced in CI, not by memory
   (`tools/check_licences.py`).
4. **No face recognition in v1**, on licence grounds here and on legal grounds
   in [ADR-0006](0006-privacy-by-design-no-identifiable-data-by-default.md).
   The two arguments are independent and both conclude the same thing.
5. **`ultralytics` is not an allowed dependency anywhere in the repo**, including
   notebooks and comparison scripts, because an AGPL import in a notebook that
   produces a published benchmark number is still a derivative work.

## Consequences

**Easier:** the licence position is clean and auditable. Every number in the
paper was produced by code that could ship in a commercial product, so the
research artefacts and the product artefacts are the same artefacts. There is
no future migration where benchmarks have to be re-run under a different model.

**Harder:** DETR fine-tuning is slower to converge and has fewer
copy-paste tutorials than YOLO. We give up the largest community in the field.
Some published aerial-detection baselines are YOLO-based, so comparisons in the
paper need care — we cannot simply cite a YOLO VisDrone number and imply it was
measured on our pipeline.

**Committed to:** licence review is part of adding any model, weight file, or
vision dependency. The CI check exists so this survives the point where nobody
remembers this ADR.

**Revisit if:** an Apache-2.0 or MIT detector appears that is materially better
on small aerial objects, or if the project's commercial thesis is abandoned in
favour of a fully open-source release — in which case AGPL stops being a
constraint and Option A reopens.

## References

- Ultralytics licensing FAQ — enumerated Enterprise triggers.
- RF-DETR model card and benchmark table (Apache-2.0 for Nano–Large; PML 1.0 for XL/2XL via `rfdetr[plus]`).
- D-FINE repository notes on Objects365 checkpoint terms.
- VisDrone2019 object-size distribution; SAHI sliced-inference gains.
- Full audit: `docs/research/cv-models.md`.
