"""Tests for the privacy map.

Weighted deliberately towards the fail-closed paths. A bug that makes the system
*over*-restrict costs a sortie; a bug that makes it under-restrict is a
cognizable offence under BNS s.77 attaching to the individual pilot. The tests
are asymmetric because the consequences are.
"""

from __future__ import annotations

import math

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from aegis.domain.geo import Altitude, AltitudeBand, AltitudeDatum, GeoPoint, LocalFrame, LocalPoint
from aegis.domain.ids import PrivacyMapId, SiteId, ZoneId
from aegis.domain.privacy import (
    AngularRegion,
    Aperture,
    ApertureKind,
    CameraPose,
    GimbalLimits,
    PrivacyMap,
    SignatureError,
    VerdictKind,
    _minimal_arc,
)

SITE_ORIGIN = GeoPoint(lat=18.5204, lon=73.8567)  # Pune
KEY = b"test-signing-key-not-a-real-one"


def _agl(m: float) -> Altitude:
    return Altitude(m, AltitudeDatum.AGL)


def _offset(east: float, north: float) -> GeoPoint:
    """A WGS-84 point at a metre offset from the site origin."""
    return LocalFrame(SITE_ORIGIN).to_geo(LocalPoint(east=east, north=north))


def _square(east: float, north: float, half: float = 2.0) -> tuple[GeoPoint, ...]:
    return (
        _offset(east - half, north - half),
        _offset(east + half, north - half),
        _offset(east + half, north + half),
        _offset(east - half, north + half),
    )


def _balcony(zone: str, east: float, north: float, floor: float = 3.0, ceiling: float = 9.0):
    return Aperture(
        id=ZoneId(zone),
        kind=ApertureKind.BALCONY,
        footprint=_square(east, north),
        band=AltitudeBand(floor=_agl(floor), ceiling=_agl(ceiling)),
        registered_by="A-402",
    )


def _map(*apertures: Aperture, signed: bool = True) -> PrivacyMap:
    m = PrivacyMap(
        id=PrivacyMapId("01JQMAPTEST0000000000000000"),
        site_id=SiteId("01JQSITETEST000000000000000"),
        version=1,
        boundary=_square(0.0, 0.0, half=200.0),
        apertures=apertures,
        origin=SITE_ORIGIN,
    )
    return m.sign(KEY) if signed else m


def _pose(
    *,
    east: float = 0.0,
    north: float = 0.0,
    agl: float = 6.0,
    uncertainty: float = 1.0,
    age: float = 0.05,
    hfov: float = 60.0,
    vfov: float = 40.0,
) -> CameraPose:
    return CameraPose(
        position=_offset(east, north),
        altitude_agl=_agl(agl),
        hfov_deg=hfov,
        vfov_deg=vfov,
        position_uncertainty_m=uncertainty,
        pose_age_s=age,
    )


class TestMinimalArc:
    """The north wrap is where naive min/max silently produces a 358-degree arc."""

    def test_simple_span(self) -> None:
        assert _minimal_arc([10.0, 20.0, 30.0]) == (10.0, 30.0)

    def test_span_across_north_takes_the_short_way(self) -> None:
        lo, hi = _minimal_arc([350.0, 355.0, 5.0, 10.0])
        assert (lo, hi) == (350.0, 10.0)
        # 20 degrees through north, not 340 the other way.
        assert (hi - lo) % 360.0 == pytest.approx(20.0)

    def test_single_azimuth(self) -> None:
        assert _minimal_arc([42.0]) == (42.0, 42.0)

    def test_empty_rejected(self) -> None:
        with pytest.raises(ValueError, match="no azimuths"):
            _minimal_arc([])

    @settings(max_examples=200, deadline=None)
    @given(st.lists(st.floats(0.0, 359.999), min_size=1, max_size=12))
    def test_arc_always_contains_every_input(self, azimuths: list[float]) -> None:
        lo, hi = _minimal_arc(azimuths)
        region = AngularRegion(lo, hi, -90.0, 90.0)
        for a in azimuths:
            assert region.contains(a, 0.0), f"{a} not in arc [{lo}, {hi}]"


