"""The corroboration gate: what has to be true before an aircraft leaves the pad.

This is the mechanism [ADR-0002](../../docs/adr/0002-trigger-driven-response-not-scheduled-patrol.md)
turns on. There is no patrol schedule, so this class is the *only* thing that
launches the drone, which makes it the most safety- and nuisance-relevant piece
of logic in the system.

## What counts as corroboration

Either of:

**(a) Multi-modal agreement.** At least ``min_families`` distinct
``ModalityFamily`` values, reported by at least two distinct *nodes*, within a
time window and a spatial radius.

Requiring distinct families is what filters nuisance: a monkey on the boundary
wall trips every mechanical and passive-IR sensor it touches but does not
produce a vision person-class detection. Requiring distinct nodes as well is a
deliberate extra: a single ESP32 carrying both a PIR and a camera shares power,
link and firmware with itself, so a brownout or a firmware bug can trip both.
Those failure modes correlate, and correlated failures are exactly what
corroboration is supposed to exclude.

**(b) High-confidence detection in a high-value zone.** One observation, above a
confidence threshold, inside a zone the society has designated. This is the
escape hatch for the case where multi-modal agreement is impossible because only
one sensor covers the spot.

Everything else raises a **ticket** — a human-reviewable item — and does not
launch an aircraft. That is the normal outcome and it is not a failure.

## Why the gates come after the decision

Corroboration ("is this real?") and admission ("may we fly right now?") are
separate questions with separate audit requirements. A resident complaint about
a 23:00 launch needs to distinguish "the system did not believe the alarm" from
"the system believed it but was not permitted to fly", and folding those into
one boolean destroys that distinction.
"""

from __future__ import annotations

import math
from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum

from aegis.domain.geo import GeoPoint, haversine_m
from aegis.domain.ids import DispatchId, SensorNodeId, ZoneId, new_ulid
from aegis.domain.sensing import ModalityFamily, SensorEvent, SensorNode

__all__ = [
    "CorroborationGate",
    "CorroborationPolicy",
    "Decision",
    "DecisionReason",
    "DispatchOutcome",
    "FleetState",
]

_SECONDS_PER_HOUR = 3600.0


class DispatchOutcome(str, Enum):
    DISPATCH = "dispatch"
    """Corroborated and permitted. Launch."""

    TICKET = "ticket"
    """Not corroborated. Raise a human-reviewable item; do not launch."""

    SUPPRESSED = "suppressed"
    """Corroborated, but already being handled, or inside a cooldown."""

    INHIBITED = "inhibited"
    """Corroborated and not otherwise suppressed, but flight is not permitted
    right now — night hours without opt-in, rate limit, or no available
    aircraft."""


class DecisionReason(str, Enum):
    MULTI_MODAL = "multi_modal"
    HIGH_CONFIDENCE_HIGH_VALUE = "high_confidence_high_value"
    SINGLE_SENSOR = "single_sensor"
    INSUFFICIENT_FAMILIES = "insufficient_families"
    SINGLE_NODE = "single_node"
    COOLDOWN = "cooldown"
    ALREADY_ENGAGED = "already_engaged"
    NIGHT_HOURS = "night_hours"
    RATE_LIMIT = "rate_limit"
    NO_AIRCRAFT = "no_aircraft"


@dataclass(frozen=True, slots=True)
class CorroborationPolicy:
    """Per-site tuning. Every default here is defended in ADR-0002."""

    window_s: float = 45.0
    """How long two observations may be apart and still be about the same event.
    Long enough for someone to cross a fence and be seen by a camera; short
    enough that unrelated events do not pair up."""

    radius_m: float = 40.0
    """How far apart two observations may be and still be about the same event."""

    min_families: int = 2
    min_nodes: int = 2

    high_confidence_threshold: float = 0.90
    high_value_zones: frozenset[ZoneId] = frozenset()

    cooldown_s: float = 300.0
    """After a dispatch, further events near the same place are suppressed.
    Without this, one intruder generates a dispatch every time they trip
    another sensor."""

    max_dispatches_per_hour: int = 6
    """A hard airborne-time ceiling. Battery cycle life and the noise budget are
    both functions of this number (ADR-0002)."""

    night_dispatch_enabled: bool = False
    """Off by default. CPCB Noise Rules 2000 set 45 dB(A) in residential zones
    between 22:00 and 06:00, and a 2 kg quad near an occupied facade exceeds it.
    Enabling this is a per-society decision with its own general-body
    resolution."""

    night_start_hour: int = 22
    night_end_hour: int = 6
    utc_offset_hours: float = 5.5
    """IST. Stored per site rather than read from the process environment, so a
    cloud replay in a different timezone reaches the same verdict as the edge
    node did."""

    def __post_init__(self) -> None:
        if self.min_families < 1:
            raise ValueError("min_families must be at least 1")
        if self.min_nodes < 1:
            raise ValueError("min_nodes must be at least 1")
        if not 0.0 <= self.high_confidence_threshold <= 1.0:
            raise ValueError("high_confidence_threshold must be in [0, 1]")

    def is_night(self, at_s: float) -> bool:
        """Whether ``at_s`` falls in the restricted night window, in site-local time."""
        local_hour = ((at_s / _SECONDS_PER_HOUR) + self.utc_offset_hours) % 24.0
        if self.night_start_hour > self.night_end_hour:  # window crosses midnight
            return local_hour >= self.night_start_hour or local_hour < self.night_end_hour
        return self.night_start_hour <= local_hour < self.night_end_hour


