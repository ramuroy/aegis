# infra — deployment and observability

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
