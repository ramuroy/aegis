"""Tests for georeferencing.

Most of these check the projection against geometry that can be worked out by
hand — at 45 degrees depression the ground range equals the height, at nadir the
hit is directly beneath, and so on. An implementation that is subtly wrong about
axis conventions passes none of them.

The error-budget tests are checked against the independently-researched figures
in `docs/research/cv-models.md` (2-5 m CEP on barometric altitude, 0.5-1.5 m with
RTK and a DSM). Agreement between an analytic propagation written here and a
literature figure found elsewhere is decent evidence neither is nonsense.
"""

from __future__ import annotations

import math

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from aegis.domain.geo import Altitude, AltitudeDatum, GeoPoint, LocalFrame
from aegis.vision.camera import (
    CameraIntrinsics,
    DistortionCoefficients,
    UndistortionError,
)
from aegis.vision.georef import (
    MIN_DEPRESSION_DEG,
    ErrorTerm,
    FlatGround,
    GimbalAttitude,
    PoseUncertainty,
    georeference,
)

ORIGIN = GeoPoint(lat=18.5204, lon=73.8567)
FRAME = LocalFrame(ORIGIN)
CAM = CameraIntrinsics.from_fov(hfov_deg=69.0, width=1920, height=1080)


def _agl(m: float) -> Altitude:
    return Altitude(m, AltitudeDatum.AGL)


def _centre_box(size: float = 40.0) -> tuple[float, float, float, float]:
    """A box whose foot point is exactly the principal point."""
    cx, cy = CAM.cx, CAM.cy
    return (cx - size / 2, cy - size, cx + size / 2, cy)


def _geo(
    *,
    az: float = 0.0,
    el: float = -45.0,
    alt: float = 40.0,
    bbox: tuple[float, float, float, float] | None = None,
    uncertainty: PoseUncertainty | None = None,
    intrinsics: CameraIntrinsics | None = None,
):
    return georeference(
        bbox=bbox if bbox is not None else _centre_box(),
        intrinsics=intrinsics or CAM,
        camera_position=ORIGIN,
        camera_altitude=_agl(alt),
        attitude=GimbalAttitude(azimuth_deg=az, elevation_deg=el),
        frame=FRAME,
        ground=FlatGround(),
        uncertainty=uncertainty,
    )


class TestIntrinsics:
    def test_fov_round_trips(self) -> None:
        cam = CameraIntrinsics.from_fov(hfov_deg=69.0, width=1920, height=1080)
        assert cam.hfov_deg == pytest.approx(69.0, abs=0.01)

    def test_vertical_fov_follows_from_square_pixels(self) -> None:
        cam = CameraIntrinsics.from_fov(hfov_deg=90.0, width=1920, height=1080)
        # tan(v/2) / tan(h/2) == height / width for square pixels.
        ratio = math.tan(math.radians(cam.vfov_deg) / 2) / math.tan(math.radians(90.0) / 2)
        assert ratio == pytest.approx(1080 / 1920, rel=1e-6)

    def test_zero_focal_length_rejected(self) -> None:
        with pytest.raises(ValueError, match="focal lengths"):
            CameraIntrinsics(fx=0.0, fy=100.0, cx=1.0, cy=1.0, width=10, height=10)


class TestUndistortion:
    DISTORTED = CameraIntrinsics.from_fov(
        hfov_deg=90.0,
        width=1920,
        height=1080,
        distortion=DistortionCoefficients(k1=-0.28, k2=0.09, p1=0.0007, p2=-0.0004, k3=-0.014),
    )

    def test_identity_distortion_is_a_no_op(self) -> None:
        assert CAM.undistort(100.0, 200.0) == CAM.normalise(100.0, 200.0)

    @settings(max_examples=300, deadline=None)
    @given(
        x=st.floats(min_value=-1.2, max_value=1.2),
        y=st.floats(min_value=-0.7, max_value=0.7),
    )
    def test_undistort_inverts_distort(self, x: float, y: float) -> None:
        """Round-trip from an *ideal* coordinate, which is the well-defined direction.

        Starting from a pixel is the tempting way to write this and it is wrong:
        the forward map is not surjective onto the whole image, so some pixels
        correspond to no ray and the round-trip has nothing to find. Starting
        from an ideal coordinate guarantees the target is reachable by
        construction.
        """
        px, py = self.DISTORTED.distort(x, y)
        bx, by = self.DISTORTED.undistort(px, py)
        assert bx == pytest.approx(x, abs=1e-6)
        assert by == pytest.approx(y, abs=1e-6)

    def test_pixels_outside_the_models_range_are_refused(self) -> None:
        """The frame corner of this calibration is genuinely unreachable.

        r_d = r*R(r^2) peaks near 1.03 for these coefficients, but the 16:9
        corner needs 1.077. Returning the nearest reachable point would put a
        detection metres from the truth with no way for the caller to tell.
        """
        with pytest.raises(UndistortionError, match="representable radius"):
            self.DISTORTED.undistort(50.0, 50.0)

    def test_the_centre_region_is_comfortably_invertible(self) -> None:
        """The refusal above must not mean the lens is unusable in general."""
        for px, py in ((960.0, 540.0), (700.0, 400.0), (1300.0, 700.0), (400.0, 900.0)):
            x, y = self.DISTORTED.undistort(px, py)
            bx, by = self.DISTORTED.distort(x, y)
            assert bx == pytest.approx(px, abs=1e-3)
            assert by == pytest.approx(py, abs=1e-3)


