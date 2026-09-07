"""Tests for the geospatial primitives.

The interesting tests here are the ones that assert a *refusal*: the whole
purpose of the ``Altitude`` type is to make datum confusion impossible, so most
of its value is in the operations it declines to perform.
"""

from __future__ import annotations

import math

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from aegis.domain.geo import (
    Altitude,
    AltitudeBand,
    AltitudeDatum,
    GeoPoint,
    LocalFrame,
    LocalPoint,
    bearing_deg,
    haversine_m,
)

# A real site: a residential neighbourhood in Pune. Used as the anchor for the
# local-frame tests because the geoid undulation there is large and negative,
# which is exactly the case that catches HAE/AMSL confusion.
PUNE = GeoPoint(lat=18.5204, lon=73.8567)
PUNE_GEOID_UNDULATION_M = -64.8

# Latitudes are bounded away from the poles: the ENU tangent-plane
# approximation degenerates as cos(lat) approaches zero, and AEGIS sites are
# residential societies, not polar research stations.
_lats = st.floats(min_value=-80.0, max_value=80.0, allow_nan=False, allow_infinity=False)
_lons = st.floats(min_value=-179.0, max_value=179.0, allow_nan=False, allow_infinity=False)
_offsets = st.floats(min_value=-500.0, max_value=500.0, allow_nan=False, allow_infinity=False)


class TestAltitudeDatumSafety:
    """The type exists to prevent datum confusion. Verify it actually does."""

    def test_subtracting_different_datums_raises(self) -> None:
        agl = Altitude(30.0, AltitudeDatum.AGL)
        amsl = Altitude(590.0, AltitudeDatum.AMSL)
        with pytest.raises(TypeError, match="convert explicitly"):
            _ = agl - amsl

    def test_subtracting_same_datum_gives_a_plain_float(self) -> None:
        a = Altitude(50.0, AltitudeDatum.AGL)
        b = Altitude(30.0, AltitudeDatum.AGL)
        assert a - b == pytest.approx(20.0)

    def test_hae_to_amsl_applies_undulation_with_the_right_sign(self) -> None:
        # Over Pune the geoid sits ~65 m *below* the ellipsoid, so an aircraft
        # at 500 m HAE is at ~565 m AMSL. Getting this sign wrong is a 130 m
        # error, which is more than the entire legal altitude envelope.
        hae = Altitude(500.0, AltitudeDatum.HAE)
        amsl = hae.to_amsl(geoid_undulation_m=PUNE_GEOID_UNDULATION_M)
        assert amsl.datum is AltitudeDatum.AMSL
        assert amsl.metres == pytest.approx(564.8)

    def test_amsl_to_amsl_is_identity(self) -> None:
        amsl = Altitude(564.8, AltitudeDatum.AMSL)
        assert amsl.to_amsl(geoid_undulation_m=PUNE_GEOID_UNDULATION_M) is amsl

    def test_agl_cannot_become_amsl_without_terrain(self) -> None:
        agl = Altitude(30.0, AltitudeDatum.AGL)
        with pytest.raises(TypeError, match="without terrain data"):
            agl.to_amsl(geoid_undulation_m=PUNE_GEOID_UNDULATION_M)

    def test_amsl_to_agl_subtracts_terrain(self) -> None:
        amsl = Altitude(590.0, AltitudeDatum.AMSL)
        agl = amsl.to_agl(terrain_amsl_m=560.0)
        assert agl.datum is AltitudeDatum.AGL
        assert agl.metres == pytest.approx(30.0)

    def test_hae_to_agl_requires_going_via_amsl(self) -> None:
        hae = Altitude(500.0, AltitudeDatum.HAE)
        with pytest.raises(TypeError, match="convert .* to AMSL"):
            hae.to_agl(terrain_amsl_m=560.0)

    @pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
    def test_non_finite_altitude_rejected(self, bad: float) -> None:
        with pytest.raises(ValueError, match="finite"):
            Altitude(bad, AltitudeDatum.AGL)


