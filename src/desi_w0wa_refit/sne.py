"""Type Ia supernova samples and offset-marginalized chi-squared.

Conventions extracted from the official sources (see RESULTS.md section 2
and the pinned files in data_manifest.json, never from memory):

- Offset marginalization [Goliath et al. 2001, astro-ph/0104009,
  Eqs. (A9)-(A12)]: with d = mag - mu_model,
  ``chi2_marg = a - b^2 / c`` where ``a = d^T C^-1 d``,
  ``b = d^T C^-1 1`` and ``c = 1^T C^-1 1``.
  This equals cobaya's PantheonPlus ``_marginalize_abs_mag`` projection
  and differs from the official DES script
  (``data/DES-SN5YR_SN_only_cosmosis_likelihood.py``) only by the
  parameter-independent constant ``+ ln(c / 2 pi)``, exposed here as
  ``offset_log_norm`` for absolute-chi2 comparisons.

- Pantheon+ [cobaya ``sn.pantheonplus``; Brout et al. 2022,
  arXiv:2202.04077]: columns m_b_corr / zHD / zHEL, cosmology cut
  zHD > 0.01, covariance ``Pantheon+SH0ES_STAT+SYS.cov`` (first line
  N = 1701, then N^2 values).

- DES-SN5YR v1.2 [official SN_only_cosmosis_likelihood.py; cobaya
  ``sn.desy5``]: columns MU / zHD / zHEL / MUERR_FINAL, no redshift cut,
  total covariance = STAT+SYS.txt.gz + diag(MUERR_FINAL^2).

- Union3 [cobaya ``sn.union3``; Rubin et al., arXiv:2311.12098]:
  22 spline nodes, mb = distance modulus at arbitrary zero point,
  zhel = zcmb, 22x22 magnitude covariance.

The theory vector matching all three samples is
``mu = 5 log10((1 + z_hel) * D_M(z_cmb) / 10 pc)`` (cobaya base SN class:
``5 log10((1 + zhel) (1 + zcmb) D_A)``); any constant zero point is
absorbed by the marginalized offset.
"""

from __future__ import annotations

import gzip
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from scipy.linalg import cho_factor, cho_solve

from desi_w0wa_refit.bao import FloatArray, validate_covariance

BoolArray = NDArray[np.bool_]


def read_packed_covariance(path: Path) -> FloatArray:
    """Read an N / N^2-values covariance file (gzip if suffix is .gz)."""
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            text = fh.read()
    else:
        text = path.read_text(encoding="utf-8")
    tokens = text.split()
    n = int(tokens[0])
    values = np.asarray(tokens[1:], dtype=np.float64)
    if values.size != n * n:
        raise ValueError(f"{path}: expected {n * n} covariance values, found {values.size}")
    return values.reshape(n, n)


