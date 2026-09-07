"""The privacy map: one artefact that is both approved policy and runtime config.

See [ADR-0006](../../docs/adr/0006-privacy-by-design-no-identifiable-data-by-default.md).

A ``PrivacyMap`` is a signed, versioned description of the society boundary plus
every registered private aperture — window, balcony, private door, terrace. It
is simultaneously the annexure to the RWA's approved privacy policy and the
configuration that constrains the gimbal at 30 Hz. Because they are the same
file, deployed behaviour cannot drift from approved policy.

## How enforcement works

The naive approach is a boolean: "does the camera frustum intersect a protected
volume?" That answers the wrong question. It tells you a violation is occurring
but not what to do about it, so the only available response is to close the
shutter — which throws away the entire sortie because one balcony clipped the
corner of the frame.

Instead, each aperture is projected from the aircraft's *current position* into
the camera's angular space as an (azimuth, elevation) region, expanded by the
camera's half-FOV. That yields a set of **forbidden boresight directions**:
gimbal angles which, if commanded, would put the aperture somewhere in frame.

This formulation is strictly more useful. It is cheap (a handful of ``atan2``
calls per aperture, easily 30 Hz for hundreds of apertures), and it produces a
*corrective action* rather than a verdict: clamp the commanded gimbal to the
nearest permitted direction, and close the shutter only when no permitted
direction is near enough to be useful.

## Fail-closed

Every degradation path reduces capability. If the pose is stale, the GNSS
solution is degraded, or the map signature does not verify, the result is a
closed shutter and a stowed gimbal — never an unconstrained camera. Uncertainty
in the aircraft's own position is folded in as an angular inflation of every
forbidden region, so a worse position fix mechanically produces wider exclusions.
"""

from __future__ import annotations

import hashlib
import hmac
import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Final

from aegis.domain.geo import Altitude, AltitudeBand, AltitudeDatum, GeoPoint, LocalFrame, LocalPoint
from aegis.domain.ids import PrivacyMapId, SiteId, ZoneId

__all__ = [
    "AngularRegion",
    "Aperture",
    "ApertureKind",
    "CameraPose",
    "GimbalLimits",
    "PrivacyMap",
    "PrivacyVerdict",
    "SignatureError",
    "VerdictKind",
]

# Below this distance the angular projection of an aperture becomes unstable
# (the aircraft is effectively inside the protected volume) and any commanded
# direction could sweep it. Treated as an unconditional shutter-closed case.
_PROXIMITY_FLOOR_M: Final = 3.0

# How far a commanded gimbal direction may be nudged before clamping is
# considered useless and the shutter closes instead. Beyond ~25 deg the operator
# is no longer looking at what they asked for, so silently redirecting them is
# worse than an honest refusal.
_MAX_USEFUL_CLAMP_DEG: Final = 25.0


class ApertureKind(str, Enum):
    """What kind of private opening this is.

    Kept explicit rather than collapsed into "aperture" because the review
    workflow differs: a balcony is registered by the resident who owns it, while
    a stairwell window is registered by the RWA, and the two have different
    evidence requirements when a resident disputes coverage.
    """

    WINDOW = "window"
    BALCONY = "balcony"
    PRIVATE_DOOR = "private_door"
    TERRACE = "terrace"
    COURTYARD = "courtyard"


class VerdictKind(str, Enum):
    ALLOW = "allow"
    """The commanded direction is permitted as-is."""

    CLAMPED = "clamped"
    """The direction was adjusted to the nearest permitted one."""

    SHUTTER_CLOSED = "shutter_closed"
    """No useful permitted direction. Capture is inhibited."""


class SignatureError(RuntimeError):
    """The privacy map's signature did not verify.

    This is fatal by design. An unverified map is indistinguishable from a
    tampered one, and the whole guarantee of ADR-0006 is that the deployed
    constraint is the approved constraint.
    """


