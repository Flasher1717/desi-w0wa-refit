"""Finite-difference curvature sigma at a MAP point (PREREGISTRATION.md
P10.3-P10.4).

- Central-difference Hessian H of chi2 in the 5-parameter space
  (omega_m, h, omega_b_h2, w0, wa) with FIXED pre-registered steps;
  Fisher F = H/2, covariance C = 2 H^-1,
  sigma_curv(p) = sqrt(C[p, p]).
- The steps are sized to dominate the optimizer noise floor
  (fatol 1e-10, reproducibility ~1e-9) and are checked against the
  prior box and the w0 + wa < 0 hard wall BEFORE differencing.
- Boundary-MAP policy (P10.4): if the MAP lies within 2 FD steps of
  any box bound or |w0 + wa| < 0.05, the row is flagged and sigma_curv
  is withheld.
- The central-difference residual gradient at the evaluation point is
  reported (frozen MAPs are read from JSON-rounded records and are not
  exactly stationary; they are never re-optimized, P10.3).
- sigma_curv assumes a Gaussian peak; it is a curvature quantity, never
  a posterior interval (pre-registered caveat, P10.3).
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np

from desi_w0wa_refit.bao import FloatArray

# P10.3 fixed steps, in the (omega_m, h, omega_b_h2, w0, wa) order.
FD_STEPS_W0WA = (1e-3, 1e-3, 1e-4, 1e-2, 3e-2)
W0_PLUS_WA_MARGIN = 0.05  # P10.4
BOUNDARY_STEPS = 2.0  # P10.4: "within 2 FD steps of any bound"


@dataclass(frozen=True)
class CurvatureResult:
    """sigma_curv at a MAP, or the reason it is withheld (P10.4)."""

    sigma_w0: float | None
    sigma_wa: float | None
    boundary_flagged: bool
    flag_reason: str | None
    residual_gradient: tuple[float, ...] | None
    chi2_at_point: float


def boundary_flag_reason(
    x_map: Sequence[float] | FloatArray,
    bounds: Sequence[tuple[float, float]],
    steps: Sequence[float],
    *,
    check_w0_wa_wall: bool = True,
) -> str | None:
    """P10.4 flag: near a box bound (2 FD steps) or the w0+wa wall."""
    for value, (low, high), step in zip(x_map, bounds, steps, strict=True):
        if value - low < BOUNDARY_STEPS * step or high - value < BOUNDARY_STEPS * step:
            return f"MAP within {BOUNDARY_STEPS:g} FD steps of a prior bound"
    if check_w0_wa_wall and abs(float(x_map[-2]) + float(x_map[-1])) < W0_PLUS_WA_MARGIN:
        return f"|w0 + wa| < {W0_PLUS_WA_MARGIN} (hard-prior wall)"
    return None


def fd_gradient(
    chi2_fn: Callable[[FloatArray], float], x_map: FloatArray, steps: Sequence[float]
) -> FloatArray:
    """Central-difference gradient (residual-gradient report, P10.3)."""
    n = x_map.size
    gradient = np.empty(n, dtype=np.float64)
    for i in range(n):
        forward = x_map.copy()
        backward = x_map.copy()
        forward[i] += steps[i]
        backward[i] -= steps[i]
        gradient[i] = (chi2_fn(forward) - chi2_fn(backward)) / (2.0 * steps[i])
    return gradient


def fd_hessian(
    chi2_fn: Callable[[FloatArray], float], x_map: FloatArray, steps: Sequence[float]
) -> FloatArray:
    """Central-difference Hessian (4-point stencil off-diagonal)."""
    n = x_map.size
    hessian = np.empty((n, n), dtype=np.float64)
    f_center = chi2_fn(x_map)
    for i in range(n):
        plus = x_map.copy()
        minus = x_map.copy()
        plus[i] += steps[i]
        minus[i] -= steps[i]
        hessian[i, i] = (chi2_fn(plus) - 2.0 * f_center + chi2_fn(minus)) / steps[i] ** 2
    for i in range(n):
        for j in range(i + 1, n):
            pp = x_map.copy()
            pm = x_map.copy()
            mp = x_map.copy()
            mm = x_map.copy()
            pp[i] += steps[i]
            pp[j] += steps[j]
            pm[i] += steps[i]
            pm[j] -= steps[j]
            mp[i] -= steps[i]
            mp[j] += steps[j]
            mm[i] -= steps[i]
            mm[j] -= steps[j]
            value = (chi2_fn(pp) - chi2_fn(pm) - chi2_fn(mp) + chi2_fn(mm)) / (
                4.0 * steps[i] * steps[j]
            )
            hessian[i, j] = value
            hessian[j, i] = value
    return hessian


def curvature_sigmas(
    chi2_fn: Callable[[FloatArray], float],
    x_map: Sequence[float],
    bounds: Sequence[tuple[float, float]],
    *,
    steps: Sequence[float] = FD_STEPS_W0WA,
    check_w0_wa_wall: bool = True,
) -> CurvatureResult:
    """P10.3 sigma_curv(w0), sigma_curv(wa) at a (possibly frozen) MAP.

    The last two parameters of ``x_map`` must be (w0, wa). Pure chi2
    evaluations only -- never a re-fit.
    """
    x = np.asarray(x_map, dtype=np.float64)
    reason = boundary_flag_reason(x, bounds, steps, check_w0_wa_wall=check_w0_wa_wall)
    chi2_at_point = chi2_fn(x)
    if reason is not None:
        return CurvatureResult(
            sigma_w0=None,
            sigma_wa=None,
            boundary_flagged=True,
            flag_reason=reason,
            residual_gradient=None,
            chi2_at_point=chi2_at_point,
        )
    if not np.isfinite(chi2_at_point):
        return CurvatureResult(
            sigma_w0=None,
            sigma_wa=None,
            boundary_flagged=True,
            flag_reason="chi2 not finite at the MAP point",
            residual_gradient=None,
            chi2_at_point=chi2_at_point,
        )
    gradient = fd_gradient(chi2_fn, x, steps)
    gradient_report = tuple(float(g) for g in gradient) if np.isfinite(gradient).all() else None
    hessian = fd_hessian(chi2_fn, x, steps)
    if not np.isfinite(hessian).all():
        return CurvatureResult(
            sigma_w0=None,
            sigma_wa=None,
            boundary_flagged=True,
            flag_reason="stencil crossed a hard prior (non-finite Hessian entry)",
            residual_gradient=gradient_report,
            chi2_at_point=chi2_at_point,
        )
    try:
        covariance = 2.0 * np.linalg.inv(hessian)
    except np.linalg.LinAlgError:
        return CurvatureResult(
            sigma_w0=None,
            sigma_wa=None,
            boundary_flagged=True,
            flag_reason="singular Hessian",
            residual_gradient=tuple(float(g) for g in gradient),
            chi2_at_point=chi2_at_point,
        )
    var_w0 = float(covariance[-2, -2])
    var_wa = float(covariance[-1, -1])
    if var_w0 <= 0.0 or var_wa <= 0.0:
        return CurvatureResult(
            sigma_w0=None,
            sigma_wa=None,
            boundary_flagged=True,
            flag_reason="non-positive curvature variance",
            residual_gradient=tuple(float(g) for g in gradient),
            chi2_at_point=chi2_at_point,
        )
    return CurvatureResult(
        sigma_w0=float(np.sqrt(var_w0)),
        sigma_wa=float(np.sqrt(var_wa)),
        boundary_flagged=False,
        flag_reason=None,
        residual_gradient=tuple(float(g) for g in gradient),
        chi2_at_point=chi2_at_point,
    )
