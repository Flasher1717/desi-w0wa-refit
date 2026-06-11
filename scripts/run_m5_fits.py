"""Run the pre-registered M5 fits: 5 combinations x 2 models (P4).

Gates [PREREGISTRATION.md P4, anchors from 2503.14738v3 Table 6]:

  G5.1  BAO alone          published 1.7 sigma  ->  N in [1.5, 1.9]
  G5.2  BAO+CMB compressed published 2.4 sigma  ->  N in [2.1, 2.7]
        (same compression as ours: EXACT anchor)
  G5.3  BAO+CMB+Pantheon+  published 2.8 sigma (full CMB) -> [1.8, 3.1]
  G5.4  BAO+CMB+Union3     published 3.8 sigma (full CMB) -> [2.8, 4.1]
  G5.5  BAO+CMB+DESY5      published 4.2 sigma (full CMB) -> [3.2, 4.5]
  G5.6  ordering N(P+) < N(Union3) < N(DESY5)

For G5.3-G5.5 the difference N_pipeline - N_published is REPORTED as the
measure of the compression effect (GO M1.2a), to be compared with the
-0.7 sigma DESI measures on BAO+CMB (2.4 vs 3.1).

Start counts are fixed BEFORE the runs (P7): 24 starts for LCDM fits,
40 for w0waCDM fits; seeds derive from ROOT_SEED via derive_seed.

Writes results/m5_fits.json. Usage: uv run python scripts/run_m5_fits.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

from desi_w0wa_refit.arms import Arm, make_bao_only_arm, make_cmb_arm
from desi_w0wa_refit.bao import load_bao_data
from desi_w0wa_refit.cmb import CMBCompressedPrior
from desi_w0wa_refit.fitting import minimize_multistart, nsigma_from_delta_chi2
from desi_w0wa_refit.sne import load_des_sn5yr, load_pantheon_plus, load_union3

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"

N_STARTS_LCDM = 24
N_STARTS_W0WA = 40

GATES = {
    "BAO": ("G5.1", 1.7, (1.5, 1.9)),
    "BAO+CMB": ("G5.2", 2.4, (2.1, 2.7)),
    "BAO+CMB+PantheonPlus": ("G5.3", 2.8, (1.8, 3.1)),
    "BAO+CMB+Union3": ("G5.4", 3.8, (2.8, 4.1)),
    "BAO+CMB+DES-SN5YR": ("G5.5", 4.2, (3.2, 4.5)),
}


def fit_arm(arm: Arm) -> dict[str, object]:
    print(f"\n=== {arm.name} (n_data = {arm.n_data}) ===")
    t0 = time.perf_counter()
    fit_lcdm = minimize_multistart(
        arm.chi2_lcdm,
        list(arm.bounds_lcdm),
        run_name=f"m5-{arm.name}-lcdm",
        n_starts=N_STARTS_LCDM,
    )
    print(
        f"  LCDM   chi2 = {fit_lcdm.chi2:10.3f}  "
        + "  ".join(
            f"{name}={value:.5g}"
            for name, value in zip(arm.param_names_lcdm, fit_lcdm.x, strict=True)
        )
    )
    fit_w0wa = minimize_multistart(
        arm.chi2_w0wa,
        list(arm.bounds_w0wa),
        run_name=f"m5-{arm.name}-w0wacdm",
        n_starts=N_STARTS_W0WA,
        constraint=Arm.w0wa_start_constraint,
    )
    print(
        f"  w0waCDM chi2 = {fit_w0wa.chi2:9.3f}  "
        + "  ".join(
            f"{name}={value:.5g}"
            for name, value in zip(arm.param_names_w0wa, fit_w0wa.x, strict=True)
        )
    )
    runtime = time.perf_counter() - t0

    delta_chi2_map = fit_w0wa.chi2 - fit_lcdm.chi2  # negative favours w0waCDM
    nsigma = nsigma_from_delta_chi2(-delta_chi2_map)
    delta_aic = delta_chi2_map + 2.0 * 2
    delta_bic = delta_chi2_map + 2.0 * float(np.log(arm.n_data))
    gate_id, published, (low, high) = GATES[arm.name]
    gate_pass = low <= nsigma <= high
    print(
        f"  Delta chi2_MAP = {delta_chi2_map:+.3f}  ->  {nsigma:.3f} sigma"
        f"  (published {published}, gate {gate_id} window [{low}, {high}])"
        f"  pass={gate_pass}"
    )

    return {
        "n_data": arm.n_data,
        "lcdm": {
            "chi2": fit_lcdm.chi2,
            "params": dict(zip(arm.param_names_lcdm, [float(v) for v in fit_lcdm.x], strict=True)),
            "n_starts": fit_lcdm.n_starts,
            "top5_start_chi2s": [float(v) for v in fit_lcdm.start_chi2s[:5]],
        },
        "w0wacdm": {
            "chi2": fit_w0wa.chi2,
            "params": dict(zip(arm.param_names_w0wa, [float(v) for v in fit_w0wa.x], strict=True)),
            "n_starts": fit_w0wa.n_starts,
            "top5_start_chi2s": [float(v) for v in fit_w0wa.start_chi2s[:5]],
        },
        "delta_chi2_map": delta_chi2_map,
        "nsigma": nsigma,
        "delta_aic": delta_aic,
        "delta_bic": delta_bic,
        "gate": gate_id,
        "published_nsigma": published,
        "gate_window": [low, high],
        "nsigma_minus_published": nsigma - published,
        "pass": gate_pass,
        "runtime_s": round(runtime, 1),
    }


def main() -> int:
    print("Loading data...")
    bao = load_bao_data(
        DATA_DIR / "desi_gaussian_bao_ALL_GCcomb_mean.txt",
        DATA_DIR / "desi_gaussian_bao_ALL_GCcomb_cov.txt",
    )
    prior = CMBCompressedPrior()
    pantheon = load_pantheon_plus(
        DATA_DIR / "Pantheon+SH0ES.dat", DATA_DIR / "Pantheon+SH0ES_STAT+SYS.cov"
    )
    union3 = load_union3(DATA_DIR / "Union3_lcparam_full.txt", DATA_DIR / "Union3_mag_covmat.txt")
    des = load_des_sn5yr(DATA_DIR / "DES-SN5YR_HD.csv", DATA_DIR / "DES-SN5YR_STAT+SYS.txt.gz")

    arms = [
        make_bao_only_arm(bao),
        make_cmb_arm(bao, prior),
        make_cmb_arm(bao, prior, pantheon),
        make_cmb_arm(bao, prior, union3),
        make_cmb_arm(bao, prior, des),
    ]

    results: dict[str, dict[str, object]] = {}
    nsigmas: dict[str, float] = {}
    for arm in arms:
        arm_result = fit_arm(arm)
        results[arm.name] = arm_result
        nsigma_value = arm_result["nsigma"]
        assert isinstance(nsigma_value, float)
        nsigmas[arm.name] = nsigma_value

    # G5.6: pre-registered ordering of the three SNe arms.
    n_pp = nsigmas["BAO+CMB+PantheonPlus"]
    n_u3 = nsigmas["BAO+CMB+Union3"]
    n_des = nsigmas["BAO+CMB+DES-SN5YR"]
    ordering_pass = n_pp < n_u3 < n_des
    results["G5.6_ordering"] = {
        "criterion": "N(P+) < N(Union3) < N(DESY5)",
        "values": [n_pp, n_u3, n_des],
        "pass": ordering_pass,
    }
    print(f"\nG5.6 ordering: {n_pp:.3f} < {n_u3:.3f} < {n_des:.3f} -> pass={ordering_pass}")

    RESULTS_DIR.mkdir(exist_ok=True)
    out_path = RESULTS_DIR / "m5_fits.json"
    out_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"\nWritten {out_path}")

    all_pass = all(bool(entry["pass"]) for entry in results.values())
    print(f"ALL GATES PASS: {all_pass}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