@dataclass(frozen=True)
class SNSample:
    """A supernova sample with validated covariance and offset marginalization."""

    name: str
    z_cmb: FloatArray
    z_hel: FloatArray
    mag: FloatArray
    cov: FloatArray
    survey_ids: FloatArray | None = None
    _cho: tuple[FloatArray, bool] = field(repr=False, compare=False, default=(np.empty(0), False))
    _cinv_one: FloatArray = field(repr=False, compare=False, default_factory=lambda: np.empty(0))
    _one_cinv_one: float = field(repr=False, compare=False, default=0.0)

    def __post_init__(self) -> None:
        n = self.mag.size
        if not (self.z_cmb.size == self.z_hel.size == n):
            raise ValueError(
                f"{self.name}: inconsistent lengths z_cmb={self.z_cmb.size}, "
                f"z_hel={self.z_hel.size}, mag={n}"
            )
        if self.survey_ids is not None and self.survey_ids.size != n:
            raise ValueError(f"{self.name}: survey_ids length {self.survey_ids.size} != {n}")
        validate_covariance(self.cov, name=f"{self.name} covariance")
        if self.cov.shape[0] != n:
            raise ValueError(f"{self.name}: covariance dimension {self.cov.shape[0]} != {n}")
        cho = cho_factor(self.cov, lower=True)
        ones = np.ones(n, dtype=np.float64)
        cinv_one = cho_solve(cho, ones)
        object.__setattr__(self, "_cho", (np.asarray(cho[0]), cho[1]))
        object.__setattr__(self, "_cinv_one", cinv_one)
        object.__setattr__(self, "_one_cinv_one", float(ones @ cinv_one))

    @property
    def n_sne(self) -> int:
        return self.mag.size

    @property
    def offset_log_norm(self) -> float:
        """The constant ln(c / 2 pi) kept by the official DES convention."""
        return float(np.log(self._one_cinv_one / (2.0 * np.pi)))

    @property
    def cholesky_lower(self) -> FloatArray:
        """Lower Cholesky factor L (L L^T = cov), the SAME factor the chi2
        uses; mock noise draws are L @ xi [PREREGISTRATION.md P9.2]."""
        return np.tril(self._cho[0])

    def chi2_marginalized(self, mu_model: FloatArray) -> float:
        """Offset-marginalized chi-squared, a - b^2/c [Goliath A9-A12]."""
        return self.chi2_marginalized_with_mag(self.mag, mu_model)

    def chi2_marginalized_with_mag(self, mag: FloatArray, mu_model: FloatArray) -> float:
        """Same offset-profiled a - b^2/c for an alternative magnitude
        vector (M11 mock draws use the identical code path as the real
        data, PREREGISTRATION.md P9.2)."""
        if mag.shape != self.mag.shape:
            raise ValueError(f"{self.name}: mag shape {mag.shape} != data shape {self.mag.shape}")
        if mu_model.shape != self.mag.shape:
            raise ValueError(
                f"{self.name}: model shape {mu_model.shape} != data shape {self.mag.shape}"
            )
        if not np.isfinite(mu_model).all():
            raise ValueError(f"{self.name}: model contains non-finite entries")
        delta = mag - mu_model
        a = float(delta @ cho_solve(self._cho, delta))
        b = float(delta @ self._cinv_one)
        return a - b * b / self._one_cinv_one

    def profiled_offset(self, mag: FloatArray, mu_model: FloatArray) -> float:
        """The analytically profiled additive offset b/c [Goliath eq. 21]."""
        delta = mag - mu_model
        return float((delta @ self._cinv_one) / self._one_cinv_one)

    def subset(self, mask: BoolArray) -> SNSample:
        """Sub-sample (data vector and covariance) selected by a boolean mask."""
        if mask.shape != self.mag.shape:
            raise ValueError(f"{self.name}: mask shape {mask.shape} != data shape {self.mag.shape}")
        idx = np.flatnonzero(mask)
        if idx.size == 0:
            raise ValueError(f"{self.name}: mask selects no supernovae")
        return SNSample(
            name=self.name,
            z_cmb=self.z_cmb[idx],
            z_hel=self.z_hel[idx],
            mag=self.mag[idx],
            cov=self.cov[np.ix_(idx, idx)],
            survey_ids=None if self.survey_ids is None else self.survey_ids[idx],
        )


def _read_named_columns(
    path: Path, columns: tuple[str, ...], *, sep: str | None = None
) -> dict[str, FloatArray]:
    """Read whitespace- or sep-separated columns by header name."""
    lines = path.read_text(encoding="utf-8").splitlines()
    header = lines[0].removeprefix("#").strip()
    names = [token.strip() for token in header.split(sep)]
    try:
        indices = {column: names.index(column) for column in columns}
    except ValueError as exc:
        raise ValueError(f"{path}: missing expected column in header {names!r}") from exc
    rows = [line.split(sep) for line in lines[1:] if line.strip()]
    out: dict[str, FloatArray] = {}
    for column, index in indices.items():
        out[column] = np.asarray([row[index] for row in rows], dtype=np.float64)
    return out


