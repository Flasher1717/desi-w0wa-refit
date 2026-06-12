"""V3 paired common SNe between Pantheon+ and DES-SN5YR
(PREREGISTRATION.md P11; SPEC_V21 volet V3).

Matching rule (P11.1, established in M10 from the real files):
- CIDs are read as STRINGS (49 Pantheon+ CIDs carry leading zeros);
- normalization: strip, lowercase, drop a leading "sn" prefix ONLY when
  followed by a digit (protects "SNF20080514-002", merges the internal
  Pantheon+ inconsistency "2016coj"/"SN2016coj");
- exact equality of the normalized key; per-pair guard |dzHD| < 0.01.

Tier R (P11.2, Efstathiou Table 1 replication -- DECLARED non-blind):
same-survey pairs (normalized key AND same IDSURVEY in both releases),
Delta_i = m_b_corr - (MU - 19.33) [arXiv:2408.07175 Eq. 2], unweighted
group means, SEM = std(ddof=0)/sqrt(N).

Tier P (P11.3, the blind primary paired analysis): object-level match,
ONE mu per object per release -- the same-IDSURVEY Pantheon+ row when
it exists, otherwise smallest m_b_corr_err_DIAG, tie-break ascending
IDSURVEY (GO M10.5); Delta mu_i = MU_SH0ES - MU_DES; primary statistic
S = mean(Delta mu, low-z) - mean(Delta mu, high-z) with the
source-sample split (high-z = DES IDSURVEY 10); empirical SEMs are THE
primary uncertainty (GO amendment A2: inter-release correlations are
unknown and unmodeled, catalogue errors are not a valid uncertainty
for the differences).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from desi_w0wa_refit.bao import FloatArray
from desi_w0wa_refit.sne import read_packed_covariance

EFSTATHIOU_ZERO_POINT = -19.33  # arXiv:2408.07175 Eq. 2
Z_MATCH_GUARD = 0.01  # P11.1
TIER_P_EXCLUDED_CID = "1304442"  # P11.3 pre-registered exclusion
DES_HIGH_Z_IDSURVEY = 10  # source-sample split (P11.3)


def normalize_cid(cid: str) -> str:
    """P11.1 normalization (strip, lowercase, 'sn'+digit prefix drop)."""
    key = cid.strip().lower()
    if key.startswith("sn") and len(key) > 2 and key[2].isdigit():
        key = key[2:]
    return key


@dataclass(frozen=True)
class PantheonRow:
    """One Pantheon+ catalogue row (file order index kept for covariance)."""

    cid: str
    key: str
    idsurvey: int
    zhd: float
    m_b_corr: float
    m_b_corr_err_diag: float
    mu_sh0es: float
    file_index: int


@dataclass(frozen=True)
class DesRow:
    """One DES-SN5YR catalogue row."""

    cid: str
    key: str
    idsurvey: int
    zhd: float
    mu: float
    muerr_final: float
    file_index: int


def load_pantheon_rows(dat_path: Path, *, z_min: float = 0.01) -> list[PantheonRow]:
    """Pantheon+ rows with zHD > z_min (the project's cosmology cut)."""
    lines = dat_path.read_text(encoding="utf-8").splitlines()
    names = lines[0].split()
    idx = {
        name: names.index(name)
        for name in (
            "CID",
            "IDSURVEY",
            "zHD",
            "m_b_corr",
            "m_b_corr_err_DIAG",
            "MU_SH0ES",
        )
    }
    rows: list[PantheonRow] = []
    for file_index, line in enumerate(lines[1:]):
        tokens = line.split()
        if not tokens:
            continue
        zhd = float(tokens[idx["zHD"]])
        if zhd <= z_min:
            continue
        cid = tokens[idx["CID"]]
        rows.append(
            PantheonRow(
                cid=cid,
                key=normalize_cid(cid),
                idsurvey=int(tokens[idx["IDSURVEY"]]),
                zhd=zhd,
                m_b_corr=float(tokens[idx["m_b_corr"]]),
                m_b_corr_err_diag=float(tokens[idx["m_b_corr_err_DIAG"]]),
                mu_sh0es=float(tokens[idx["MU_SH0ES"]]),
                file_index=file_index,
            )
        )
    return rows


def load_des_rows(hd_path: Path) -> list[DesRow]:
    """All 1829 DES-SN5YR rows (no cut, P9.1 convention)."""
    lines = hd_path.read_text(encoding="utf-8").splitlines()
    names = [token.strip() for token in lines[0].split(",")]
    idx = {name: names.index(name) for name in ("CID", "IDSURVEY", "zHD", "MU", "MUERR_FINAL")}
    rows: list[DesRow] = []
    for file_index, line in enumerate(lines[1:]):
        if not line.strip():
            continue
        tokens = [token.strip() for token in line.split(",")]
        cid = tokens[idx["CID"]]
        rows.append(
            DesRow(
                cid=cid,
                key=normalize_cid(cid),
                idsurvey=int(tokens[idx["IDSURVEY"]]),
                zhd=float(tokens[idx["zHD"]]),
                mu=float(tokens[idx["MU"]]),
                muerr_final=float(tokens[idx["MUERR_FINAL"]]),
                file_index=file_index,
            )
        )
    return rows


@dataclass(frozen=True)
class TierRPair:
    """Same-survey pair (Efstathiou replication, P11.2)."""

    des: DesRow
    pantheon: PantheonRow

    @property
    def delta(self) -> float:
        """Delta_i = m_b_corr - (MU - 19.33) [Eq. 2 convention]."""
        return self.pantheon.m_b_corr - (self.des.mu + EFSTATHIOU_ZERO_POINT)


@dataclass(frozen=True)
class TierPPair:
    """Object-level pair with ONE mu per release (P11.3)."""

    des: DesRow
    pantheon: PantheonRow
    pantheon_rule: str  # "same-survey" | "smallest-err"

    @property
    def delta_mu(self) -> float:
        """Delta mu_i = MU_SH0ES - MU_DES."""
        return self.pantheon.mu_sh0es - self.des.mu


def tier_r_pairs(pantheon_rows: list[PantheonRow], des_rows: list[DesRow]) -> list[TierRPair]:
    """Same-survey pairs, deterministic (sorted by DES file order)."""
    by_key_survey: dict[tuple[str, int], list[PantheonRow]] = {}
    for row in pantheon_rows:
        by_key_survey.setdefault((row.key, row.idsurvey), []).append(row)
    pairs: list[TierRPair] = []
    for des in sorted(des_rows, key=lambda r: r.file_index):
        candidates = by_key_survey.get((des.key, des.idsurvey), [])
        if not candidates:
            continue
        if len(candidates) > 1:
            raise ValueError(
                f"Tier R: duplicate Pantheon+ rows for key={des.key!r} "
                f"IDSURVEY={des.idsurvey} (zero-duplicate requirement, P11.4)"
            )
        pantheon = candidates[0]
        if abs(pantheon.zhd - des.zhd) >= Z_MATCH_GUARD:
            raise ValueError(
                f"Tier R: |dzHD| guard failed for {des.cid!r} ({pantheon.zhd} vs {des.zhd})"
            )
        pairs.append(TierRPair(des=des, pantheon=pantheon))
    return pairs


def tier_p_pairs(pantheon_rows: list[PantheonRow], des_rows: list[DesRow]) -> list[TierPPair]:
    """Object-level pairs with the GO M10.5 duplicate rule."""
    by_key: dict[str, list[PantheonRow]] = {}
    for row in pantheon_rows:
        by_key.setdefault(row.key, []).append(row)
    pairs: list[TierPPair] = []
    for des in sorted(des_rows, key=lambda r: r.file_index):
        candidates = by_key.get(des.key)
        if not candidates:
            continue
        same_survey = [row for row in candidates if row.idsurvey == des.idsurvey]
        if same_survey:
            if len(same_survey) > 1:
                raise ValueError(f"Tier P: duplicate same-survey Pantheon+ rows for {des.key!r}")
            chosen, rule = same_survey[0], "same-survey"
        else:
            chosen = min(candidates, key=lambda r: (r.m_b_corr_err_diag, r.idsurvey))
            rule = "smallest-err"
        if abs(chosen.zhd - des.zhd) >= Z_MATCH_GUARD:
            raise ValueError(
                f"Tier P: |dzHD| guard failed for {des.cid!r} ({chosen.zhd} vs {des.zhd})"
            )
        pairs.append(TierPPair(des=des, pantheon=chosen, pantheon_rule=rule))
    keys = [pair.des.key for pair in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("Tier P: duplicate object keys in the matched set (P11.4)")
    return pairs


def unweighted_mean_sem(values: list[float]) -> tuple[float, float]:
    """Unweighted mean and SEM = std(ddof=0)/sqrt(N) (P11.2 convention)."""
    n = len(values)
    mean = sum(values) / n
    std = math.sqrt(sum((v - mean) ** 2 for v in values) / n)
    return mean, std / math.sqrt(n)


def read_pantheon_covariance_raw(cov_path: Path) -> FloatArray:
    """Released 1701x1701 STAT+SYS matrix in file order (the w^T C w
    quadratic form symmetrizes the release rounding asymmetry)."""
    return read_packed_covariance(cov_path)


def read_des_total_covariance(cov_path: Path, hd_path: Path) -> FloatArray:
    """1829x1829 STAT+SYS + diag(MUERR_FINAL^2), file order (the P3
    total-covariance convention)."""
    cov = read_packed_covariance(cov_path)
    muerr = np.asarray([row.muerr_final for row in load_des_rows(hd_path)], dtype=np.float64)
    return cov + np.diag(muerr**2)
