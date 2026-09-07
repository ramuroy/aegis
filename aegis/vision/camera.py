"""Camera intrinsics and lens distortion.

A pinhole model with Brown-Conrady distortion. Nothing exotic — the value here
is in getting the *inverse* right, because georeferencing needs pixel → ray, and
the distortion model is only defined in the forward direction (ray → pixel).

The forward model is:

    x_d = x (1 + k1 r² + k2 r⁴ + k3 r⁶) + 2 p1 x y + p2 (r² + 2x²)
    y_d = y (1 + k1 r² + k2 r⁴ + k3 r⁶) + p1 (r² + 2y²) + 2 p2 x y

where (x, y) are ideal normalised image coordinates and r² = x² + y². There is
no closed-form inverse, so undistortion is iterative. Most implementations run a
fixed 5 or 20 iterations and hope; this one iterates to a tolerance and reports
when it fails to converge, because a silently non-converged undistortion puts a
detection metres away from where it actually is and nothing downstream can tell.

## The model has a maximum representable radius

This is not obvious and it bites in practice. The distorted radius is
``r_d = r · R(r²)``, and for barrel distortion ``R`` decreases with ``r``, so
``r_d`` is not monotonic — it peaks and then falls back. For an ordinary
action-camera calibration (90-degree lens, k1 = -0.28, k2 = 0.09, k3 = -0.014)
``r_d`` maxes out at about **1.03** near ``r = 1.7``, while the corner of a
16:9 frame sits at ``r_d = 1.077``.

Those corner pixels correspond to **no ray at all**: they are outside the
model's range, and no solver can invert them because there is nothing to find.
The iteration here detects that as a stalled residual and raises, rather than
returning the nearest reachable point as though it were an answer. A caller
seeing this on real imagery has a calibration that does not cover its own sensor
corners, which is worth knowing.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

__all__ = ["CameraIntrinsics", "DistortionCoefficients", "UndistortionError"]

# Wide-angle lenses at large radii are where the iteration struggles. 30 is
# generous: typical convergence for a 90-degree lens is 4-6 iterations.
_MAX_ITERATIONS: Final = 30
_MAX_BACKTRACKS: Final = 24
_TOLERANCE: Final = 1e-8


class UndistortionError(RuntimeError):
    """Undistortion failed to converge.

    Raised rather than returning a best guess. A detection georeferenced from a
    non-converged pixel can be tens of metres out, and the caller cannot detect
    that from the result — so the failure has to be loud.
    """


def _residual(
    x: float, y: float, xd: float, yd: float, d: DistortionCoefficients
) -> tuple[float, float]:
    """How far ``distort(x, y)`` lands from the target distorted point."""
    r2 = x * x + y * y
    radial = 1.0 + r2 * (d.k1 + r2 * (d.k2 + r2 * d.k3))
    return (
        x * radial + 2.0 * d.p1 * x * y + d.p2 * (r2 + 2.0 * x * x) - xd,
        y * radial + d.p1 * (r2 + 2.0 * y * y) + 2.0 * d.p2 * x * y - yd,
    )


@dataclass(frozen=True, slots=True)
class DistortionCoefficients:
    """Brown-Conrady coefficients, in OpenCV's ordering."""

    k1: float = 0.0
    k2: float = 0.0
    p1: float = 0.0
    p2: float = 0.0
    k3: float = 0.0

    @property
    def is_identity(self) -> bool:
        return self.k1 == self.k2 == self.p1 == self.p2 == self.k3 == 0.0


