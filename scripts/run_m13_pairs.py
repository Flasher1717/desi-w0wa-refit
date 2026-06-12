"""M13: V3 paired common SNe (PREREGISTRATION.md P11).

Tier R -- Efstathiou Table 1 replication (anchor gates, DECLARED
non-blind, P11.2): same-survey pairs, Delta_i = m_b_corr - (MU - 19.33),
unweighted group means, SEM = std(ddof=0)/sqrt(N).
  G13.1 exact counts: 145/118/14/27/18/3/7 (all low-z 187)
  G13.2 group means within +/-0.001 of Table 1
  G13.3 row differential (all low-z) - (DES) within +/-0.002 of -0.0360

Tier P -- the blind primary paired analysis (P11.3, never computed
before this run): 335 common objects, one mu per release (same-survey
row, else smallest m_b_corr_err_DIAG, tie-break ascending IDSURVEY),
Delta mu_i = MU_SH0ES - MU_DES, source-sample split (high-z = DES
IDSURVEY 10), PRIMARY statistic S = mean(low) - mean(high) with
empirical SEMs in quadrature; pre-registered exclusion of 1304442
(with/without sensitivity line); SECONDARY covariance-aware error from
the released per-release covariance sub-blocks (the cross-release
correlation is unknown and unmodeled, GO amendment A2).

Output: results/m13_pairs.json. Exit code 1 if a G13 gate fails.

Usage: uv run python scripts/run_m13_pairs.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from desi_w0wa_refit.pairs import (
    TIER_P_EXCLUDED_CID,
    TierPPair,
    TierRPair,
    load_des_rows,
    load_pantheon_rows,
    read_des_total_covariance,
    read_pantheon_covariance_raw,
    tier_p_pairs,
    tier_r_pairs,
    unweighted_mean_sem,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"

# G13.1-G13.2 targets (Efstathiou Table 1; means verified in M10).
TABLE1_TARGETS: dict[int, tuple[str, int, float]] = {
    10: ("DES5Y", 145, -0.0122),
    150: ("FOUND", 118, -0.0508),
    63: ("CFA3S", 14, -0.0344),
    64: ("CFA3K", 27, -0.0616),
    65: ("CFA4P2", 18, -0.0547),
    66: ("CFA4P3", 3, 0.0285),
    5: ("CSP", 7, 0.0037),
}
ALL_LOWZ_TARGET = (187, -0.0482)
DIFFERENTIAL_TARGET = -0.0360
MEAN_TOL = 0.001  # G13.2
DIFF_TOL = 0.002  # G13.3
CORRECTED_SEMS = {"DES5Y": 0.0055, "FOUND": 0.0070, "all_low_z": 0.0058}


def tier_r_report(pairs_r: list[TierRPair], results: dict[str, object]) -> bool:
    by_survey: dict[int, list[float]] = {}
    for pair in pairs_r:
        by_survey.setdefault(pair.des.idsurvey, []).append(pair.delta)
    lowz = [pair.delta for pair in pairs_r if pair.des.idsurvey != 10]

    groups: dict[str, object] = {}
    all_pass = True
    for idsurvey, (label, count_target, mean_target) in TABLE1_TARGETS.items():
        deltas = by_survey.get(idsurvey, [])
        mean, sem = unweighted_mean_sem(deltas)
        count_ok = len(deltas) == count_target
        mean_ok = abs(mean - mean_target) <= MEAN_TOL
        all_pass = all_pass and count_ok and mean_ok
        groups[label] = {
            "idsurvey": idsurvey,
            "n": len(deltas),
            "n_target": count_target,
            "mean": mean,
            "mean_target_table1": mean_target,
            "sem_ddof0": sem,
            "g13_1_count_pass": count_ok,
            "g13_2_mean_pass": mean_ok,
        }
        print(
            f"  {label:7s} N={len(deltas):3d}/{count_target:3d}  mean={mean:+.4f} "
            f"(target {mean_target:+.4f})  SEM={sem:.4f}  "
            f"pass={count_ok and mean_ok}"
        )
    lowz_mean, lowz_sem = unweighted_mean_sem(lowz)
    lowz_count_ok = len(lowz) == ALL_LOWZ_TARGET[0]
    lowz_mean_ok = abs(lowz_mean - ALL_LOWZ_TARGET[1]) <= MEAN_TOL
    des_mean, _ = unweighted_mean_sem(by_survey[10])
    differential = lowz_mean - des_mean
    diff_ok = abs(differential - DIFFERENTIAL_TARGET) <= DIFF_TOL
    all_pass = all_pass and lowz_count_ok and lowz_mean_ok and diff_ok
    print(
        f"  all-low-z N={len(lowz)}/187  mean={lowz_mean:+.4f} (target -0.0482)  SEM={lowz_sem:.4f}"
    )
    print(
        f"  G13.3 differential (lowz - DES) = {differential:+.4f} "
        f"(target {DIFFERENTIAL_TARGET:+.4f} +/- {DIFF_TOL})  pass={diff_ok}"
    )
    results["tier_r"] = {
        "non_blind_disclosure": (
            "computed in M10 to establish the matching rule; this is a "
            "pipeline-reproducibility gate on numbers known at freeze (P11.2)"
        ),
        "n_pairs": len(pairs_r),
        "groups": groups,
        "all_low_z": {
            "n": len(lowz),
            "mean": lowz_mean,
            "sem_ddof0": lowz_sem,
            "count_pass": lowz_count_ok,
            "mean_pass": lowz_mean_ok,
        },
        "differential_lowz_minus_des": differential,
        "g13_3_pass": diff_ok,
        "sem_note": (
            "printed Table 1 errors +/-0.0006 (DES5Y) and +/-0.0007 (FOUND) are "
            "apparent decimal typos; comparison targets are the corrected "
            f"values {CORRECTED_SEMS} (P11.2, GO M10.1)"
        ),
        "pass": all_pass,
    }
    return all_pass


def split_low_high(pairs: list[TierPPair]) -> tuple[list[TierPPair], list[TierPPair]]:
    low = [pair for pair in pairs if pair.des.idsurvey != 10]
    high = [pair for pair in pairs if pair.des.idsurvey == 10]
    return low, high


def primary_statistic(pairs: list[TierPPair]) -> dict[str, float]:
    low, high = split_low_high(pairs)
    mean_low, sem_low = unweighted_mean_sem([pair.delta_mu for pair in low])
    mean_high, sem_high = unweighted_mean_sem([pair.delta_mu for pair in high])
    return {
        "n_low": len(low),
        "n_high": len(high),
        "mean_delta_mu_low": mean_low,
        "sem_low": sem_low,
        "mean_delta_mu_high": mean_high,
        "sem_high": sem_high,
        "s_low_minus_high": mean_low - mean_high,
        "sem_s_quadrature": float(np.hypot(sem_low, sem_high)),
    }


def covariance_aware_variance(pairs: list[TierPPair]) -> dict[str, float]:
    """Secondary error: w^T C w per release for the S weight vector
    (+1/N_low on low, -1/N_high on high); cross-release unmodeled."""
    low, high = split_low_high(pairs)
    weight_low, weight_high = 1.0 / len(low), -1.0 / len(high)
    pp_cov = read_pantheon_covariance_raw(DATA_DIR / "Pantheon+SH0ES_STAT+SYS.cov")
    des_cov = read_des_total_covariance(
        DATA_DIR / "DES-SN5YR_STAT+SYS.txt.gz", DATA_DIR / "DES-SN5YR_HD.csv"
    )
    pp_indices = [pair.pantheon.file_index for pair in low + high]
    des_indices = [pair.des.file_index for pair in low + high]
    weights = np.asarray([weight_low] * len(low) + [weight_high] * len(high))
    var_pp = float(weights @ pp_cov[np.ix_(pp_indices, pp_indices)] @ weights)
    var_des = float(weights @ des_cov[np.ix_(des_indices, des_indices)] @ weights)
    return {
        "var_from_pantheon_block": var_pp,
        "var_from_des_block": var_des,
        "sigma_s_covariance_aware": float(np.sqrt(var_pp + var_des)),
    }


def main() -> int:
    print("Loading catalogues...")
    pantheon_rows = load_pantheon_rows(DATA_DIR / "Pantheon+SH0ES.dat")
    des_rows = load_des_rows(DATA_DIR / "DES-SN5YR_HD.csv")
    results: dict[str, object] = {"preregistration": "P11 (frozen at this run)"}

    print("Tier R (Efstathiou Table 1 replication, anchor gates)...")
    pairs_r = tier_r_pairs(pantheon_rows, des_rows)
    tier_r_pass = tier_r_report(pairs_r, results)

    print("Tier P (blind primary paired analysis)...")
    pairs_all = tier_p_pairs(pantheon_rows, des_rows)
    if len(pairs_all) != 335:
        raise RuntimeError(f"Tier P: {len(pairs_all)} pairs, expected the pinned 335")
    pairs_primary = [pair for pair in pairs_all if pair.des.cid != TIER_P_EXCLUDED_CID]
    rule_counts = {
        rule: sum(1 for pair in pairs_all if pair.pantheon_rule == rule)
        for rule in ("same-survey", "smallest-err")
    }

    primary = primary_statistic(pairs_primary)
    sensitivity = primary_statistic(pairs_all)
    secondary = covariance_aware_variance(pairs_primary)
    print(
        f"  PRIMARY S = {primary['s_low_minus_high']:+.4f} "
        f"+/- {primary['sem_s_quadrature']:.4f} (empirical, "
        f"N = {primary['n_low']:.0f} low / {primary['n_high']:.0f} high, "
        f"1304442 excluded)"
    )
    print(
        f"  with 1304442: S = {sensitivity['s_low_minus_high']:+.4f} "
        f"+/- {sensitivity['sem_s_quadrature']:.4f}"
    )
    print(
        f"  secondary covariance-aware sigma_S = "
        f"{secondary['sigma_s_covariance_aware']:.4f} (cross-release unmodeled)"
    )

    # Descriptive complement (P11.3): per-group table for BOTH
    # definitions, and S under the Tier R magnitude-based definition.
    by_survey: dict[int, list[TierPPair]] = {}
    for pair in pairs_all:
        by_survey.setdefault(pair.des.idsurvey, []).append(pair)
    per_group: dict[str, object] = {}
    for idsurvey, group_pairs in sorted(by_survey.items()):
        mu_mean, mu_sem = unweighted_mean_sem([pair.delta_mu for pair in group_pairs])
        mb_mean, mb_sem = unweighted_mean_sem(
            [pair.pantheon.m_b_corr - (pair.des.mu - 19.33) for pair in group_pairs]
        )
        per_group[str(idsurvey)] = {
            "n": len(group_pairs),
            "mean_delta_mu_MU_based": mu_mean,
            "sem_delta_mu": mu_sem,
            "mean_delta_mb_based": mb_mean,
            "sem_delta_mb": mb_sem,
        }
    low_all, high_all = split_low_high(pairs_all)
    mb_low, _ = unweighted_mean_sem(
        [pair.pantheon.m_b_corr - (pair.des.mu - 19.33) for pair in low_all]
    )
    mb_high, _ = unweighted_mean_sem(
        [pair.pantheon.m_b_corr - (pair.des.mu - 19.33) for pair in high_all]
    )

    results["tier_p"] = {
        "n_objects": len(pairs_all),
        "n_primary_after_exclusion": len(pairs_primary),
        "excluded_cid": TIER_P_EXCLUDED_CID,
        "exclusion_reason": "zHD revised between releases (0.22449 vs 0.21711)",
        "duplicate_rule_counts": rule_counts,
        "primary": primary,
        "sensitivity_with_1304442": sensitivity,
        "secondary_covariance_aware": {
            **secondary,
            "limitation": (
                "inter-release correlations of the paired differences are "
                "unknown and unmodeled (shared low-z source photometry); the "
                "empirical dispersion is THE primary uncertainty (GO A2)"
            ),
        },
        "descriptive_per_group": per_group,
        "descriptive_s_mb_based_all335": mb_low - mb_high,
    }

    RESULTS_DIR.mkdir(exist_ok=True)
    out_path = RESULTS_DIR / "m13_pairs.json"
    out_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"Written {out_path}")
    print(f"TIER R GATES PASS: {tier_r_pass}")
    return 0 if tier_r_pass else 1


if __name__ == "__main__":
    sys.exit(main())