@dataclass(frozen=True, slots=True)
class FleetState:
    """What the gate needs to know about the aircraft, supplied by the caller."""

    aircraft_available: bool = True
    engaged_near: tuple[GeoPoint, ...] = ()
    """Locations already being covered by an airborne aircraft. A second
    dispatch to a spot a drone is already looking at is pure noise and battery
    burn."""


@dataclass(frozen=True, slots=True)
class Decision:
    outcome: DispatchOutcome
    reason: DecisionReason
    at_s: float
    location: GeoPoint
    contributing_events: tuple[SensorEvent, ...]
    families: frozenset[ModalityFamily]
    nodes: frozenset[SensorNodeId]
    dispatch_id: DispatchId | None = None
    detail: str = ""

    @property
    def should_launch(self) -> bool:
        return self.outcome is DispatchOutcome.DISPATCH

    @property
    def corroborated(self) -> bool:
        """Whether the gate believed the alarm, regardless of whether it flew.

        Kept distinct from ``should_launch`` so an audit can tell "did not
        believe it" apart from "believed it but was not permitted to fly"."""
        return self.reason in (
            DecisionReason.MULTI_MODAL,
            DecisionReason.HIGH_CONFIDENCE_HIGH_VALUE,
        ) or self.outcome in (DispatchOutcome.SUPPRESSED, DispatchOutcome.INHIBITED)


