# perception — detection models

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
