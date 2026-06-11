"""M7: pre-registered low-z sensitivity cuts (PREREGISTRATION.md P5).

Cuts CLOSED at the M1 GO — none added after first numbers; applied to
the BAO+CMB+DES-SN5YR and BAO+CMB+Pantheon+ arms (P8 pipeline):

  C-a  z > 0.1                       [DESI DR2 Fig. 14; Efstathiou 2408.07175]
  C-b  exclude CfA (IDSURVEY 61-66) + CSP (5), keep Foundation (150)
       and the P+ misc low-z (50, 51, 56, 57, 18)   [2502.04212]
  C-c  DES: pure DES (IDSURVEY = 10); P+: z > 0.1   [DESI VII.3]
  C-d  z > 0.025 (control)           [Dovekie 2511.07517 Sec. 2.2]

z is zHD (the cosmology redshift of both releases). Baselines are the
full arms from results/m5_fits_corrected.json. The reporting metric is
FROZEN (P5): Coupure | N_SNe | Delta chi2_MAP | Nsigma | Delta Nsigma
vs baseline | w0_MAP | wa_MAP | Delta w0 | Delta wa.

Pre-registered deviation note: P5 planned to freeze the sub-samples by
file hash at download time (M2); the SHA256 of each filtered data
vector is recorded here at the first M7 run instead (before any fit of
that cut), in results/m7_cuts.json.

Fits: same engine and start counts as M5 (24 LCDM / 40 w0waCDM, seeded
Sobol starts, run names "m7-<sample>-<cut>-<model>").

Usage: uv run python scripts/run_m7_cuts.py
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
from desi_w0wa_refit.fitting import minimize_multistart, nsigma_from_delta_chi2
from desi_w0wa_refit.sne import SNSample, load_des_sn5yr, load_pantheon_plus

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
M5_RESULTS = RESULTS_DIR / "m5_fits_corrected.json"

N_STARTS_LCDM = 24
N_STARTS_W0WA = 40

CFA_IDS = (61, 62, 63, 64, 65, 66)
CSP_ID = 5


def sample_hash(sample: SNSample) -> str:
    digest = hashlib.sha256()
    for array in (sample.z_cmb, sample.z_hel, sample.mag):
        digest.update(np.ascontiguousarray(array).tobytes())
    if sample.survey_ids is not None:
        digest.update(np.ascontiguousarray(sample.survey_ids).tobytes())
    return digest.hexdigest()


def apply_cut(sample: SNSample, cut: str) -> SNSample:
    ids = sample.survey_ids
    assert ids is not None
    if cut == "C-a":
        return sample.subset(sample.z_cmb > 0.1)
    if cut == "C-b":
        excluded = np.isin(ids.astype(int), (CSP_ID, *CFA_IDS))
        return sample.subset(~excluded)
    if cut == "C-c":
        if sample.name == "DES-SN5YR":
            return sample.subset(ids.astype(int) == 10)
        return sample.subset(sample.z_cmb > 0.1)
    if cut == "C-d":
        return sample.subset(sample.z_cmb > 0.025)
    raise ValueError(f"unknown cut {cut!r}")


def fit_arm_models(arm: Arm, run_prefix: str) -> tuple[float, float, dict[str, float]]:
    """Returns (chi2_lcdm, chi2_w0wa, w0wa best-fit params)."""
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

    results: dict[str, object] = {}
    for sample_name, sample in samples.items():
        arm_key = f"BAO+CMB+{sample_name}"
        baseline = m5[arm_key]
        base_nsigma = float(baseline["nsigma"])
        base_w0 = float(baseline["w0wacdm"]["params"]["w0"])
        base_wa = float(baseline["w0wacdm"]["params"]["wa"])
        table: dict[str, object] = {
            "baseline": {
                "n_sne": sample.n_sne,
                "delta_chi2_map": baseline["delta_chi2_map"],
                "nsigma": base_nsigma,
                "w0_map": base_w0,
                "wa_map": base_wa,
            }
        }
        print(f"\n=== {arm_key} (baseline {base_nsigma:.3f} sigma, N={sample.n_sne}) ===")
        for cut in ("C-a", "C-b", "C-c", "C-d"):
            t0 = time.perf_counter()
            cut_sample = apply_cut(sample, cut)
            cut_hash = sample_hash(cut_sample)
            arm = make_cmb_arm(bao, prior, cut_sample)
            chi2_lcdm, chi2_w0wa, params = fit_arm_models(arm, f"m7-{sample_name}-{cut}")
            delta_chi2 = chi2_w0wa - chi2_lcdm
            nsigma = nsigma_from_delta_chi2(-delta_chi2)
            row = {
                "n_sne": cut_sample.n_sne,
                "subset_sha256": cut_hash,
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
                "runtime_s": round(time.perf_counter() - t0, 1),
            }
            table[cut] = row
            print(
                f"  {cut}: N={cut_sample.n_sne:5d}  Dchi2={delta_chi2:+8.3f}  "
                f"N_sigma={nsigma:5.3f}  dN={nsigma - base_nsigma:+6.3f}  "
                f"w0={params['w0']:+7.4f} ({params['w0'] - base_w0:+7.4f})  "
                f"wa={params['wa']:+7.4f} ({params['wa'] - base_wa:+7.4f})  "
                f"[{row['runtime_s']}s]"
            )
        results[arm_key] = table

    out_path = RESULTS_DIR / "m7_cuts.json"
    out_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"\nWritten {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
