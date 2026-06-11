"""Unit tests for the BAO Gaussian likelihood (synthetic fixtures, no data/)."""

import math
from pathlib import Path

import numpy as np
import pytest

from desi_w0wa_refit.bao import BAOData, CovarianceError, load_bao_data, validate_covariance

MEAN_TEXT = """\
# [z] [value at z] [quantity]
0.295 7.9 DV_over_rs
0.510 13.6 DM_over_rs
0.510 21.9 DH_over_rs
"""

COV_TEXT = """\
0.04 0.0 0.0
0.0 0.09 -0.01
0.0 -0.01 0.16
"""


@pytest.fixture
def synthetic_files(tmp_path: Path) -> tuple[Path, Path]:
    mean_path = tmp_path / "mean.txt"
    cov_path = tmp_path / "cov.txt"
    mean_path.write_text(MEAN_TEXT, encoding="utf-8")
    cov_path.write_text(COV_TEXT, encoding="utf-8")
    return mean_path, cov_path


def test_load_parses_measurements(synthetic_files: tuple[Path, Path]) -> None:
    data = load_bao_data(*synthetic_files)
    assert data.n_points == 3
    np.testing.assert_allclose(data.z, [0.295, 0.510, 0.510])
    np.testing.assert_allclose(data.values, [7.9, 13.6, 21.9])
    assert data.observables == ("DV_over_rs", "DM_over_rs", "DH_over_rs")


def test_chi2_zero_at_data_vector(synthetic_files: tuple[Path, Path]) -> None:
    data = load_bao_data(*synthetic_files)
    assert abs(data.chi2(data.values.copy())) < 1e-14


def test_chi2_matches_hand_computation(synthetic_files: tuple[Path, Path]) -> None:
    data = load_bao_data(*synthetic_files)
    predicted = data.values + np.array([0.2, -0.3, 0.4])
    residual = predicted - data.values
    expected = float(residual @ np.linalg.inv(data.cov) @ residual)
    assert math.isclose(data.chi2(predicted), expected, rel_tol=1e-12)


def test_chi2_diagonal_case_explicit(synthetic_files: tuple[Path, Path]) -> None:
    mean_path, cov_path = synthetic_files
    cov_path.write_text("0.04 0.0 0.0\n0.0 0.09 0.0\n0.0 0.0 0.16\n", encoding="utf-8")
    data = load_bao_data(mean_path, cov_path)
    predicted = data.values + np.array([0.2, 0.3, 0.4])
    # (0.2^2/0.04) + (0.3^2/0.09) + (0.4^2/0.16) = 1 + 1 + 1
    assert math.isclose(data.chi2(predicted), 3.0, rel_tol=1e-12)


def test_unknown_observable_rejected(tmp_path: Path) -> None:
    mean_path = tmp_path / "mean.txt"
    mean_path.write_text("0.3 7.9 DA_over_rs\n", encoding="utf-8")
    cov_path = tmp_path / "cov.txt"
    cov_path.write_text("0.01\n", encoding="utf-8")
    with pytest.raises(ValueError, match="unknown observable"):
        load_bao_data(mean_path, cov_path)


def test_dimension_mismatch_rejected(synthetic_files: tuple[Path, Path]) -> None:
    mean_path, cov_path = synthetic_files
    cov_path.write_text("0.04 0.0\n0.0 0.09\n", encoding="utf-8")
    with pytest.raises(ValueError, match="does not match"):
        load_bao_data(mean_path, cov_path)


def test_asymmetric_covariance_rejected() -> None:
    cov = np.array([[1.0, 0.5], [0.4, 1.0]])
    with pytest.raises(CovarianceError, match="not symmetric"):
        validate_covariance(cov)


def test_non_positive_definite_covariance_rejected() -> None:
    cov = np.array([[1.0, 2.0], [2.0, 1.0]])
    with pytest.raises(CovarianceError, match="not positive definite"):
        validate_covariance(cov)


def test_non_finite_covariance_rejected() -> None:
    cov = np.array([[1.0, np.nan], [np.nan, 1.0]])
    with pytest.raises(CovarianceError, match="non-finite"):
        validate_covariance(cov)


def test_non_finite_prediction_rejected(synthetic_files: tuple[Path, Path]) -> None:
    data = load_bao_data(*synthetic_files)
    bad = data.values.copy()
    bad[0] = np.inf
    with pytest.raises(ValueError, match="non-finite"):
        data.chi2(bad)


def test_wrong_prediction_shape_rejected(synthetic_files: tuple[Path, Path]) -> None:
    data = load_bao_data(*synthetic_files)
    with pytest.raises(ValueError, match="shape"):
        data.chi2(np.array([1.0, 2.0]))


def test_inconsistent_lengths_rejected() -> None:
    with pytest.raises(ValueError, match="inconsistent lengths"):
        BAOData(
            z=np.array([0.3]),
            values=np.array([7.9, 8.0]),
            observables=("DV_over_rs",),
            cov=np.eye(2),
        )
