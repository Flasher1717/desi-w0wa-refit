"""V5 DES-Dovekie loader tests (PREREGISTRATION.md P13, GO M15).

Synthetic checks of the SNANA HD parser and the inverse-covariance npz reader,
plus data-anchored checks that the pinned Dovekie files (commit c9a4fcaf) load
with the verified structure: 1820 SNe, Foundation = IDSURVEY 150, SPD total
covariance C = inv(inv_cov) with no diagonal added, and a valid Foundation LOO.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from desi_w0wa_refit.sne import load_des_dovekie, read_inverse_covariance_npz

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Verified IDSURVEY distribution on the pinned Dovekie HD (P13.3).
DOVEKIE_IDSURVEY_COUNTS = {5: 8, 10: 1623, 63: 16, 64: 31, 65: 22, 66: 3, 150: 117}
DOVEKIE_N = 1820
FOUNDATION_ID = 150


def _write_synthetic_npz(path: Path, inv_cov: np.ndarray) -> None:
    """Pack an inverse covariance upper-triangular (triu order) into an npz with
    keys (nsn, cov), mimicking the Dovekie release format."""
    n = inv_cov.shape[0]
    packed = inv_cov[np.triu_indices(n)].astype(np.float32)
    np.savez(path, nsn=np.array([n]), cov=packed)


def test_read_inverse_covariance_npz_round_trip(tmp_path: Path) -> None:
    rng = np.random.default_rng(20260613)
    a = rng.standard_normal((4, 4))
    inv_cov = a @ a.T + 4.0 * np.eye(4)  # SPD
    npz = tmp_path / "inv.npz"
    _write_synthetic_npz(npz, inv_cov)
    cov = read_inverse_covariance_npz(npz)
    np.testing.assert_allclose(cov, cov.T, atol=1e-12)  # symmetric
    assert np.linalg.eigvalsh(cov).min() > 0.0  # SPD
    # cov is the inverse of inv_cov (float32 packing => loose tolerance)
    np.testing.assert_allclose(np.linalg.inv(cov), inv_cov, rtol=1e-5, atol=1e-5)


def test_read_inverse_covariance_npz_rejects_wrong_length(tmp_path: Path) -> None:
    npz = tmp_path / "bad.npz"
    np.savez(npz, nsn=np.array([4]), cov=np.ones(5, dtype=np.float32))  # need 10
    with pytest.raises(ValueError, match="upper-triangular"):
        read_inverse_covariance_npz(npz)


def test_load_des_dovekie_synthetic_end_to_end(tmp_path: Path) -> None:
    """A tiny matching HD + npz exercises the SNANA parser and the loader."""
    hd = tmp_path / "hd.csv"
    hd.write_text(
        "# header comment\n"
        "VARNAMES: CID IDSURVEY zHD zHEL MU MUERR MUERR_VPEC MUERR_SYS PROBIA_BEAMS\n"
        "SN: objA 150 0.10 0.10 38.0 0.10 0.05 0.03 1.0\n"
        "SN: objB  10 0.20 0.20 40.0 0.10 0.05 0.03 1.0\n"
        "SN: objC  10 0.30 0.30 41.0 0.10 0.05 0.03 1.0\n",
        encoding="utf-8",
    )
    rng = np.random.default_rng(1)
    a = rng.standard_normal((3, 3))
    inv_cov = a @ a.T + 3.0 * np.eye(3)
    npz = tmp_path / "cov.npz"
    _write_synthetic_npz(npz, inv_cov)
    sample = load_des_dovekie(hd, npz)
    assert sample.n_sne == 3
    assert sample.survey_ids is not None
    np.testing.assert_array_equal(sample.survey_ids.astype(int), [150, 10, 10])
    np.testing.assert_allclose(sample.z_cmb, [0.10, 0.20, 0.30])
    np.testing.assert_allclose(sample.mag, [38.0, 40.0, 41.0])
    np.testing.assert_allclose(np.linalg.inv(sample.cov), inv_cov, rtol=1e-4, atol=1e-4)


@pytest.mark.requires_data
def test_dovekie_counts_and_foundation() -> None:
    sample = load_des_dovekie(
        DATA_DIR / "DES-Dovekie_HD.csv", DATA_DIR / "DES-Dovekie_STAT+SYS.npz"
    )
    assert sample.n_sne == DOVEKIE_N
    assert sample.survey_ids is not None
    ids = sample.survey_ids.astype(np.int64)
    counts = {code: int(np.count_nonzero(ids == code)) for code in DOVEKIE_IDSURVEY_COUNTS}
    assert counts == DOVEKIE_IDSURVEY_COUNTS
    assert int(ids.size) == DOVEKIE_N  # the listed codes account for every SN
    assert counts[FOUNDATION_ID] == 117


@pytest.mark.requires_data
def test_dovekie_covariance_is_spd_and_full_dimension() -> None:
    sample = load_des_dovekie(
        DATA_DIR / "DES-Dovekie_HD.csv", DATA_DIR / "DES-Dovekie_STAT+SYS.npz"
    )
    assert sample.cov.shape == (DOVEKIE_N, DOVEKIE_N)
    assert np.linalg.eigvalsh(sample.cov).min() > 0.0  # SPD (Cholesky also ran)


@pytest.mark.requires_data
def test_dovekie_foundation_loo_subset() -> None:
    """Removing Foundation (150) leaves 1703 SNe with an SPD sub-covariance."""
    sample = load_des_dovekie(
        DATA_DIR / "DES-Dovekie_HD.csv", DATA_DIR / "DES-Dovekie_STAT+SYS.npz"
    )
    assert sample.survey_ids is not None
    mask = sample.survey_ids.astype(np.int64) != FOUNDATION_ID
    loo = sample.subset(mask)
    assert loo.n_sne == DOVEKIE_N - 117  # 1703
    assert np.linalg.eigvalsh(loo.cov).min() > 0.0
