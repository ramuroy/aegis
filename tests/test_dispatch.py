"""Tests for the corroboration gate.

This class is the only thing in AEGIS that launches an aircraft, so the tests
cover both directions of failure. Under-dispatching means a missed intrusion;
over-dispatching means noise complaints, battery burn, and a society that
unplugs the system. Both are covered, and the nuisance cases (a monkey tripping
three mechanical sensors) get as much attention as the real ones.
"""

from __future__ import annotations

import pytest

from aegis.domain.dispatch import (
    CorroborationGate,
    CorroborationPolicy,
    DecisionReason,
    DispatchOutcome,
    FleetState,
)
from aegis.domain.geo import GeoPoint, LocalFrame, LocalPoint
from aegis.domain.ids import EventId, SensorNodeId, SiteId, ZoneId, new_ulid
from aegis.domain.sensing import SensorClass, SensorEvent, SensorHealth, SensorNode

SITE = SiteId("01JQSITE00000000000000000")
ORIGIN = GeoPoint(lat=18.5204, lon=73.8567)
FRAME = LocalFrame(ORIGIN)
HIGH_VALUE = ZoneId("zone-clubhouse")


def _at(east: float = 0.0, north: float = 0.0) -> GeoPoint:
    return FRAME.to_geo(LocalPoint(east=east, north=north))


def _local_hour(hour: float, *, utc_offset: float = 5.5) -> float:
    """An epoch time whose site-local hour is ``hour``."""
    return ((hour - utc_offset) % 24.0) * 3600.0


def _node(name: str, cls: SensorClass, health: SensorHealth = SensorHealth.OK) -> SensorNode:
    return SensorNode(
        id=SensorNodeId(name),
        site_id=SITE,
        location=_at(),
        classes=frozenset({cls}),
        health=health,
    )


def _event(
    node: str,
    cls: SensorClass,
    at_s: float,
    *,
    east: float = 0.0,
    north: float = 0.0,
    confidence: float = 0.7,
    zone: ZoneId | None = None,
) -> SensorEvent:
    return SensorEvent(
        id=EventId(new_ulid()),
        node_id=SensorNodeId(node),
        sensor_class=cls,
        at_s=at_s,
        location=_at(east, north),
        confidence=confidence,
        zone_id=zone,
    )


def _gate(**kw) -> CorroborationGate:
    policy = CorroborationPolicy(**kw)
    return CorroborationGate(
        policy,
        nodes=[
            _node("fence-1", SensorClass.FENCE_VIBRATION),
            _node("fence-2", SensorClass.FENCE_VIBRATION),
            _node("pir-1", SensorClass.PIR_MOTION),
            _node("cam-1", SensorClass.FIXED_CAMERA_PERSON),
        ],
    )


# Daytime, so night inhibition never confounds a test that is about something else.
NOON = _local_hour(12.0)


