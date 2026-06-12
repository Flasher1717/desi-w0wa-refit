"""Keeley-style chi-squared mock test engine (PREREGISTRATION.md P9).

Replicates the recipe of Keeley, Shafieloo & L'Huillier
[arXiv:2212.07917v3, Sec. 2], with the paper's unstated degrees of
freedom resolved by the pre-registration (P9.2-P9.3):

- Mock data vectors: mag_mock = mu_fid + L xi with xi ~ N(0, I) and L
  the SAME lower Cholesky factor the chi2 uses
  (``SNSample.cholesky_lower``); one ``default_rng`` per mock, seeded
  ``derive_seed(f"{seed_stream}-{i}")`` (P7 scheme).
- Per-mock fit: flat LCDM, Omega_m the only nonlinear parameter
  (bounded [0.01, 1.0], ``minimize_scalar`` bounded, xatol = 1e-8 --
  the P0-validated configuration), the additive offset profiled
  analytically (Goliath 2001 eq. 21: A - B^2/E, exactly
  ``SNSample.chi2_marginalized_with_mag``, no log term). The fiducial
  h = 0.7 is a pure writing convention absorbed by the offset
  (``sn_only_chi2`` uses the same value).
- IDENTICAL code path for the real-data chi2 and every mock.
- Failure policy (P9.2): a fit is flagged when the optimizer reports
  non-convergence or its optimum sits within ``BOUND_MARGIN`` of an
  Omega_m bound; the caller aborts interpretation above 1% flagged.
- Statistic (P9.3): k = #{chi2_mock < chi2_real}, p = (k+1)/(N+1),
  one-sided LOW tail; both Gaussian conversions are reported, the
  two-sided one being the Keeley-comparison number.

Diagnostics (P9.4c, descriptive, non-gating): the std of the
offset-removed normalized residuals (Keeley: 0.93 on Pantheon+) and
the uniform diagonal subtraction delta^2 tuned so chi2_min = N
(Keeley: 0.002 on Pantheon+).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq, minimize_scalar
from scipy.stats import norm

from desi_w0wa_refit.bao import FloatArray
from desi_w0wa_refit.cosmology import Background
from desi_w0wa_refit.fitting import derive_seed
from desi_w0wa_refit.sne import SNSample

OMEGA_M_BOUNDS = (0.01, 1.0)  # P9.2, the P0-validated configuration
XATOL = 1e-8
BOUND_MARGIN = 1e-4  # an optimum this close to a bound is a clipped fit
H_FIDUCIAL = 0.7  # Keeley's H0 = 70 km/s/Mpc writing convention


@dataclass(frozen=True)
class LcdmProfiledFit:
    """Best offset-profiled flat-LCDM fit of one magnitude vector."""

    omega_m: float
    chi2: float
    flagged: bool


@dataclass(frozen=True)
class MockTestResult:
    """Outcome of one P9 mock run (the chi2 array is seed-reproducible)."""

    n_mocks: int
    fid_omega_m: float
    seed_stream: str
    chi2_real: float
    omega_m_real: float
    k_below: int
    n_flagged: int
    p_low_tail: float
    z_one_sided: float
    z_two_sided: float
    mock_chi2: FloatArray


def mu_lcdm(sample: SNSample, omega_m: float) -> FloatArray:
    """Distance modulus of flat LCDM (h = H_FIDUCIAL, offset-degenerate)."""
    background = Background(h=H_FIDUCIAL, omega_cb=omega_m)
    return background.distance_modulus(sample.z_cmb, sample.z_hel)


def fit_lcdm_profiled(sample: SNSample, mag: FloatArray) -> LcdmProfiledFit:
    """P9.2 per-vector fit: Omega_m bounded scalar, offset profiled."""

    def chi2_fn(omega_m: float) -> float:
        return sample.chi2_marginalized_with_mag(mag, mu_lcdm(sample, omega_m))

    result = minimize_scalar(
        chi2_fn, bounds=OMEGA_M_BOUNDS, method="bounded", options={"xatol": XATOL}
    )
    omega_m = float(result.x)
    flagged = not bool(result.success) or not (
        OMEGA_M_BOUNDS[0] + BOUND_MARGIN < omega_m < OMEGA_M_BOUNDS[1] - BOUND_MARGIN
    )
    return LcdmProfiledFit(omega_m=omega_m, chi2=float(result.fun), flagged=flagged)


def draw_mock(sample: SNSample, mu_fid: FloatArray, seed: int) -> FloatArray:
    """One mock magnitude vector mu_fid + L xi, xi ~ N(0, I) [P9.2]."""
    rng = np.random.default_rng(seed)
    return mu_fid + sample.cholesky_lower @ rng.standard_normal(sample.n_sne)


def run_mock_chi2s(
    sample: SNSample, *, seed_stream: str, n_mocks: int, fid_omega_m: float
) -> tuple[FloatArray, int]:
    """The mock chi2_min distribution and the flagged-fit count."""
    mu_fid = mu_lcdm(sample, fid_omega_m)
    chi2s = np.empty(n_mocks, dtype=np.float64)
    n_flagged = 0
    for index in range(n_mocks):
        mock_mag = draw_mock(sample, mu_fid, derive_seed(f"{seed_stream}-{index}"))
        fit = fit_lcdm_profiled(sample, mock_mag)
        chi2s[index] = fit.chi2
        n_flagged += int(fit.flagged)
    return chi2s, n_flagged


def run_mock_test(
    sample: SNSample, *, seed_stream: str, n_mocks: int, fid_omega_m: float
) -> MockTestResult:
    """Full P9 mock test against the sample's own (real) magnitudes."""
    real_fit = fit_lcdm_profiled(sample, sample.mag)
    chi2s, n_flagged = run_mock_chi2s(
        sample, seed_stream=seed_stream, n_mocks=n_mocks, fid_omega_m=fid_omega_m
    )
    k_below = int(np.sum(chi2s < real_fit.chi2))
    p_low = (k_below + 1) / (n_mocks + 1)
    return MockTestResult(
        n_mocks=n_mocks,
        fid_omega_m=fid_omega_m,
        seed_stream=seed_stream,
        chi2_real=real_fit.chi2,
        omega_m_real=real_fit.omega_m,
        k_below=k_below,
        n_flagged=n_flagged,
        p_low_tail=p_low,
        z_one_sided=float(norm.isf(p_low)),
        z_two_sided=float(norm.isf(p_low / 2.0)),
        mock_chi2=chi2s,
    )


