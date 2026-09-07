# Contributing to AEGIS

Start with [`docs/STATE.md`](docs/STATE.md) — it says where the project is and
what to do next. Then read [`docs/adr/`](docs/adr/), particularly 0002, 0003 and
0006, which are where the design actually lives.

## Setup

```bash
make doctor    # what is installed, and the exact fix for what is not
make setup     # bootstrap Python and web dependencies
make test      # should be green
make help      # everything else
```

Full toolchain instructions: [`docs/ops/setup.md`](docs/ops/setup.md). You do not
need all four toolchains — that document says what each one unlocks.

## Rules that are not negotiable

These are not style preferences. Each one is load-bearing for an ADR's analysis,
and breaking one means the ADR has to be redone before anything ships.

1. **No patches to ArduPilot C++ source.** Upstream PR, or work around it. Running
   stock upstream firmware is what keeps GPLv3 off our code
   ([ADR-0005](docs/adr/0005-ardupilot-over-px4.md)).
2. **`ultralytics` is never a dependency** — not in `services/`, not in
   `perception/`, not in a notebook, not for a one-off comparison. AGPL-3.0's
   network clause means serving inference is conveying, and a benchmark number
   produced by an AGPL import is a derivative work
   ([ADR-0004](docs/adr/0004-rf-detr-over-ultralytics-yolo.md)).
3. **Licence review is per-artefact, not per-repo.** A permissively-licensed
   repository can ship differently-licensed weights. RF-DETR XL/2XL are PML 1.0,
   not Apache-2.0. D-FINE's Objects365 checkpoints are not commercially cleared
   even though the repo is Apache-2.0. Check the artefact you are actually
   downloading.
4. **Identification is never a default, a toggle, or a premium tier.** Any feature
   that would make the system routinely emit identifiable personal data is out of
   scope, not a backlog item
   ([ADR-0006](docs/adr/0006-privacy-by-design-no-identifiable-data-by-default.md)).
5. **Every degradation must reduce capability.** Stale pose, degraded GNSS, a
   failed signature, an unhealthy sensor — each must make the system do *less*.
   If a change lets a degraded state do as much as a healthy one, it is a bug.
6. **Every reported number must be reproducible from this repository.** If you
   cannot regenerate it with a command in the repo, it does not go in the README,
   the paper, or a commit message.

## Decisions

Write an [ADR](docs/adr/) when a decision is any of:

- expensive to reverse later (data model, wire protocol, framework);
- trading one discipline's interest against another's;
- something a reasonable engineer would ask "why on earth did they do it that
  way?" about;
- a deliberate *non*-decision — something deferred, and why.

Routine choices do not get one. Copy [`docs/adr/_template.md`](docs/adr/_template.md),
take the next number, and add a row to the index.

**ADRs are immutable once `Accepted`.** Changing your mind means writing ADR *N+1*
that supersedes it, and marking the old one `Superseded by NNNN`. Never edit the
reasoning in an accepted ADR — the history of the thinking is the most valuable
part.

## Commits

Small, atomic, and explaining **why**. The diff already says what.

```
feat(domain): corroboration gate

The only thing in AEGIS that launches an aircraft. Dispatch requires
either multi-modal agreement or one high-confidence detection in a
high-value zone.

Requiring distinct nodes as well as distinct families is deliberate:
one ESP32 carrying both a PIR and a camera shares power, link and
firmware with itself, so a brownout trips both. Correlated failures
are precisely what corroboration exists to exclude.
```

Prefixes: `feat`, `fix`, `docs`, `test`, `build`, `refactor`, `style`, `chore`.
Scope is the subsystem (`domain`, `vision`, `autonomy`, `services`, `web`,
`firmware`, `adr`).

One logical change per commit. If the summary line needs an "and", it is two
commits.

## Tests

```bash
make test                      # everything
pytest tests/test_privacy.py   # one file
pytest -m "not slow"           # skip the slow ones
```

Markers: `slow`, `sitl` (needs a running SITL), `gpu`, `integration` (needs the
compose stack).

Two things this codebase expects of tests that are worth stating:

**Test the refusals.** Much of the domain model's value is in what it declines to
do — `Altitude` refusing cross-datum arithmetic, the privacy map refusing a stale
pose, the gate refusing a single-sensor event. Those tests carry more weight than
the happy paths.

**Reach for property tests on anything numerical.** Every defect found in this
codebase so far was found by Hypothesis, not by an example test: a systematic bias
in a distance function, a bearing that could return exactly 360.0, and an
undistortion that diverged at wide-lens corners. Example tests confirmed all three
were fine.

When a property test fails, work out whether the code or the property is wrong
before touching either. Two of those three findings were code bugs; one was a test
asserting a tolerance that the maths could not deliver. Loosening a tolerance to
get green is only correct when you can say *why* the looser bound is the real one —
and then that reason goes in the docstring.

## Style

`ruff` for both linting and formatting; `mypy` strict on the domain model and
services, lenient on training scripts where the numeric stack is poorly typed.

```bash
make lint
make fmt
```

Comments should explain *why*, and especially why the obvious alternative was not
chosen. A comment restating the code is noise; a comment recording that
fixed-point iteration was tried first and diverged at the image corners saves the
next person a day.