class TestCorroboration:
    def test_single_sensor_raises_a_ticket_not_an_aircraft(self) -> None:
        d = _gate().offer(_event("fence-1", SensorClass.FENCE_VIBRATION, NOON))
        assert d.outcome is DispatchOutcome.TICKET
        assert d.reason is DecisionReason.SINGLE_SENSOR
        assert not d.should_launch
        assert not d.corroborated

    def test_two_sensors_of_the_same_family_do_not_corroborate(self) -> None:
        """The monkey case. Two fence sensors agreeing is one observation twice."""
        g = _gate()
        g.offer(_event("fence-1", SensorClass.FENCE_VIBRATION, NOON))
        d = g.offer(_event("fence-2", SensorClass.FENCE_VIBRATION, NOON + 3, east=10))
        assert d.outcome is DispatchOutcome.TICKET
        assert d.reason is DecisionReason.INSUFFICIENT_FAMILIES

    def test_two_families_from_two_nodes_dispatch(self) -> None:
        g = _gate()
        g.offer(_event("fence-1", SensorClass.FENCE_VIBRATION, NOON))
        d = g.offer(_event("cam-1", SensorClass.FIXED_CAMERA_PERSON, NOON + 5, east=12))
        assert d.outcome is DispatchOutcome.DISPATCH
        assert d.reason is DecisionReason.MULTI_MODAL
        assert d.should_launch
        assert d.dispatch_id is not None
        assert len(d.families) == 2

    def test_two_families_from_one_node_do_not_dispatch(self) -> None:
        """One board's PIR and camera share power, link and firmware.

        A brownout or a firmware bug trips both, so their failure modes
        correlate — which is exactly what corroboration is meant to exclude.
        """
        g = _gate()
        g.offer(_event("combo-1", SensorClass.PIR_MOTION, NOON))
        d = g.offer(_event("combo-1", SensorClass.FIXED_CAMERA_PERSON, NOON + 2))
        assert d.outcome is DispatchOutcome.TICKET
        assert d.reason is DecisionReason.SINGLE_NODE

    def test_events_outside_the_time_window_do_not_pair(self) -> None:
        g = _gate(window_s=30.0)
        g.offer(_event("fence-1", SensorClass.FENCE_VIBRATION, NOON))
        d = g.offer(_event("cam-1", SensorClass.FIXED_CAMERA_PERSON, NOON + 120))
        assert d.outcome is DispatchOutcome.TICKET

    def test_events_outside_the_radius_do_not_pair(self) -> None:
        g = _gate(radius_m=40.0)
        g.offer(_event("fence-1", SensorClass.FENCE_VIBRATION, NOON))
        d = g.offer(_event("cam-1", SensorClass.FIXED_CAMERA_PERSON, NOON + 5, east=300))
        assert d.outcome is DispatchOutcome.TICKET
        assert d.reason is DecisionReason.SINGLE_SENSOR

    def test_high_confidence_in_a_high_value_zone_dispatches_alone(self) -> None:
        g = _gate(high_value_zones=frozenset({HIGH_VALUE}), high_confidence_threshold=0.9)
        d = g.offer(
            _event("cam-1", SensorClass.FIXED_CAMERA_PERSON, NOON, confidence=0.95, zone=HIGH_VALUE)
        )
        assert d.outcome is DispatchOutcome.DISPATCH
        assert d.reason is DecisionReason.HIGH_CONFIDENCE_HIGH_VALUE

    def test_high_confidence_outside_a_high_value_zone_does_not(self) -> None:
        g = _gate(high_value_zones=frozenset({HIGH_VALUE}))
        d = g.offer(
            _event(
                "cam-1",
                SensorClass.FIXED_CAMERA_PERSON,
                NOON,
                confidence=0.99,
                zone=ZoneId("zone-parking"),
            )
        )
        assert d.outcome is DispatchOutcome.TICKET

    def test_low_confidence_in_a_high_value_zone_does_not(self) -> None:
        g = _gate(high_value_zones=frozenset({HIGH_VALUE}), high_confidence_threshold=0.9)
        d = g.offer(
            _event("cam-1", SensorClass.FIXED_CAMERA_PERSON, NOON, confidence=0.5, zone=HIGH_VALUE)
        )
        assert d.outcome is DispatchOutcome.TICKET