class CorroborationGate:
    """Stateful sliding-window correlator. One instance per site, on the edge node.

    Deliberately holds no I/O and no clock of its own: every decision is a pure
    function of the events offered and the state accumulated from prior offers.
    That is what makes a dispatch reproducible from the event log during an
    incident review, which is a requirement rather than a nicety — a resident
    disputing a launch is entitled to see why it happened.
    """

    def __init__(
        self,
        policy: CorroborationPolicy | None = None,
        nodes: Iterable[SensorNode] = (),
    ) -> None:
        self.policy = policy or CorroborationPolicy()
        self._nodes: dict[SensorNodeId, SensorNode] = {n.id: n for n in nodes}
        self._recent: deque[SensorEvent] = deque()
        self._dispatch_times: deque[float] = deque()
        self._last_dispatch: list[tuple[float, GeoPoint]] = []

    def register(self, node: SensorNode) -> None:
        self._nodes[node.id] = node

    def offer(self, event: SensorEvent, fleet: FleetState | None = None) -> Decision:
        """Offer one sensor event to the gate and get a decision."""
        fleet = fleet or FleetState()
        self._evict(before=event.at_s - self.policy.window_s)
        self._recent.append(event)

        cluster = self._cluster_around(event)
        families = frozenset(e.family for e in cluster)
        nodes = frozenset(e.node_id for e in cluster)

        verdict = self._assess(event, cluster, families, nodes)
        if verdict is None:
            return self._decide(
                DispatchOutcome.TICKET,
                self._ticket_reason(cluster, families, nodes),
                event,
                cluster,
                families,
                nodes,
            )

        # Corroborated. Now the separate question of whether we may fly.
        blocked = self._admission_check(event, fleet)
        if blocked is not None:
            outcome, reason, detail = blocked
            return self._decide(outcome, reason, event, cluster, families, nodes, detail=detail)

        self._dispatch_times.append(event.at_s)
        self._last_dispatch.append((event.at_s, event.location))
        return self._decide(
            DispatchOutcome.DISPATCH,
            verdict,
            event,
            cluster,
            families,
            nodes,
            dispatch_id=DispatchId(new_ulid()),
        )

    # --- internals --------------------------------------------------------

    def _evict(self, *, before: float) -> None:
        while self._recent and self._recent[0].at_s < before:
            self._recent.popleft()
        cutoff = before - self.policy.cooldown_s
        self._last_dispatch = [(t, p) for t, p in self._last_dispatch if t >= cutoff]

    def _cluster_around(self, event: SensorEvent) -> tuple[SensorEvent, ...]:
        """Events close enough in time and space to plausibly be the same incident.

        Only events from nodes that currently count are included: a stale or
        tampered node must not be able to supply the second family that
        authorises a launch. Events from unregistered nodes are admitted, since
        refusing them would make the gate fail *open* on a provisioning gap.
        """
        window, radius = self.policy.window_s, self.policy.radius_m
        out = []
        for candidate in self._recent:
            if abs(candidate.at_s - event.at_s) > window:
                continue
            node = self._nodes.get(candidate.node_id)
            if node is not None and not node.counts_for_corroboration:
                continue
            if haversine_m(candidate.location, event.location) > radius:
                continue
            out.append(candidate)
        return tuple(out)

    def _assess(
        self,
        event: SensorEvent,
        cluster: tuple[SensorEvent, ...],
        families: frozenset[ModalityFamily],
        nodes: frozenset[SensorNodeId],
    ) -> DecisionReason | None:
        p = self.policy
        if len(families) >= p.min_families and len(nodes) >= p.min_nodes:
            return DecisionReason.MULTI_MODAL
        if (
            event.confidence >= p.high_confidence_threshold
            and event.zone_id is not None
            and event.zone_id in p.high_value_zones
        ):
            return DecisionReason.HIGH_CONFIDENCE_HIGH_VALUE
        return None

    def _ticket_reason(
        self,
        cluster: tuple[SensorEvent, ...],
        families: frozenset[ModalityFamily],
        nodes: frozenset[SensorNodeId],
    ) -> DecisionReason:
        """Say precisely what was missing. This ends up in the operator's queue."""
        if len(cluster) <= 1:
            return DecisionReason.SINGLE_SENSOR
        if len(nodes) < self.policy.min_nodes:
            return DecisionReason.SINGLE_NODE
        return DecisionReason.INSUFFICIENT_FAMILIES

    def _admission_check(
        self, event: SensorEvent, fleet: FleetState
    ) -> tuple[DispatchOutcome, DecisionReason, str] | None:
        p = self.policy

        for at_s, where in self._last_dispatch:
            if (
                event.at_s - at_s < p.cooldown_s
                and haversine_m(where, event.location) <= p.radius_m
            ):
                return (
                    DispatchOutcome.SUPPRESSED,
                    DecisionReason.COOLDOWN,
                    f"dispatched {event.at_s - at_s:.0f}s ago within {p.radius_m:.0f}m",
                )

        for where in fleet.engaged_near:
            if haversine_m(where, event.location) <= p.radius_m:
                return (
                    DispatchOutcome.SUPPRESSED,
                    DecisionReason.ALREADY_ENGAGED,
                    "an aircraft is already covering this location",
                )

        if not fleet.aircraft_available:
            return (DispatchOutcome.INHIBITED, DecisionReason.NO_AIRCRAFT, "no aircraft available")

        if p.is_night(event.at_s) and not p.night_dispatch_enabled:
            return (
                DispatchOutcome.INHIBITED,
                DecisionReason.NIGHT_HOURS,
                f"night dispatch disabled ({p.night_start_hour:02d}:00-"
                f"{p.night_end_hour:02d}:00 local, CPCB 45 dB(A) limit)",
            )

        recent = sum(1 for t in self._dispatch_times if event.at_s - t < _SECONDS_PER_HOUR)
        if recent >= p.max_dispatches_per_hour:
            return (
                DispatchOutcome.INHIBITED,
                DecisionReason.RATE_LIMIT,
                f"{recent} dispatches in the last hour, limit is {p.max_dispatches_per_hour}",
            )

        return None

    @staticmethod
    def _decide(
        outcome: DispatchOutcome,
        reason: DecisionReason,
        event: SensorEvent,
        cluster: tuple[SensorEvent, ...],
        families: frozenset[ModalityFamily],
        nodes: frozenset[SensorNodeId],
        *,
        dispatch_id: DispatchId | None = None,
        detail: str = "",
    ) -> Decision:
        return Decision(
            outcome=outcome,
            reason=reason,
            at_s=event.at_s,
            location=_centroid([e.location for e in cluster] or [event.location]),
            contributing_events=cluster,
            families=families,
            nodes=nodes,
            dispatch_id=dispatch_id,
            detail=detail,
        )


def _centroid(points: list[GeoPoint]) -> GeoPoint:
    """Mean position of a cluster, as the point the aircraft is sent to.

    Longitude is averaged through unit vectors rather than arithmetically, so a
    cluster straddling the antimeridian does not produce a point on the opposite
    side of the planet. AEGIS sites are nowhere near 180 degrees, but a
    correctness bug that only manifests in Fiji is still a correctness bug, and
    the fix is four lines.
    """
    if len(points) == 1:
        return points[0]
    lat = sum(p.lat for p in points) / len(points)
    x = sum(math.cos(math.radians(p.lon)) for p in points) / len(points)
    y = sum(math.sin(math.radians(p.lon)) for p in points) / len(points)
    return GeoPoint(lat=lat, lon=math.degrees(math.atan2(y, x)))
