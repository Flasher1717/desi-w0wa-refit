"""M16: V4 -- effect of the corrected SN covariance on the w0waCDM preference
(PREREGISTRATION.md P12, GO M15 decisions A/B).

SENSITIVITY analysis -- never "the" corrected preference; the published
covariance stays the FROZEN v1.1.0 baseline. For each arm
BAO+CMB+{Pantheon+, DES-SN5YR}, the SN covariance block is corrected three
ways (factors computed on the arm's OWN SN-only flat-LCDM fit, decision B),
both models are refit, and dNsigma vs the frozen baseline is reported:

  (i-kappa) PRIMARY    C -> C * kappa, kappa = chi2_min/N  (control chi2/dof=1)
  (i-s)     DESCRIPTIVE C -> C * s_diag^2 (V1 diagonal std; chi2/dof != 1)
  (ii)      C -> C - delta^2 I, delta^2 so chi2_min = N     (control chi2/dof=1)

Gates: G16.1 control chi2/dof -> 1 for (i-kappa) and (ii) (by construction);
G16.3 the uncorrected baseline refit reproduces the frozen Nsigma (the only
difference is the covariance). Baselines read VERBATIM from
results/m5_fits_corrected.json (frozen, never re-fit for the headline numbers).
Output: results/m16_v4.json only -- no frozen file is touched.

Usage: uv run python scripts/run_m16_v4.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from desi_w0wa_refit.arms import Arm, make_cmb_arm
from desi_w0wa_refit.bao import BAOData, load_bao_data
from desi_w0wa_refit.cmb import CMBCompressedPrior
from desi_w0wa_refit.covariance_correction import (
    corrected_reduced_chi2,
    correction_factors,
    rescale_covariance,
    subtract_diagonal,
)
from desi_w0wa_refit.fitting import minimize_multistart, nsigma_from_delta_chi2
from desi_w0wa_refit.sne import SNSample, load_des_sn5yr, load_pantheon_plus

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
M5_RESULTS = RESULTS_DIR / "m5_fits_corrected.json"

N_STARTS_LCDM = 24
N_STARTS_W0WA = 40

# G16.1 control tolerances (PREREGISTRATION.md P12.5).
# (i-kappa): a uniform positive rescale leaves the SN-only argmin unchanged, so
# chi2/dof = 1 to machine precision.
CONTROL_TOL_EXACT = 1e-9
# (ii): delta2 from delta2_for_chi2_eq_n is found by brentq on the ROOT
# LOCATION (xtol on delta2), not on the chi2 VALUE; with d(chi2)/d(delta2)
# ~1e6 for the real arms, chi2/N lands within ~few x 1e-5 of 1 (e.g. 1.000024
# on P+ N=1590), physically chi2_min = N to 5 significant figures. The gate is
# set to that achievable value-precision, not the unreachable 1e-6.
CONTROL_TOL_DELTA2 = 1e-3
BASELINE_TOL = 0.05  # G16.3: refit baseline Nsigma matches the frozen value


def fit_arm_models(arm: Arm, run_prefix: str) -> tuple[float, float, dict[str, float]]:
    """Same engine and start counts as M5/M7/M12 (24 LCDM / 40 w0waCDM)."""
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


def fit_corrected_arm(
    bao: BAOData,
    prior: CMBCompressedPrior,
    corrected: SNSample,
    *,
    base_nsigma: float,
    base_w0: float,
    base_wa: float,
    run_prefix: str,
) -> dict[str, object]:
    """Fit one corrected arm and return its frozen-format metric row."""
    arm = make_cmb_arm(bao, prior, corrected)
    chi2_lcdm, chi2_w0wa, params = fit_arm_models(arm, run_prefix)
    delta_chi2 = chi2_w0wa - chi2_lcdm
    nsigma = nsigma_from_delta_chi2(-delta_chi2)
    return {
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
    }


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

    results: dict[str, object] = {
        "preregistration": "P12 (frozen at this run); GO M15 decisions A and B",
        "note": "SENSITIVITY analysis; the published covariance stays the frozen v1.1.0 baseline",
    }

    for sample_name, sample in samples.items():
        arm_key = f"BAO+CMB+{sample_name}"
        baseline = m5[arm_key]
        base_nsigma = float(baseline["nsigma"])
        base_params = {name: float(value) for name, value in baseline["w0wacdm"]["params"].items()}
        base_w0, base_wa = base_params["w0"], base_params["wa"]

        print(f"\n=== {arm_key} === (baseline frozen Nsigma = {base_nsigma:.3f})")

        # G16.3: refit the UNCORRECTED baseline arm; only the covariance differs.
        t0 = time.perf_counter()
        base_arm = make_cmb_arm(bao, prior, sample)
        b_lcdm, b_w0wa, _ = fit_arm_models(base_arm, f"m16-{sample_name}-baseline")
        refit_nsigma = nsigma_from_delta_chi2(-(b_w0wa - b_lcdm))
        baseline_check_ok = abs(refit_nsigma - base_nsigma) < BASELINE_TOL
        print(
            f"  G16.3 baseline refit Nsigma = {refit_nsigma:.4f} "
            f"(frozen {base_nsigma:.4f}, |d| = {abs(refit_nsigma - base_nsigma):.4f}) "
            f"[{'PASS' if baseline_check_ok else 'FAIL'}, {round(time.perf_counter() - t0, 1)}s]"
        )
        if not baseline_check_ok:
            raise RuntimeError(
                f"{arm_key} G16.3: refit Nsigma {refit_nsigma} off frozen {base_nsigma} "
                f"by > {BASELINE_TOL} -- the harness does not reproduce the baseline (STOP audit)"
            )

        # Correction factors on the arm's OWN SN-only fit (decision B).
        factors = correction_factors(sample)
        print(
            f"  factors: N={factors.n_sne}  chi2_min={factors.chi2_min_sn_only:.4f}  "
            f"reduced={factors.reduced_chi2:.6f}  kappa={factors.kappa:.6f}  "
            f"s_diag={factors.s_diag:.6f}  delta2={factors.delta2:.7f}"
        )

        scenario_defs: tuple[tuple[str, SNSample, float | None], ...] = (
            ("i_kappa", rescale_covariance(sample, factors.kappa), CONTROL_TOL_EXACT),
            ("i_sdiag", rescale_covariance(sample, factors.s_diag**2), None),
            ("ii_delta2", subtract_diagonal(sample, factors.delta2), CONTROL_TOL_DELTA2),
        )

        scenarios: dict[str, object] = {}
        for scenario_key, corrected, control_tol in scenario_defs:
            t1 = time.perf_counter()
            control = corrected_reduced_chi2(corrected)
            if control_tol is not None and abs(control - 1.0) > control_tol:
                raise RuntimeError(
                    f"{arm_key} {scenario_key} G16.1: control reduced chi2 = {control} "
                    f"!= 1 (tol {control_tol}) -- correction implementation bug (STOP audit)"
                )
            row = fit_corrected_arm(
                bao,
                prior,
                corrected,
                base_nsigma=base_nsigma,
                base_w0=base_w0,
                base_wa=base_wa,
                run_prefix=f"m16-{sample_name}-{scenario_key}",
            )
            row["control_reduced_chi2"] = control
            row["control_gated_to_one"] = control_tol is not None
            row["control_tol"] = control_tol
            row["runtime_s"] = round(time.perf_counter() - t1, 1)
            scenarios[scenario_key] = row
            print(
                f"  {scenario_key:10s} ctrl_red_chi2={control:.6f}  "
                f"Dchi2={row['delta_chi2_map']:+8.3f}  Nsigma={row['nsigma']:.3f}  "
                f"dN={row['delta_nsigma_vs_baseline']:+.3f}  "
                f"w0={row['w0_map']:+.4f} wa={row['wa_map']:+.4f}  [{row['runtime_s']}s]"
            )

        results[arm_key] = {
            "baseline": {
                "n_sne": sample.n_sne,
                "nsigma": base_nsigma,
                "delta_chi2_map": float(baseline["delta_chi2_map"]),
                "w0_map": base_w0,
                "wa_map": base_wa,
                "source": "results/m5_fits_corrected.json (frozen v1.1.0)",
                "refit_nsigma_g16_3": refit_nsigma,
                "refit_matches_frozen": baseline_check_ok,
            },
            "correction_factors": {
                "n_sne": factors.n_sne,
                "chi2_min_sn_only": factors.chi2_min_sn_only,
                "reduced_chi2": factors.reduced_chi2,
                "kappa": factors.kappa,
                "s_diag": factors.s_diag,
                "delta2": factors.delta2,
                "chi2_at_delta2": factors.chi2_at_delta2,
                "sample_note": "computed on the arm's own SN-only LCDM fit (GO M15 decision B)",
            },
            "scenarios": scenarios,
        }

    out_path = RESULTS_DIR / "m16_v4.json"
    out_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"\nWritten {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
