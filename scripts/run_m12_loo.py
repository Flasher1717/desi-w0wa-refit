"""M12: V2 leave-one-group-out decomposition (PREREGISTRATION.md P10).

CLOSED group grids (P10.1, frozen at this run; sizes are post-load,
i.e. after the Pantheon+ zHD > 0.01 cut):

  Pantheon+ arm (baseline N = 1590), 5 FRESH rows:
    cfa {61-66} -> 1433     csp {5} -> 1514     foundation {150} -> 1417
    misc-lowz {18,50,51,56,57} -> 1389          des-in-pp {10} -> 1387
  + 1 AGGREGATED row cfa+csp {61-66, 5} -> 1357: by composition exactly
    the M7 C-b subsample; fit columns REUSED verbatim from
    results/m7_cuts.json (coherence-checked by subset SHA256), only
    sigma_curv computed at its frozen MAP.

  DES-SN5YR arm (baseline N = 1829), 4 FRESH rows:
    foundation {150} -> 1711    des {10} -> 194 (expected boundary MAP)
    cfa-only-desc {63-66} -> 1761 (descriptive)
    csp-only-desc {5} -> 1821 (descriptive, small-N caveat)
  + 1 PRIMARY row cfa+csp {5, 63-66} -> 1753 = the M7 C-b DES subsample,
    reused the same way.

Metric (P10.2, frozen): per row N_SNe | Dchi2_MAP | Nsigma | dNsigma |
w0_MAP | wa_MAP | dw0 | dwa | sigma_curv(w0) | sigma_curv(wa) |
dsigma_curv(w0) | dsigma_curv(wa). Baselines are read VERBATIM from
results/m5_fits_corrected.json (frozen, never re-fit); baseline
sigma_curv comes from pure chi2 evaluations at the frozen MAP (P10.3).

Fits: same engine and start counts as M5/M7 (24 LCDM / 40 w0waCDM),
fresh deterministic seed streams via run names m12-<sample>-loo-<group>.
Output: results/m12_loo.json only -- no frozen file is touched.

Usage: uv run python scripts/run_m12_loo.py
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
from desi_w0wa_refit.sne import SNSample, load_des_sn5yr, load_pantheon_plus

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
M5_RESULTS = RESULTS_DIR / "m5_fits_corrected.json"
M7_RESULTS = RESULTS_DIR / "m7_cuts.json"

N_STARTS_LCDM = 24
N_STARTS_W0WA = 40

# P10.1 closed grids: (group key, IDSURVEY codes, expected remaining N).
FRESH_GROUPS: dict[str, tuple[tuple[str, tuple[int, ...], int], ...]] = {
    "PantheonPlus": (
        ("cfa", (61, 62, 63, 64, 65, 66), 1433),
        ("csp", (5,), 1514),
        ("foundation", (150,), 1417),
        ("misc-lowz", (18, 50, 51, 56, 57), 1389),
        ("des-in-pp", (10,), 1387),
    ),
    "DES-SN5YR": (
        ("foundation", (150,), 1711),
        ("des", (10,), 194),
        ("cfa-only-desc", (63, 64, 65, 66), 1761),
        ("csp-only-desc", (5,), 1821),
    ),
}
# Aggregated CfA+CSP rows reused from the frozen M7 C-b records.
REUSED_CFA_CSP_IDS = (5, 61, 62, 63, 64, 65, 66)
REUSED_EXPECTED_N = {"PantheonPlus": 1357, "DES-SN5YR": 1753}
DESCRIPTIVE_KEYS = {"cfa-only-desc", "csp-only-desc"}


def sample_hash(sample: SNSample) -> str:
    """SHA256 of the filtered data vector (same convention as M7)."""
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
    """Same engine and start counts as M5/M7."""
    fit_lcdm = minimize_multistart(
        arm.chi2_lcdm,
        list(arm.bounds_lcdm),
        run_name=f"{run_prefix}-lcdm",
        n_starts=N_STARTS_LCDM,
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
    samples = {
        "PantheonPlus": load_pantheon_plus(
            DATA_DIR / "Pantheon+SH0ES.dat", DATA_DIR / "Pantheon+SH0ES_STAT+SYS.cov"
        ),
        "DES-SN5YR": load_des_sn5yr(
            DATA_DIR / "DES-SN5YR_HD.csv", DATA_DIR / "DES-SN5YR_STAT+SYS.txt.gz"
        ),
    }
    m5 = json.loads(M5_RESULTS.read_text(encoding="utf-8"))
    m7 = json.loads(M7_RESULTS.read_text(encoding="utf-8"))

    results: dict[str, object] = {"preregistration": "P10 (frozen at this run)"}
    for sample_name, sample in samples.items():
        arm_key = f"BAO+CMB+{sample_name}"
        baseline = m5[arm_key]
        base_nsigma = float(baseline["nsigma"])
        base_params = {name: float(value) for name, value in baseline["w0wacdm"]["params"].items()}
        base_w0, base_wa = base_params["w0"], base_params["wa"]

        # Baseline sigma_curv: pure evaluations at the FROZEN MAP (P10.3).
        print(f"\n=== {arm_key} === baseline sigma_curv at the frozen MAP...")
        baseline_arm = make_cmb_arm(bao, prior, sample)
        base_curv = arm_curvature(baseline_arm, base_params)
        if base_curv.sigma_w0 is None or base_curv.sigma_wa is None:
            raise RuntimeError(f"{arm_key}: baseline sigma_curv withheld ({base_curv.flag_reason})")
        print(
            f"  baseline sigma_curv(w0) = {base_curv.sigma_w0:.4f}, "
            f"sigma_curv(wa) = {base_curv.sigma_wa:.4f}"
        )
        table: dict[str, object] = {
            "baseline": {
                "n_sne": sample.n_sne,
                "delta_chi2_map": float(baseline["delta_chi2_map"]),
                "nsigma": base_nsigma,
                "w0_map": base_w0,
                "wa_map": base_wa,
                "source": "results/m5_fits_corrected.json (frozen)",
                **curvature_payload(base_curv),
            }
        }

        # Reused CfA+CSP row (== M7 C-b by composition, GO M10.4).
        reused = remove_groups(sample, REUSED_CFA_CSP_IDS)
        reused_hash = sample_hash(reused)
        m7_row = m7[arm_key]["C-b"]
        if reused.n_sne != REUSED_EXPECTED_N[sample_name]:
            raise RuntimeError(
                f"{arm_key} cfa+csp: N = {reused.n_sne}, expected {REUSED_EXPECTED_N[sample_name]}"
            )
        if reused_hash != m7_row["subset_sha256"]:
            raise RuntimeError(
                f"{arm_key} cfa+csp: subset hash {reused_hash} does not reproduce "
                f"the frozen M7 C-b hash {m7_row['subset_sha256']}"
            )
        print(f"  cfa+csp row: M7 C-b hash reproduced ({reused_hash[:16]}...), reusing fit")
        reused_arm = make_cmb_arm(bao, prior, reused)
        reused_params = {name: float(value) for name, value in m7_row["w0wa_params"].items()}
        reused_curv = arm_curvature(reused_arm, reused_params)
        table["cfa+csp"] = {
            "reused_from": "results/m7_cuts.json C-b (frozen, GO M10.4)",
            "group_ids": list(REUSED_CFA_CSP_IDS),
            "n_sne": reused.n_sne,
            "subset_sha256": reused_hash,
            "chi2_lcdm": float(m7_row["chi2_lcdm"]),
            "chi2_w0wa": float(m7_row["chi2_w0wa"]),
            "delta_chi2_map": float(m7_row["delta_chi2_map"]),
            "nsigma": float(m7_row["nsigma"]),
            "delta_nsigma_vs_baseline": float(m7_row["delta_nsigma_vs_baseline"]),
            "w0_map": float(m7_row["w0_map"]),
            "wa_map": float(m7_row["wa_map"]),
            "delta_w0": float(m7_row["delta_w0"]),
            "delta_wa": float(m7_row["delta_wa"]),
            **curvature_payload(reused_curv),
            "delta_sigma_curv_w0": None
            if reused_curv.sigma_w0 is None
            else reused_curv.sigma_w0 - base_curv.sigma_w0,
            "delta_sigma_curv_wa": None
            if reused_curv.sigma_wa is None
            else reused_curv.sigma_wa - base_curv.sigma_wa,
        }

        # Fresh LOO rows.
        for group_key, group_ids, expected_n in FRESH_GROUPS[sample_name]:
            t0 = time.perf_counter()
            loo_sample = remove_groups(sample, group_ids)
            if loo_sample.n_sne != expected_n:
                raise RuntimeError(
                    f"{arm_key} {group_key}: N = {loo_sample.n_sne}, expected {expected_n} (P10.1)"
                )
            loo_hash = sample_hash(loo_sample)
            arm = make_cmb_arm(bao, prior, loo_sample)
            chi2_lcdm, chi2_w0wa, params = fit_arm_models(arm, f"m12-{sample_name}-loo-{group_key}")
            delta_chi2 = chi2_w0wa - chi2_lcdm
            nsigma = nsigma_from_delta_chi2(-delta_chi2)
            curv = arm_curvature(arm, params)
            row: dict[str, object] = {
                "group_ids": list(group_ids),
                "descriptive": group_key in DESCRIPTIVE_KEYS,
                "n_sne": loo_sample.n_sne,
                "subset_sha256": loo_hash,
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
                if curv.sigma_w0 is None
                else curv.sigma_w0 - base_curv.sigma_w0,
                "delta_sigma_curv_wa": None
                if curv.sigma_wa is None
                else curv.sigma_wa - base_curv.sigma_wa,
                "runtime_s": round(time.perf_counter() - t0, 1),
            }
            table[group_key] = row
            sigma_text = (
                f"s(w0)={curv.sigma_w0:.4f} s(wa)={curv.sigma_wa:.4f}"
                if curv.sigma_w0 is not None and curv.sigma_wa is not None
                else f"sigma WITHHELD ({curv.flag_reason})"
            )
            print(
                f"  {group_key:14s} N={loo_sample.n_sne:5d}  Dchi2={delta_chi2:+8.3f}  "
                f"N_sigma={nsigma:5.3f}  dN={nsigma - base_nsigma:+6.3f}  "
                f"w0={params['w0']:+7.4f}  wa={params['wa']:+7.4f}  {sigma_text}  "
                f"[{row['runtime_s']}s]"
            )
        results[arm_key] = table

    out_path = RESULTS_DIR / "m12_loo.json"
    out_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"\nWritten {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