def _read_pantheon_plus_covariance(cov_path: Path) -> FloatArray:
    """Read and symmetrize the released Pantheon+ STAT+SYS covariance.

    The file carries last-printed-digit rounding asymmetries (778
    entries, max |C - C^T| = 3e-8 measured at first download); it is
    symmetrized here under a hard 1e-7 guard. The official consumers
    (cobaya, the DES script) never check symmetry.
    """
    cov = read_packed_covariance(cov_path)
    max_asymmetry = float(np.abs(cov - cov.T).max())
    if max_asymmetry > 1e-7:
        raise ValueError(
            f"{cov_path}: asymmetry {max_asymmetry} exceeds the documented "
            "release-rounding level (1e-7); investigate before symmetrizing"
        )
    return 0.5 * (cov + cov.T)


def load_pantheon_plus(dat_path: Path, cov_path: Path, *, z_min: float = 0.01) -> SNSample:
    """Load Pantheon+ with the cosmology cut zHD > z_min (default 0.01)."""
    cols = _read_named_columns(dat_path, ("zHD", "zHEL", "m_b_corr", "IDSURVEY"))
    full = SNSample(
        name="PantheonPlus",
        z_cmb=cols["zHD"],
        z_hel=cols["zHEL"],
        mag=cols["m_b_corr"],
        cov=_read_pantheon_plus_covariance(cov_path),
        survey_ids=cols["IDSURVEY"],
    )
    return full.subset(full.z_cmb > z_min)


def load_pantheon_plus_keeley(dat_path: Path, cov_path: Path) -> SNSample:
    """Load Pantheon+ in the Keeley/SH0ES-mode selection (N = 1580).

    Selection: zHD > 0.01 AND IS_CALIBRATOR == 0 [Keeley et al.,
    arXiv:2212.07917v3 Sec. 2]. The 1580 count always includes the
    calibrator clause (P0 erratum v1.1.1; RESULTS.md section 2.2:
    zHD > 0.01 alone gives 1590, minus the 10 calibrators above the
    cut gives 1580). Used by the M11 G11.2 anchor run only.
    """
    cols = _read_named_columns(dat_path, ("zHD", "zHEL", "m_b_corr", "IDSURVEY", "IS_CALIBRATOR"))
    full = SNSample(
        name="PantheonPlus-Keeley",
        z_cmb=cols["zHD"],
        z_hel=cols["zHEL"],
        mag=cols["m_b_corr"],
        cov=_read_pantheon_plus_covariance(cov_path),
        survey_ids=cols["IDSURVEY"],
    )
    return full.subset((full.z_cmb > 0.01) & (cols["IS_CALIBRATOR"] == 0.0))


def load_des_sn5yr(hd_path: Path, cov_path: Path) -> SNSample:
    """Load DES-SN5YR; total covariance = STAT+SYS + diag(MUERR_FINAL^2)."""
    cols = _read_named_columns(hd_path, ("zHD", "zHEL", "MU", "MUERR_FINAL", "IDSURVEY"), sep=",")
    cov = read_packed_covariance(cov_path)
    cov = cov + np.diag(cols["MUERR_FINAL"] ** 2)
    return SNSample(
        name="DES-SN5YR",
        z_cmb=cols["zHD"],
        z_hel=cols["zHEL"],
        mag=cols["MU"],
        cov=cov,
        survey_ids=cols["IDSURVEY"],
    )


