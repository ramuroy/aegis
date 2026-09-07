"""Georeferencing: a detection's pixel box becomes a position on the ground.

Everything downstream of the detector works in world coordinates — the
corroboration gate correlates by distance, the privacy map reasons about
apertures, the operator sees a pin on a map. So this module is the bridge, and
its accuracy sets a floor on everything above it.

## The method

1. Take the **foot point** of the bounding box (bottom-centre), not the centre.
   A person's feet are on the ground; their centroid is about a metre above it,
   and at a 30-degree depression angle that metre becomes ~1.7 m of horizontal
   error. Using the centre is the single most common mistake in drone
   georeferencing and it produces a bias, not noise, so it never averages out.
2. Undistort that pixel to an ideal ray in the camera frame.
3. Rotate the ray into world ENU using the gimbal's absolute attitude.
4. Intersect with the ground — a flat plane by default, or a site DSM.

## The error budget is the actual product

A position without an uncertainty is not usable for correlation: the
corroboration gate needs to know whether two observations 15 m apart are the
same event or two different ones, and that depends entirely on how well each is
known. So this module propagates the three dominant terms analytically and
reports which one dominates.

For a camera at height `h` looking down at depression angle `ε`, the horizontal
ground range is `R = h / tan(ε)`. Differentiating:

| Source | Sensitivity | Note |
| --- | --- | --- |
| Altitude `δh` | `∂R/∂h = 1/tan(ε) = R/h` | Barometric drift dominates without RTK |
| Attitude `δε` | `∂R/∂ε = h / sin²(ε)` | Blows up near the horizon |
| Position `δp` | `1` | Enters directly, GNSS-limited |

The `1/sin²(ε)` term is why shallow look angles are refused rather than merely
flagged: at 10 degrees depression, one milliradian of gimbal error becomes
33 cm at 40 m range, and the small-object detection quality is already poor
there. Below ``MIN_DEPRESSION_DEG`` the result is not returned.

Expected performance, consistent with the numbers in `docs/research/cv-models.md`:
**2-5 m CEP** on barometric altitude, **0.5-1.5 m** with RTK and a site DSM.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Final, Protocol

from aegis.domain.geo import Altitude, AltitudeDatum, GeoPoint, LocalFrame, LocalPoint
from aegis.vision.camera import CameraIntrinsics

__all__ = [
    "MIN_DEPRESSION_DEG",
    "ErrorTerm",
    "FlatGround",
    "GeoreferenceResult",
    "GimbalAttitude",
    "GroundModel",
    "PoseUncertainty",
    "georeference",
]

# Below this depression angle the 1/sin^2 attitude sensitivity makes the result
# worse than useless, and it degrades fast: 20 deg is ~8.5x the error of 45 deg,
# 10 deg is ~33x. Detections near the horizon are dropped, not merely flagged.
MIN_DEPRESSION_DEG: Final = 12.0

# Ratio at which one error term is called dominant rather than the budget being
# reported as mixed. Chosen so "altitude-dominated" means "fix the altitude
# source and the problem goes away", which is actionable.
_DOMINANCE_RATIO: Final = 1.5


class ErrorTerm(str, Enum):
    ALTITUDE = "altitude"
    ATTITUDE = "attitude"
    POSITION = "position"
    MIXED = "mixed"


@dataclass(frozen=True, slots=True)
class GimbalAttitude:
    """Absolute camera attitude, as a three-axis stabilised gimbal reports it.

    ``azimuth_deg`` is a bearing clockwise from true north. ``elevation_deg`` is
    positive up, so a downward-looking camera has a negative elevation and a
    *depression* angle of ``-elevation_deg``.
    """

    azimuth_deg: float
    elevation_deg: float
    roll_deg: float = 0.0

    @property
    def depression_deg(self) -> float:
        return -self.elevation_deg


@dataclass(frozen=True, slots=True)
class PoseUncertainty:
    """One-sigma uncertainties on the aircraft's own state."""

    altitude_m: float = 2.0
    """Barometric altitude is the usual weak link. A tuned baro drifts 1-3 m
    over a sortie; RTK with a site DSM gets this to ~0.1 m."""

    attitude_deg: float = 0.5
    """Combined gimbal encoder and IMU attitude error."""

    position_m: float = 1.5
    """Horizontal GNSS error. ~1.5 m for a good multi-band fix, ~0.02 m RTK."""

    @classmethod
    def rtk_with_dsm(cls) -> PoseUncertainty:
        return cls(altitude_m=0.1, attitude_deg=0.3, position_m=0.02)


class GroundModel(Protocol):
    """Where the ground is. Implemented by a flat plane or a site DSM."""

    def height_at(self, point: LocalPoint) -> float:
        """Ground height in metres, in the site-local ENU frame."""
        ...


@dataclass(frozen=True, slots=True)
class FlatGround:
    """A horizontal plane. Adequate for most societies, which are graded flat."""

    height_m: float = 0.0

    def height_at(self, point: LocalPoint) -> float:
        return self.height_m


@dataclass(frozen=True, slots=True)
class GeoreferenceResult:
    position: GeoPoint
    local: LocalPoint
    ground_range_m: float
    depression_deg: float
    horizontal_uncertainty_m: float
    """One-sigma horizontal error. Multiply by 1.177 for CEP (50%), by 2.45 for
    R95, under a circular-normal assumption."""

    dominant_error: ErrorTerm
    error_breakdown: dict[ErrorTerm, float]

    @property
    def cep_m(self) -> float:
        return self.horizontal_uncertainty_m * 1.177


