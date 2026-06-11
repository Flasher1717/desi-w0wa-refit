"""Unit tests for the M5 arm chi2 builders (synthetic data)."""

import numpy as np
import pytest

from desi_w0wa_refit.arms import Arm, bao_predictions, make_bao_only_arm, make_cmb_arm
from desi_w0wa_refit.bao import BAOData
from desi_w0wa_refit.cmb import CMBCompressedPrior
from desi_w0wa_refit.cosmology import Background
from desi_w0wa_refit.sne import SNSample


def _toy_bao() -> BAOData:
    # Mimics the real layout: BGS DV-only, one (DM, DH) pair, and the Lya
    # block with the verified DH-before-DM inversion.
    background = Background(h=1.0, omega_cb=0.3)
    z = np.asarray([0.295, 0.51, 0.51, 2.33, 2.33])
    observables = ("DV_over_rs", "DM_over_rs", "DH_over_rs", "DH_over_rs", "DM_over_rs")
    rd = 100.0
    d_m = background.comoving_distance_mpc(z)
    d_h = background.hubble_distance_mpc(z)
    d_v = (z * d_m**2 * d_h) ** (1.0 / 3.0)
    table = {"DM_over_rs": d_m, "DH_over_rs": d_h, "DV_over_rs": d_v}
    values = np.asarray([table[obs][i] / rd for i, obs in enumerate(observables)], dtype=np.float64)
    cov = np.diag(np.full(5, 0.01**2))
    return BAOData(z=z, values=values, observables=observables, cov=cov)


def _toy_sn() -> SNSample:
    z = np.linspace(0.05, 1.0, 12)
    background = Background(h=0.7, omega_cb=0.3)
    mag = np.asarray(background.distance_modulus(z, z), dtype=np.float64)
    cov = np.diag(np.full(12, 0.05**2))
    return SNSample(name="toy", z_cmb=z, z_hel=z, mag=mag, cov=cov)


def test_bao_predictions_respect_row_order_including_lya_inversion() -> None:
    bao = _toy_bao()
    background = Background(h=1.0, omega_cb=0.3)
    predictions = bao_predictions(background, bao, 100.0)
    np.testing.assert_allclose(predictions, bao.values, rtol=1e-12)
    assert abs(bao.chi2(predictions)) < 1e-12


def test_bao_only_arm_recovers_truth_and_nests_lcdm() -> None:
    bao = _toy_bao()
    arm = make_bao_only_arm(bao)
    x_lcdm = np.asarray([0.3, 100.0])
    assert arm.chi2_lcdm(x_lcdm) < 1e-12
    x_w0wa = np.asarray([0.3, 100.0, -1.0, 0.0])
    assert arm.chi2_w0wa(x_w0wa) == arm.chi2_lcdm(x_lcdm)


def test_hard_priors_return_inf() -> None:
    bao = _toy_bao()
    arm = make_bao_only_arm(bao)
    assert arm.chi2_w0wa(np.asarray([0.3, 100.0, 0.5, 0.5])) == float("inf")  # w0+wa >= 0
    assert arm.chi2_w0wa(np.asarray([0.3, 5.0, -1.0, 0.0])) == float("inf")  # hrd low
    assert arm.chi2_lcdm(np.asarray([0.999, 100.0])) == float("inf")  # omega_m high
    cmb_arm = make_cmb_arm(bao, CMBCompressedPrior())
    assert cmb_arm.chi2_lcdm(np.asarray([0.05, 0.95, 0.09])) == float("inf")  # omega_c < 0


def test_cmb_arm_counts_data_points() -> None:
    bao = _toy_bao()
    prior = CMBCompressedPrior()
    arm = make_cmb_arm(bao, prior)
    assert arm.n_data == bao.n_points + 3
    with_sn = make_cmb_arm(bao, prior, _toy_sn())
    assert with_sn.n_data == bao.n_points + 3 + 12
    assert with_sn.name == "BAO+CMB+toy"


def test_cmb_arm_chi2_is_finite_and_lcdm_nested() -> None:
    bao = _toy_bao()
    arm = make_cmb_arm(bao, CMBCompressedPrior(), _toy_sn())
    x_lcdm = np.asarray([0.31, 0.68, 0.0222])
    value = arm.chi2_lcdm(x_lcdm)
    assert np.isfinite(value)
    x_w0wa = np.asarray([0.31, 0.68, 0.0222, -1.0, 0.0])
    assert arm.chi2_w0wa(x_w0wa) == value


def test_w0wa_start_constraint() -> None:
    assert Arm.w0wa_start_constraint(np.asarray([0.3, 100.0, -1.0, -0.5]))
    assert not Arm.w0wa_start_constraint(np.asarray([0.3, 100.0, 0.5, 0.5]))


def test_bao_predictions_rejects_nothing_but_matches_shapes() -> None:
    bao = _toy_bao()
    background = Background(h=1.0, omega_cb=0.25, w0=-0.8, wa=-0.4)
    predictions = bao_predictions(background, bao, 95.0)
    assert predictions.shape == bao.values.shape
    assert np.isfinite(predictions).all()
    with pytest.raises(ValueError, match="shape"):
        bao.chi2(predictions[:3])