class TestGeoPointValidation:
    @pytest.mark.parametrize("lat", [90.001, -90.001, 1000.0])
    def test_latitude_out_of_range_rejected(self, lat: float) -> None:
        with pytest.raises(ValueError, match="latitude"):
            GeoPoint(lat=lat, lon=0.0)

    @pytest.mark.parametrize("lon", [180.001, -180.001, 1000.0])
    def test_longitude_out_of_range_rejected(self, lon: float) -> None:
        with pytest.raises(ValueError, match="longitude"):
            GeoPoint(lat=0.0, lon=lon)

    def test_poles_and_antimeridian_accepted(self) -> None:
        GeoPoint(lat=90.0, lon=180.0)
        GeoPoint(lat=-90.0, lon=-180.0)


class TestLocalFrame:
    def test_origin_maps_to_zero(self) -> None:
        frame = LocalFrame(PUNE)
        local = frame.to_local(PUNE)
        assert local.east == pytest.approx(0.0, abs=1e-9)
        assert local.north == pytest.approx(0.0, abs=1e-9)

    def test_north_offset_is_positive_north(self) -> None:
        frame = LocalFrame(PUNE)
        # ~111 km per degree of latitude, so 0.001 deg is ~111 m north.
        local = frame.to_local(GeoPoint(lat=PUNE.lat + 0.001, lon=PUNE.lon))
        assert local.north == pytest.approx(110.6, abs=1.0)
        assert local.east == pytest.approx(0.0, abs=1e-6)

    def test_east_offset_shrinks_with_latitude(self) -> None:
        # A degree of longitude is ~105 km at Pune's latitude but only ~78 km
        # at 45 deg. If this ever comes out equal, cos(lat) has been dropped.
        at_pune = LocalFrame(PUNE).to_local(GeoPoint(lat=PUNE.lat, lon=PUNE.lon + 0.01))
        at_45 = LocalFrame(GeoPoint(lat=45.0, lon=0.0)).to_local(GeoPoint(lat=45.0, lon=0.01))
        assert at_pune.east > at_45.east

    @settings(max_examples=300, deadline=None)
    @given(lat=_lats, lon=_lons, de=_offsets, dn=_offsets)
    def test_local_geo_roundtrip_is_sub_millimetre(
        self, lat: float, lon: float, de: float, dn: float
    ) -> None:
        """to_geo(to_local(p)) == p, to well below the accuracy we ever need.

        Site extents are a few hundred metres, so the tangent-plane
        approximation should be effectively exact. If this test ever loosens,
        the georeferencing error budget in the paper needs revisiting.
        """
        frame = LocalFrame(GeoPoint(lat=lat, lon=lon))
        original = LocalPoint(east=de, north=dn)
        roundtripped = frame.to_local(frame.to_geo(original))
        assert roundtripped.east == pytest.approx(original.east, abs=1e-4)
        assert roundtripped.north == pytest.approx(original.north, abs=1e-4)

    @settings(max_examples=200, deadline=None)
    @given(lat=_lats, lon=_lons, de=_offsets, dn=_offsets)
    def test_local_frame_agrees_with_haversine(
        self, lat: float, lon: float, de: float, dn: float
    ) -> None:
        """The tangent plane and the great-circle formula must broadly agree.

        Two independent implementations of "how far apart are these" agreeing is
        decent evidence neither has a sign error or a radians/degrees mistake.

        The tolerance is 0.6%, not something tighter, and that is a real
        property of the pair rather than slack: ``LocalFrame`` is ellipsoidal
        and ``haversine_m`` is spherical, so they cannot agree better than the
        sphere-vs-ellipsoid difference. Measured worst case across latitudes for
        500 m offsets is 0.56%, at the equator on a north-south leg.

        An earlier version of this test asserted 0.1% and failed — correctly.
        The investigation found ``haversine_m`` was using the WGS-84 semi-major
        axis as its sphere radius, which biased every distance high near the
        equator (0.67% worst case). Switching to the IUGG mean radius removed
        the bias; the residual below is irreducible.
        """
        assume(math.hypot(de, dn) > 1.0)
        origin = GeoPoint(lat=lat, lon=lon)
        frame = LocalFrame(origin)
        target = frame.to_geo(LocalPoint(east=de, north=dn))

        planar = math.hypot(de, dn)
        great_circle = haversine_m(origin, target)
        assert great_circle == pytest.approx(planar, rel=6e-3)


