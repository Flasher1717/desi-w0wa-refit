"""M4 tests for the compressed CMB prior and pre-recombination formulas.

Pre-registered anchors (PREREGISTRATION.md P1-P2): Aubourg Eq. (16)
reproduces the DESI DR2 published anchor r_d = 147.05 Mpc at the Planck
point within 0.3 %; Aubourg and DESI Eq. (2) agree within 0.3 % over the
prior domain; the P1 constants equal the pinned official yaml exactly and
round to the printed Eqs. (35)-(36).
"""

import itertools
import re
from pathlib import Path

import numpy as np
import pytest

from desi_w0wa_refit.cmb import (
    CMB_PRIOR_COV,
    CMB_PRIOR_MEAN,
    CMBCompressedPrior,
    DESIParams,
    sound_horizon_drag_aubourg_mpc,
    sound_horizon_drag_desi_eq2_mpc,
    z_star_hu_sugiyama,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def test_aubourg_rd_reproduces_published_desi_anchor() -> None:
    # 2503.14738v3, Section I: r_d = 147.05 Mpc at omega_b = 0.02236,
    # omega_bc = 0.1432, Neff = 3.04 ("scaled to the best-fit values from
    # Planck"). Tolerance 0.3 % = documented/estimated precisions summed.
    r_d = sound_horizon_drag_aubourg_mpc(0.02236, 0.1432)
    assert abs(r_d / 147.05 - 1.0) < 0.003


def test_aubourg_and_desi_eq2_agree_over_prior_domain() -> None:
    # "Domaine des priors" (P2): (omega_b, omega_bc) are constrained ONLY
    # by the Gaussian CMB prior (the BAO-only arm never evaluates r_d), so
    # the domain where the formulas are actually used is mean +/- 5 sigma
    # of that prior — any best-fit beyond 5 sigma would already contribute
    # Delta chi2 > 25 and fail the gates loudly. Both formulas are power
    # laws calibrated at the Planck point and diverge away from it
    # (measured: 0.21 % at +/-5 sigma, 0.31 % at +/-10 sigma, 0.70 % at
    # the arbitrary corner omega_bc = 0.10); interpretation documented in
    # RESULTS.md (M4 notes).
    mean_b, mean_bc = CMB_PRIOR_MEAN[1], CMB_PRIOR_MEAN[2]
    sigma_b = float(np.sqrt(CMB_PRIOR_COV[1][1]))
    sigma_bc = float(np.sqrt(CMB_PRIOR_COV[2][2]))
    for omega_b_h2, omega_bc_h2 in itertools.product(
        np.linspace(mean_b - 5 * sigma_b, mean_b + 5 * sigma_b, 9),
        np.linspace(mean_bc - 5 * sigma_bc, mean_bc + 5 * sigma_bc, 9),
    ):
        aubourg = sound_horizon_drag_aubourg_mpc(float(omega_b_h2), float(omega_bc_h2))
        desi = sound_horizon_drag_desi_eq2_mpc(float(omega_b_h2), float(omega_bc_h2))
        assert abs(aubourg / desi - 1.0) < 0.003


def test_z_star_in_expected_range_at_planck_point() -> None:
    # HS96 is percent-level; sanity window around the known decoupling epoch.
    z_star = z_star_hu_sugiyama(0.02237, 0.1430)
    assert 1080.0 < z_star < 1100.0


def test_theta_star_consistency_at_prior_mean() -> None:
    # At parameters matching the compressed-prior mean (h fixed at the
    # Planck-like 0.6736), theta_star must come out at the published value
    # within the pre-registered HS96 percent-level limitation (P2),
    # empirically bounded by gate G5.2. Loose 0.5 % sanity tolerance.
    h = 0.6736
    omega_m = (CMB_PRIOR_MEAN[2] + 0.06 / 93.14) / h**2
    params = DESIParams(omega_m=omega_m, h=h, omega_b_h2=CMB_PRIOR_MEAN[1])
    assert abs(params.omega_bc_h2 - CMB_PRIOR_MEAN[2]) < 1e-12
    assert abs(params.theta_star() / CMB_PRIOR_MEAN[0] - 1.0) < 0.005


def test_prior_chi2_zero_at_mean_and_quadratic_elsewhere() -> None:
    prior = CMBCompressedPrior()
    assert prior.chi2(*CMB_PRIOR_MEAN) == 0.0
    offset = np.asarray([1e-6, 1e-4, 1e-3])
    point = np.asarray(CMB_PRIOR_MEAN) + offset
    expected = float(offset @ np.linalg.inv(np.asarray(CMB_PRIOR_COV)) @ offset)
    assert abs(prior.chi2(*point) / expected - 1.0) < 1e-9


def test_prior_constants_round_to_printed_eqs_35_36() -> None:
    # P1 permanent consistency test: full-precision yaml values round to
    # the printed Eq. (35) means and Eq. (36) covariance (x 1e-9).
    printed_means = (0.01041, 0.02223, 0.14208)
    for full, printed in zip(CMB_PRIOR_MEAN, printed_means, strict=True):
        assert round(full, 5) == printed
    printed_cov_1e9 = (
        (0.006621, 0.12444, -1.1929),
        (0.12444, 21.344, -94.001),
        (-1.1929, -94.001, 1488.4),
    )
    for row_full, row_printed in zip(CMB_PRIOR_COV, printed_cov_1e9, strict=True):
        for full, printed in zip(row_full, row_printed, strict=True):
            scaled = full * 1e9
            assert abs(scaled - printed) <= 5.1e-5 * max(1.0, abs(printed))


@pytest.mark.requires_data
def test_prior_constants_equal_pinned_official_yaml() -> None:
    text = (DATA_DIR / "desi_dr2_cmb_compressed_prior.yaml").read_text(encoding="utf-8")
    block = re.search(r"CMB_standard_compression_PR4:.*?means:\n(.*?)observables:", text, re.DOTALL)
    assert block is not None
    numbers = [float(tok) for tok in re.findall(r"-?\d+\.\d+(?:e-?\d+)?", block.group(1))]
    assert numbers[:3] == list(CMB_PRIOR_MEAN)
    flat_cov = [value for row in CMB_PRIOR_COV for value in row]
    assert numbers[3:12] == flat_cov
    assert re.search(r"mnu:\s*\n\s*latex:[^\n]*\n\s*value: 0\.06\b", text)
    assert re.search(r"nnu:\s*\n\s*latex:[^\n]*\n\s*value: 3\.044\b", text)


def test_desi_params_mapping_matches_official_yaml_formula() -> None:
    # omch2 = omm (H0/100)^2 - mnu/93.14 - ombh2  [official yaml, pinned].
    params = DESIParams(omega_m=0.31, h=0.68, omega_b_h2=0.0223, w0=-0.9, wa=-0.4)
    omch2 = 0.31 * 0.68**2 - 0.06 / 93.14 - 0.0223
    assert abs(params.omega_bc_h2 - (omch2 + 0.0223)) < 1e-15


def test_background_from_desi_params_uses_baseline_neutrinos() -> None:
    params = DESIParams(omega_m=0.31, h=0.68, omega_b_h2=0.0223)
    background = params.background()
    assert background.t_cmb_k == 2.7255
    assert background.neff == 3.044
    assert background.m_nu_ev == (0.06,)
    assert abs(background.omega_cb * 0.68**2 - params.omega_bc_h2) < 1e-15