@dataclass(frozen=True, slots=True)
class AngularRegion:
    """A closed region of boresight directions, in degrees.

    Azimuth is a bearing clockwise from true north and wraps at 360; elevation
    is positive up, negative down, and does not wrap. The wraparound is handled
    by permitting ``az_min > az_max`` to mean "the arc through north".
    """

    az_min: float
    az_max: float
    el_min: float
    el_max: float

    @property
    def wraps(self) -> bool:
        return self.az_min > self.az_max

    def contains(self, az: float, el: float) -> bool:
        if not (self.el_min <= el <= self.el_max):
            return False
        az %= 360.0
        if self.wraps:
            return az >= self.az_min or az <= self.az_max
        return self.az_min <= az <= self.az_max

    def inflated(self, *, az_deg: float, el_deg: float) -> AngularRegion:
        """Widen the region on all sides.

        Used to fold in camera half-FOV and pose uncertainty. If inflation makes
        the azimuth span reach 360 degrees the region becomes all-azimuth, which
        is represented as the full circle rather than allowed to wrap onto
        itself and silently invert.
        """
        span = (self.az_max - self.az_min) % 360.0 if self.wraps else self.az_max - self.az_min
        if span + 2 * az_deg >= 360.0:
            return AngularRegion(0.0, 360.0, self.el_min - el_deg, self.el_max + el_deg)
        return AngularRegion(
            az_min=(self.az_min - az_deg) % 360.0,
            az_max=(self.az_max + az_deg) % 360.0,
            el_min=self.el_min - el_deg,
            el_max=self.el_max + el_deg,
        )

    def angular_distance_to(self, az: float, el: float) -> float:
        """Shortest angular distance from (az, el) to the region boundary, 0 if inside."""
        if self.contains(az, el):
            return 0.0
        d_el = max(self.el_min - el, 0.0, el - self.el_max)
        if self.wraps:
            d_az = (
                0.0
                if (az >= self.az_min or az <= self.az_max)
                else min(_arc(az, self.az_min), _arc(az, self.az_max))
            )
        else:
            d_az = (
                0.0
                if self.az_min <= az <= self.az_max
                else min(_arc(az, self.az_min), _arc(az, self.az_max))
            )
        return math.hypot(d_az, d_el)


def _arc(a: float, b: float) -> float:
    """Absolute angular separation of two bearings, in [0, 180]."""
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


@dataclass(frozen=True, slots=True)
class Aperture:
    """A registered private opening that the camera must not look into.

    ``footprint`` is the ground-projected outline of the opening as a WGS-84
    ring (not closed — the last vertex is not repeated). ``band`` is the
    vertical extent, expressed AGL, which is what makes it possible to transit
    above a building without tripping every balcony beneath it.
    """

    id: ZoneId
    kind: ApertureKind
    footprint: tuple[GeoPoint, ...]
    band: AltitudeBand
    registered_by: str
    """Flat or unit identifier of whoever registered this, for the audit trail."""

    def __post_init__(self) -> None:
        if len(self.footprint) < 3:
            raise ValueError(
                f"aperture {self.id} footprint needs at least 3 vertices, got {len(self.footprint)}"
            )
        if self.band.floor.datum is not AltitudeDatum.AGL:
            raise ValueError(
                f"aperture {self.id} band must be AGL, got {self.band.floor.datum.value} — "
                "apertures are registered relative to the ground beneath them"
            )

    def corners_local(self, frame: LocalFrame) -> list[LocalPoint]:
        """The eight-plus corners of the protected prism, in site-local ENU."""
        out: list[LocalPoint] = []
        for vertex in self.footprint:
            for height in (self.band.floor.metres, self.band.ceiling.metres):
                p = frame.to_local(vertex)
                out.append(LocalPoint(east=p.east, north=p.north, up=height))
        return out

    def angular_region_from(self, camera: LocalPoint, frame: LocalFrame) -> AngularRegion | None:
        """Project this aperture into (azimuth, elevation) as seen from ``camera``.

        Returns ``None`` if the aperture is behind nothing and in front of
        nothing — i.e. the camera is effectively inside it, where the projection
        is degenerate. Callers must treat ``None`` as unconditionally forbidden,
        not as permitted.
        """
        azimuths: list[float] = []
        elevations: list[float] = []

        for corner in self.corners_local(frame):
            de = corner.east - camera.east
            dn = corner.north - camera.north
            du = corner.up - camera.up
            horizontal = math.hypot(de, dn)
            if horizontal < _PROXIMITY_FLOOR_M:
                return None
            azimuths.append(math.degrees(math.atan2(de, dn)) % 360.0)
            elevations.append(math.degrees(math.atan2(du, horizontal)))

        az_min, az_max = _minimal_arc(azimuths)
        return AngularRegion(az_min, az_max, min(elevations), max(elevations))


def _minimal_arc(azimuths: Sequence[float]) -> tuple[float, float]:
    """Find the smallest arc containing every bearing in ``azimuths``.

    Naively taking min and max is wrong across the north wrap: bearings of 359
    and 1 degrees span two degrees through north, not 358 degrees the other way.
    Sorting and finding the largest gap gives the correct minimal arc — the
    complement of the biggest empty wedge.
    """
    if not azimuths:
        raise ValueError("no azimuths to bound")
    ordered = sorted(a % 360.0 for a in azimuths)
    if len(ordered) == 1:
        return ordered[0], ordered[0]

    widest_gap, gap_at = -1.0, 0
    for i in range(len(ordered)):
        nxt = ordered[(i + 1) % len(ordered)]
        gap = (nxt - ordered[i]) % 360.0
        if gap > widest_gap:
            widest_gap, gap_at = gap, i
    # The arc runs from just after the widest gap, round to its start.
    return ordered[(gap_at + 1) % len(ordered)], ordered[gap_at]