class TestAngularRegion:
    def test_wrapping_region_contains_across_north(self) -> None:
        r = AngularRegion(350.0, 10.0, -30.0, 30.0)
        assert r.wraps
        assert r.contains(355.0, 0.0)
        assert r.contains(5.0, 0.0)
        assert r.contains(0.0, 0.0)
        assert not r.contains(180.0, 0.0)

    def test_elevation_bounds_respected(self) -> None:
        r = AngularRegion(0.0, 90.0, -10.0, 10.0)
        assert r.contains(45.0, 0.0)
        assert not r.contains(45.0, 45.0)

    def test_inflation_beyond_full_circle_becomes_all_azimuth(self) -> None:
        """Guards against inflation wrapping a region onto itself and inverting."""
        r = AngularRegion(0.0, 350.0, -5.0, 5.0).inflated(az_deg=20.0, el_deg=2.0)
        assert r.az_min == 0.0 and r.az_max == 360.0
        for az in (0.0, 90.0, 180.0, 270.0, 359.9):
            assert r.contains(az, 0.0)

    def test_distance_is_zero_inside(self) -> None:
        r = AngularRegion(0.0, 90.0, -10.0, 10.0)
        assert r.angular_distance_to(45.0, 0.0) == 0.0

    def test_distance_uses_short_way_round(self) -> None:
        r = AngularRegion(10.0, 20.0, -5.0, 5.0)
        # 355 is 15 degrees from 10 going through north, not 345 the long way.
        assert r.angular_distance_to(355.0, 0.0) == pytest.approx(15.0, abs=0.01)


class TestSigning:
    def test_signed_map_verifies(self) -> None:
        _map(_balcony("Z1", 0.0, 30.0)).verify(KEY)

    def test_wrong_key_fails(self) -> None:
        with pytest.raises(SignatureError):
            _map(_balcony("Z1", 0.0, 30.0)).verify(b"different-key")

    def test_unsigned_map_fails(self) -> None:
        with pytest.raises(SignatureError):
            _map(_balcony("Z1", 0.0, 30.0), signed=False).verify(KEY)

    def test_moving_an_aperture_invalidates_the_signature(self) -> None:
        """The whole guarantee of ADR-0006 rests on this."""
        signed = _map(_balcony("Z1", 0.0, 30.0))
        tampered = PrivacyMap(
            id=signed.id,
            site_id=signed.site_id,
            version=signed.version,
            boundary=signed.boundary,
            apertures=(_balcony("Z1", 0.0, 60.0),),  # moved 30 m
            origin=signed.origin,
            signature=signed.signature,
        )
        with pytest.raises(SignatureError):
            tampered.verify(KEY)

    def test_moving_the_origin_invalidates_the_signature(self) -> None:
        """The origin is in the payload because changing it moves every aperture."""
        signed = _map(_balcony("Z1", 0.0, 30.0))
        tampered = PrivacyMap(
            id=signed.id,
            site_id=signed.site_id,
            version=signed.version,
            boundary=signed.boundary,
            apertures=signed.apertures,
            origin=GeoPoint(lat=SITE_ORIGIN.lat + 0.001, lon=SITE_ORIGIN.lon),
            signature=signed.signature,
        )
        with pytest.raises(SignatureError):
            tampered.verify(KEY)

    def test_aperture_order_does_not_affect_the_signature(self) -> None:
        """Otherwise a harmless reordering would look like tampering."""
        a, b = _balcony("Z1", 0.0, 30.0), _balcony("Z2", 30.0, 0.0)
        assert _map(a, b).signature == _map(b, a).signature


