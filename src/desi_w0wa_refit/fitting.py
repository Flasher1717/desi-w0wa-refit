"""Deterministic multi-start MAP optimization and significance conversion.

- Seeds: every stochastic element derives from the project root seed
  20260611 through a pure function of (root seed, run name)
  [PREREGISTRATION.md P7].
- Significance: Delta chi2_MAP between the nested models follows
  chi2(2 dof) under H0 (Wilks); the published "N sigma" is the 1D
  Gaussian equivalent, P(|X| < N) = CDF_chi2(Delta chi2 | 2 dof)
  [arXiv:2503.14738v3, Eq. (22)]. For 2 dof the survival function is
  exactly exp(-Delta chi2 / 2), so N = Phi^-1_sf(exp(-Dchi2/2) / 2).
- Best fits: Nelder-Mead from a seeded Sobol set of starting points
  inside the prior box (hard priors return +inf), the best refined once
  more from its own optimum.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np
from scipy.optimize import OptimizeResult, minimize
from scipy.stats import norm, qmc

from desi_w0wa_refit.bao import FloatArray

ROOT_SEED = 20260611


def derive_seed(run_name: str) -> int:
    """Pure derivation of a 32-bit seed from the root seed and a run name."""
    digest = hashlib.sha256(f"{ROOT_SEED}:{run_name}".encode()).digest()
    return int.from_bytes(digest[:4], "big")


def nsigma_from_delta_chi2(delta_chi2: float, dof: int = 2) -> float:
    """Gaussian-equivalent N sigma of a Delta chi2_MAP [Eq. (22) convention].

    For the project's case dof = 2 the chi2 survival function is exactly
    exp(-x/2), evaluated directly so large significances stay accurate.
    """
    if delta_chi2 <= 0.0:
        return 0.0
    if dof != 2:
        raise ValueError("project convention is 2 extra parameters (dof=2)")
    sf = math.exp(-0.5 * delta_chi2)
    return float(norm.isf(0.5 * sf))


def aic(chi2_min: float, n_params: int) -> float:
    """Akaike information criterion, chi2 + 2k."""
    return chi2_min + 2.0 * n_params


def bic(chi2_min: float, n_params: int, n_data: int) -> float:
    """Bayesian information criterion, chi2 + k ln n."""
    return chi2_min + n_params * math.log(n_data)


@dataclass(frozen=True)
class FitResult:
    """Best fit from a deterministic multi-start optimization."""

    x: FloatArray
    chi2: float
    n_starts: int
    start_chi2s: FloatArray  # final chi2 of each start, sorted ascending


def minimize_multistart(
    chi2_fn: Callable[[FloatArray], float],
    bounds: Sequence[tuple[float, float]],
    *,
    run_name: str,
    n_starts: int = 24,
    constraint: Callable[[FloatArray], bool] | None = None,
) -> FitResult:
    """Nelder-Mead from a seeded Sobol start set inside the prior box.

    ``chi2_fn`` must return +inf outside its own hard priors;
    ``constraint`` filters the START points only (e.g. w0 + wa < 0).
    """
    lower = np.asarray([b[0] for b in bounds], dtype=np.float64)
    upper = np.asarray([b[1] for b in bounds], dtype=np.float64)
    sampler = qmc.Sobol(d=len(bounds), scramble=True, rng=derive_seed(run_name))
    starts: list[FloatArray] = []
    while len(starts) < n_starts:
        block = qmc.scale(sampler.random(8), lower, upper)
        for row in block:
            point = np.asarray(row, dtype=np.float64)
            if constraint is None or constraint(point):
                starts.append(point)
            if len(starts) == n_starts:
                break

    def run_one(x0: FloatArray) -> OptimizeResult:
        return minimize(
            chi2_fn,
            x0,
            method="Nelder-Mead",
            bounds=list(bounds),
            options={"xatol": 1e-10, "fatol": 1e-10, "maxiter": 20000, "maxfev": 20000},
        )

    results = [run_one(x0) for x0 in starts]
    best = min(results, key=lambda r: float(r.fun))
    # One refinement pass from the best optimum (cheap, guards stalls).
    refined = run_one(np.asarray(best.x, dtype=np.float64))
    if float(refined.fun) < float(best.fun):
        best = refined
    start_chi2s = np.sort(np.asarray([float(r.fun) for r in results], dtype=np.float64))
    return FitResult(
        x=np.asarray(best.x, dtype=np.float64),
        chi2=float(best.fun),
        n_starts=n_starts,
        start_chi2s=start_chi2s,
    )
