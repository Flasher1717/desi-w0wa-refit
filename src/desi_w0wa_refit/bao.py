"""DESI DR2 BAO data loading and Gaussian likelihood.

File formats follow CobayaSampler/bao_data (pinned in data_manifest.json):
- measurements: whitespace-separated rows ``z value observable`` with one
  comment line; observables are DV_over_rs, DM_over_rs, DH_over_rs.
- covariance: full N x N matrix in plain text, rows ordered exactly like
  the measurement rows (note: the Lya block lists DH before DM).

The likelihood is a pure Gaussian, chi2 = x^T C^-1 x with
x = prediction - measurement, matching cobaya's ``bao.desi_dr2``
(logp = -chi2/2, rs_fid = 1 so data are already in units of r_d).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import numpy as np
from numpy.typing import NDArray

BAOObservable = Literal["DV_over_rs", "DM_over_rs", "DH_over_rs"]
_KNOWN_OBSERVABLES: frozenset[str] = frozenset(("DV_over_rs", "DM_over_rs", "DH_over_rs"))

FloatArray = NDArray[np.float64]


class CovarianceError(ValueError):
    """Raised when a covariance matrix fails validation."""


def validate_covariance(cov: FloatArray, *, name: str = "covariance") -> None:
    """Check finiteness, symmetry and positive definiteness (P0 pattern)."""
    if cov.ndim != 2 or cov.shape[0] != cov.shape[1]:
        raise CovarianceError(f"{name}: expected a square matrix, got shape {cov.shape}")
    if not np.isfinite(cov).all():
        raise CovarianceError(f"{name}: contains non-finite entries")
    if not np.allclose(cov, cov.T, rtol=1e-12, atol=0.0):
        raise CovarianceError(f"{name}: not symmetric")
    try:
        np.linalg.cholesky(cov)
    except np.linalg.LinAlgError as exc:
        raise CovarianceError(f"{name}: not positive definite") from exc


@dataclass(frozen=True)
class BAOData:
    """Parsed BAO measurements with validated covariance."""

    z: FloatArray
    values: FloatArray
    observables: tuple[BAOObservable, ...]
    cov: FloatArray
    _cholesky: FloatArray = field(repr=False, compare=False, default_factory=lambda: np.empty(0))

    def __post_init__(self) -> None:
        n = self.values.size
        if not (self.z.size == n == len(self.observables)):
            raise ValueError(
                f"inconsistent lengths: z={self.z.size}, values={n}, "
                f"observables={len(self.observables)}"
            )
        validate_covariance(self.cov, name="BAO covariance")
        if self.cov.shape[0] != n:
            raise ValueError(
                f"covariance dimension {self.cov.shape[0]} does not match {n} measurements"
            )
        object.__setattr__(self, "_cholesky", np.linalg.cholesky(self.cov))

    @property
    def n_points(self) -> int:
        return self.values.size

    def chi2(self, predicted: FloatArray) -> float:
        """Gaussian chi-squared of a prediction vector against the data."""
        if predicted.shape != self.values.shape:
            raise ValueError(
                f"prediction shape {predicted.shape} does not match data shape {self.values.shape}"
            )
        if not np.isfinite(predicted).all():
            raise ValueError("prediction contains non-finite entries")
        residual = predicted - self.values
        whitened = np.linalg.solve(self._cholesky, residual)
        return float(whitened @ whitened)


def _parse_measurement_line(
    line: str, *, lineno: int, path: Path
) -> tuple[float, float, BAOObservable]:
    parts = line.split()
    if len(parts) != 3:
        raise ValueError(f"{path}:{lineno}: expected 3 columns 'z value observable', got {line!r}")
    z, value, observable = float(parts[0]), float(parts[1]), parts[2]
    if observable == "DV_over_rs" or observable == "DM_over_rs" or observable == "DH_over_rs":
        return z, value, observable
    raise ValueError(f"{path}:{lineno}: unknown observable {observable!r}")


def load_bao_data(mean_path: Path, cov_path: Path) -> BAOData:
    """Load and validate a bao_data-format measurement/covariance pair."""
    z_list: list[float] = []
    value_list: list[float] = []
    observable_list: list[BAOObservable] = []
    for lineno, raw_line in enumerate(mean_path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        z, value, observable = _parse_measurement_line(line, lineno=lineno, path=mean_path)
        z_list.append(z)
        value_list.append(value)
        observable_list.append(observable)
    if not z_list:
        raise ValueError(f"{mean_path}: no measurement rows found")
    cov = np.atleast_2d(np.loadtxt(cov_path, dtype=np.float64))
    return BAOData(
        z=np.asarray(z_list, dtype=np.float64),
        values=np.asarray(value_list, dtype=np.float64),
        observables=tuple(observable_list),
        cov=cov,
    )
