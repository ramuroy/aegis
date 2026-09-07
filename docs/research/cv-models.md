# Computer Vision & Models

> Research note for [AEGIS](../../README.md). Compiled 2026-09-07 from a multi-agent
> web research sweep. Every claim below is sourced; confidence levels are the
> researcher's own and are preserved verbatim.

## Summary

The single most consequential decision in this layer is not accuracy, it is
licensing: every Ultralytics YOLO generation through YOLO26 (released Jan 2026)
is AGPL-3.0, and Ultralytics explicitly names "embedded deployments in hardware,
edge devices, robotics, cameras" and "internal business tools" as
Enterprise-License triggers — so a product sold to RWAs must either open-source
the entire stack including weights, buy an enterprise licence (one reported
quote ~USD 5,000/yr), or use an Apache-2.0 detector. The clean commercial path
in 2026 is RF-DETR (Apache-2.0 for Nano→Large; RF-DETR-S = 53.0 COCO AP at 512px
/ 3.5 ms T4-FP16, RF-DETR-M = 54.7 at 576px / 4.4 ms), with D-FINE (Apache-2.0,
D-FINE-S 48.5 AP / 3.49 ms) and DEIM (Apache-2.0) as fallbacks; avoid DEIMv2
(custom licence, commercial contact required, DINOv3 backbone) and YOLOv13
(AGPL, forked from Ultralytics). For aerial small objects the real fix is
resolution and slicing, not architecture: 68% of VisDrone objects are under
32×32 px, a stock YOLO11s only reaches ~32-39.5% mAP50 on VisDrone, and SAHI
(MIT) sliced inference buys +5-7 AP at ~4-6× the compute — so run SAHI in a
periodic "sweep" mode, not every frame. On hardware, a Jetson Orin Nano Super
8GB (≈₹31,959 + 18% GST) does 640-px detection in ~4.6 ms (FP16 TensorRT) and is
the right ground-station brain; a Raspberry Pi 5 + Hailo-8L is a distant second
because the Pi's PCIe Gen3 ×1 link halves the model-zoo throughput (yolov8s: 110
FPS model-zoo vs ~28.6 FPS measured on a Pi 5). Tracking should use the
Apache-2.0 Roboflow `trackers` + MIT `supervision` stack (ByteTrack/BoT-SORT
with camera-motion compensation), not AGPL BoxMOT, and cross-pass person Re-ID
from 40 m is not viable — re-associate by georeferenced world position and time
instead. Behaviour analytics that actually work in production are geometric and
rule-based in world coordinates (zone intrusion, tripwire, dwell/loitering,
direction, count) after georeferencing; fight, fall and abandoned-object
detection remain research-grade with 30-60% first-generation false-alarm rates,
so use a small VLM (Moondream 3.1 locally, or Claude Haiku 4.5 at $1/$5 per MTok
≈ ₹0.3/alert) purely as a second-opinion filter and alert-text writer. ANPR from
30-50 m is physically impossible with a wide lens — at 40 m a 48 MP wide camera
gives ~7.2 mm/px, i.e. ~9 px per character against a ≥20-25 px minimum — so put
ANPR on a fixed gate camera (fast-plate-ocr, MIT) and use the drone only for
vehicle presence/colour/type. Face recognition should be excluded from v1 on
both legal and licensing grounds: the DPDP Rules 2025 were notified 14 Nov 2025
with substantive compliance due May 2027 and penalties up to ₹250 crore, and
InsightFace's buffalo_l/antelopev2 weights are non-commercial-research-only
(OpenCV Zoo YuNet+SFace is the Apache-2.0 alternative if a gate-side, opt-in
enrolment is ever built). Georeferencing is solved arithmetic, not research:
undistort the bbox foot point, rotate the ray by gimbal attitude, intersect with
a ground plane or an OpenDroneMap-derived DSM, and convert with `pymap3d` (BSD,
v3.2.0, has `lookAtSpheroid`) — expect 2-5 m CEP on barometric altitude and
0.5-1.5 m with RTK plus a site DSM.

## Hard constraints

- **LICENSING** — Ultralytics YOLO (v5/v8/v11/v12/YOLO26) is AGPL-3.0. Using it in
  a product sold to societies requires either publishing the complete source of
  the entire derivative work including model weights, or buying an Ultralytics
  Enterprise License. Ultralytics explicitly lists 'embedded deployments in
  hardware, edge devices, robotics, cameras, or appliances', SaaS/APIs, internal
  business tools, and 'custom-trained or fine-tuned YOLO models in a proprietary
  or commercial setting' as Enterprise triggers.
- **LICENSING** — YOLOv13 (iMoonLab) is AGPL-3.0 and is built on the Ultralytics
  codebase, so it carries identical obligations. BoxMOT (mikel-brostrom) is
  AGPL-3.0 and cannot be linked into a closed-source product.
- **LICENSING** — DEIMv2 is released under a bespoke 'DEIMv2 License' that directs
  commercial users to contact the authors; it also depends on DINOv3 backbones
  with their own terms. Not usable off the shelf commercially.
- **LICENSING** — D-FINE is Apache-2.0 but its Objects365-pretrained checkpoints
  (\*_obj365, \*_obj2coco) are explicitly flagged by the authors as possibly
  subject to Objects365 dataset terms and 'should not be assumed to be
  commercially cleared'. Use COCO-only checkpoints.
- **LICENSING** — InsightFace pretrained face-recognition models (buffalo_l,
  buffalo_s/m, antelopev2) are non-commercial research only; only the code is MIT.
  Commercial use requires a separate licence from InsightFace.
- **LICENSING** — RF-DETR XL and 2XL detection models (and Seg-XL/Seg-2XL) are
  under PML 1.0 via rfdetr[plus], not Apache-2.0. Only Nano through Large are
  Apache-2.0.
- **LEGAL (India)** — The DPDP Act 2023 with the DPDP Rules 2025 (notified 14 Nov
  2025) is in force with a phased runway: Data Protection Board from Nov 2025,
  consent-manager framework from Nov 2026, all remaining substantive obligations
  from May 2027. Facial images are personal data; consent is the primary lawful
  ground for FRT. Maximum penalty ₹250 crore for failure to maintain reasonable
  security safeguards. The RWA (and plausibly you as a processor) carries notice,
  purpose-limitation, retention, erasure and breach-reporting duties.
- **PHYSICS (ANPR)** — Reliable plate OCR requires ≥20 px character height (25 px
  practical) and ~100-150 px across plate width, with ≥2 px stroke width. At 40 m
  AGL a 48 MP / 24 mm-equivalent camera gives ~7.2 mm/px → ~9 px characters. Drone
  ANPR at 30-50 m with a wide lens is not achievable at any software quality.
- **PHYSICS (small objects)** — At 40 m AGL, downscaling a 48 MP frame to a 640-px
  network input makes a standing adult ~15-25 px tall and a near-nadir adult ~5-7
  px. Below ~15 px, detection recall collapses without sliced inference and/or a
  higher input resolution. Near-nadir gimbal angles must be avoided for person
  detection.
- **PHYSICS (night)** — A drone-mounted IR illuminator cannot usefully light a
  scene at 30-50 m within the power/weight budget. In unlit areas, RGB night
  recall is effectively zero. Either fly thermal or do not claim night coverage
  from the air.
- **SUPPLY CHAIN** — Teledyne FLIR cores are US export-controlled and the primary
  maker channel (GroupGets) will not ship Lepton to India (North America,
  Australia, UK, Switzerland and EU only). Any FLIR-based thermal plan needs a
  compliant India distributor and duty/GST budget.
