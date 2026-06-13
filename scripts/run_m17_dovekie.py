"""M17: V5 -- Foundation under Dovekie (PREREGISTRATION.md P13, GO M15).

Inter-release comparison (NOT a replacement of the frozen DR2-era v1.2 anchor).
The DES-Dovekie sample (pinned commit c9a4fcaf) is fit FRESH on BAO+CMB+SN, its
baseline Nsigma is anchored to the published 3.2 sigma via the compression-aware
window G17.1 = [2.4, 3.4], and the SAME frozen leave-one-group-out metric as V2
(P10) is re-run. The headline binary question is whether the Foundation lever
(v1.2 M12: -1.335 sigma) persists after recalibration.

Group grid (P13.3, mirror of the v1.2 DES grid; counts pinned):
  foundation {150} -> 1703    des {10} -> 197 (expected boundary MAP)
  cfa+csp {5,63-66} -> 1740   cfa-only-desc {63-66} -> 1748 (desc.)
  csp-only-desc {5} -> 1812 (desc., small-N)

Metric (P10.2 reused): Dchi2_MAP | Nsigma | dNsigma | w0/wa_MAP | dw0/dwa |
sigma_curv(w0,wa) | dsigma_curv, with the P10.3 fixed-step FD Hessian and the
P10.4 boundary-MAP policy. The baseline is FRESH (no frozen Dovekie fit exists).
v1.2 numbers are read VERBATIM from results/m12_loo.json (frozen) for the
side-by-side comparison. Output: results/m17_dovekie.json only.

Coherence gate H (verified at setup, RESULTS s12): the official DES-Dovekie
likelihood is a straight offset-marginalized Gaussian chi2 with NO per-SN BEAMS
weighting, so the v1.1.0 chi2_marginalized engine is faithful (N = 1820).

Usage: uv run python scripts/run_m17_dovekie.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

from desi_w0wa_refit.arms import Arm, make_cmb_arm
from desi_w0wa_refit.bao import load_bao_data
from desi_w0wa_refit.cmb import CMBCompressedPrior
from desi_w0wa_refit.curvature import CurvatureResult, curvature_sigmas
from desi_w0wa_refit.fitting import minimize_multistart, nsigma_from_delta_chi2
from desi_w0wa_refit.sne import SNSample, load_des_dovekie

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
M12_RESULTS = RESULTS_DIR / "m12_loo.json"

N_STARTS_LCDM = 24
N_STARTS_W0WA = 40

ANCHOR_WINDOW = (2.4, 3.4)  # G17.1 (P13.4): compression-aware window around 3.2 sigma

# P13.3 closed grid: (group key, IDSURVEY codes, expected remaining N, descriptive).
DOVEKIE_GROUPS: tuple[tuple[str, tuple[int, ...], int, bool], ...] = (
    ("foundation", (150,), 1703, False),
    ("des", (10,), 197, False),
    ("cfa+csp", (5, 63, 64, 65, 66), 1740, False),
    ("cfa-only-desc", (63, 64, 65, 66), 1748, True),
    ("csp-only-desc", (5,), 1812, True),
)


def sample_hash(sample: SNSample) -> str:
    """SHA256 of the filtered data vector (same convention as M7/M12)."""
    digest = hashlib.sha256()
    for array in (sample.z_cmb, sample.z_hel, sample.mag):
        digest.update(np.ascontiguousarray(array).tobytes())
    if sample.survey_ids is not None:
        digest.update(np.ascontiguousarray(sample.survey_ids).tobytes())
    return digest.hexdigest()


def remove_groups(sample: SNSample, ids: tuple[int, ...]) -> SNSample:
    survey_ids = sample.survey_ids
    assert survey_ids is not None
    return sample.subset(~np.isin(survey_ids.astype(int), ids))


def fit_arm_models(arm: Arm, run_prefix: str) -> tuple[float, float, dict[str, float]]:
    """Same engine and start counts as M5/M7/M12 (24 LCDM / 40 w0waCDM)."""
    fit_lcdm = minimize_multistart(
        arm.chi2_lcdm, list(arm.bounds_lcdm), run_name=f"{run_prefix}-lcdm", n_starts=N_STARTS_LCDM
    )
    fit_w0wa = minimize_multistart(
        arm.chi2_w0wa,
        list(arm.bounds_w0wa),
        run_name=f"{run_prefix}-w0wacdm",
        n_starts=N_STARTS_W0WA,
        constraint=Arm.w0wa_start_constraint,
    )
    params = dict(zip(arm.param_names_w0wa, [float(v) for v in fit_w0wa.x], strict=True))
    return fit_lcdm.chi2, fit_w0wa.chi2, params


def curvature_payload(result: CurvatureResult) -> dict[str, object]:
    return {
        "sigma_curv_w0": result.sigma_w0,
        "sigma_curv_wa": result.sigma_wa,
        "boundary_flagged": result.boundary_flagged,
        "flag_reason": result.flag_reason,
        "residual_gradient": result.residual_gradient,
        "chi2_w0wa_at_map_point": result.chi2_at_point,
    }


def arm_curvature(arm: Arm, params: dict[str, float]) -> CurvatureResult:
    x_map = [params[name] for name in arm.param_names_w0wa]
    return curvature_sigmas(arm.chi2_w0wa, x_map, arm.bounds_w0wa)


def main() -> int:
    print("Loading data...")
    bao = load_bao_data(
        DATA_DIR / "desi_gaussian_bao_ALL_GCcomb_mean.txt",
        DATA_DIR / "desi_gaussian_bao_ALL_GCcomb_cov.txt",
    )
    prior = CMBCompressedPrior()
    dovekie = load_des_dovekie(
        DATA_DIR / "DES-Dovekie_HD.csv", DATA_DIR / "DES-Dovekie_STAT+SYS.npz"
    )
    print(f"  Dovekie sample: N = {dovekie.n_sne}")
    m12 = json.loads(M12_RESULTS.read_text(encoding="utf-8"))
    v12_des = m12["BAO+CMB+DES-SN5YR"]

    # FRESH baseline fit (no frozen Dovekie fit exists).
    print("\n=== baseline BAO+CMB+DES-Dovekie (fresh fit) ===")
    t0 = time.perf_counter()
    baseline_arm = make_cmb_arm(bao, prior, dovekie)
    base_lcdm, base_w0wa, base_params = fit_arm_models(baseline_arm, "m17-dovekie-baseline")
    base_delta_chi2 = base_w0wa - base_lcdm
    base_nsigma = nsigma_from_delta_chi2(-base_delta_chi2)
    base_w0, base_wa = base_params["w0"], base_params["wa"]
    base_curv = arm_curvature(baseline_arm, base_params)
    anchor_ok = ANCHOR_WINDOW[0] <= base_nsigma <= ANCHOR_WINDOW[1]
    print(
        f"  Dchi2={base_delta_chi2:+.3f}  Nsigma={base_nsigma:.4f}  "
        f"w0={base_w0:+.4f} wa={base_wa:+.4f}  "
        f"[G17.1 anchor {ANCHOR_WINDOW}: {'PASS' if anchor_ok else 'FAIL'}, "
        f"{round(time.perf_counter() - t0, 1)}s]"
    )
    if not anchor_ok:
        raise RuntimeError(
            f"G17.1: Dovekie baseline Nsigma {base_nsigma:.4f} outside the pre-registered "
            f"window {ANCHOR_WINDOW} -- pipeline bug until proven otherwise (STOP audit, "
            "MILESTONES entry; published Dovekie significance is 3.2 sigma with full CMB)"
        )

    results: dict[str, object] = {
        "preregistration": "P13 (frozen at this run); GO M15 decisions D/E/G/H/I",
        "status": "inter-release comparison; v1.2 stays the frozen DR2-era anchor (m12_loo.json)",
        "dovekie_pin": "des-science/DES-SN5YR commit c9a4fcaf (Dovekie, Popovic et al. 2026)",
        "published_significance": "3.2 sigma full CMB (arXiv:2511.07517 S10.6); ours compressed",
        "anchor_window_g17_1": list(ANCHOR_WINDOW),
        "baseline": {
            "n_sne": dovekie.n_sne,
            "chi2_lcdm": base_lcdm,
            "chi2_w0wa": base_w0wa,
            "delta_chi2_map": base_delta_chi2,
            "nsigma": base_nsigma,
            "anchor_pass_g17_1": anchor_ok,
            "w0_map": base_w0,
            "wa_map": base_wa,
            "w0wa_params": base_params,
            **curvature_payload(base_curv),
        },
        "groups": {},
    }
    groups_out: dict[str, object] = {}

    for group_key, group_ids, expected_n, descriptive in DOVEKIE_GROUPS:
        t1 = time.perf_counter()
        loo = remove_groups(dovekie, group_ids)
        if loo.n_sne != expected_n:
            raise RuntimeError(f"{group_key}: N = {loo.n_sne}, expected {expected_n} (P13.3)")
        arm = make_cmb_arm(bao, prior, loo)
        chi2_lcdm, chi2_w0wa, params = fit_arm_models(arm, f"m17-dovekie-loo-{group_key}")
        delta_chi2 = chi2_w0wa - chi2_lcdm
        nsigma = nsigma_from_delta_chi2(-delta_chi2)
        curv = arm_curvature(arm, params)
        v12_row = v12_des.get(group_key, {})
        row: dict[str, object] = {
            "group_ids": list(group_ids),
            "descriptive": descriptive,
            "n_sne": loo.n_sne,
            "subset_sha256": sample_hash(loo),
            "chi2_lcdm": chi2_lcdm,
            "chi2_w0wa": chi2_w0wa,
            "delta_chi2_map": delta_chi2,
            "nsigma": nsigma,
            "delta_nsigma_vs_baseline": nsigma - base_nsigma,
            "w0_map": params["w0"],
            "wa_map": params["wa"],
            "delta_w0": params["w0"] - base_w0,
            "delta_wa": params["wa"] - base_wa,
            "w0wa_params": params,
            **curvature_payload(curv),
            "delta_sigma_curv_w0": None
            if curv.sigma_w0 is None or base_curv.sigma_w0 is None
            else curv.sigma_w0 - base_curv.sigma_w0,
            "delta_sigma_curv_wa": None
            if curv.sigma_wa is None or base_curv.sigma_wa is None
            else curv.sigma_wa - base_curv.sigma_wa,
            "v12_delta_nsigma": v12_row.get("delta_nsigma_vs_baseline"),
            "v12_nsigma": v12_row.get("nsigma"),
            "runtime_s": round(time.perf_counter() - t1, 1),
        }
        groups_out[group_key] = row
        sigma_text = (
            f"s(w0)={curv.sigma_w0:.4f} s(wa)={curv.sigma_wa:.4f}"
            if curv.sigma_w0 is not None and curv.sigma_wa is not None
            else f"sigma WITHHELD ({curv.flag_reason})"
        )
        v12_dn = v12_row.get("delta_nsigma_vs_baseline")
        v12_text = f"v1.2 dN={v12_dn:+.3f}" if isinstance(v12_dn, (int, float)) else "v1.2 dN=n/a"
        print(
            f"  {group_key:14s} N={loo.n_sne:5d}  Dchi2={delta_chi2:+8.3f}  "
            f"Nsigma={nsigma:5.3f}  dN={nsigma - base_nsigma:+6.3f}  ({v12_text})  "
            f"w0={params['w0']:+7.4f} wa={params['wa']:+7.4f}  {sigma_text}  "
            f"[{row['runtime_s']}s]"
        )

    results["groups"] = groups_out
    out_path = RESULTS_DIR / "m17_dovekie.json"
    out_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"\nWritten {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