class TestProjectionGeometry:
    def test_at_45_degrees_ground_range_equals_height(self) -> None:
        r = _geo(el=-45.0, alt=40.0)
        assert r is not None
        assert r.ground_range_m == pytest.approx(40.0, rel=1e-6)

    def test_nadir_lands_directly_beneath(self) -> None:
        r = _geo(el=-90.0, alt=40.0)
        assert r is not None
        assert r.ground_range_m == pytest.approx(0.0, abs=1e-6)

    @pytest.mark.parametrize(
        ("az", "east", "north"),
        [(0.0, 0.0, 40.0), (90.0, 40.0, 0.0), (180.0, 0.0, -40.0), (270.0, -40.0, 0.0)],
    )
    def test_azimuth_points_the_right_way(self, az: float, east: float, north: float) -> None:
        r = _geo(az=az, el=-45.0, alt=40.0)
        assert r is not None
        assert r.local.east == pytest.approx(east, abs=1e-4)
        assert r.local.north == pytest.approx(north, abs=1e-4)

    def test_hit_is_on_the_ground(self) -> None:
        r = _geo()
        assert r is not None
        assert r.local.up == pytest.approx(0.0, abs=1e-9)

    def test_raised_ground_shortens_the_range(self) -> None:
        flat = georeference(
            bbox=_centre_box(),
            intrinsics=CAM,
            camera_position=ORIGIN,
            camera_altitude=_agl(40.0),
            attitude=GimbalAttitude(0.0, -45.0),
            frame=FRAME,
            ground=FlatGround(0.0),
        )
        raised = georeference(
            bbox=_centre_box(),
            intrinsics=CAM,
            camera_position=ORIGIN,
            camera_altitude=_agl(40.0),
            attitude=GimbalAttitude(0.0, -45.0),
            frame=FRAME,
            ground=FlatGround(10.0),
        )
        assert flat is not None and raised is not None
        assert raised.ground_range_m == pytest.approx(30.0, rel=1e-6)
        assert raised.ground_range_m < flat.ground_range_m

    @settings(max_examples=150, deadline=None)
    @given(
        depression=st.floats(min_value=MIN_DEPRESSION_DEG + 1, max_value=89.0),
        alt=st.floats(min_value=5.0, max_value=120.0),
    )
    def test_range_matches_the_closed_form(self, depression: float, alt: float) -> None:
        """R = h / tan(depression), for the boresight ray."""
        r = _geo(el=-depression, alt=alt)
        assert r is not None
        assert r.ground_range_m == pytest.approx(alt / math.tan(math.radians(depression)), rel=1e-6)


class TestRefusals:
    def test_above_the_horizon_returns_none(self) -> None:
        assert _geo(el=+10.0) is None

    def test_level_returns_none(self) -> None:
        assert _geo(el=0.0) is None

    def test_shallow_depression_refused(self) -> None:
        assert _geo(el=-(MIN_DEPRESSION_DEG - 0.1)) is None

    def test_just_past_the_threshold_is_accepted(self) -> None:
        assert _geo(el=-(MIN_DEPRESSION_DEG + 0.1)) is not None

    def test_non_agl_altitude_rejected(self) -> None:
        with pytest.raises(ValueError, match="must be AGL"):
            georeference(
                bbox=_centre_box(),
                intrinsics=CAM,
                camera_position=ORIGIN,
                camera_altitude=Altitude(560.0, AltitudeDatum.AMSL),
                attitude=GimbalAttitude(0.0, -45.0),
                frame=FRAME,
            )