- **HARDWARE** — Raspberry Pi 5 exposes only PCIe Gen3 ×1 to the AI HAT, roughly
  halving Hailo model-zoo host-to-device bandwidth. Hailo's published FPS are
  'hw_only' with synthetic data and no pre/post-processing, measured on a PCIe
  Gen3 ×4 Intel host — they are not achievable on a Pi 5.
- **GOVERNANCE** — Any FRT or AI analytics feature in an Indian housing society
  must be defaulted OFF and switched on only by a separate, knowingly taken
  general-body resolution with its own documented safeguards; it must not arrive
  bundled with a camera or drone upgrade.

## Findings

### Detectors and licensing

- **Ultralytics YOLO26 shipped January 2026 under AGPL-3.0, NMS-free, five
  scales** — YOLO26n 40.9 mAP50-95 (40.1 end-to-end/NMS-free), 38.9 ms CPU ONNX,
  1.7 ms T4 TensorRT10, 2.4M params, 5.5 GFLOPs. YOLO26s 48.6 / 87.2 ms / 2.5 ms /
  9.5M / 20.9B. YOLO26m 53.1 / 220 ms / 4.7 ms / 20.4M / 68.4B. YOLO26l 55.0 / 6.2
  ms. YOLO26x 57.5 / 11.8 ms. Architecture: DFL removed, ProgLoss + STAL, MuSGD
  optimizer, native nms=False. Licence AGPL-3.0 + Enterprise option.
  [source](https://docs.ultralytics.com/models/yolo26/)

- **Ultralytics' own licence page states that embedded/edge deployment and any
  commercial or internal closed-source use requires an Enterprise License** — AGPL
  compliance requires you to 'publicly release the complete corresponding source
  code for the entire derivative work, including the larger application,
  modifications, scripts, configuration files, and, where applicable, model
  weights.' Enterprise triggers explicitly listed: any commercial product or
  service; proprietary/closed-source software; internal business tools;
  SaaS/APIs/cloud using YOLO behind the scenes; 'embedded deployments in hardware,
  edge devices, robotics, cameras, or appliances'; custom-trained/fine-tuned YOLO
  models in a commercial setting. [source](https://www.ultralytics.com/license)

- **RF-DETR is Apache-2.0 for Nano through Large and is the strongest
  licence-clean real-time detector in 2026** — Detection: RF-DETR-N 48.4 AP
  @384px, 2.3 ms, 30.5M params; -S 53.0 @512px, 3.5 ms, 32.1M; -M 54.7 @576px, 4.4
  ms, 33.7M; -L 56.5 @704px, 6.8 ms, 33.9M — all Apache-2.0. XL (58.6 @700px, 11.5
  ms, 126.4M) and 2XL (60.1 @880px, 17.2 ms, 126.9M) require rfdetr[plus] under
  PML 1.0. Segmentation Seg-N..Seg-L (40.3-47.1 AP) also Apache-2.0. Keypoint
  preview 71.8 AP @576px. Latency = NVIDIA T4, TensorRT FP16. ICLR 2026 paper.
  [source](https://rfdetr.roboflow.com/develop/)

- **RF-DETR is trained at multiple resolutions so you can trade accuracy for
  latency at runtime without retraining, and leads RF100-VL (transfer to real
  custom datasets)** — Roboflow: 'we train the model at multiple resolutions,
  which means we can choose to run the model at different resolutions at runtime
  to tradeoff accuracy and latency without retraining.' RF100-VL is a 100-dataset
  benchmark that explicitly includes aerial imagery. No published Jetson Orin
  Nano/NX latency figures — only T4 TensorRT10 FP16.
  [source](https://blog.roboflow.com/rf-detr/)

- **D-FINE is Apache-2.0 but its Objects365-pretrained checkpoints are NOT
  commercially clear** — D-FINE-N 42.8 AP / 2.12 ms T4 / 4M params; -S 48.5 / 3.49
  ms / 10M; -M 52.3 / 5.62 ms / 19M; -L 54.0 / 8.07 ms / 31M; -X 55.8 / 12.89 ms /
  62M. Repo warns: 'Checkpoints trained or pretrained on Objects365 (\*_obj365,
  \*_obj2coco) may be subject to the Objects365 dataset terms and should not be
  assumed to be commercially cleared under the D-FINE license.'
  [source](https://github.com/Peterande/D-FINE)

- **DEIM (Apache-2.0) is a training recipe that lifts D-FINE and RT-DETRv2 by
  ~0.5-1.5 AP at identical latency** — DEIM D-FINE: N 43.0 / 2.12 ms / 4M; S 49.0
  / 3.49 ms / 10M; M 52.7 / 5.62 ms / 19M; L 54.7 / 8.07 ms / 31M; X 56.5 / 12.89
  ms / 62M. DEIM RT-DETRv2: S 49.0 / 4.59 ms / 20M; M 50.9 / 6.40 ms; M\* 53.2 /
  6.90 ms; L 54.3 / 9.15 ms / 42M; X 55.5 / 13.66 ms / 76M.
  [source](https://github.com/ShihuaHuang95/DEIM)

- **DEIMv2 is technically excellent but licence-blocked for commercial use and
  depends on DINOv3 backbones** — Atto 23.8 AP / 0.5M / 0.8 GFLOPs / 1.10 ms;
  Femto 31.0 / 1.0M / 1.7 / 1.45; Pico 38.5 / 1.5M / 5.2 / 2.13; N 43.0 / 3.6M /
  6.8 / 2.32; S 50.9 / 9.7M / 25.6 / 5.78; M 53.0 / 18.1M / 52.2 / 8.80; L 56.0 /
  32.2M / 96.7 / 10.47; X 57.8 / 50.3M / 151.6 / 13.75. Released under a bespoke
  'DEIMv2 License' with 'For commercial licensing inquiries, please Contact Us'.
  S/M use ViT-Tiny distilled from DINOv3-S; L/X use DINOv3-S/S+ directly.
  [source](https://github.com/Intellindust-AI-Lab/DEIMv2)

- **YOLOv13 is AGPL-3.0 and is a fork of the Ultralytics codebase — it inherits
  the same commercial obligation** — Released 21 June 2025 (code) / 22 June 2025
  (weights). YOLOv13-N 41.6 mAP50-95 / 2.5M / 6.4 GFLOPs / 1.97 ms; -S 48.0 / 9.0M
  / 20.8G / 2.98 ms; -L 53.4 / 27.6M / 88.4G / 8.63 ms; -X 54.8 / 64.0M / 199.2G /
  14.67 ms. Repo states 'The code is based on Ultralytics'.
  [source](https://github.com/iMoonLab/yolov13)

- **RT-DETRv4 (ECCV 2026) distils vision foundation models into real-time DETRs
  and reaches 49.7/53.5/55.4/57.0 AP at 273/169/124/78 FPS** — arXiv 2510.25257,
  posted 29 Oct 2025, paper CC BY 4.0; official code at
  github.com/RT-DETRs/RT-DETRv4. Repository licence not separately verified —
  check before adopting. [source](https://arxiv.org/abs/2510.25257) *(likely)*

### Edge compute and accelerators

- **Jetson Orin Nano Super 8GB runs 640-px detection at ~4.6 ms FP16 / 3.8 ms INT8
  with TensorRT** — Ultralytics benchmark on Orin Nano Super Dev Kit, JetPack 7.2,
  Ultralytics 8.4.33, 640 px, batch 1, inference only (no pre/post-processing):
  YOLO26n PyTorch 15.60 ms, ONNX 15.76 ms, TensorRT FP32 7.53 ms, FP16 4.57 ms,
  INT8 3.80 ms. INT8 costs accuracy (mAP 0.449 vs 0.480 FP16 in their table).
  ~3.4× speedup FP16 vs PyTorch.
  [source](https://docs.ultralytics.com/guides/nvidia-jetson/)

- **Raspberry Pi 5 CPU-only is ~15 FPS for a nano detector at 640 px — NCNN is the
  fastest export** — RPi5, Raspberry Pi OS Bookworm, 640 px FP32, inference only:
  YOLO26n PyTorch 299.09 ms, ONNX 125.99 ms, OpenVINO 104.55 ms, NCNN 67.03 ms
  (≈15 FPS). YOLO26s NCNN 91.87 ms. Ultralytics notes YOLO26m/l/x are 'too big to
  run' usefully on a Pi.
  [source](https://docs.ultralytics.com/guides/raspberry-pi/)

- **Hailo-8L model-zoo FPS are chip-only numbers on a PCIe Gen3 ×4 host and do not
  transfer to a Raspberry Pi 5** — Hailo-8L zoo (640×640, INT8): yolov8s 44.6 mAP,
  110 FPS batch-1 / 208 batch-8; yolov8m 49.2, 51.0/87.0; yolov11n 37.5, 157/371;
  yolov11s 45.1, 92.0/192; detr_resnet_v1_18_bn 31.5 @800px, 23.4/50.0. Hailo-8
  (26 TOPS) equivalents: yolov8s 491 FPS batch-1, yolov11s 111/303. Measured on
  Intel i5-9400, PCIe Gen3 ×4, Dataflow Compiler v2.19.0, 'hw_only' synthetic
  data.
  [source](https://github.com/hailo-ai/hailo_model_zoo/blob/master/docs/public_models/HAILO8/HAILO8_object_detection.rst)

- **Hailo staff confirm the Raspberry Pi 5's single PCIe lane roughly halves
  host-to-device bandwidth versus the benchmark rig** — Hailo community response:
  'the official Model Zoo benchmarks are measured on a system with PCIe Gen3 x2
  (two lanes), while the RPi5 connects at PCIe Gen3 x1 (one lane), giving you
  roughly half the host-to-device bandwidth.' Published numbers are hw_only with
  no pre/post-processing. Users report ~28.59 FPS running yolov8s.hef end-to-end
  on a Pi 5 + Hailo-8L.
  [source](https://community.hailo.ai/t/benchmark-performance-differs-from-hailo-model-zoo-results-on-raspberry-pi-5-hailo-8l/19293)

- **Raspberry Pi AI HAT+ 2 (Hailo-10H, 40 TOPS INT4, 8 GB dedicated RAM) exists at
  $200 and is aimed at on-device LLM/VLM, not just CV** — Raspberry Pi states 40
  TOPS INT4, computer-vision performance 'comparable to the original AI HAT+ at 26
  TOPS', 8 GB of dedicated memory, 'ideal for running large language models (LLMs)
  and vision-language models (VLMs) locally', in production until at least January
  2036. The 26-TOPS Hailo-8 AI HAT+ is $110.
  [source](https://www.raspberrypi.com/products/ai-hat-plus-2/)

- **Jetson Orin Nano Super Developer Kit is listed in India at ₹31,959 + 18% GST
  (≈₹37,700 landed), $249 internationally, 67 TOPS** — ElectroPi.in listing
  ₹31,959 ex-GST (out of stock at time of check); also stocked/listed by Amazon.in
  (Cherry India), ThinkRobotics, Tanna TechBiz, MG Super Labs, Fab.to.Lab.
  Launched 17 Dec 2024, 8 GB LPDDR5.
  [source](https://www.electropi.in/nvidia-jetson-orin-nano-super-developer-kit)
  *(likely)*

### Aerial datasets, small objects and tracking

- **VisDrone2019 is the right primary fine-tuning corpus and quantifies the
  small-object problem** — 10,209 images, 54,203 annotated objects, 10 classes
  (pedestrian, people, bicycle, car, van, truck, tricycle, awning-tricycle, bus,
  motor). 68% of objects occupy fewer than 32×32 pixels. Ultralytics ships a ready
  visdrone.yaml loader.
  [source](https://docs.ultralytics.com/datasets/detect/visdrone)

- **Stock detectors score badly on VisDrone: expect ~32-40% mAP50 before any
  aerial-specific work** — Reported baselines: YOLO11n ≈32.0% mAP50, YOLO11s
  ≈39.5% mAP50 on VisDrone2019 val. 2025-26 research improvements: PC-YOLO11s
  43.8%, MSEF-YOLO11s +6.6 pts over YOLO11s, DSPE-ViT 43.2% mAP50 at ~6.0M params
  / 15.8 GFLOPs. A ready-made fine-tuned checkpoint exists at HF
  dronefreak/visdrone-yolov11s (AGPL-encumbered).
  [source](https://www.nature.com/articles/s41598-026-35301-2) *(likely)*

- **SAHI (MIT, obss/sahi) is the highest-leverage small-object trick and now
  supports RF-DETR and RT-DETR directly** — Original paper reports +6.8/+5.1/+5.3
  AP for FCOS/VFNet/TOOD from sliced inference alone, and +12.7/+13.4/+14.5 AP
  cumulative with slicing-aided fine-tuning. Framework-agnostic backends:
  Ultralytics (YOLO26/YOLO11/YOLOE), RT-DETR incl. v2, RF-DETR, HuggingFace,
  TorchVision, MMDetection, Detectron2, YOLOv5, GroundingDINO. Typical slices
  640×640 or 832×832 with ~0.2 overlap. Licence confirmed MIT (obss, 2020).
  [source](https://raw.githubusercontent.com/obss/sahi/main/LICENSE)

- **SAHI's cost is roughly linear in slice count — 4 slices is fastest, 12-15
  slices covers small objects but is prohibitive on edge** — 2026 ASAHI work:
  'fixing 4 slices yields the fastest speed, it sacrifices accuracy on small
  objects; conversely, 12 or 15 slices improve coverage but incur significant
  computational overhead', with an adaptive policy selecting 6 or 12 slices by
  input resolution. Practical implication: a 2×2 or 3×2 sweep costs 4-6× a single
  forward pass. [source](https://arxiv.org/html/2604.19233v1) *(likely)*

- **Okutama-Action is still the only sizeable aerial concurrent-human-action
  dataset and it is small** — 43 one-minute fully annotated sequences, 12 action
  classes (running, walking, lying, sitting, standing, reading, drinking,
  pushing/pulling, carrying, calling, handshaking, hugging), with abrupt camera
  movement and multi-labelled actors. Original release 2017 — old; re-verify
  licence terms directly on the repo.
  [source](https://github.com/miquelmarti/Okutama-Action) *(likely)*

- **DOTA v2.0 is the oriented-bounding-box aerial benchmark: 11,268 images,
  1,793,658 instances, 18 categories** — Annotations from Google Earth and GF-2
  satellite. Ultralytics auto-downloads a ~2 GB packaged version. Useful for OBB
  pretraining of vehicle/rooftop assets, less useful for people.
  [source](https://docs.ultralytics.com/datasets/obb/dota-v2)

- **Two genuinely new (2025-2026) aerial thermal person datasets exist and matter
  for night patrol** — AIResQ (Scientific Data, 2026): 9,788 IR images up to
  2048×1536 from drone perspectives, varying weather and terrain, for SAR.
  Extended UAV thermal human-detection benchmark (MDPI J. Imaging 11(12):436,
  2025): >75,000 thermal images (30% pure background) from ten sources incl. new
  DJI M3T mountain captures, 60/20/20 split; access by request form at
  arh.dcae.pub.ro. [source](https://www.nature.com/articles/s41597-026-07663-9)
  *(likely)*

- **Roboflow `trackers` (Apache-2.0) + `supervision` (MIT) is the licence-clean
  tracking stack; BoxMOT is AGPL-3.0** — trackers implements SORT, ByteTrack,
  OC-SORT, BoT-SORT, C-BIoU and McByte, detector-agnostic via
  supervision.Detections, Python 3.10+, ~71K monthly PyPI installs. supervision
  provides PolygonZone (filter detections inside polygons) and LineZone (count
  crossings) — i.e. tripwires and zones out of the box, MIT-licensed. BoxMOT
  (mikel-brostrom) is AGPL-3.0, v19.0.0 released 11 May 2026.
  [source](https://trackers.roboflow.com/latest/)

- **BoxMOT's MOT17-ablation table sets realistic tracker expectations: appearance
  cues buy ~2-4 HOTA over motion-only** — OccluBoost HOTA 71.10 / MOTA 78.50 /
  IDF1 85.28 (appearance); BotSORT 69.68 / 78.23 / 82.33; BoostTrack 69.25 / 75.91
  / 83.20; StrongSORT 68.05; DeepOCSORT 67.95; ByteTrack 67.68 / 78.04 / 79.16
  (motion-only); HybridSORT 67.31; OCSORT 66.44; SFSORT 62.65. ReID options
  include LightMBN, OSNet, CLIP-ReID (heavy) with auto-download. Licence AGPL-3.0.
  [source](https://github.com/mikel-brostrom/boxmot)

- **Camera-motion compensation is mandatory for drone tracking — BoT-SORT-style
  GMC via pyramidal Lucas-Kanade affine estimation is the standard fix** —
  BoT-SORT combines a Kalman filter with camera-motion compensation using global
  motion compensation (affine transforms from image keypoints tracked with
  pyramidal Lucas-Kanade optical flow). UCMCTrack (AAAI, arXiv 2312.08952) takes
  the alternative route of modelling motion on the ground plane rather than in
  image space. A 2025 multi-UAV thermal baseline pairs YOLOv12 with BoT-SORT-ReID
  (arXiv 2503.17237). [source](https://arxiv.org/pdf/2503.17237)

### Behaviour analytics and VLM triage

- **Behaviour-analytics false-alarm rates are the deployment killer, and
  abandoned-object detection is the weakest link** — Industry summary for 2026:
  'First-generation systems run 30-60% false alarms; 2026 best-of-breed systems
  achieve under 10% false alarm rates using temporal windowing, ensembles, and
  human-in-the-loop review. False-positive rate is the KPI that kills most
  deployments.' Abandoned-object detection 'must achieve high recall while keeping
  false alarms low; occlusion, lighting change, and crowd interaction are the main
  difficulties, and performance is best on isolated objects in less dynamic
  scenes.'
  [source](https://www.forasoft.com/blog/article/detecting-anomalies-surveillance-footage)
  *(likely)*

- **On UCF-Crime, classical I3D + weakly-supervised MIL still beats VLM
  approaches; VLM value is semantic describability and zero-shot speed, not AUC**
  — I3D backbones with weakly-supervised MIL heads hold ~97% AUC on UCF-Crime;
  transformer video models (TimeSformer, VideoSwin, VideoMAE) win on
  Avenue/ShanghaiTech but are cloud-only. TEVAD (I3D + SwinBERT caption
  embeddings) raises AUC from 83.1% visual-only to 85.3%. CLIP/VLM zero-shot is
  recommended when anomalies are 'semantically describable (like person climbing
  fence or package left unattended)', with lower accuracy ceilings but much higher
  velocity.
  [source](https://www.forasoft.com/blog/article/real-time-anomaly-detection-video-surveillance)
  *(likely)*

- **Moondream is the most practical small VLM for on-edge anomaly description,
  with measured Jetson latency and a cheap cloud fallback** — Moondream 3.1 = 9B
  sparse MoE with 2B active params (BSL 1.1 + Additional Use Grant: free for
  personal/research/most commercial, prohibited to resell as a hosted competing
  service). Moondream 2 = 2B dense, 'commercially friendly'; Moondream 2 0.5B for
  constrained hardware. Capabilities: Query, Caption, Detect, Point, Segment.
  Photon local engine latency 49 ms (B200) to 514 ms (Jetson AGX Orin). Cloud API
  $0.06 per 1,000 images. [source](https://moondream.ai/)

- **Cloud VLM second-opinion on alerts costs roughly ₹0.25-0.30 per alert with
  Claude Haiku 4.5** — Claude Haiku 4.5 (`claude-haiku-4-5`) is $1.00 / $5.00 per
  million input/output tokens, 200K context, vision-capable. A single ~1000×1000
  crop plus prompt ≈ 2,000 input tokens; a 200-token alert description → ~$0.003 ≈
  ₹0.27 at ₹90/USD. 100 alerts/day ≈ ₹810/month. Escalating hard cases to
  `claude-opus-5` ($5/$25 per MTok) costs ~₹1.35/alert.
  [source](https://docs.claude.com/en/docs/about-claude/pricing) *(likely)*

- **Qwen3-VL is available in 2B/4B and is documented for Jetson via vLLM AWQ-4bit,
  but its licence is NOT plain Apache-2.0** — Jetson AI Lab publishes Qwen3-VL-4B
  and 8B recipes using a vLLM container with AWQ 4-bit weights; the benchmark
  table for Orin-class devices currently reads 'No data available for this
  combination', so no verified tokens/sec on Orin Nano Super. Qwen's text models
  are Apache-2.0 but reporting indicates the VL line uses the Tongyi Qianwen
  licence with restrictions (including a separate agreement for EU deployment) —
  verify before shipping.
  [source](https://www.jetson-ai-lab.com/models/qwen3-vl-4b/) *(uncertain)*

### Plates, faces, and Indian legal / governance constraints

- **ANPR needs ≥20-25 px character height and ~100 px plate width — this is the
  physics that rules out drone ANPR at 30-50 m** — Industry design rules: 'an
  individual character must be a minimum of 20 pixels high'; 'minimum of 25 pixels
  on the vertical side of the license plate characters'; most LPR software
  requires 100-150 px across plate width, with ~100 px as Plate Recognizer's
  practical design target; minimum character stroke width 2 px.
  [source](https://platerecognizer.com/lpr-camera-resolution-guide/)

- **Worked GSD math for a DJI Mavic 3T-class payload confirms drone ANPR is only
  borderline with a tele lens at nadir and impossible with the wide** — Mavic 3T
  wide: 1/2" CMOS, 48 MP, 8000×6000, 24 mm equiv, 84° DFOV → HFOV ≈71.5°. At 40 m
  AGL nadir: swath = 2·40·tan(35.77°) = 57.6 m over 8000 px → GSD 7.2 mm/px. An
  Indian LMV plate is 500×120 mm → 69 px wide; characters ≈9 px tall — far below
  the 20-25 px floor. Mavic 3T tele: 12 MP, 4000×3000, 162 mm equiv, 15° DFOV →
  GSD ≈2.1 mm/px at 40 m → plate ≈237 px wide, characters ≈31 px — readable only
  at near-normal incidence, zero motion blur, and perfect focus.
  [source](https://enterprise.dji.com/mavic-3-enterprise/specs) *(likely)*

- **fast-plate-ocr (MIT) is the licence-clean plate OCR and is fast enough to be
  free at the gate** — Four pretrained CCT (Compact Convolutional Transformer)
  models: cct-xs-v1-global 0.3232 ms / 3094 plates/s; cct-s-v1-global 0.5877 ms /
  1702/s; cct-xs-v2-global 0.4664 ms / 2144/s; cct-s-v2-global 0.6758 ms / 1480/s
  (RTX 3090, ONNX Runtime). Models are 'global' multi-country; optional
  plate-region prediction. No India-specific checkpoint — expect to fine-tune on
  Indian plates. [source](https://github.com/ankandrew/fast-plate-ocr)

- **Indian plate geometry (HSRP): LMV 500×120 mm, MCV/HCV 340×200 mm, two-wheeler
  rear 200×100 mm, front 285×45 mm** — HSRP is aluminium with a patented chromium
  hologram, laser numbering, and retro-reflective film with 'India' at 45°. Colour
  coding: private = black on white; private EV = white on green; commercial
  transport = black on yellow; rental = yellow on black. Colour is a useful cheap
  drone-level signal even when the number is unreadable.
  [source](https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_India)

- **InsightFace code is MIT but the pretrained recognition models (buffalo_l,
  buffalo_s/m, antelopev2) are non-commercial research only** — InsightFace: 'code
  is released under the MIT License with no limitations for commercial usage.
  However, pre-trained models are for non-commercial research only.' Commercial
  licensing of the open-sourced packs goes through
  recognition-oss-pack@insightface.ai. Both manual GitHub downloads and the python
  library's auto-download are covered by the non-commercial policy.
  [source](https://www.insightface.ai/solutions/face-recognition-licensing)

- **OpenCV Zoo YuNet (detector) + SFace (recognizer) is the Apache-2.0
  commercial-friendly face pipeline if face recognition is ever required** — Both
  ship in opencv_zoo under Apache-2.0, avoiding the InsightFace weights problem
  entirely. Accuracy is materially below ArcFace/buffalo_l, which is acceptable
  for a small, opt-in resident gallery but not for open-set watchlists.
  [source](https://www.insightface.ai/solutions/face-recognition-licensing)
  *(likely)*

- **India's DPDP Rules 2025 were notified 14 November 2025 with a phased runway
  and substantive obligations biting in May 2027** — Ministry of Electronics and
  IT notified the Rules on 14 Nov 2025. Phase 1 (from Nov 2025): Data Protection
  Board of India constituted. Phase 2 (from Nov 2026): consent-manager framework
  live. Phase 3 (May 2027): all remaining substantive compliance obligations.
  Maximum penalty ₹250 crore for failure to maintain reasonable security
  safeguards. Facial images are personal data; consent is the primary lawful
  ground for FRT processing.
  [source](https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/nov/doc20251117695301.pdf)

- **Emerging Indian RWA practice is that FRT/AI analytics must be a separate,
  knowingly approved general-body decision, defaulted OFF** — 2026 housing-society
  CCTV policy guidance: 'State the default clearly: audio recording off, and any
  facial-recognition or AI analytics off unless the general body has separately,
  knowingly approved it with its own safeguards. These are high-intrusion features
  that should never arrive quietly bundled with a camera upgrade.' This is the
  governance shape your product should ship with, not the exception.
  [source](https://www.studiomatrx.org/guides/housing-society-cctv-policy-india)
  *(likely)*

### Night vision, sensor fusion and georeferencing

- **Thermal is the only thing that works at night, but 640×512 at 40 m gives only
  blob-level detection** — DJI Mavic 3T thermal: 640×512 @30 fps, 12 μm pitch, 40
  mm equiv, 61° DFOV, NETD ≤50 mK @F1.0, 28× digital zoom. Derived HFOV ≈49.4° →
  swath at 40 m AGL ≈36.8 m over 640 px → GSD ≈57 mm/px. A standing adult ≈30 px
  tall side-on, ~9 px from near-nadir: enough for 'a warm human-shaped thing is at
  these coordinates', not for classification or identity. Aircraft 920 g, 45 min
  max flight time. [source](https://enterprise.dji.com/mavic-3-enterprise/specs)
  *(likely)*

- **FLIR Lepton/Boson cores are hard to source into India — the main hobby
  distributor refuses Indian shipments** — GroupGets: 'can only ship FLIR Lepton
  to North America, Australia, United Kingdom, Switzerland, and the European Union
  Countries, and any orders with delivery addresses outside these regions will be
  canceled.' Lepton 3.5 (160×120, <50 mK, 11.8×12.7×7.2 mm) lists at $164; Boson
  640×512 modules $1,923-$2,486. DigiKey India stocks Lepton but with
  import/duty/GST overheads.
  [source](https://groupgets.com/products/flir-lepton-3-5)

- **Chinese OEM LWIR modules (InfiRay Mini2/Tiny1-C class, 256×192 or 640×512 @12
  μm) are the realistic India-importable thermal path at $230-$1,600** — InfiRay
  Mini series uses a 12 μm VOx WLP detector with an in-house ASIC, marketed for
  UAV/robotics integration in 256×192, 384×288 and 640×512 with ~9.1 mm lenses.
  Distributor pricing spans ~$230 (entry) to ~$1,600, falling to ~$1,200 at
  500-unit volumes. Note: Chinese thermal cores are NDAA-non-compliant, which
  matters only if you ever sell to government buyers.
  [source](https://www.thermal-image.com/product/mini2-640512-9mm-thermal-imaging-camera-module-for-drones/)
  *(uncertain)*

- **ONVIF Profile M is the correct standard for fusing the drone's detections with
  existing society CCTV and VMS** — Profile M standardises analytics metadata and
  event handling between edge devices and clients (VMS, NVR, cloud). It defines
  generic object classification plus specified metadata for geolocation, vehicle,
  licence plate, human face and human body; bounding boxes, centre-of-gravity,
  class labels and attributes are serialised as ONVIF Scene Description XML inside
  an RTP payload. It also defines rule configuration for events and event delivery
  over JSON/MQTT for IoT.
  [source](https://www.onvif.org/blog/2023/04/27/expanding-the-potential-of-metadata-with-profile-m/)

- **Frigate 0.17.2 (June 2026) is the pragmatic ground-CCTV analytics layer and
  now natively supports Hailo-8/8L; the project dropped its Coral recommendation
  in 2026** — Frigate auto-selects the right default model for Hailo-8 vs
  Hailo-8L. It splits work into hardware video decode (H.264/H.265) and detection
  on an accelerator. Real-time MQTT event push to Home Assistant fires within ~100
  ms of detection, versus 10-30 s polling in other NVRs. In 2026 Frigate stopped
  recommending Google Coral; Hailo is the recommended low-power detector, Intel
  iGPU the free option if already present.
  [source](https://terminalbytes.com/best-hardware-for-frigate-nvr-2026/)
  *(likely)*

- **pymap3d (BSD, v3.2.0, 8 July 2025, pure-Python, no mandatory deps) provides
  exactly the coordinate transforms georeferencing needs, including
  ray-to-ellipsoid intersection** — Supports geodetic ↔ ECEF ↔ ENU ↔ NED ↔ AER ↔
  ECI conversions plus lookAtSpheroid (given lat0, lon0, h0, azimuth and tilt,
  returns the intersection of the look ray with the WGS-84 spheroid). Python ≥3.9;
  NumPy optional for vectorised arrays. This makes ned2geodetic / enu2geodetic a
  one-liner per detection. [source](https://pypi.org/project/pymap3d/)

- **OpenDroneMap (stable 3.5.6, 7 July 2025) is the free way to build the site
  DSM/orthomosaic that georeferencing and zone-drawing depend on** — ODM processes
  drone imagery into orthomosaics, DEMs/DSMs and 3D models using GDAL and PDAL,
  understands geotagged EXIF by default, and emits camera exterior-orientation
  parameters in reconstruction.json. Published 2025 pipelines combine ODM's DEM
  plus rasterio affine transforms to convert bounding boxes to geospatial
  coordinates while correcting camera tilt and terrain variation (see MatchPlant,
  arXiv 2506.12295). [source](https://www.opendronemap.org/)

## Recommendations

| Recommendation | Rationale | Alternatives rejected |
| --- | --- | --- |
| Ship RF-DETR-S (Apache-2.0, 53.0 COCO AP @512px) as the primary detector, fine-tuned on VisDrone2019 person/car/motor/bicycle plus 2-4 weeks of site footage. Keep D-FINE-S (COCO-only checkpoint) as a licence-clean fallback and as the export target if RF-DETR's TensorRT conversion misbehaves. | It is the only 2026 detector family that is genuinely Apache-2.0 at the sizes you need, leads RF100-VL (transfer to real custom datasets, aerial included), and its multi-resolution training lets you dial 384/512/576/704 at runtime without retraining — which is exactly what you want when the drone climbs and objects shrink. RF-DETR is also NMS-free by construction, so tracker input is stable. | Ultralytics YOLO26/YOLO11 rejected: AGPL-3.0, and Ultralytics explicitly names embedded/edge and internal commercial use as Enterprise triggers — you would have to open-source the whole product including weights, or buy a licence (one reported quote ~$5,000/yr) before you have revenue. YOLOv13 rejected for the same reason (AGPL, Ultralytics fork). DEIMv2 rejected despite the best accuracy/params curve: custom licence requiring commercial contact plus a DINOv3 backbone dependency. RT-DETRv4 is promising (57.0 AP at 78 FPS) but the repo licence is unverified — revisit before v2. |
| Do the inference on the GROUND, not on the drone, for v1: stream 1080p/H.265 down, decode and run the whole CV stack on a Jetson Orin Nano Super 8GB (≈₹31,959 + 18% GST) or a mini-PC with an RTX-class GPU. Only add onboard compute when you actually need link-loss autonomy or BVLOS. | 640-px inference is 4.57 ms FP16 on Orin Nano Super, so a single ground box handles the drone stream plus several fixed cameras. You avoid the payload, power, thermal-throttling and vibration penalties on a small airframe, and you can update models without touching flight hardware. End-to-end drone→alert latency lands at ~0.6-1.5 s (encode 100-200 ms + link 150-400 ms + decode ~30 ms + inference 15-40 ms + logic), which is irrelevant for a security response measured in minutes. | Onboard Jetson Orin NX/Nano module: adds 100-200 g plus carrier, heat and a second software update path for no latency benefit that a guard can perceive. Raspberry Pi 5 + Hailo-8L: the Pi's PCIe Gen3 ×1 link cuts model-zoo throughput roughly in half (110 FPS zoo vs ~28.6 FPS measured for yolov8s), the Hailo compiler path constrains you to zoo-friendly architectures (RF-DETR is not a first-class citizen there), and Pi5 CPU-only is only ~15 FPS with NCNN. Keep the Pi 5 + AI HAT+ for the fixed ground cameras where 15-25 FPS per stream is genuinely enough. |
| Use SAHI (MIT) in a duty-cycled 'sweep' mode rather than on every frame: full-frame inference at 15-20 FPS for tracking continuity, plus a 2×2 or 3×2 sliced pass every N frames (or whenever AGL > ~35 m or the mission is in 'search' state). | Sliced inference is worth +5-7 AP on small objects but costs 4-6× a single forward pass, and at 40 m AGL a person downscaled to a 640-px network input is only ~15-25 px tall (and as little as 5-7 px from near-nadir, because an overhead human projects a ~0.5 m footprint). Duty-cycling gets you the recall on the sweep and keeps the tracker fed cheaply in between. | Always-on SAHI: drops you to 5-8 FPS on Orin Nano Super and breaks tracking. Raising network input to 1280/1536 instead: costs ~4× FLOPs anyway and still loses to slicing on sub-16-px targets. A P2 detection head: helps, but requires you to fork and maintain the architecture — do it only after slicing plus a 45-60° oblique gimbal angle has been exhausted. |
| Track with Roboflow `trackers` (Apache-2.0) + `supervision` (MIT) — ByteTrack for throughput, BoT-SORT with global motion compensation when the drone is moving. Do NOT use BoxMOT (AGPL-3.0) in the shipped product; use it only offline to benchmark. | Camera-motion compensation is non-negotiable on a drone: BoT-SORT's affine GMC from pyramidal Lucas-Kanade keypoints is what stops ID churn when the airframe yaws. supervision's PolygonZone and LineZone give you zones and tripwires with no extra dependency, and the whole stack is permissively licensed. BoxMOT's own MOT17 ablation shows appearance-based trackers only buy ~2-4 HOTA over ByteTrack — not worth an AGPL obligation. | BoxMOT (AGPL-3.0, v19.0.0) despite having the best menu (OccluBoost HOTA 71.10, BoostTrack, DeepOCSORT). Ultralytics' built-in .track() — AGPL again. UCMCTrack is architecturally attractive for drones because it models motion on the ground plane rather than in image space; consider porting its idea into your own world-coordinate tracker once georeferencing is solid. |
| Do not attempt person Re-ID across patrol passes. Re-associate identities by georeferenced world position + timestamp + coarse appearance (dominant clothing colour, height estimate, vehicle association), and treat a 'same person' link as a probabilistic hint shown to the guard, never as an assertion. | Aerial top-down/oblique views at 30-50 m destroy the fine texture that ReID embeddings depend on; a person occupies 15-30 px on the network input. Meanwhile you already have something better: once every detection has a lat/lon, a person who was at gate B two minutes ago and is now 40 m along the same path is trivially linkable by kinematics. This also sidesteps the biometric-processing question under the DPDP framework. | OSNet/LightMBN/CLIP-ReID via BoxMOT: AGPL, plus the aerial domain gap makes reported market-1501/MSMT17 numbers meaningless here. Aerial-specific ReID (PRAI-1581 lineage) is research-grade — no production-quality checkpoint you can ship. |
| Build the anomaly layer as geometric rules in WORLD coordinates first — zone intrusion, virtual tripwire with direction, dwell-time loitering, speed threshold, restricted-hours presence, occupancy count — and add a VLM only as a second-opinion filter and alert-text writer on top of a rule that already fired. | Rules in world coordinates are deterministic, explainable to an RWA committee, tunable per zone, and immune to the 30-60% false-alarm rates that kill first-generation behaviour analytics. Once every detection has a lat/lon, zones are drawn once on the ODM orthomosaic and are valid from any drone pose — you never re-draw them per camera angle. The VLM then answers one narrow question ('is this alert real, and describe it in one sentence') instead of doing open-ended anomaly detection. | End-to-end video anomaly detection (I3D+MIL, VideoMAE, memory networks): ~97% AUC on UCF-Crime does not survive contact with one society's footage, needs weeks of labelled site video, and produces an unexplainable score. Fight/violence detection, fall detection and abandoned-object detection: all still research-grade — abandoned-object in particular only works on isolated objects in low-dynamic scenes. Ship them as v2 'beta' detectors with a human in the loop, if at all. |
| For the VLM second opinion, start with Claude Haiku 4.5 in the cloud ($1/$5 per MTok ≈ ₹0.27/alert, ~₹810/month at 100 alerts/day) and keep Moondream 2/3.1 as the on-prem fallback for societies that refuse cloud. Send a 3-frame montage plus the rule that fired, and ask for a boolean plus one sentence. | Cloud is 20× cheaper than the engineering cost of maintaining an edge VLM runtime, and the volume is tiny because only fired rules escalate. Moondream is the right local option: Detect/Point/Caption/Query on 2B active params, 514 ms measured on Jetson AGX Orin, Moondream 2 explicitly 'commercially friendly'. Its cloud tier at $0.06/1K images is also the cheapest bulk option if you ever want to describe every frame. | Qwen3-VL-2B/4B: licence is likely Tongyi Qianwen not Apache-2.0, and Jetson AI Lab currently publishes no Orin-class throughput numbers — you would be flying blind on both compliance and performance. SmolVLM2 (2.2B): fast but weaker at the fine-grained security judgements you need. Running any VLM on every frame: pointless cost — the detector already tells you where to look. |
| Kill drone-based ANPR. Put ANPR on a fixed gate camera (plate detector + fast-plate-ocr, MIT, fine-tuned on Indian plates) and have the drone contribute vehicle presence, type, colour and plate-colour class (white/yellow/green/black) only. | The physics is decisive: at 40 m a 48 MP wide camera yields ~7.2 mm/px, so a 500×120 mm Indian LMV plate is ~69 px wide with ~9 px characters — against a hard floor of 20-25 px per character and ~100 px plate width. Even the 162 mm-equivalent tele only just clears the bar (≈2.1 mm/px, ~31 px characters) and only at near-normal incidence with zero motion blur. Plates are vertical surfaces; a downward-looking drone sees them foreshortened. Meanwhile a ₹15-25k fixed camera at the gate solves the problem completely with a controlled geometry. | Drone tele-camera ANPR: only works hovering nearly level with the vehicle at short range, which is unsafe, noisy and slow. Super-resolution upscaling before OCR: hallucinates characters — unacceptable when the output is a vehicle accusation. OpenALPR-derived Indian forks: mostly stale and not maintained for HSRP fonts. |
| Exclude face recognition from v1 entirely, and say so explicitly in the product description. If a society later demands it, implement it only as opt-in resident enrolment at a fixed gate kiosk using OpenCV Zoo YuNet + SFace (Apache-2.0), never on the drone, never as an open-set watchlist, defaulted OFF and requiring a separate recorded general-body resolution. | Two independent blockers. Legal: the DPDP Rules 2025 were notified 14 Nov 2025 with substantive obligations landing May 2027 and penalties up to ₹250 crore for security-safeguard failures; facial images are personal data and consent is the primary lawful ground — an RWA becomes a Data Fiduciary with notice, retention, breach-reporting and erasure duties it is structurally unequipped to discharge, and you inherit the blame. Licensing: InsightFace's buffalo_l/antelopev2 weights are non-commercial-research-only, so the default open-source face stack is not shippable. Commercially, 'we deliberately do not do face recognition' is a differentiator with residents, not a gap. | Licensing buffalo_l commercially from InsightFace: solves the weights problem, not the DPDP problem, and adds a per-deployment cost. Face recognition on the drone itself: worst of all worlds — 15-30 px faces from 40 m produce garbage embeddings AND maximum legal exposure. Face *detection* for privacy blurring is fine and recommended — that is a different feature. |
| Do not build a custom thermal payload. If night patrol is a hard requirement, buy an integrated thermal aircraft (Mavic 3T class: 640×512 @30 fps, 12 μm, 40 mm equiv, NETD ≤50 mK, 920 g, 45 min). If night patrol is not a hard requirement for v1, use RGB in lit areas only and hand night coverage to the fixed ground cameras, with the drone dispatched for verification. | Three reasons. Sourcing: FLIR's main hobby channel will not ship Lepton to India at all and FLIR cores are US export-controlled; Chinese OEM modules (InfiRay Mini2 class, $230-$1,600) are importable but NDAA-non-compliant and come with integration, calibration and ROS/GStreamer work you have not budgeted. Physics: at 40 m a 640×512 thermal gives ~57 mm/px, so a person is ~30 px side-on and ~9 px near-nadir — a warm blob with coordinates, not a classification. Honesty: a low-light RGB plus an IR illuminator does NOT solve this — a drone-mountable illuminator cannot usefully light a scene 40 m away within the power budget, so in unlit areas RGB recall is effectively zero. | FLIR Lepton 3.5 (160×120, $164): resolution is far too low for 40 m — a person would be ~2-3 px. FLIR Boson 640 ($1,923-$2,486): good core, but export friction plus ~₹1.8-2.3 lakh per unit destroys the BOM for a society-scale product. Low-light RGB + IR illuminator: fails on illuminator reach and power. A thermal blob detector is still worth wiring in as a cue-generator for an RGB confirmation pass if you go thermal. |
| Georeference every detection with this exact pipeline: (1) take the bbox foot point (bottom-centre) and undistort it; (2) back-project d_cam = normalize(K⁻¹[u,v,1]ᵀ); (3) rotate to NED with R = Rz(gimbal_yaw)·Ry(gimbal_pitch)·Rx(gimbal_roll) from the gimbal's world-frame attitude; (4) intersect with the ground: t = h_agl / d_down, giving north = t·d_north, east = t·d_east; (5) convert with pymap3d.ned2geodetic(n, e, d, lat0, lon0, h0). Replace the flat plane with an ODM-derived DSM and ray-march (bisect on terrain height) for sloped sites; pymap3d.lookAtSpheroid is the ellipsoid-only shortcut. | This is arithmetic with a BSD-licensed library (pymap3d 3.2.0, pure Python, no mandatory deps), not a research problem. The error budget is dominated by two terms: attitude error gives ground error ≈ h·sec²θ·δθ (at h=40 m, θ=45°, δθ=1° → ~1.4 m), and altitude error gives ≈ tanθ·δh (δh=2 m barometric → ~2 m). So expect 2-5 m CEP with barometric altitude and 0.5-1.5 m with RTK plus a site DSM — good enough for 'which block, which lane', not for 'which parking slot'. Barometric drift is the biggest single lever: fix it with RTK or by pre-surveying the site DSM once with OpenDroneMap (3.5.6). | Per-frame homography from 4 ground control points: excellent and more accurate for fixed waypoint presets (and worth doing as an override at each preset), but it does not generalise to free flight. Frame-to-orthomosaic feature matching for pose correction: the most robust option and the right v2 upgrade — it fixes GPS/attitude drift simultaneously — but it costs 20-50 ms/frame and needs the ODM orthomosaic built first. Depth estimation from monocular RGB: unnecessary when you already know altitude and have a ground plane. |
| Fuse ground sensors through a single MQTT event bus carrying geo-tagged, schema-versioned events, with Frigate 0.17.x (Hailo or Intel iGPU) handling the existing society CCTV, ONVIF Profile M pulled from any camera that supports it, and ESP32 nodes bridging PIR sensors, door/gate contacts and barrier relays. Correlate drone and ground events on (time window, world position, class). | Every event in the system — drone detection, camera detection, PIR trip, barrier open, gate ANPR read — becomes the same shape: {t, lat, lon, class, confidence, source, media_ref}. That makes cross-modal confirmation a spatial-temporal join rather than bespoke glue per sensor, and it makes 'PIR at the east wall → dispatch drone to waypoint 7 → confirm or clear' a three-line rule. Frigate pushes to MQTT within ~100 ms of detection (vs 10-30 s polling in commercial NVRs), and ONVIF Profile M standardises object class, bounding box, geolocation and licence-plate metadata as Scene Description XML over RTP with JSON/MQTT event delivery — so newer cameras contribute analytics without you re-decoding their streams. | Point-to-point integrations per sensor vendor: unmaintainable across societies with mixed Hikvision/CP Plus/Dahua estates. Pulling every camera's RTSP into your own detector: burns GPU you do not have and duplicates work cameras already do. A commercial VMS as the hub: adds per-channel licence cost that kills the RWA price point. |
| Set expectations numerically with the customer up front: daylight person detection at 30-40 m AGL with a 45-60° oblique gimbal, after site fine-tuning, lands around 0.55-0.70 mAP50 (zero-shot VisDrone-only is ~0.35-0.40); end-to-end alert latency 0.6-1.5 s; detection geolocation 2-5 m CEP; night RGB recall in unlit areas ≈ 0; no plate reading from the air; no face recognition. | The published research numbers people quote (97% UCF-Crime AUC, 60.1 COCO AP) are not what a society will experience, and the gap is where these deployments die. Committing to a specific, defensible envelope — and to a 2-6 week site fine-tuning period before the accuracy claim applies — converts a credibility risk into a project milestone. It also makes the oblique-gimbal requirement contractual: near-nadir flight shrinks a person to 5-7 px and is the single most common way to make the whole system look broken. | Marketing COCO/VisDrone numbers as product accuracy: guarantees a failed pilot. Promising 'AI detects anything unusual': the fastest route to a 30-60% false-alarm rate and a cancelled contract. |

## Open questions

- Onboard vs ground inference is stated as a recommendation but depends on the
  regulatory workstream: if DGCA conditions for this deployment require autonomous
  behaviour on link loss (e.g. detect-and-avoid or geofence enforcement without a
  downlink), some detection must move onboard and the Orin Nano Super dev kit must
  be replaced by an Orin NX/Nano module on a lightweight carrier. Confirm with the
  regulatory/airframe agents.
- What is the actual night-operation requirement? DGCA night-flight permissions,
  society lighting levels, and whether the RWA will accept 'ground cameras cover
  nights, the drone covers days and responds at night' materially change whether
  thermal is in the BOM at all.
- Verified India landed cost and lead time for (a) Jetson Orin Nano Super 8GB, (b)
  Raspberry Pi AI HAT+ 2 (Hailo-10H, $200), (c) an InfiRay-class 640×512 LWIR
  module. The one India price found (₹31,959 ex-GST for the Jetson) was out of
  stock.
- Does the target society have RTK/NTRIP available (e.g. a CORS base or a local
  base station)? This is the difference between 2-5 m and 0.5-1.5 m detection
  geolocation, and it decides whether zone boundaries can be drawn at parking-slot
  granularity.
- What existing CCTV estate will you integrate with, and do any of those cameras
  support ONVIF Profile M? If they are older Profile S/T-only devices, you must
  decode their RTSP yourself and the ground GPU budget grows.
- Exact licence of the RT-DETRv4 repository (RT-DETRs/RT-DETRv4) — the paper is CC
  BY 4.0 but the code licence was not verified. If Apache-2.0, it becomes a
  serious alternative to RF-DETR at 57.0 AP / 78 FPS.
- Whether Qwen3-VL 2B/4B is Apache-2.0 or Tongyi Qianwen licensed — this decides
  whether it is a viable on-edge VLM for you at all.
- How much site footage can be collected and labelled before the first paid pilot?
  The 0.55-0.70 mAP50 expectation assumes 2-4 weeks of site-specific data; with
  zero site data you are at the ~0.35-0.40 VisDrone-transfer level.
- Data residency: will societies accept cloud VLM calls (Claude/Moondream cloud)
  for alert triage, or does the DPDP posture push you to an on-prem-only mode?
  This decides whether Moondream local on the Jetson is optional or mandatory.
- Is there an insurance or police-liaison requirement that constrains retention of
  drone video (duration, encryption, access log)? DPDP retention limits and RWA
  policy will set this, and it changes storage sizing.

## Unverified or risky

The researcher could not confirm the following claims. Do not rely on any of
them without checking the primary source first.

- The Ultralytics Jetson/RPi benchmark tables report YOLO26n mAP50-95 of
  ~0.476-0.480, which does not match the official COCO figure of 40.9 — the
  benchmark almost certainly runs on a small validation subset (COCO128-style).
  Treat the LATENCY numbers as indicative and ignore the mAP column in those
  tables.
- Hailo-8L model-zoo numbers (yolov8s 110 FPS batch-1 / 208 batch-8) were read
  from the HAILO8L page in a single fetch and are internally consistent with the
  Hailo-8 page (yolov8s 491 FPS), but I could not independently re-verify the 8L
  page. The practically important number is the reported ~28.6 FPS end-to-end
  measured by users on a Pi 5 + Hailo-8L.
- Indian plate CHARACTER dimensions under Rule 50 CMVR (commonly cited as 65 mm
  height / 40 mm width / 7 mm stroke for four-wheelers) could NOT be verified —
  Wikipedia gives only overall plate sizes (LMV 500×120 mm). My ANPR pixel math
  uses the verified 500×120 mm plate and a 65 mm character height assumption; if
  the true character height differs, the per-character pixel counts shift
  proportionally, though the wide-camera conclusion (impossible at 40 m) holds
  under any plausible value.
- The Mavic 3T GSD figures (7.2 mm/px wide, 2.1 mm/px tele, 57 mm/px thermal at 40
  m) are MY derivations from DJI's published DFOV and image sizes, not
  DJI-published numbers. The DFOV→HFOV conversion assumes the stated aspect ratio
  and no significant distortion correction cropping.
- Currency conversion uses ~₹90/USD. All USD-derived INR figures (Moondream cloud,
  Claude API per-alert costs, FLIR/InfiRay module prices, AI HAT+ 2 at $200) are
  estimates before import duty and 18% GST.
- Frigate's own licence was not verified in this session (I believe MIT but did
  not confirm) — check before embedding it in a commercial deliverable rather than
  deploying it as a separate service the customer installs.
- InfiRay Mini2/Tiny1-C pricing ($230-$1,600, ~$1,200 at 500 units) came from
  aggregator/distributor pages rather than InfiRay directly, and no weight figure
  was obtained for the 256×192 module. Treat as a rough planning range only.
- The 'SSDM-YOLO: 39.6% mAP@0.5 with 2.6M params at 98 FPS on Jetson Orin Nano'
  and 'DSPE-ViT 43.2% mAP@0.5' VisDrone figures came from search snippets, not
  from fetched primary papers.
- Moondream 2's licence was not confirmed (Moondream's site says 'commercially
  friendly' and Moondream 3.1 is verified as BSL 1.1 + Additional Use Grant).
  Verify Moondream 2's exact licence on its Hugging Face card before shipping it
  on-prem.
- The '30-60% first-generation false alarm rate, under 10% for 2026 best-of-breed'
  figures come from an industry blog, not a peer-reviewed evaluation.
  Directionally right, but do not quote as a spec.
- Web search budget was exhausted before I could research (a) Indian legal
  precedent specifically on drone-mounted cameras overlooking neighbouring private
  property, and (b) aerial person Re-ID benchmarks (PRAI-1581 and successors).
  Both should be picked up by the regulatory agent and a follow-up run
  respectively.
- The Ultralytics Enterprise License price of '$5000/year' is a single anecdotal
  user report on Quora, not a published price. Ultralytics does not publish
  enterprise pricing — get a real quote before assuming it is affordable.