class TestFailClosed:
    """Every degradation must reduce capability, never leave it unchanged."""

    def test_stale_pose_closes_the_shutter(self) -> None:
        v = _map(_balcony("Z1", 0.0, 30.0)).constrain(_pose(age=2.0), 180.0, 0.0)
        assert v.kind is VerdictKind.SHUTTER_CLOSED
        assert not v.shutter_open
        assert "old" in v.reason

    def test_degraded_position_closes_the_shutter(self) -> None:
        v = _map(_balcony("Z1", 0.0, 30.0)).constrain(_pose(uncertainty=50.0), 180.0, 0.0)
        assert v.kind is VerdictKind.SHUTTER_CLOSED
        assert "uncertainty" in v.reason

    def test_shutter_closed_stows_the_gimbal_level_not_down(self) -> None:
        """A camera stowed pointing down still frames the ground beneath it."""
        limits = GimbalLimits()
        v = _map(_balcony("Z1", 0.0, 30.0)).constrain(_pose(age=9.9), 180.0, -80.0, limits)
        assert v.elevation == limits.stow_elevation == 0.0

    def test_proximity_to_an_aperture_closes_the_shutter(self) -> None:
        """Inside the protected volume the angular projection is degenerate."""
        v = _map(_balcony("Z1", 0.0, 2.0)).constrain(_pose(), 180.0, 0.0)
        assert v.kind is VerdictKind.SHUTTER_CLOSED
        assert ZoneId("Z1") in v.triggering_apertures

    def test_degradation_never_widens_permission(self) -> None:
        """Property: worse inputs must never turn a refusal into an allowance."""
        pmap = _map(_balcony("Z1", 0.0, 30.0))
        good = pmap.constrain(_pose(uncertainty=0.5), 0.0, 0.0)
        bad = pmap.constrain(_pose(uncertainty=4.0), 0.0, 0.0)
        rank = {VerdictKind.ALLOW: 0, VerdictKind.CLAMPED: 1, VerdictKind.SHUTTER_CLOSED: 2}
        assert rank[bad.kind] >= rank[good.kind]