class TestFootPoint:
    def test_foot_point_is_nearer_than_the_box_centre(self) -> None:
        """Using the centre is the classic error and it produces a *bias*.

        A person's centroid is ~1 m above their feet; at 30 degrees depression
        that becomes ~1.7 m of extra ground range that never averages out.
        """
        cx, cy = CAM.cx, CAM.cy
        tall_box = (cx - 20, cy - 120, cx + 20, cy)  # 120 px tall
        foot = _geo(el=-30.0, bbox=tall_box)

        centre_y = (tall_box[1] + tall_box[3]) / 2
        centre_box = (tall_box[0], centre_y, tall_box[2], centre_y)
        centre = _geo(el=-30.0, bbox=centre_box)

        assert foot is not None and centre is not None
        assert foot.ground_range_m < centre.ground_range_m

    def test_bias_magnitude_matches_the_analytic_estimate(self) -> None:
        """A target 1 m above ground is displaced by 1/tan(depression)."""
        # Place the camera so that a 1 m height error is exactly what separates
        # the two rays: compare a ground hit against a hit computed as if the
        # camera were 1 m higher, at the same look angle.
        depression = 30.0
        base = _geo(el=-depression, alt=40.0)
        one_up = _geo(el=-depression, alt=41.0)
        assert base is not None and one_up is not None
        expected = 1.0 / math.tan(math.radians(depression))
        assert one_up.ground_range_m - base.ground_range_m == pytest.approx(expected, rel=1e-6)
        assert expected == pytest.approx(1.73, abs=0.01)


class TestErrorBudget:
    def test_barometric_cep_matches_the_researched_range(self) -> None:
        """2-5 m CEP on barometric altitude (docs/research/cv-models.md)."""
        r = _geo(el=-45.0, alt=40.0, uncertainty=PoseUncertainty())
        assert r is not None
        assert 2.0 <= r.cep_m <= 5.0, f"CEP {r.cep_m:.2f} m outside the researched range"

    def test_rtk_cep_matches_the_researched_range(self) -> None:
        """0.5-1.5 m with RTK and a site DSM."""
        r = _geo(el=-45.0, alt=40.0, uncertainty=PoseUncertainty.rtk_with_dsm())
        assert r is not None
        assert 0.5 <= r.cep_m <= 1.5, f"CEP {r.cep_m:.2f} m outside the researched range"

    def test_rtk_is_attitude_limited(self) -> None:
        """A genuinely useful result: once GNSS is fixed, the gimbal dominates.

        It says where the next engineering effort should go, which a single
        aggregate error number would not.
        """
        r = _geo(el=-45.0, alt=40.0, uncertainty=PoseUncertainty.rtk_with_dsm())
        assert r is not None
        assert r.dominant_error is ErrorTerm.ATTITUDE

    def test_shallow_angles_are_altitude_limited(self) -> None:
        r = _geo(el=-20.0, alt=40.0, uncertainty=PoseUncertainty())
        assert r is not None
        assert r.dominant_error is ErrorTerm.ALTITUDE

    def test_error_grows_as_the_angle_shallows(self) -> None:
        steep = _geo(el=-70.0, alt=40.0)
        shallow = _geo(el=-20.0, alt=40.0)
        assert steep is not None and shallow is not None
        assert shallow.horizontal_uncertainty_m > steep.horizontal_uncertainty_m

    def test_error_grows_with_altitude(self) -> None:
        low = _geo(el=-45.0, alt=20.0)
        high = _geo(el=-45.0, alt=100.0)
        assert low is not None and high is not None
        assert high.horizontal_uncertainty_m > low.horizontal_uncertainty_m

    def test_breakdown_sums_in_quadrature_to_the_total(self) -> None:
        r = _geo()
        assert r is not None
        quad = math.sqrt(sum(v**2 for v in r.error_breakdown.values()))
        assert quad == pytest.approx(r.horizontal_uncertainty_m, rel=1e-9)

    @settings(max_examples=150, deadline=None)
    @given(
        depression=st.floats(min_value=MIN_DEPRESSION_DEG + 1, max_value=88.0),
        alt=st.floats(min_value=5.0, max_value=120.0),
    )
    def test_uncertainty_is_always_positive_and_finite(self, depression: float, alt: float) -> None:
        r = _geo(el=-depression, alt=alt)
        assume(r is not None)
        assert r is not None
        assert math.isfinite(r.horizontal_uncertainty_m)
        assert r.horizontal_uncertainty_m > 0.0
