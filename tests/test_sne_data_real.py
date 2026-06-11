"""External-anchor tests against the real pinned SNe files.

Auto-skipped when data/ is absent (see conftest). Spot values are verbatim
file contents recorded at first download (2026-06-11); sample compositions
match RESULTS.md section 2 (Pantheon+ 1701 -> 1590 after the zHD > 0.01
cut; DES-SN5YR 1829 = 1635 DES + 8 CSP + 68 CfA + 118 Foundation;
Union3 22 spline nodes).
"""

from pathlib import Path

import numpy as np
import pytest

from desi_w0wa_refit.sne import (
    SNSample,
    load_des_sn5yr,
    load_pantheon_plus,
    load_union3,
    read_packed_covariance,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

pytestmark = pytest.mark.requires_data


@pytest.fixture(scope="module")
def pantheon() -> SNSample:
    return load_pantheon_plus(
        DATA_DIR / "Pantheon+SH0ES.dat", DATA_DIR / "Pantheon+SH0ES_STAT+SYS.cov"
    )


@pytest.fixture(scope="module")
def des() -> SNSample:
    return load_des_sn5yr(DATA_DIR / "DES-SN5YR_HD.csv", DATA_DIR / "DES-SN5YR_STAT+SYS.txt.gz")


@pytest.fixture(scope="module")
def union3() -> SNSample:
    return load_union3(DATA_DIR / "Union3_lcparam_full.txt", DATA_DIR / "Union3_mag_covmat.txt")


def test_pantheon_cosmology_cut_keeps_1590(pantheon: SNSample) -> None:
    assert pantheon.n_sne == 1590
    assert float(pantheon.z_cmb.min()) > 0.01


def test_pantheon_full_covariance_header_and_corner() -> None:
    cov = read_packed_covariance(DATA_DIR / "Pantheon+SH0ES_STAT+SYS.cov")
    assert cov.shape == (1701, 1701)
    assert abs(float(cov[0, 0]) - 0.03177108) < 1e-12
    assert abs(float(cov[0, 1]) - 0.00575443) < 1e-12


def test_des_sample_composition(des: SNSample) -> None:
    assert des.n_sne == 1829
    assert des.survey_ids is not None
    ids, counts = np.unique(des.survey_ids.astype(int), return_counts=True)
    composition = dict(zip(ids.tolist(), counts.tolist(), strict=True))
    assert composition[10] == 1635  # DES
    assert composition[5] == 8  # CSP
    assert composition[150] == 118  # Foundation
    assert sum(composition[k] for k in (63, 64, 65, 66)) == 68  # CfA


def test_des_first_row_and_total_covariance(des: SNSample) -> None:
    # First HD.csv row: CID 1246275, IDSURVEY 10, zHD 0.24605, zHEL 0.24651,
    # MU 40.5938, MUERR_FINAL 0.0968. Total covariance adds MUERR_FINAL^2
    # to the diagonal of the systematic matrix (first value 1.931931e-04).
    assert abs(float(des.z_cmb[0]) - 0.24605) < 1e-12
    assert abs(float(des.z_hel[0]) - 0.24651) < 1e-12
    assert abs(float(des.mag[0]) - 40.5938) < 1e-12
    assert abs(float(des.cov[0, 0]) - (1.931931e-04 + 0.0968**2)) < 1e-12
    assert abs(float(des.cov[0, 1]) - 1.591030e-04) < 1e-12


def test_union3_nodes(union3: SNSample) -> None:
    assert union3.n_sne == 22
    assert abs(float(union3.z_cmb[0]) - 0.05) < 1e-12
    assert abs(float(union3.z_cmb[-1]) - 2.26226) < 1e-12
    assert abs(float(union3.mag[0]) - 36.630361) < 1e-12
    assert abs(float(union3.mag[-1]) - 45.997159) < 1e-12
    assert abs(float(union3.cov[0, 0]) - 0.0086044441289678) < 1e-15
    assert abs(float(union3.cov[0, 1]) - 0.0078396482652654) < 1e-15
    np.testing.assert_array_equal(union3.z_hel, union3.z_cmb)


def test_real_covariances_are_spd_via_loaders(
    pantheon: SNSample, des: SNSample, union3: SNSample
) -> None:
    # SNSample.__post_init__ already Cholesky-validates; assert the loaders
    # produced usable objects with finite marginalized chi2 at a crude model.
    for sample in (pantheon, des, union3):
        mu_crude = 5.0 * np.log10(3e5 * sample.z_cmb * (1.0 + sample.z_cmb)) + 25.0
        chi2 = sample.chi2_marginalized(mu_crude)
        assert np.isfinite(chi2)
        assert chi2 > 0.0


def test_marginalization_offset_invariance_on_real_des(des: SNSample) -> None:
    mu_crude = 5.0 * np.log10(3e5 * des.z_cmb * (1.0 + des.z_cmb)) + 25.0
    chi2_ref = des.chi2_marginalized(mu_crude)
    assert abs(des.chi2_marginalized(mu_crude + 11.3) - chi2_ref) < 1e-6
