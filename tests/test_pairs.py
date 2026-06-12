"""V3 matching tests (PREREGISTRATION.md P11.1, P11.4).

Pinned counts (measured in M10, verified twice independently):
335 common objects (Tier P), 332 same-survey pairs (Tier R), 4 DES
low-z SNe with no Pantheon+ counterpart, 3 Tier-P-only cross-survey
objects. Matching is deterministic and duplicate-free; a SN paired
with itself gives Delta mu = 0 exactly.
"""

from __future__ import annotations

import random
from pathlib import Path

import pytest

from desi_w0wa_refit.pairs import (
    TIER_P_EXCLUDED_CID,
    DesRow,
    PantheonRow,
    load_des_rows,
    load_pantheon_rows,
    normalize_cid,
    tier_p_pairs,
    tier_r_pairs,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PP_DAT = DATA_DIR / "Pantheon+SH0ES.dat"
DES_CSV = DATA_DIR / "DES-SN5YR_HD.csv"


def test_normalize_cid_rules() -> None:
    assert normalize_cid("SN2016hpx") == "2016hpx"
    assert normalize_cid("sn2007af") == "2007af"
    assert normalize_cid("SNF20080514-002") == "snf20080514-002"  # protected
    assert normalize_cid(" 2007af ") == "2007af"
    assert normalize_cid("1998BU") == "1998bu"
    assert normalize_cid("ASASSN-15bc") == "asassn-15bc"
    assert normalize_cid("010026") == "010026"  # leading zeros kept


def test_self_pairing_gives_delta_mu_zero() -> None:
    """[TESTS] V3: a SN paired with itself gives Delta mu = 0 exactly."""
    des_rows = [
        DesRow(
            cid=f"199{i}ab",
            key=normalize_cid(f"199{i}ab"),
            idsurvey=10,
            zhd=0.1 + 0.01 * i,
            mu=38.0 + 0.1 * i,
            muerr_final=0.1,
            file_index=i,
        )
        for i in range(5)
    ]
    pantheon_rows = [
        PantheonRow(
            cid=row.cid,
            key=row.key,
            idsurvey=row.idsurvey,
            zhd=row.zhd,
            m_b_corr=row.mu - 19.33,
            m_b_corr_err_diag=0.1,
            mu_sh0es=row.mu,
            file_index=row.file_index,
        )
        for row in des_rows
    ]
    for pair in tier_p_pairs(pantheon_rows, des_rows):
        assert pair.delta_mu == 0.0
        assert pair.pantheon_rule == "same-survey"
    for pair_r in tier_r_pairs(pantheon_rows, des_rows):
        assert pair_r.delta == 0.0


@pytest.mark.requires_data
def test_pinned_counts() -> None:
    """P11.1: 335 Tier P / 332 Tier R / 4 unmatched / 3 cross-survey."""
    pantheon_rows = load_pantheon_rows(PP_DAT)
    des_rows = load_des_rows(DES_CSV)
    pairs_p = tier_p_pairs(pantheon_rows, des_rows)
    pairs_r = tier_r_pairs(pantheon_rows, des_rows)
    assert len(pairs_p) == 335
    assert len(pairs_r) == 332

    pp_keys = {row.key for row in pantheon_rows}
    lowz_keys = {row.key for row in des_rows if row.idsurvey != 10}
    unmatched = lowz_keys - pp_keys
    assert unmatched == {"2001ay", "2004gc", "2007ob", "2007r"}

    tier_r_keys = {pair.des.key for pair in pairs_r}
    tier_p_keys = {pair.des.key for pair in pairs_p}
    assert tier_p_keys - tier_r_keys == {"2005hj", "2005ir", "2006ev"}


@pytest.mark.requires_data
def test_tier_r_group_counts_match_table1() -> None:
    """G13.1 pinned permanently: Efstathiou Table 1 counts."""
    pairs = tier_r_pairs(load_pantheon_rows(PP_DAT), load_des_rows(DES_CSV))
    counts: dict[int, int] = {}
    for pair in pairs:
        counts[pair.des.idsurvey] = counts.get(pair.des.idsurvey, 0) + 1
    assert counts == {10: 145, 150: 118, 63: 14, 64: 27, 65: 18, 66: 3, 5: 7}


@pytest.mark.requires_data
def test_matching_is_deterministic_under_input_order() -> None:
    """P11.4: input order does not change the matched set."""
    pantheon_rows = load_pantheon_rows(PP_DAT)
    des_rows = load_des_rows(DES_CSV)
    baseline = tier_p_pairs(pantheon_rows, des_rows)
    shuffled_pp = pantheon_rows.copy()
    shuffled_des = des_rows.copy()
    random.Random(20260611).shuffle(shuffled_pp)
    random.Random(20260612).shuffle(shuffled_des)
    shuffled = tier_p_pairs(shuffled_pp, shuffled_des)
    as_tuples = [
        (p.des.cid, p.pantheon.cid, p.pantheon.idsurvey, p.pantheon_rule) for p in baseline
    ]
    as_tuples_shuffled = [
        (p.des.cid, p.pantheon.cid, p.pantheon.idsurvey, p.pantheon_rule) for p in shuffled
    ]
    assert as_tuples == as_tuples_shuffled


@pytest.mark.requires_data
def test_z_guard_isolates_1304442() -> None:
    """P11.4: 1304442 is the only pair with |dz| > 0.003; second max
    is 0.00207."""
    pairs = tier_p_pairs(load_pantheon_rows(PP_DAT), load_des_rows(DES_CSV))
    dz_by_cid = {pair.des.cid: abs(pair.pantheon.zhd - pair.des.zhd) for pair in pairs}
    above = [cid for cid, dz in dz_by_cid.items() if dz > 0.003]
    assert above == [TIER_P_EXCLUDED_CID]
    second_max = max(dz for cid, dz in dz_by_cid.items() if cid != TIER_P_EXCLUDED_CID)
    assert abs(second_max - 0.00207) < 5e-5