def georeference(
    *,
    bbox: tuple[float, float, float, float],
    intrinsics: CameraIntrinsics,
    camera_position: GeoPoint,
    camera_altitude: Altitude,
    attitude: GimbalAttitude,
    frame: LocalFrame,
    ground: GroundModel | None = None,
    uncertainty: PoseUncertainty | None = None,
) -> GeoreferenceResult | None:
    """Project a detection box onto the ground.

    ``bbox`` is ``(x1, y1, x2, y2)`` in pixels, image convention (y down).

    Returns ``None`` when the geometry does not admit a usable answer — the ray
    points at or above the horizon, or the depression angle is below
    ``MIN_DEPRESSION_DEG``. Both are ordinary operating conditions during a
    climb or a turn, not errors, so they are not raised.
    """
    if camera_altitude.datum is not AltitudeDatum.AGL:
        raise ValueError(
            f"camera altitude must be AGL for ground intersection, got "
            f"{camera_altitude.datum.value}"
        )

    ground = ground or FlatGround()
    uncertainty = uncertainty or PoseUncertainty()

    depression = attitude.depression_deg
    if depression < MIN_DEPRESSION_DEG:
        return None

    # --- 1. Foot point, not centre. See module docstring. ------------------
    x1, y1, x2, y2 = bbox
    foot_px = (x1 + x2) / 2.0
    foot_py = max(y1, y2)

    # --- 2. Pixel -> ideal camera-frame ray --------------------------------
    xn, yn = intrinsics.undistort(foot_px, foot_py)

    # --- 3. Camera frame -> world ENU --------------------------------------
    az = math.radians(attitude.azimuth_deg)
    el = math.radians(attitude.elevation_deg)
    roll = math.radians(attitude.roll_deg)

    # Boresight, and the image right/down axes expressed in ENU.
    fwd = (math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el))
    right = (math.cos(az), -math.sin(az), 0.0)
    down = _cross(fwd, right)

    if roll:
        c, s = math.cos(roll), math.sin(roll)
        right, down = (
            _add(_scale(right, c), _scale(down, s)),
            _add(_scale(down, c), _scale(right, -s)),
        )

    ray = _normalise(_add(fwd, _add(_scale(right, xn), _scale(down, yn))))

    # --- 4. Intersect with the ground --------------------------------------
    camera_local = frame.to_local(camera_position, up=camera_altitude.metres)

    if ray[2] >= 0.0:
        return None  # at or above the horizon

    hit = _intersect_ground(camera_local, ray, ground)
    if hit is None:
        return None

    ground_range = camera_local.ground_distance_to(hit)
    height = camera_local.up - hit.up
    if height <= 0.0:
        return None

    # --- 5. Propagate the error budget -------------------------------------
    # Sensitivities are taken at the *achieved* geometry rather than the
    # commanded one, so a gimbal that is not where it was told still reports an
    # honest uncertainty.
    eps = math.radians(max(depression, MIN_DEPRESSION_DEG))
    sin_eps = math.sin(eps)
    tan_eps = math.tan(eps)

    err_alt = uncertainty.altitude_m / tan_eps
    err_att = height * math.radians(uncertainty.attitude_deg) / (sin_eps * sin_eps)
    err_pos = uncertainty.position_m

    breakdown = {
        ErrorTerm.ALTITUDE: err_alt,
        ErrorTerm.ATTITUDE: err_att,
        ErrorTerm.POSITION: err_pos,
    }
    total = math.sqrt(err_alt**2 + err_att**2 + err_pos**2)

    ordered = sorted(breakdown.items(), key=lambda kv: kv[1], reverse=True)
    dominant = (
        ordered[0][0]
        if ordered[1][1] == 0.0 or ordered[0][1] / ordered[1][1] >= _DOMINANCE_RATIO
        else ErrorTerm.MIXED
    )

    return GeoreferenceResult(
        position=frame.to_geo(hit, alt=Altitude(hit.up, AltitudeDatum.AGL)),
        local=hit,
        ground_range_m=ground_range,
        depression_deg=depression,
        horizontal_uncertainty_m=total,
        dominant_error=dominant,
        error_breakdown=breakdown,
    )


def _intersect_ground(
    origin: LocalPoint, ray: tuple[float, float, float], ground: GroundModel
) -> LocalPoint | None:
    """Walk the ray down to the ground.

    For a flat plane this is one division. For a DSM it is a short fixed-point
    iteration: intersect with the plane at the current estimate's height, look
    up the true height there, repeat. Converges in two or three steps for
    realistic terrain and is far cheaper than ray-marching the raster.
    """
    height_guess = ground.height_at(origin)
    hit: LocalPoint | None = None

    for _ in range(8):
        if ray[2] >= 0.0:
            return None
        t = (height_guess - origin.up) / ray[2]
        if t <= 0.0:
            return None
        hit = LocalPoint(
            east=origin.east + t * ray[0],
            north=origin.north + t * ray[1],
            up=origin.up + t * ray[2],
        )
        actual = ground.height_at(hit)
        if abs(actual - height_guess) < 0.05:
            return LocalPoint(east=hit.east, north=hit.north, up=actual)
        height_guess = actual

    return hit


def _cross(a: tuple[float, float, float], b: tuple[float, float, float]):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _add(a: tuple[float, float, float], b: tuple[float, float, float]):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _scale(a: tuple[float, float, float], k: float):
    return (a[0] * k, a[1] * k, a[2] * k)


def _normalise(a: tuple[float, float, float]):
    n = math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2)
    if n == 0.0:
        raise ValueError("cannot normalise a zero-length ray")
    return (a[0] / n, a[1] / n, a[2] / n)
