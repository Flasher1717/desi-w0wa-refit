"""V4 covariance-correction tests (PREREGISTRATION.md P12, GO M15).

Synthetic checks of the two pre-registered Keeley corrections plus the
load-bearing diagonal-vs-full distinction (decision A); a data-anchored check
that the DES factors reproduce the frozen V1 numbers (results/m11_mocks.json).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from desi_w0wa_refit.covariance_correction import (
    CorrectionFactors,
    corrected_reduced_chi2,
    correction_factors,
    rescale_covariance,
    subtract_diagonal,
)
from desi_w0wa_refit.fitting import derive_seed
from desi_w0wa_refit.mocks import draw_mock, mu_lcdm
from desi_w0wa_refit.sne import SNSample, load_des_sn5yr

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
N_SYNTH = 100


def _diagonal_sample(scatter_vs_cov: float, seed_tag: str) -> SNSample:
    """N=100 SNe, diagonal covariance; data drawn with a scatter equal to
    ``scatter_vs_cov`` times the declared covariance (so the SN-only reduced
    chi2 is ~scatter_vs_cov, away from 1)."""
    z = np.linspace(0.02, 1.0, N_SYNTH)
    cov = 0.04 * np.eye(N_SYNTH)
    drawer = SNSample(name="d", z_cmb=z, z_hel=z, mag=np.zeros(N_SYNTH), cov=scatter_vs_cov * cov)
    mag = draw_mock(drawer, mu_lcdm(drawer, 0.3), derive_seed(seed_tag))
    return SNSample(name="diag", z_cmb=z, z_hel=z, mag=mag, cov=cov)


def _correlated_sample(rho: float, seed_tag: str) -> SNSample:
    """N=100 SNe with a uniformly correlated covariance C = sigma^2[(1-rho)I +
    rho J]; SPD for 0 <= rho < 1. The off-diagonal makes diagonal normalization
    differ from full whitening."""
    z = np.linspace(0.02, 1.0, N_SYNTH)
    sigma2 = 0.04
    cov = sigma2 * ((1.0 - rho) * np.eye(N_SYNTH) + rho * np.ones((N_SYNTH, N_SYNTH)))
    drawer = SNSample(name="c", z_cmb=z, z_hel=z, mag=np.zeros(N_SYNTH), cov=cov)
    mag = draw_mock(drawer, mu_lcdm(drawer, 0.3), derive_seed(seed_tag))
    return SNSample(name="corr", z_cmb=z, z_hel=z, mag=mag, cov=cov)


def test_rescale_scales_chi2_by_inverse_factor() -> None:
    sample = _diagonal_sample(0.5, "v4-rescale-data")
    mu = mu_lcdm(sample, 0.35)
    base = sample.chi2_marginalized(mu)
    for factor in (0.5, 0.8, 1.3):
        scaled = rescale_covariance(sample, factor)
        np.testing.assert_allclose(scaled.chi2_marginalized(mu), base / factor, rtol=1e-10)


def test_rescale_rejects_nonpositive_factor() -> None:
    sample = _diagonal_sample(1.0, "v4-reject-data")
    for bad in (0.0, -0.5):
        with pytest.raises(ValueError, match="positive"):
            rescale_covariance(sample, bad)


def test_subtract_diagonal_lowers_the_diagonal_only() -> None:
    sample = _diagonal_sample(1.0, "v4-subtract-data")
    delta2 = 0.001
    out = subtract_diagonal(sample, delta2)
    np.testing.assert_allclose(np.diag(out.cov), np.diag(sample.cov) - delta2, atol=1e-15)
    off = out.cov - np.diag(np.diag(out.cov))
    off_in = sample.cov - np.diag(np.diag(sample.cov))
    np.testing.assert_allclose(off, off_in, atol=1e-15)


def test_kappa_rescale_lands_reduced_chi2_at_one() -> None:
    """Scenario (i-kappa): C -> C*kappa with kappa = reduced chi2 gives
    corrected reduced chi2 = 1 exactly (control gate G16.1)."""
    sample = _diagonal_sample(0.4, "v4-kappa-data")
    factors = correction_factors(sample)
    assert abs(factors.kappa - factors.reduced_chi2) < 1e-12
    assert factors.reduced_chi2 < 0.8  # genuinely away from 1
    corrected = rescale_covariance(sample, factors.kappa)
    assert abs(corrected_reduced_chi2(corrected) - 1.0) < 1e-6


def test_delta2_subtraction_lands_reduced_chi2_at_one() -> None:
    """Scenario (ii): C - delta^2 I gives chi2_min = N within the G16.1 gate
    tolerance. delta2_for_chi2_eq_n converges brentq on the root LOCATION
    (xtol on delta2), not on the chi2 VALUE, so chi2/N -> 1 only to the
    value-precision the Jacobian allows (~few x 1e-5 on the real correlated
    arms); the gate is 1e-3, comfortably met. A diagonal sample has a small
    Jacobian so it lands much tighter here, but we assert the gate tolerance."""
    sample = _diagonal_sample(0.6, "v4-delta2-data")
    factors = correction_factors(sample)
    corrected = subtract_diagonal(sample, factors.delta2)
    assert abs(corrected_reduced_chi2(corrected) - 1.0) < 1e-3


def test_diagonal_covariance_makes_sdiag_equal_kappa() -> None:
    """For a DIAGONAL covariance, full whitening = diagonal normalization, so
    s_diag^2 == kappa: the two scenario-(i) variants coincide (P12.2)."""
    sample = _diagonal_sample(0.5, "v4-diag-eq-data")
    factors = correction_factors(sample)
    np.testing.assert_allclose(factors.s_diag**2, factors.kappa, rtol=1e-9)


def test_correlated_covariance_separates_sdiag_from_kappa() -> None:
    """The load-bearing decision-A distinction: with OFF-diagonal correlations,
    diagonal normalization (s_diag^2) differs from full whitening (kappa =
    chi2/N), so the (i-s) control does NOT land at 1."""
    sample = _correlated_sample(0.6, "v4-corr-data")
    factors = correction_factors(sample)
    assert abs(factors.s_diag**2 - factors.kappa) > 1e-3
    corrected_s = rescale_covariance(sample, factors.s_diag**2)
    residual = corrected_reduced_chi2(corrected_s)
    assert abs(residual - 1.0) > 1e-3  # (i-s) does not reach 1
    np.testing.assert_allclose(residual, factors.reduced_chi2 / factors.s_diag**2, rtol=1e-9)


def test_corrected_samples_stay_spd() -> None:
    """All three corrections keep the covariance SPD (SNSample Cholesky)."""
    sample = _correlated_sample(0.5, "v4-spd-data")
    factors = correction_factors(sample)
    rescale_covariance(sample, factors.kappa)  # constructs => Cholesky ok
    rescale_covariance(sample, factors.s_diag**2)
    subtract_diagonal(sample, factors.delta2)


@pytest.mark.requires_data
def test_des_factors_reproduce_frozen_v1() -> None:
    """The DES correction factors (computed on the V1 sample N=1829) reproduce
    the frozen V1 numbers in results/m11_mocks.json (kappa = chi2_real/N)."""
    sample = load_des_sn5yr(DATA_DIR / "DES-SN5YR_HD.csv", DATA_DIR / "DES-SN5YR_STAT+SYS.txt.gz")
    factors = correction_factors(sample)
    assert isinstance(factors, CorrectionFactors)
    assert factors.n_sne == 1829
    m11 = json.loads((RESULTS_DIR / "m11_mocks.json").read_text(encoding="utf-8"))
    chi2_v1 = float(m11["V1_des_primary"]["chi2_real"])
    diag = m11["diagnostics_p9_4c"]["des"]
    assert abs(factors.chi2_min_sn_only - chi2_v1) < 1e-3
    np.testing.assert_allclose(factors.kappa, chi2_v1 / 1829, rtol=1e-9)
    assert abs(factors.s_diag - float(diag["normalized_residual_std_ddof0"])) < 1e-6
    assert abs(factors.delta2 - float(diag["delta2_diag_subtraction_for_chi2_eq_n"])) < 1e-6
    # G16.1 control semantics on the REAL covariance (large delta2 Jacobian):
    # (i-kappa) is exact to machine precision; (ii) lands within the 1e-3 gate.
    assert abs(corrected_reduced_chi2(rescale_covariance(sample, factors.kappa)) - 1.0) < 1e-9
    assert abs(corrected_reduced_chi2(subtract_diagonal(sample, factors.delta2)) - 1.0) < 1e-3