class TestUnhealthyNodes:
    def test_a_stale_node_cannot_supply_the_second_family(self) -> None:
        g = CorroborationGate(
            CorroborationPolicy(),
            nodes=[
                _node("fence-1", SensorClass.FENCE_VIBRATION, SensorHealth.STALE),
                _node("cam-1", SensorClass.FIXED_CAMERA_PERSON),
            ],
        )
        g.offer(_event("fence-1", SensorClass.FENCE_VIBRATION, NOON))
        d = g.offer(_event("cam-1", SensorClass.FIXED_CAMERA_PERSON, NOON + 5))
        assert d.outcome is DispatchOutcome.TICKET

    def test_a_tampered_node_cannot_supply_the_second_family(self) -> None:
        g = CorroborationGate(
            CorroborationPolicy(),
            nodes=[
                _node("fence-1", SensorClass.FENCE_VIBRATION, SensorHealth.TAMPERED),
                _node("cam-1", SensorClass.FIXED_CAMERA_PERSON),
            ],
        )
        g.offer(_event("fence-1", SensorClass.FENCE_VIBRATION, NOON))
        d = g.offer(_event("cam-1", SensorClass.FIXED_CAMERA_PERSON, NOON + 5))
        assert d.outcome is DispatchOutcome.TICKET

    def test_a_degraded_node_still_counts(self) -> None:
        """Degraded means low battery or a noisy link, not untrustworthy."""
        g = CorroborationGate(
            CorroborationPolicy(),
            nodes=[
                _node("fence-1", SensorClass.FENCE_VIBRATION, SensorHealth.DEGRADED),
                _node("cam-1", SensorClass.FIXED_CAMERA_PERSON),
            ],
        )
        g.offer(_event("fence-1", SensorClass.FENCE_VIBRATION, NOON))
        d = g.offer(_event("cam-1", SensorClass.FIXED_CAMERA_PERSON, NOON + 5))
        assert d.outcome is DispatchOutcome.DISPATCH

    def test_an_unregistered_node_is_admitted(self) -> None:
        """Refusing unknown nodes would make the gate fail open on a
        provisioning gap — the sensor reports, nothing corroborates, and the
        site silently stops dispatching."""
        g = _gate()
        g.offer(_event("brand-new-node", SensorClass.PIR_MOTION, NOON))
        d = g.offer(_event("cam-1", SensorClass.FIXED_CAMERA_PERSON, NOON + 5))
        assert d.outcome is DispatchOutcome.DISPATCH


class TestAdmissionGates:
    def _corroborate(self, g: CorroborationGate, t: float, **kw):
        g.offer(_event("fence-1", SensorClass.FENCE_VIBRATION, t, **kw))
        return g.offer(_event("cam-1", SensorClass.FIXED_CAMERA_PERSON, t + 2, **kw))

    def test_cooldown_suppresses_a_second_dispatch_nearby(self) -> None:
        g = _gate(cooldown_s=300.0)
        assert self._corroborate(g, NOON).outcome is DispatchOutcome.DISPATCH
        d = self._corroborate(g, NOON + 60, east=10)
        assert d.outcome is DispatchOutcome.SUPPRESSED
        assert d.reason is DecisionReason.COOLDOWN

    def test_cooldown_expires(self) -> None:
        g = _gate(cooldown_s=300.0)
        assert self._corroborate(g, NOON).outcome is DispatchOutcome.DISPATCH
        assert self._corroborate(g, NOON + 400).outcome is DispatchOutcome.DISPATCH

    def test_cooldown_is_local_not_site_wide(self) -> None:
        """A second intrusion 300 m away is a real second incident."""
        g = _gate(cooldown_s=300.0, radius_m=40.0)
        assert self._corroborate(g, NOON).outcome is DispatchOutcome.DISPATCH
        assert self._corroborate(g, NOON + 60, east=300).outcome is DispatchOutcome.DISPATCH

    def test_already_engaged_suppresses(self) -> None:
        g = _gate()
        g.offer(_event("fence-1", SensorClass.FENCE_VIBRATION, NOON))
        d = g.offer(
            _event("cam-1", SensorClass.FIXED_CAMERA_PERSON, NOON + 2),
            FleetState(engaged_near=(_at(5, 5),)),
        )
        assert d.outcome is DispatchOutcome.SUPPRESSED
        assert d.reason is DecisionReason.ALREADY_ENGAGED

    def test_no_aircraft_inhibits(self) -> None:
        g = _gate()
        g.offer(_event("fence-1", SensorClass.FENCE_VIBRATION, NOON))
        d = g.offer(
            _event("cam-1", SensorClass.FIXED_CAMERA_PERSON, NOON + 2),
            FleetState(aircraft_available=False),
        )
        assert d.outcome is DispatchOutcome.INHIBITED
        assert d.reason is DecisionReason.NO_AIRCRAFT

    def test_night_inhibits_by_default(self) -> None:
        g = _gate()
        d = self._corroborate(g, _local_hour(23.0))
        assert d.outcome is DispatchOutcome.INHIBITED
        assert d.reason is DecisionReason.NIGHT_HOURS
        assert "45 dB(A)" in d.detail

    def test_night_dispatch_when_the_society_has_opted_in(self) -> None:
        g = _gate(night_dispatch_enabled=True)
        assert self._corroborate(g, _local_hour(23.0)).outcome is DispatchOutcome.DISPATCH

    def test_early_morning_is_night(self) -> None:
        g = _gate()
        assert self._corroborate(g, _local_hour(3.0)).outcome is DispatchOutcome.INHIBITED

    def test_rate_limit_inhibits(self) -> None:
        g = _gate(max_dispatches_per_hour=2, cooldown_s=0.0)
        assert self._corroborate(g, NOON).outcome is DispatchOutcome.DISPATCH
        assert self._corroborate(g, NOON + 100).outcome is DispatchOutcome.DISPATCH
        d = self._corroborate(g, NOON + 200)
        assert d.outcome is DispatchOutcome.INHIBITED
        assert d.reason is DecisionReason.RATE_LIMIT

    def test_inhibited_still_counts_as_corroborated(self) -> None:
        """Audit must distinguish 'did not believe it' from 'could not fly'.

        A resident disputing a decision is entitled to that distinction, and
        collapsing both into a boolean destroys it.
        """
        g = _gate()
        d = self._corroborate(g, _local_hour(23.0))
        assert d.outcome is DispatchOutcome.INHIBITED
        assert d.corroborated
        assert not d.should_launch


