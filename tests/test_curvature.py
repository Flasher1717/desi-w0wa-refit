"""Curvature-sigma tests (PREREGISTRATION.md P10.3-P10.4).

On an exact quadratic chi2 = (x - x0)^T A (x - x0), the central FD
Hessian is exact (up to float rounding): H = 2A, C = 2 H^-1 = A^-1,
sigma(p) = sqrt(A^-1[p, p]).
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from desi_w0wa_refit.bao import FloatArray
from desi_w0wa_refit.curvature import (
    FD_STEPS_W0WA,
    boundary_flag_reason,
    curvature_sigmas,
)

BOUNDS_5D = ((0.01, 0.99), (0.2, 1.0), (0.005, 0.1), (-3.0, 1.0), (-3.0, 2.0))
X_MAP_5D = (0.31, 0.67, 0.0223, -0.77, -0.78)


def _quadratic_chi2(matrix: FloatArray, x0: FloatArray) -> Callable[[FloatArray], float]:
    def chi2_fn(x: FloatArray) -> float:
        delta = x - x0
        return float(delta @ matrix @ delta)

    return chi2_fn


def test_quadratic_sigmas_are_exact() -> None:
    rng = np.random.default_rng(20260611)
    raw = rng.standard_normal((5, 5))
    matrix = raw @ raw.T + 5.0 * np.eye(5)  # SPD, well-conditioned
    x0 = np.asarray(X_MAP_5D)
    result = curvature_sigmas(_quadratic_chi2(matrix, x0), X_MAP_5D, BOUNDS_5D)
    assert not result.boundary_flagged
    expected = np.linalg.inv(matrix)
    assert result.sigma_w0 is not None and result.sigma_wa is not None
    np.testing.assert_allclose(result.sigma_w0, np.sqrt(expected[3, 3]), rtol=1e-6)
    np.testing.assert_allclose(result.sigma_wa, np.sqrt(expected[4, 4]), rtol=1e-6)
    assert result.residual_gradient is not None
    assert max(abs(g) for g in result.residual_gradient) < 1e-6


def test_residual_gradient_reported_off_map() -> None:
    matrix = np.diag([4.0, 4.0, 4.0, 4.0, 4.0])
    x0 = np.asarray(X_MAP_5D)
    shifted = tuple(v + 0.002 for v in X_MAP_5D)
    result = curvature_sigmas(_quadratic_chi2(matrix, x0), shifted, BOUNDS_5D)
    assert not result.boundary_flagged
    assert result.residual_gradient is not None
    # gradient of x^T A x at delta = 0.002 per axis: 2 A delta = 0.016
    np.testing.assert_allclose(result.residual_gradient, [0.016] * 5, rtol=1e-6)


def test_boundary_flag_near_box_bound() -> None:
    near_bound = (0.01 + 1.5 * FD_STEPS_W0WA[0], 0.67, 0.0223, -0.77, -0.78)
    reason = boundary_flag_reason(near_bound, BOUNDS_5D, FD_STEPS_W0WA)
    assert reason is not None and "bound" in reason


def test_boundary_flag_near_w0_wa_wall() -> None:
    near_wall = (0.31, 0.67, 0.0223, -0.5, 0.47)  # w0 + wa = -0.03
    reason = boundary_flag_reason(near_wall, BOUNDS_5D, FD_STEPS_W0WA)
    assert reason is not None and "w0 + wa" in reason
    matrix = np.eye(5)
    result = curvature_sigmas(_quadratic_chi2(matrix, np.asarray(near_wall)), near_wall, BOUNDS_5D)
    assert result.boundary_flagged
    assert result.sigma_w0 is None


def test_stencil_crossing_hard_prior_is_flagged() -> None:
    """A chi2 returning +inf inside the stencil withholds sigma_curv."""
    x0 = np.asarray(X_MAP_5D)
    matrix = np.eye(5)
    quadratic = _quadratic_chi2(matrix, x0)

    def chi2_fn(x: FloatArray) -> float:
        if float(x[4]) < -0.79:  # wall just one wa-step below the MAP
            return float("inf")
        return quadratic(x)

    result = curvature_sigmas(chi2_fn, X_MAP_5D, BOUNDS_5D)
    assert result.boundary_flagged
    assert result.flag_reason is not None and "stencil" in result.flag_reason