@dataclass(frozen=True, slots=True)
class GimbalLimits:
    """Mechanical and configured limits of the gimbal, in degrees."""

    tilt_min: float = -90.0
    tilt_max: float = 30.0
    stow_azimuth: float = 0.0
    stow_elevation: float = 0.0
    """Where the gimbal parks when capture is inhibited. Level and forward, not
    down: a stowed-down camera still frames the ground beneath the aircraft."""


@dataclass(frozen=True, slots=True)
class CameraPose:
    """Everything needed to evaluate a privacy constraint at one instant."""

    position: GeoPoint
    altitude_agl: Altitude
    hfov_deg: float
    vfov_deg: float
    position_uncertainty_m: float
    """Horizontal 95% error radius from the GNSS solution. Inflates every
    exclusion region, so a degraded fix mechanically widens the no-look cones."""
    pose_age_s: float
    """Age of the pose estimate. Stale pose is a fail-closed condition."""

    def __post_init__(self) -> None:
        if self.altitude_agl.datum is not AltitudeDatum.AGL:
            raise ValueError("camera pose altitude must be AGL")
        if not (0.0 < self.hfov_deg < 180.0 and 0.0 < self.vfov_deg < 180.0):
            raise ValueError(f"implausible FOV: {self.hfov_deg} x {self.vfov_deg}")


@dataclass(frozen=True, slots=True)
class PrivacyVerdict:
    kind: VerdictKind
    azimuth: float
    elevation: float
    shutter_open: bool
    triggering_apertures: tuple[ZoneId, ...] = ()
    reason: str = ""


