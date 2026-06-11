"""External-anchor tests against the real pinned DESI DR2 BAO files.

Auto-skipped when data/ is absent (see conftest). Expected values come from
arXiv:2503.14738v3 Table 4 and the verbatim file contents documented in
RESULTS.md section 2.1 (cross-checked by two independent extractions).
"""

import math
from pathlib import Path

import numpy as np
import pytest

from desi_w0wa_refit.bao import BAOData, load_bao_data

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

pytestmark = pytest.mark.requires_data

EXPECTED_Z = [
    0.295,
    0.510,
    0.510,
    0.706,
    0.706,
    0.934,
    0.934,
    1.321,
    1.321,
    1.484,
    1.484,
    2.33,
    2.33,
]


@pytest.fixture(scope="module")
def real_data() -> BAOData:
    return load_bao_data(
        DATA_DIR / "desi_gaussian_bao_ALL_GCcomb_mean.txt",
        DATA_DIR / "desi_gaussian_bao_ALL_GCcomb_cov.txt",
    )


def test_thirteen_points(real_data: BAOData) -> None:
    assert real_data.n_points == 13


def test_effective_redshifts(real_data: BAOData) -> None:
    np.testing.assert_allclose(real_data.z, EXPECTED_Z, rtol=0, atol=1e-12)


def test_observable_pattern_including_lya_inversion(real_data: BAOData) -> None:
    # BGS is DV-only; all other tracers are (DM, DH) pairs EXCEPT Lya (z=2.33)
    # where the file lists DH before DM (verified quirk of the release).
    assert real_data.observables[0] == "DV_over_rs"
    assert real_data.observables[1:11] == ("DM_over_rs", "DH_over_rs") * 5
    assert real_data.observables[11] == "DH_over_rs"
    assert real_data.observables[12] == "DM_over_rs"


def test_values_match_table4_rounding(real_data: BAOData) -> None:
    # arXiv:2503.14738v3 Table 4 quotes these to 3 decimals. The paper
    # TRUNCATES at least one entry instead of rounding (file has
    # 38.98897... printed as 38.988), so the tolerance must cover a full
    # unit in the last printed decimal: |file - table| < 1e-3.
    table4 = {
        (0.295, "DV_over_rs"): 7.942,
        (0.510, "DM_over_rs"): 13.588,
        (0.510, "DH_over_rs"): 21.863,
        (0.706, "DM_over_rs"): 17.351,
        (0.706, "DH_over_rs"): 19.455,
        (0.934, "DM_over_rs"): 21.576,
        (0.934, "DH_over_rs"): 17.641,
        (1.321, "DM_over_rs"): 27.601,
        (1.321, "DH_over_rs"): 14.176,
        (1.484, "DM_over_rs"): 30.512,
        (1.484, "DH_over_rs"): 12.817,
        (2.33, "DH_over_rs"): 8.632,
        (2.33, "DM_over_rs"): 38.988,
    }
    for z, observable, value in zip(
        real_data.z, real_data.observables, real_data.values, strict=True
    ):
        assert abs(float(value) - table4[(float(z), observable)]) < 1e-3


def test_covariance_is_validated_on_load(real_data: BAOData) -> None:
    # BAOData.__post_init__ already enforces symmetry/SPD/finiteness;
    # spot-check documented entries (RESULTS.md 2.1, agent-verified verbatim).
    assert real_data.cov.shape == (13, 13)
    assert math.isclose(float(real_data.cov[0, 0]), 5.78998687e-03, rel_tol=1e-9)
    assert math.isclose(float(real_data.cov[1, 2]), -3.26062007e-02, rel_tol=1e-9)
    assert math.isclose(float(real_data.cov[12, 11]), -2.31395216e-02, rel_tol=1e-7)


def test_block_diagonal_structure(real_data: BAOData) -> None:
    # Zero covariance between different tracers (blocks: 1,2,2,2,2,2,2).
    blocks = [(0, 1), (1, 3), (3, 5), (5, 7), (7, 9), (9, 11), (11, 13)]
    cov = real_data.cov
    for i, (start_i, end_i) in enumerate(blocks):
        for j, (start_j, end_j) in enumerate(blocks):
            if i != j:
                assert np.all(cov[start_i:end_i, start_j:end_j] == 0.0)


def test_chi2_zero_at_data(real_data: BAOData) -> None:
    assert abs(real_data.chi2(real_data.values.copy())) < 1e-12
