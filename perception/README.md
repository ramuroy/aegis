# perception — detection models

## Next implementation slice: 2026-09-08

1. Establish primary-source licence/provenance records for proposed VisDrone/UAVDT
   datasets, exact RF-DETR code/weights and transitive dependencies. Preserve the
   no-AGPL/no-ultralytics boundary; model selection is not blanket licence clearance.
2. Build reproducible dataset preparation with documented inputs and splits.
3. Implement a minimal inference baseline feeding the existing camera/georeferencing
   types before layering SAHI sweeps, export and acceleration onto it.
4. Record exact model, data, hardware and procedure before reporting evaluation or
   ONNX/TensorRT performance. The documented Jetson platform still needs exact
   compatibility confirmation before installation or deployment.

No dataset download, training, export or benchmark was performed in this session.
This software task is separate from the [physical-flight gates](../docs/research/drone-regulation.md).
Read the [handoff](../docs/HANDOFF-2026-09-08.md) for decisions retained and rationale.


Dataset preparation, training, evaluation and export. This is *offline* work: the
deployed inference path lives on the companion computer and runs ONNX/TensorRT,
not PyTorch.

**Status:** not started. Longest pole, and fully unblocked — the detector choice,
licence position and error budget are all settled.

## What goes here

```
datasets/   VisDrone / UAVDT preparation, aerial-specific augmentation
training/   RF-DETR fine-tuning
eval/       benchmark harness — mAP by object size, FPS on named hardware
export/     ONNX and TensorRT export, INT8 calibration
notebooks/  exploration; never a source of a published number
```

## Constraints that already apply

- **RF-DETR, Nano through Large only.** XL and 2XL are PML 1.0, not Apache-2.0.
  ([ADR-0004](../docs/adr/0004-rf-detr-over-ultralytics-yolo.md))
- **`ultralytics` is not installable here.** Not for training, not for a
  comparison, not in a notebook. AGPL-3.0.
- **Checkpoints are audited individually.** D-FINE is a permitted fallback but
  only its COCO-only weights; the Objects365-pretrained variants are not
  commercially cleared even though the repo is Apache-2.0.
- **Small objects are solved with resolution and SAHI**, not architecture — 68%
  of VisDrone objects are under 32×32 px. SAHI costs 4–6× compute, so it runs in
  a periodic sweep, not on every frame.
- **No face recognition.** Excluded on both licence and legal grounds.

`make data`, `make train`, `make eval`, `make export`.
Background: [`docs/research/cv-models.md`](../docs/research/cv-models.md).
