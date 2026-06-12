"""M11 mock-engine tests (PREREGISTRATION.md P9.5 G11.1 + [TESTS] V1).

G11.1: on a synthetic sample with diagonal covariance, the mock
chi2_min distribution must match the analytic chi2(N - 2) law (offset
profiled + Omega_m fitted): the empirical percentile of the analytic
median must fall within +/-2%. Everything is seeded, hence exact.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from scipy.stats import chi2 as chi2_dist

from desi_w0wa_refit.fitting import derive_seed
from desi_w0wa_refit.mocks import (
    OMEGA_M_BOUNDS,
    LcdmProfiledFit,
    delta2_for_chi2_eq_n,
    draw_mock,
    fit_lcdm_profiled,
    mu_lcdm,
    normalized_residual_std,
    run_mock_chi2s,
    run_mock_test,
)
from desi_w0wa_refit.sne import SNSample, load_pantheon_plus_keeley

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

N_SYNTH = 120
SIGMA_SYNTH = 0.05
FID_OMEGA_M = 0.3


@pytest.fixture(scope="module")
def synthetic_sample() -> SNSample:
    """N=120 SNe, diagonal covariance, data drawn at the fiducial."""
    z = np.linspace(0.02, 1.0, N_SYNTH)
    sample_noiseless = SNSample(
        name="synthetic",
        z_cmb=z,
        z_hel=z,
        mag=np.zeros(N_SYNTH),
        cov=SIGMA_SYNTH**2 * np.eye(N_SYNTH),
    )
    mag = draw_mock(
        sample_noiseless, mu_lcdm(sample_noiseless, FID_OMEGA_M), derive_seed("test-g111-data")
    )
    return SNSample(
        name="synthetic", z_cmb=z, z_hel=z, mag=mag, cov=SIGMA_SYNTH**2 * np.eye(N_SYNTH)
    )


def test_chi2_with_mag_matches_chi2_marginalized(synthetic_sample: SNSample) -> None:
    mu = mu_lcdm(synthetic_sample, 0.35)
    direct = synthetic_sample.chi2_marginalized(mu)
    via_mag = synthetic_sample.chi2_marginalized_with_mag(synthetic_sample.mag, mu)
    assert direct == via_mag


def test_cholesky_lower_reconstructs_covariance(synthetic_sample: SNSample) -> None:
    lower = synthetic_sample.cholesky_lower
    np.testing.assert_allclose(lower @ lower.T, synthetic_sample.cov, atol=1e-12)


def test_profiled_offset_minimizes_chi2(synthetic_sample: SNSample) -> None:
    """chi2 with the profiled offset subtracted equals the profiled chi2."""
    mu = mu_lcdm(synthetic_sample, FID_OMEGA_M)
    offset = synthetic_sample.profiled_offset(synthetic_sample.mag, mu)
    chi2_at_offset = synthetic_sample.chi2_marginalized_with_mag(synthetic_sample.mag, mu + offset)
    assert abs(chi2_at_offset - synthetic_sample.chi2_marginalized(mu)) < 1e-9
    # and it is the minimum: nearby offsets do worse
    for shift in (-0.01, 0.01):
        worse = (synthetic_sample.mag - mu - offset - shift) @ np.linalg.solve(
            synthetic_sample.cov, synthetic_sample.mag - mu - offset - shift
        )
        assert worse > synthetic_sample.chi2_marginalized(mu)


def test_seed_reproducibility(synthetic_sample: SNSample) -> None:
    """[TESTS] V1: the mock distribution is reproducible from the seed."""
    first, flag_a = run_mock_chi2s(
        synthetic_sample, seed_stream="test-repro", n_mocks=5, fid_omega_m=FID_OMEGA_M
    )
    second, flag_b = run_mock_chi2s(
        synthetic_sample, seed_stream="test-repro", n_mocks=5, fid_omega_m=FID_OMEGA_M
    )
    np.testing.assert_array_equal(first, second)
    assert flag_a == flag_b
    other, _ = run_mock_chi2s(
        synthetic_sample, seed_stream="test-repro-other", n_mocks=5, fid_omega_m=FID_OMEGA_M
    )
    assert not np.array_equal(first, other)


def test_g11_1_synthetic_percentile(synthetic_sample: SNSample) -> None:
    """G11.1: empirical percentile of the analytic chi2(N-2) median
    within +/-2% of 50% (P9.5)."""
    n_mocks = 2000
    chi2s, n_flagged = run_mock_chi2s(
        synthetic_sample, seed_stream="test-g111-mock", n_mocks=n_mocks, fid_omega_m=FID_OMEGA_M
    )
    assert n_flagged == 0
    analytic_median = float(chi2_dist.ppf(0.5, N_SYNTH - 2))
    empirical_percentile = float(np.mean(chi2s < analytic_median))
    assert abs(empirical_percentile - 0.5) < 0.02


def test_flagged_when_omega_m_clips() -> None:
    """A vector favoring Omega_m below the bound is flagged, not silently
    clipped (P9.2 failure policy)."""
    z = np.linspace(0.02, 1.0, 40)
    reference = SNSample(name="tmp", z_cmb=z, z_hel=z, mag=np.zeros(40), cov=np.eye(40))
    # a magnitude shape MORE extreme than the Omega_m = 0.01 bound
    # (linear extrapolation past the bound in model space)
    extrapolated = 2.0 * mu_lcdm(reference, 0.01) - mu_lcdm(reference, 0.2)
    sample = SNSample(name="clip", z_cmb=z, z_hel=z, mag=extrapolated, cov=1e-4 * np.eye(40))
    fit = fit_lcdm_profiled(sample, sample.mag)
    assert fit.flagged
    assert fit.omega_m < OMEGA_M_BOUNDS[0] + 2e-4


def test_run_mock_test_statistics(synthetic_sample: SNSample) -> None:
    """p = (k+1)/(N+1) and the count come from the same array."""
    result = run_mock_test(
        synthetic_sample, seed_stream="test-stat", n_mocks=20, fid_omega_m=FID_OMEGA_M
    )
    assert result.k_below == int(np.sum(result.mock_chi2 < result.chi2_real))
    assert result.p_low_tail == (result.k_below + 1) / 21
    assert result.n_mocks == 20
    assert result.z_two_sided >= result.z_one_sided


def test_delta2_is_additive_under_diagonal_inflation(synthetic_sample: SNSample) -> None:
    """C + a*I shifts the delta2 root by exactly +a (same objective),
    and the root reaches chi2_min = N."""
    injected = 0.0004
    inflated = SNSample(
        name="inflated",
        z_cmb=synthetic_sample.z_cmb,
        z_hel=synthetic_sample.z_hel,
        mag=synthetic_sample.mag,
        cov=synthetic_sample.cov + injected * np.eye(N_SYNTH),
    )
    delta2_base, chi2_base = delta2_for_chi2_eq_n(synthetic_sample)
    delta2_inflated, chi2_inflated = delta2_for_chi2_eq_n(inflated)
    assert abs(chi2_base - N_SYNTH) < 0.01
    assert abs(chi2_inflated - N_SYNTH) < 0.01
    assert abs((delta2_inflated - delta2_base) - injected) < 5e-7


def test_normalized_residual_std_is_order_one(synthetic_sample: SNSample) -> None:
    fit = fit_lcdm_profiled(synthetic_sample, synthetic_sample.mag)
    assert isinstance(fit, LcdmProfiledFit)
    std = normalized_residual_std(synthetic_sample, fit)
    assert 0.8 < std < 1.2


@pytest.mark.requires_data
def test_pantheon_plus_keeley_selection_is_1580() -> None:
    """The Keeley/SH0ES-mode count, calibrator clause included."""
    sample = load_pantheon_plus_keeley(
        DATA_DIR / "Pantheon+SH0ES.dat", DATA_DIR / "Pantheon+SH0ES_STAT+SYS.cov"
    )
    assert sample.n_sne == 1580
