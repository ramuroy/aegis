"""Geospatial primitives.

The one idea this module exists to enforce: **an altitude is meaningless without
its reference datum**, and mixing datums is the most common source of silent,
dangerous errors in drone software.

There are four altitudes in play at any moment and they routinely differ by tens
of metres:

* **AGL** — height above the ground directly below. What a rangefinder measures
  and what obstacle clearance actually cares about.
* **AMSL** — height above mean sea level. What airspace limits are written in,
  and what a barometer reports after calibration.
* **HAE** — height above the WGS-84 ellipsoid. What raw GNSS reports. Differs
  from AMSL by the geoid undulation, which is roughly **-65 to -100 m across
  India** — one of the largest geoid anomalies anywhere on Earth. A system that
  conflates HAE and AMSL over Pune is wrong by about 65 metres, which is more
  than the entire legal altitude envelope.
* **AHL** — height above the launch/home point. What most ground stations
  display and what ``RTL_ALT_M`` is expressed in.

Conflating any two of these produces a number that looks plausible, passes every
unit test written by the person who conflated them, and flies the aircraft into
something. So ``Altitude`` carries its datum in the type, and conversions are
explicit and require the data needed to perform them.

Coordinates are WGS-84 (EPSG:4326) throughout. Site-local work uses an ENU
tangent plane anchored at a per-site origin, which is accurate to well under a
centimetre over the few-hundred-metre extent of a residential society and avoids
the projection choice entirely.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Final

__all__ = [
    "Altitude",
    "AltitudeBand",
    "AltitudeDatum",
    "GeoPoint",
    "LocalFrame",
    "LocalPoint",
    "bearing_deg",
    "haversine_m",
]

# WGS-84 defining parameters.
_WGS84_A: Final = 6_378_137.0  # semi-major axis, metres
_WGS84_F: Final = 1 / 298.257_223_563  # flattening
_WGS84_E2: Final = _WGS84_F * (2 - _WGS84_F)  # first eccentricity squared

# IUGG mean radius, R1 = (2a + b) / 3. Used for the spherical haversine.
#
# It is tempting to reuse _WGS84_A here, and wrong: the semi-major axis is the
# equatorial radius, so a sphere of that radius over-reports every distance near
# the equator. A property test comparing haversine against the ellipsoidal
# LocalFrame caught this as a systematic 0.67% bias on a north-south leg at the
# equator. The mean radius spreads the error instead of biasing it, bringing the
# worst case to 0.56%.
_WGS84_R_MEAN: Final = 6_371_008.8


class AltitudeDatum(str, Enum):
    """What an altitude is measured *from*."""

    AGL = "agl"
    """Above ground level — height over the terrain directly below."""

    AMSL = "amsl"
    """Above mean sea level — the datum airspace rules are written in."""

    HAE = "hae"
    """Height above the WGS-84 ellipsoid — what raw GNSS reports."""

    AHL = "ahl"
    """Above home/launch point — what most GCS displays and RTL_ALT_M use."""


@dataclass(frozen=True, slots=True)
class Altitude:
    """A height, inseparable from its datum.

    Arithmetic between altitudes of different datums raises rather than
    silently producing a number. That is the entire point of the type.
    """

    metres: float
    datum: AltitudeDatum

    def __post_init__(self) -> None:
        if not math.isfinite(self.metres):
            raise ValueError(f"altitude must be finite, got {self.metres}")

    def __sub__(self, other: Altitude) -> float:
        if self.datum is not other.datum:
            raise TypeError(
                f"cannot subtract {other.datum.value} altitude from "
                f"{self.datum.value} altitude — convert explicitly first"
            )
        return self.metres - other.metres

    def to_amsl(self, *, geoid_undulation_m: float) -> Altitude:
        """Convert HAE to AMSL.

        ``geoid_undulation_m`` is the local geoid height (EGM2008 or similar),
        which over India is large and negative — roughly -65 m near Pune,
        approaching -100 m off the south-east coast. There is no sensible
        default: passing the wrong sign here is a 130 m error, so the caller
        must supply it from a geoid model for the site.
        """
        if self.datum is AltitudeDatum.AMSL:
            return self
        if self.datum is not AltitudeDatum.HAE:
            raise TypeError(f"cannot convert {self.datum.value} to AMSL without terrain data")
        return Altitude(self.metres - geoid_undulation_m, AltitudeDatum.AMSL)

    def to_agl(self, *, terrain_amsl_m: float) -> Altitude:
        """Convert AMSL to AGL given the terrain elevation beneath the point."""
        if self.datum is AltitudeDatum.AGL:
            return self
        if self.datum is not AltitudeDatum.AMSL:
            raise TypeError(f"convert {self.datum.value} to AMSL before converting to AGL")
        return Altitude(self.metres - terrain_amsl_m, AltitudeDatum.AGL)

    def __str__(self) -> str:
        return f"{self.metres:.1f} m {self.datum.value.upper()}"


@dataclass(frozen=True, slots=True)
class GeoPoint:
    """A WGS-84 (EPSG:4326) position."""

    lat: float
    lon: float
    alt: Altitude | None = None

    def __post_init__(self) -> None:
        if not -90.0 <= self.lat <= 90.0:
            raise ValueError(f"latitude out of range: {self.lat}")
        if not -180.0 <= self.lon <= 180.0:
            raise ValueError(f"longitude out of range: {self.lon}")

    def __str__(self) -> str:
        base = f"{self.lat:.7f},{self.lon:.7f}"
        return f"{base} @ {self.alt}" if self.alt else base


@dataclass(frozen=True, slots=True)
class LocalPoint:
    """A position in a site-local East-North-Up tangent frame, in metres."""

    east: float
    north: float
    up: float = 0.0

    def distance_to(self, other: LocalPoint) -> float:
        return math.dist((self.east, self.north, self.up), (other.east, other.north, other.up))

    def ground_distance_to(self, other: LocalPoint) -> float:
        """Horizontal distance, ignoring altitude difference."""
        return math.hypot(self.east - other.east, self.north - other.north)


class LocalFrame:
    """An ENU tangent plane anchored at a site origin.

    Over the few-hundred-metre extent of a residential society the tangent-plane
    approximation is accurate to well under a centimetre, so this is exact for
    every purpose AEGIS has while avoiding a projected-CRS choice entirely.

    The frame is constructed once per site and reused; the trigonometry at the
    origin is computed in ``__init__`` rather than per-call because the
    georeferencing path runs this per detection per frame.
    """

    __slots__ = ("_lat0_rad", "_m_per_deg_lat", "_m_per_deg_lon", "origin")

    def __init__(self, origin: GeoPoint) -> None:
        self.origin = origin
        lat0 = math.radians(origin.lat)
        self._lat0_rad = lat0

        # Meridional and normal radii of curvature at the origin latitude.
        # Using both (rather than a spherical Earth) keeps the error below a
        # millimetre at society scale and costs two extra multiplications once.
        sin2 = math.sin(lat0) ** 2
        denom = 1.0 - _WGS84_E2 * sin2
        r_meridional = _WGS84_A * (1.0 - _WGS84_E2) / (denom**1.5)
        r_normal = _WGS84_A / math.sqrt(denom)

        self._m_per_deg_lat = math.radians(1.0) * r_meridional
        self._m_per_deg_lon = math.radians(1.0) * r_normal * math.cos(lat0)

    def to_local(self, point: GeoPoint, *, up: float = 0.0) -> LocalPoint:
        return LocalPoint(
            east=(point.lon - self.origin.lon) * self._m_per_deg_lon,
            north=(point.lat - self.origin.lat) * self._m_per_deg_lat,
            up=up,
        )

    def to_geo(self, point: LocalPoint, *, alt: Altitude | None = None) -> GeoPoint:
        return GeoPoint(
            lat=self.origin.lat + point.north / self._m_per_deg_lat,
            lon=self.origin.lon + point.east / self._m_per_deg_lon,
            alt=alt,
        )


@dataclass(frozen=True, slots=True)
class AltitudeBand:
    """A vertical slice, used by the privacy map to bound where a constraint applies.

    A balcony aperture is not protected at every altitude — the constraint that
    matters is "do not look into this opening", which applies within a band
    around the opening's height, not from the ground to the flight ceiling.
    Modelling it as a band rather than a column is what makes it possible to
    overfly a building at 40 m without tripping every balcony below.
    """

    floor: Altitude
    ceiling: Altitude

    def __post_init__(self) -> None:
        if self.floor.datum is not self.ceiling.datum:
            raise ValueError(
                f"altitude band mixes datums: floor is {self.floor.datum.value}, "
                f"ceiling is {self.ceiling.datum.value}"
            )
        if self.ceiling.metres <= self.floor.metres:
            raise ValueError(
                f"altitude band ceiling ({self.ceiling}) must exceed floor ({self.floor})"
            )

    def contains(self, alt: Altitude) -> bool:
        if alt.datum is not self.floor.datum:
            raise TypeError(
                f"cannot test {alt.datum.value} altitude against a "
                f"{self.floor.datum.value} band — convert explicitly first"
            )
        return self.floor.metres <= alt.metres <= self.ceiling.metres


def haversine_m(a: GeoPoint, b: GeoPoint) -> float:
    """Great-circle ground distance in metres, on a sphere of mean Earth radius.

    This is a *spherical* approximation of an ellipsoidal Earth, so it carries
    an inherent error of up to ~0.56% regardless of implementation quality. That
    is fine for what it is used for — coarse plausibility checks such as "is this
    detection even inside the site?" — where a ``LocalFrame`` has not already
    been constructed.

    Anywhere accuracy matters, and everywhere inside the perception loop, use
    ``LocalFrame``: it is ellipsoidal, sub-millimetre at site scale, and faster
    because the trigonometry at the origin is precomputed.
    """
    phi1, phi2 = math.radians(a.lat), math.radians(b.lat)
    dphi = phi2 - phi1
    dlam = math.radians(b.lon - a.lon)
    h = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * _WGS84_R_MEAN * math.asin(math.sqrt(h))


def bearing_deg(frm: GeoPoint, to: GeoPoint) -> float:
    """Initial great-circle bearing in degrees, clockwise from true north.

    Returns a value in ``[0, 360)``. The explicit upper-bound check is not
    redundant with the modulo: for a bearing a hair below due north, ``atan2``
    returns a tiny negative number, and ``-1e-148 % 360.0`` evaluates to exactly
    ``360.0`` in IEEE-754 because ``360.0 - 1e-148`` is not representable. A
    property test caught this; downstream code that buckets bearings into
    sectors would have indexed off the end of the array.
    """
    phi1, phi2 = math.radians(frm.lat), math.radians(to.lat)
    dlam = math.radians(to.lon - frm.lon)
    y = math.sin(dlam) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlam)
    deg = math.degrees(math.atan2(y, x)) % 360.0
    return 0.0 if deg >= 360.0 else deg