@dataclass(frozen=True)
class PrivacyMap:
    """A signed, versioned set of apertures for one site."""

    id: PrivacyMapId
    site_id: SiteId
    version: int
    boundary: tuple[GeoPoint, ...]
    apertures: tuple[Aperture, ...]
    origin: GeoPoint
    """Anchor for the site-local ENU frame. Part of the signed payload, because
    changing it would silently move every aperture."""
    signature: str = ""
    max_pose_age_s: float = 0.5
    max_position_uncertainty_m: float = 5.0

    _frame: LocalFrame = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_frame", LocalFrame(self.origin))

    # --- Signing ----------------------------------------------------------

    def canonical_payload(self) -> bytes:
        """A deterministic byte encoding of everything that must not change silently.

        Hand-rolled rather than JSON-dumped because JSON key ordering, float
        repr and unicode escaping all vary between implementations, and a
        signature that depends on the serialiser version is not a signature.
        """
        parts: list[str] = [
            f"v={self.version}",
            f"site={self.site_id}",
            f"map={self.id}",
            f"origin={self.origin.lat:.9f},{self.origin.lon:.9f}",
        ]
        for pt in self.boundary:
            parts.append(f"b={pt.lat:.9f},{pt.lon:.9f}")
        for ap in sorted(self.apertures, key=lambda a: a.id):
            parts.append(
                f"a={ap.id}|{ap.kind.value}|{ap.band.floor.metres:.3f}|"
                f"{ap.band.ceiling.metres:.3f}|{ap.registered_by}"
            )
            for pt in ap.footprint:
                parts.append(f"p={pt.lat:.9f},{pt.lon:.9f}")
        return "\n".join(parts).encode("utf-8")

    def sign(self, key: bytes) -> PrivacyMap:
        sig = hmac.new(key, self.canonical_payload(), hashlib.sha256).hexdigest()
        return PrivacyMap(
            id=self.id,
            site_id=self.site_id,
            version=self.version,
            boundary=self.boundary,
            apertures=self.apertures,
            origin=self.origin,
            signature=sig,
            max_pose_age_s=self.max_pose_age_s,
            max_position_uncertainty_m=self.max_position_uncertainty_m,
        )

    def verify(self, key: bytes) -> None:
        expected = hmac.new(key, self.canonical_payload(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, self.signature):
            raise SignatureError(
                f"privacy map {self.id} v{self.version} failed signature verification"
            )

    # --- Runtime enforcement ---------------------------------------------

    def constrain(
        self,
        pose: CameraPose,
        commanded_az: float,
        commanded_el: float,
        limits: GimbalLimits | None = None,
    ) -> PrivacyVerdict:
        """Constrain a commanded gimbal direction to something permitted.

        This is the 30 Hz path. It is deliberately allocation-light and does no
        I/O; everything it needs is in the map and the pose.
        """
        limits = limits or GimbalLimits()

        # --- Fail-closed gates, checked before any geometry -----------------
        if pose.pose_age_s > self.max_pose_age_s:
            return self._closed(
                limits,
                f"pose is {pose.pose_age_s:.2f}s old, limit is {self.max_pose_age_s:.2f}s",
            )
        if pose.position_uncertainty_m > self.max_position_uncertainty_m:
            return self._closed(
                limits,
                f"position uncertainty {pose.position_uncertainty_m:.1f}m exceeds "
                f"{self.max_position_uncertainty_m:.1f}m",
            )

        camera = self._frame.to_local(pose.position, up=pose.altitude_agl.metres)

        # Pose uncertainty becomes angular inflation: the closer the aperture,
        # the more a metre of position error matters. Computed per aperture
        # against its own range rather than once globally.
        forbidden: list[tuple[AngularRegion, ZoneId]] = []
        for aperture in self.apertures:
            region = aperture.angular_region_from(camera, self._frame)
            if region is None:
                return self._closed(
                    limits,
                    f"aircraft is within {_PROXIMITY_FLOOR_M:.0f}m of aperture {aperture.id}",
                    (aperture.id,),
                )
            range_m = self._range_to(camera, aperture)
            uncertainty_deg = math.degrees(
                math.atan2(pose.position_uncertainty_m, max(range_m, _PROXIMITY_FLOOR_M))
            )
            forbidden.append(
                (
                    region.inflated(
                        az_deg=pose.hfov_deg / 2.0 + uncertainty_deg,
                        el_deg=pose.vfov_deg / 2.0 + uncertainty_deg,
                    ),
                    aperture.id,
                )
            )

        az = commanded_az % 360.0
        el = min(max(commanded_el, limits.tilt_min), limits.tilt_max)

        hits = [zid for region, zid in forbidden if region.contains(az, el)]
        if not hits:
            return PrivacyVerdict(VerdictKind.ALLOW, az, el, shutter_open=True)

        candidate = self._nearest_permitted(az, el, forbidden, limits)
        if candidate is None:
            return self._closed(limits, "no permitted direction available", tuple(hits))

        new_az, new_el = candidate
        if math.hypot(_arc(new_az, az), new_el - el) > _MAX_USEFUL_CLAMP_DEG:
            return self._closed(
                limits,
                f"nearest permitted direction is more than {_MAX_USEFUL_CLAMP_DEG:.0f} deg away",
                tuple(hits),
            )
        return PrivacyVerdict(
            VerdictKind.CLAMPED,
            new_az,
            new_el,
            shutter_open=True,
            triggering_apertures=tuple(hits),
            reason=f"clamped away from {len(hits)} aperture(s)",
        )

    def _range_to(self, camera: LocalPoint, aperture: Aperture) -> float:
        corners = aperture.corners_local(self._frame)
        return min(camera.distance_to(c) for c in corners)

    @staticmethod
    def _nearest_permitted(
        az: float,
        el: float,
        forbidden: Sequence[tuple[AngularRegion, ZoneId]],
        limits: GimbalLimits,
    ) -> tuple[float, float] | None:
        """Search outward for the closest direction outside every forbidden region.

        A coarse ring search rather than an exact boundary solve: the exact
        answer requires intersecting up to N inflated regions, and the result
        feeds a gimbal whose own pointing accuracy is coarser than the 1-degree
        step used here. Cheap and good enough beats exact and slow on a 30 Hz
        path.
        """
        for radius in range(1, int(_MAX_USEFUL_CLAMP_DEG) + 1):
            for step in range(0, 360, 15):
                theta = math.radians(step)
                cand_az = (az + radius * math.cos(theta)) % 360.0
                cand_el = el + radius * math.sin(theta)
                if not (limits.tilt_min <= cand_el <= limits.tilt_max):
                    continue
                if all(not region.contains(cand_az, cand_el) for region, _ in forbidden):
                    return cand_az, cand_el
        return None

    @staticmethod
    def _closed(
        limits: GimbalLimits, reason: str, apertures: tuple[ZoneId, ...] = ()
    ) -> PrivacyVerdict:
        return PrivacyVerdict(
            VerdictKind.SHUTTER_CLOSED,
            limits.stow_azimuth,
            limits.stow_elevation,
            shutter_open=False,
            triggering_apertures=apertures,
            reason=reason,
        )