class TestNightWindow:
    @pytest.mark.parametrize(
        ("hour", "expected"),
        [
            (22.0, True),
            (23.5, True),
            (0.5, True),
            (5.9, True),
            (6.0, False),
            (12.0, False),
            (21.9, False),
        ],
    )
    def test_boundaries(self, hour: float, expected: bool) -> None:
        p = CorroborationPolicy()
        assert p.is_night(_local_hour(hour)) is expected

    def test_timezone_is_per_site_not_from_the_environment(self) -> None:
        """A cloud replay in UTC must reach the same verdict the edge node did."""
        ist = CorroborationPolicy(utc_offset_hours=5.5)
        utc = CorroborationPolicy(utc_offset_hours=0.0)
        t = _local_hour(23.0, utc_offset=5.5)
        assert ist.is_night(t)
        assert not utc.is_night(t)  # 17:30 UTC is daytime


class TestDecisionPayload:
    def test_decision_reports_contributing_evidence(self) -> None:
        g = _gate()
        g.offer(_event("fence-1", SensorClass.FENCE_VIBRATION, NOON))
        d = g.offer(_event("cam-1", SensorClass.FIXED_CAMERA_PERSON, NOON + 2, east=10))
        assert len(d.contributing_events) == 2
        assert d.nodes == {SensorNodeId("fence-1"), SensorNodeId("cam-1")}

    def test_dispatch_location_is_the_cluster_centroid(self) -> None:
        g = _gate()
        g.offer(_event("fence-1", SensorClass.FENCE_VIBRATION, NOON, east=0, north=0))
        d = g.offer(_event("cam-1", SensorClass.FIXED_CAMERA_PERSON, NOON + 2, east=20, north=0))
        local = FRAME.to_local(d.location)
        assert local.east == pytest.approx(10.0, abs=1.0)
        assert local.north == pytest.approx(0.0, abs=1.0)


class TestPolicyValidation:
    def test_min_families_must_be_positive(self) -> None:
        with pytest.raises(ValueError, match="min_families"):
            CorroborationPolicy(min_families=0)

    def test_threshold_must_be_a_probability(self) -> None:
        with pytest.raises(ValueError, match="high_confidence_threshold"):
            CorroborationPolicy(high_confidence_threshold=1.5)