class TestBearing:
    @pytest.mark.parametrize(
        ("dlat", "dlon", "expected"),
        [(0.01, 0.0, 0.0), (-0.01, 0.0, 180.0), (0.0, 0.01, 90.0), (0.0, -0.01, 270.0)],
    )
    def test_cardinal_directions(self, dlat: float, dlon: float, expected: float) -> None:
        got = bearing_deg(PUNE, GeoPoint(lat=PUNE.lat + dlat, lon=PUNE.lon + dlon))
        assert got == pytest.approx(expected, abs=0.1)

    @settings(max_examples=200, deadline=None)
    @given(lat=_lats, lon=_lons, de=_offsets, dn=_offsets)
    def test_bearing_always_in_range(self, lat: float, lon: float, de: float, dn: float) -> None:
        assume(math.hypot(de, dn) > 1.0)
        origin = GeoPoint(lat=lat, lon=lon)
        target = LocalFrame(origin).to_geo(LocalPoint(east=de, north=dn))
        assert 0.0 <= bearing_deg(origin, target) < 360.0

    def test_bearing_just_west_of_north_does_not_return_360(self) -> None:
        """Regression: the modulo alone let 360.0 through.

        For a target a hair west of due north, atan2 returns a tiny negative
        value; ``-1e-148 % 360.0`` is exactly 360.0 in IEEE-754 because
        ``360.0 - 1e-148`` is not representable. Code bucketing bearings into
        sectors would index off the end of its array.
        """
        origin = GeoPoint(lat=0.0, lon=0.0)
        target = LocalFrame(origin).to_geo(LocalPoint(east=-2.5e-145, north=2.0))
        assert bearing_deg(origin, target) < 360.0


class TestAltitudeBand:
    def test_mixed_datum_band_rejected(self) -> None:
        with pytest.raises(ValueError, match="mixes datums"):
            AltitudeBand(
                floor=Altitude(10.0, AltitudeDatum.AGL),
                ceiling=Altitude(20.0, AltitudeDatum.AMSL),
            )

    def test_inverted_band_rejected(self) -> None:
        with pytest.raises(ValueError, match="must exceed floor"):
            AltitudeBand(
                floor=Altitude(20.0, AltitudeDatum.AGL),
                ceiling=Altitude(10.0, AltitudeDatum.AGL),
            )

    def test_contains_is_inclusive_at_both_edges(self) -> None:
        band = AltitudeBand(
            floor=Altitude(6.0, AltitudeDatum.AGL),
            ceiling=Altitude(9.0, AltitudeDatum.AGL),
        )
        assert band.contains(Altitude(6.0, AltitudeDatum.AGL))
        assert band.contains(Altitude(9.0, AltitudeDatum.AGL))
        assert band.contains(Altitude(7.5, AltitudeDatum.AGL))
        assert not band.contains(Altitude(5.9, AltitudeDatum.AGL))
        assert not band.contains(Altitude(9.1, AltitudeDatum.AGL))

    def test_contains_rejects_wrong_datum(self) -> None:
        band = AltitudeBand(
            floor=Altitude(6.0, AltitudeDatum.AGL),
            ceiling=Altitude(9.0, AltitudeDatum.AGL),
        )
        with pytest.raises(TypeError, match="convert explicitly"):
            band.contains(Altitude(7.0, AltitudeDatum.AMSL))

    def test_second_floor_balcony_band_excludes_overflight(self) -> None:
        """The motivating case from ADR-0006.

        A second-floor balcony is protected in a band around its own height.
        An aircraft transiting at 40 m AGL must not trip it, or every transit
        over a building trips every balcony beneath it and the constraint
        becomes unenforceable in practice.
        """
        balcony = AltitudeBand(
            floor=Altitude(3.0, AltitudeDatum.AGL),
            ceiling=Altitude(9.0, AltitudeDatum.AGL),
        )
        assert balcony.contains(Altitude(6.0, AltitudeDatum.AGL))  # hovering at balcony height
        assert not balcony.contains(Altitude(40.0, AltitudeDatum.AGL))  # transiting overhead
