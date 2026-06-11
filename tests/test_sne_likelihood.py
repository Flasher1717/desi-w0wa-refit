"""Unit tests for the SN offset-marginalized likelihood (synthetic data)."""

import gzip
from pathlib import Path

import numpy as np
import pytest
from scipy.optimize import minimize_scalar

from desi_w0wa_refit.sne import SNSample, read_packed_covariance


def _toy_sample(n: int = 6, seed: int = 20260611) -> SNSample:
    rng = np.random.default_rng(seed)
    z = np.sort(rng.uniform(0.02, 1.0, n))
    base = rng.normal(0.0, 0.05, (n, n))
    cov = base @ base.T + np.eye(n) * 0.05
    mag = 5.0 * np.log10(3e5 * z) + 25.0 + rng.normal(0.0, 0.05, n)
    return SNSample(name="toy", z_cmb=z, z_hel=z, mag=mag, cov=cov)


def test_marginalized_chi2_equals_brute_force_minimum() -> None:
    sample = _toy_sample()
    mu_model = 5.0 * np.log10(2.9e5 * sample.z_cmb) + 25.0
    inv_cov = np.linalg.inv(sample.cov)

    def chi2_at_offset(offset: float) -> float:
        delta = sample.mag - mu_model - offset
        return float(delta @ inv_cov @ delta)

    brute = minimize_scalar(chi2_at_offset, bounds=(-5.0, 5.0), method="bounded")
    assert abs(sample.chi2_marginalized(mu_model) - brute.fun) < 1e-9


def test_marginalized_chi2_is_offset_invariant() -> None:
    sample = _toy_sample()
    mu_model = 5.0 * np.log10(2.9e5 * sample.z_cmb) + 25.0
    chi2_ref = sample.chi2_marginalized(mu_model)
    for offset in (-19.4, -3.0, 0.7, 42.0):
        assert abs(sample.chi2_marginalized(mu_model + offset) - chi2_ref) < 1e-8


def test_offset_log_norm_matches_des_convention() -> None:
    sample = _toy_sample()
    inv_cov = np.linalg.inv(sample.cov)
    expected = np.log(np.sum(inv_cov) / (2.0 * np.pi))
    assert abs(sample.offset_log_norm - expected) < 1e-10


def test_subset_extracts_consistent_block() -> None:
    sample = _toy_sample(n=8)
    mask = sample.z_cmb > float(np.median(sample.z_cmb))
    sub = sample.subset(mask)
    idx = np.flatnonzero(mask)
    assert sub.n_sne == idx.size
    np.testing.assert_array_equal(sub.mag, sample.mag[idx])
    np.testing.assert_array_equal(sub.cov, sample.cov[np.ix_(idx, idx)])


def test_subset_rejects_empty_mask() -> None:
    sample = _toy_sample()
    with pytest.raises(ValueError, match="selects no supernovae"):
        sample.subset(np.zeros(sample.n_sne, dtype=bool))


def test_chi2_rejects_wrong_shape_and_non_finite() -> None:
    sample = _toy_sample()
    with pytest.raises(ValueError, match="shape"):
        sample.chi2_marginalized(np.zeros(sample.n_sne + 1))
    bad = np.zeros(sample.n_sne)
    bad[0] = np.nan
    with pytest.raises(ValueError, match="non-finite"):
        sample.chi2_marginalized(bad)


def _write_packed(path: Path, cov: "np.ndarray[tuple[int, ...], np.dtype[np.float64]]") -> None:
    lines = [str(cov.shape[0])] + [repr(float(v)) for v in cov.ravel()]
    text = "\n".join(lines) + "\n"
    if path.suffix == ".gz":
        with gzip.open(path, "wt", encoding="utf-8") as fh:
            fh.write(text)
    else:
        path.write_text(text, encoding="utf-8")


def test_read_packed_covariance_plain_and_gzip(tmp_path: Path) -> None:
    rng = np.random.default_rng(7)
    base = rng.normal(size=(4, 4))
    cov = base @ base.T + np.eye(4)
    for name in ("cov.txt", "cov.txt.gz"):
        path = tmp_path / name
        _write_packed(path, cov)
        np.testing.assert_allclose(read_packed_covariance(path), cov, rtol=0, atol=1e-15)


def test_read_packed_covariance_rejects_truncated_file(tmp_path: Path) -> None:
    path = tmp_path / "bad.txt"
    path.write_text("3\n1.0\n2.0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="expected 9 covariance values"):
        read_packed_covariance(path)
