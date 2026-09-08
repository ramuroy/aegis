# infra — deployment and observability

## Continuation boundary: 2026-09-08

This session added no CI workflow, licence checker, infrastructure deployment or
toolchain installation. The no-AGPL boundary is an accepted policy, not a claim
that automated dependency enforcement is already operating. The planned licence
checker remains unfinished. Treat setup and CI material below as plans unless
separate execution evidence is supplied. See the [handoff](../docs/HANDOFF-2026-09-08.md).


**Status:** not started.

```
compose/   the edge stack: broker, MediaMTX, inference worker, NATS leaf
k8s/       cloud manifests
grafana/   dashboards — fleet health, sensor-node health, dispatch outcomes
```

## Constraints that already apply

- **MinIO is not available for new work.** The community repository was archived
  25 April 2026, is source-only and AGPLv3. Use S3, SeaweedFS (Apache-2.0) or
  Garage.
- **EMQX ≥ 5.9 is BSL 1.1**, free production use limited to a single node. Only
  ≤ 5.8 is Apache-2.0. Mosquitto or NanoMQ instead.
- **Plain partitioned Postgres beats a dedicated TSDB** below ~10k points/sec, and
  AWS RDS does not offer the `timescaledb` extension anyway.
- **CERT-In: ICT logs retained 180 days within Indian jurisdiction**, clocks synced
  to NIC or NPL NTP. This binds today, not from 2027.

Background: [`docs/research/architecture.md`](../docs/research/architecture.md).