def normalized_residual_std(sample: SNSample, fit: LcdmProfiledFit) -> float:
    """Keeley Sec. 2 diagnostic: std (ddof=0) of the offset-removed
    residuals over the square root of the covariance diagonal."""
    delta = sample.mag - mu_lcdm(sample, fit.omega_m)
    offset = sample.profiled_offset(sample.mag, mu_lcdm(sample, fit.omega_m))
    residuals = (delta - offset) / np.sqrt(np.diag(sample.cov))
    return float(np.std(residuals))


def delta2_for_chi2_eq_n(sample: SNSample, *, xtol: float = 1e-7) -> tuple[float, float]:
    """Keeley Sec. 2 diagnostic: the uniform diagonal subtraction
    delta^2 such that the best-fit chi2 equals N (0.002 on Pantheon+).

    Signed generalization: negative delta^2 means an ADDITION to the
    diagonal (the chi2_real > N case). Returns (delta2, chi2_at_root).
    The positive search domain is bounded by the smallest covariance
    eigenvalue, which keeps C - delta^2 I positive definite.
    """

    def chi2_min_adjusted(delta2: float) -> float:
        adjusted = SNSample(
            name=f"{sample.name}-delta2",
            z_cmb=sample.z_cmb,
            z_hel=sample.z_hel,
            mag=sample.mag,
            cov=sample.cov - delta2 * np.eye(sample.n_sne),
            survey_ids=sample.survey_ids,
        )
        return fit_lcdm_profiled(adjusted, adjusted.mag).chi2

    target = float(sample.n_sne)

    def gap(delta2: float) -> float:
        return chi2_min_adjusted(delta2) - target

    gap_zero = gap(0.0)
    if gap_zero == 0.0:
        return 0.0, target
    # chi2_min increases as delta2 grows (errors shrink), so bracket
    # towards positive delta2 when chi2_real < N, negative otherwise.
    if gap_zero < 0.0:
        eigval_min = float(np.linalg.eigvalsh(sample.cov)[0])
        upper_limit = 0.99 * eigval_min
        upper = min(0.001, upper_limit)
        while gap(upper) < 0.0:
            if upper >= upper_limit:
                raise ValueError(
                    f"{sample.name}: chi2_min stays below N within the SPD domain "
                    f"(delta2 <= {upper_limit:.6g})"
                )
            upper = min(2.0 * upper, upper_limit)
        bracket = (0.0, upper)
    else:
        lower = -0.001
        while gap(lower) > 0.0:
            lower *= 2.0
            if lower < -1.0:
                raise ValueError(f"{sample.name}: no delta2 in (-1, 0) reaches chi2_min = N")
        bracket = (lower, 0.0)
    delta2 = float(brentq(gap, *bracket, xtol=xtol))
    return delta2, chi2_min_adjusted(delta2)