class TestConstraint:
    def test_looking_away_is_allowed(self) -> None:
        # Balcony is due north; look due south.
        v = _map(_balcony("Z1", 0.0, 30.0)).constrain(_pose(), 180.0, 0.0)
        assert v.kind is VerdictKind.ALLOW
        assert v.shutter_open
        assert v.azimuth == pytest.approx(180.0)

    def test_looking_straight_at_a_balcony_is_not_allowed(self) -> None:
        v = _map(_balcony("Z1", 0.0, 30.0)).constrain(_pose(), 0.0, 0.0)
        assert v.kind is not VerdictKind.ALLOW
        assert ZoneId("Z1") in v.triggering_apertures

    def test_near_miss_is_clamped_rather_than_shuttered(self) -> None:
        """Clamping preserves the sortie; shuttering throws it away."""
        # Balcony due north; command a heading just off it so a small nudge escapes.
        v = _map(_balcony("Z1", 0.0, 60.0)).constrain(_pose(), 40.0, 0.0)
        assert v.kind in (VerdictKind.ALLOW, VerdictKind.CLAMPED)
        assert v.shutter_open

    def test_clamped_direction_is_actually_permitted(self) -> None:
        """The corrective action must not itself violate the constraint."""
        pmap = _map(_balcony("Z1", 0.0, 60.0))
        v = pmap.constrain(_pose(), 5.0, 0.0)
        if v.kind is VerdictKind.CLAMPED:
            recheck = pmap.constrain(_pose(), v.azimuth, v.elevation)
            assert recheck.kind is VerdictKind.ALLOW, (
                f"clamped to {v.azimuth:.1f}/{v.elevation:.1f}, which is still forbidden"
            )

    def test_surrounded_by_apertures_closes_the_shutter(self) -> None:
        """Nowhere to look is a legitimate and expected outcome."""
        ring = [
            _balcony(f"Z{i}", 25.0 * math.sin(math.radians(a)), 25.0 * math.cos(math.radians(a)))
            for i, a in enumerate(range(0, 360, 30))
        ]
        v = _map(*ring).constrain(_pose(), 0.0, 0.0)
        assert v.kind is VerdictKind.SHUTTER_CLOSED

    def test_transiting_high_above_does_not_trip_a_balcony(self) -> None:
        """The motivating case for altitude bands (ADR-0006).

        If overflight tripped every balcony beneath it, the constraint would be
        unenforceable in practice and would be turned off.
        """
        pmap = _map(_balcony("Z1", 0.0, 30.0, floor=3.0, ceiling=9.0))
        # At 60 m AGL, 30 m north of the balcony, looking level and north: the
        # balcony is ~62 deg below the horizon, far outside a 40 deg vertical FOV.
        v = pmap.constrain(_pose(agl=60.0), 0.0, 0.0)
        assert v.kind is VerdictKind.ALLOW

    def test_hovering_at_balcony_height_does_trip_it(self) -> None:
        pmap = _map(_balcony("Z1", 0.0, 30.0, floor=3.0, ceiling=9.0))
        v = pmap.constrain(_pose(agl=6.0), 0.0, 0.0)
        assert v.kind is not VerdictKind.ALLOW

    def test_wider_fov_forbids_more(self) -> None:
        """Monotonicity: a wider lens sees more, so it must be more constrained."""
        pmap = _map(_balcony("Z1", 0.0, 60.0))
        narrow = pmap.constrain(_pose(hfov=20.0, vfov=15.0), 35.0, 0.0)
        wide = pmap.constrain(_pose(hfov=120.0, vfov=90.0), 35.0, 0.0)
        rank = {VerdictKind.ALLOW: 0, VerdictKind.CLAMPED: 1, VerdictKind.SHUTTER_CLOSED: 2}
        assert rank[wide.kind] >= rank[narrow.kind]

    def test_clamp_takes_the_smallest_total_angular_change(self) -> None:
        """Escape may be vertical, which is non-obvious but correct.

        With a balcony dead ahead, turning away in azimuth costs ~33 deg while
        tilting up over it costs ~24 deg. The search returns the smaller total
        change, so the gimbal tilts up rather than slewing round. Pinned because
        it looks like a bug in the logs until you work out why.
        """
        pmap = _map(_balcony("Z1", 0.0, 60.0))
        v = pmap.constrain(_pose(), 0.0, 0.0)
        assert v.kind is VerdictKind.CLAMPED
        assert v.elevation > 15.0, "expected a vertical escape"
        assert v.azimuth == pytest.approx(0.0, abs=1.0), "azimuth should be near-unchanged"
        # And the escape must itself be permitted.
        assert pmap.constrain(_pose(), v.azimuth, v.elevation).kind is VerdictKind.ALLOW

    def test_empty_map_allows_everything(self) -> None:
        v = _map().constrain(_pose(), 123.0, -20.0)
        assert v.kind is VerdictKind.ALLOW


class TestApertureValidation:
    def test_degenerate_footprint_rejected(self) -> None:
        with pytest.raises(ValueError, match="at least 3 vertices"):
            Aperture(
                id=ZoneId("Z1"),
                kind=ApertureKind.WINDOW,
                footprint=(_offset(0, 0), _offset(1, 1)),
                band=AltitudeBand(floor=_agl(3.0), ceiling=_agl(9.0)),
                registered_by="A-1",
            )

    def test_non_agl_band_rejected(self) -> None:
        with pytest.raises(ValueError, match="must be AGL"):
            Aperture(
                id=ZoneId("Z1"),
                kind=ApertureKind.WINDOW,
                footprint=_square(0.0, 0.0),
                band=AltitudeBand(
                    floor=Altitude(560.0, AltitudeDatum.AMSL),
                    ceiling=Altitude(570.0, AltitudeDatum.AMSL),
                ),
                registered_by="A-1",
            )