def _read_snana_hd(path: Path, columns: tuple[str, ...]) -> dict[str, FloatArray]:
    """Read SNANA-format columns by VARNAMES name from a DES-Dovekie HD file.

    Data rows are prefixed ``SN:``; comment (``#``) and blank lines are
    ignored; the column order is the ``VARNAMES:`` header line. Rows are kept
    in file order (which matches the covariance row order; the separate
    metadata file is reordered and must NOT be used with the covariance).
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    varnames: list[str] | None = None
    rows: list[list[str]] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        tokens = stripped.split()
        if tokens[0] == "VARNAMES:":
            varnames = tokens[1:]
        elif tokens[0] == "SN:":
            rows.append(tokens[1:])
    if varnames is None:
        raise ValueError(f"{path}: no VARNAMES header line found")
    try:
        indices = {column: varnames.index(column) for column in columns}
    except ValueError as exc:
        raise ValueError(f"{path}: missing expected column in VARNAMES {varnames!r}") from exc
    return {
        column: np.asarray([row[index] for row in rows], dtype=np.float64)
        for column, index in indices.items()
    }


def read_inverse_covariance_npz(path: Path) -> FloatArray:
    """Read a DES-Dovekie covariance: an npz storing the INVERSE of stat+sys.

    The npz holds (nsn, cov): ``nsn`` the dimension and ``cov`` the float32
    upper-triangular packing (incl. the diagonal, ``np.triu_indices`` order) of
    Covtot_inv. We reconstruct the symmetric inverse and return the covariance
    ``C = inv(inv_cov)`` -- exactly the official DES-Dovekie likelihood's
    ``build_covariance`` (no diag(MUERR^2) is added, unlike DES-SN5YR v1.2).
    Float32 release precision is inherited and documented (RESULTS.md s12).
    """
    with np.load(path) as data:
        n = int(np.asarray(data["nsn"]).reshape(-1)[0])
        packed = np.asarray(data["cov"], dtype=np.float64)
    expected = n * (n + 1) // 2
    if packed.size != expected:
        raise ValueError(
            f"{path}: expected {expected} upper-triangular values for n={n}, found {packed.size}"
        )
    inv_cov = np.zeros((n, n), dtype=np.float64)
    inv_cov[np.triu_indices(n)] = packed
    lower = np.tril_indices(n, -1)
    inv_cov[lower] = inv_cov.T[lower]
    cov = np.linalg.inv(inv_cov)
    # inv() of an exactly-symmetric matrix is symmetric up to roundoff;
    # symmetrize so the strict validate_covariance check passes. Integrity is
    # guaranteed upstream by the SHA256 pin and downstream by the SNSample
    # Cholesky (positive-definiteness).
    return np.asarray(0.5 * (cov + cov.T), dtype=np.float64)


def load_des_dovekie(hd_path: Path, cov_path: Path) -> SNSample:
    """Load the DES-Dovekie recalibrated sample (V5, PREREGISTRATION.md P13).

    SNANA Hubble diagram (1820 SNe; columns MU / zHD / zHEL / IDSURVEY; MUERR is
    a stat-only diagnostic, NOT added to the covariance) and the npz inverse
    covariance inverted to the total covariance C. Straight offset-marginalized
    Gaussian chi2, no per-SN BEAMS weighting (coherence gate H), matching the
    official DES-Dovekie likelihood. Foundation is IDSURVEY 150 (unchanged).
    """
    cols = _read_snana_hd(hd_path, ("zHD", "zHEL", "MU", "IDSURVEY"))
    cov = read_inverse_covariance_npz(cov_path)
    return SNSample(
        name="DES-Dovekie",
        z_cmb=cols["zHD"],
        z_hel=cols["zHEL"],
        mag=cols["MU"],
        cov=cov,
        survey_ids=cols["IDSURVEY"],
    )


def load_union3(lcparam_path: Path, cov_path: Path) -> SNSample:
    """Load Union3 (22 spline nodes, zhel = zcmb, arbitrary zero point)."""
    cols = _read_named_columns(lcparam_path, ("zcmb", "zhel", "mb"))
    cov = read_packed_covariance(cov_path)
    return SNSample(
        name="Union3",
        z_cmb=cols["zcmb"],
        z_hel=cols["zhel"],
        mag=cols["mb"],
        cov=cov,
    )