@dataclass(frozen=True, slots=True)
class CameraIntrinsics:
    """Pinhole intrinsics in pixels, plus the sensor's pixel dimensions."""

    fx: float
    fy: float
    cx: float
    cy: float
    width: int
    height: int
    distortion: DistortionCoefficients = DistortionCoefficients()

    def __post_init__(self) -> None:
        if self.fx <= 0 or self.fy <= 0:
            raise ValueError(f"focal lengths must be positive, got fx={self.fx}, fy={self.fy}")
        if self.width <= 0 or self.height <= 0:
            raise ValueError(f"invalid sensor size {self.width}x{self.height}")

    @classmethod
    def from_fov(
        cls,
        *,
        hfov_deg: float,
        width: int,
        height: int,
        distortion: DistortionCoefficients | None = None,
    ) -> CameraIntrinsics:
        """Build intrinsics from a horizontal field of view.

        Convenient for simulation and for spec sheets, which quote FOV rather
        than focal length. Assumes square pixels, which is true of every sensor
        this project will use.
        """
        if not 0.0 < hfov_deg < 180.0:
            raise ValueError(f"implausible horizontal FOV: {hfov_deg}")
        f = (width / 2.0) / math.tan(math.radians(hfov_deg) / 2.0)
        return cls(
            fx=f,
            fy=f,
            cx=width / 2.0,
            cy=height / 2.0,
            width=width,
            height=height,
            distortion=distortion or DistortionCoefficients(),
        )

    @property
    def hfov_deg(self) -> float:
        return 2.0 * math.degrees(math.atan2(self.width / 2.0, self.fx))

    @property
    def vfov_deg(self) -> float:
        return 2.0 * math.degrees(math.atan2(self.height / 2.0, self.fy))

    def normalise(self, px: float, py: float) -> tuple[float, float]:
        """Pixel coordinates to distorted normalised image coordinates."""
        return (px - self.cx) / self.fx, (py - self.cy) / self.fy

    def undistort(self, px: float, py: float) -> tuple[float, float]:
        """Pixel coordinates to *ideal* normalised image coordinates.

        Returns coordinates on the z=1 plane of the camera frame, with lens
        distortion removed. Raises ``UndistortionError`` if the iteration does
        not converge.
        """
        xd, yd = self.normalise(px, py)
        d = self.distortion
        if d.is_identity:
            return xd, yd

        # Newton-Raphson on f(x, y) = distort(x, y) - (xd, yd) = 0.
        #
        # The textbook approach is fixed-point iteration — repeatedly divide the
        # distorted point by the radial term implied by the current estimate.
        # It is two lines shorter and it diverges at the corners of a wide lens:
        # a property test caught it failing at r^2 ~ 1.16 on a 90-degree lens
        # with k1 = -0.28, which is an ordinary action-camera calibration, not a
        # pathological one. Corners are exactly where a perimeter detection sits.
        #
        # Newton converges there in 3-4 steps because it uses the local slope
        # instead of assuming the radial term is locally constant.
        x, y = xd, yd
        residual = _residual(x, y, xd, yd, d)

        for _ in range(_MAX_ITERATIONS):
            fx, fy = residual
            if abs(fx) < _TOLERANCE and abs(fy) < _TOLERANCE:
                return x, y

            r2 = x * x + y * y
            radial = 1.0 + r2 * (d.k1 + r2 * (d.k2 + r2 * d.k3))
            radial_prime = d.k1 + r2 * (2.0 * d.k2 + 3.0 * d.k3 * r2)  # dR/d(r^2)

            # Jacobian. The off-diagonal terms come out equal, which is a handy
            # check when re-deriving this by hand.
            j00 = radial + 2.0 * x * x * radial_prime + 2.0 * d.p1 * y + 6.0 * d.p2 * x
            j01 = 2.0 * x * y * radial_prime + 2.0 * d.p1 * x + 2.0 * d.p2 * y
            j11 = radial + 2.0 * y * y * radial_prime + 6.0 * d.p1 * y + 2.0 * d.p2 * x

            det = j00 * j11 - j01 * j01
            if abs(det) < 1e-12:
                raise UndistortionError(
                    f"singular distortion Jacobian (det={det:.3g}) at pixel "
                    f"({px:.1f}, {py:.1f}); the lens model is not invertible here"
                )

            step_x = (j11 * fx - j01 * fy) / det
            step_y = (j00 * fy - j01 * fx) / det

            # Backtracking line search. Undamped Newton overshoots badly at the
            # corners of a wide lens, where the radial slope has fallen to ~0.27
            # and the root is far from the starting guess: it oscillates instead
            # of converging. Halving the step until the residual actually
            # decreases makes convergence monotone, at a cost of one or two
            # extra evaluations on the handful of pixels that need it.
            magnitude = math.hypot(fx, fy)
            scale = 1.0
            for _ in range(_MAX_BACKTRACKS):
                nx, ny = x - scale * step_x, y - scale * step_y
                if math.isfinite(nx) and math.isfinite(ny):
                    trial = _residual(nx, ny, xd, yd, d)
                    if math.hypot(*trial) < magnitude:
                        x, y, residual = nx, ny, trial
                        break
                scale *= 0.5
            else:
                raise UndistortionError(
                    f"undistortion stalled at pixel ({px:.1f}, {py:.1f}) with residual "
                    f"{math.hypot(*residual):.3g}: no step reduces it. This pixel is "
                    "outside the distortion model's representable radius - see the "
                    "module docstring. The calibration does not cover this part of "
                    "the sensor."
                )

        raise UndistortionError(
            f"undistortion did not converge within {_MAX_ITERATIONS} iterations at "
            f"pixel ({px:.1f}, {py:.1f}). A non-converged result can place a detection "
            "tens of metres from its true position, so it is not returned."
        )

    def distort(self, x: float, y: float) -> tuple[float, float]:
        """Ideal normalised coordinates back to pixel coordinates.

        The forward model. Used mainly to verify ``undistort`` round-trips,
        which is the only practical way to test an iterative inverse.
        """
        d = self.distortion
        r2 = x * x + y * y
        radial = 1.0 + r2 * (d.k1 + r2 * (d.k2 + r2 * d.k3))
        xd = x * radial + 2.0 * d.p1 * x * y + d.p2 * (r2 + 2.0 * x * x)
        yd = y * radial + d.p1 * (r2 + 2.0 * y * y) + 2.0 * d.p2 * x * y
        return xd * self.fx + self.cx, yd * self.fy + self.cy
