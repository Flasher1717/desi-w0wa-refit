"""SONDE C — audit du minimiseur M5 pour le bras BAO+CMB compresse.

Re-minimise chi2_lcdm / chi2_w0wa de arms.make_cmb_arm (sans SNe) avec
differential_evolution, Nelder-Mead (depuis best-fit M5 et point officiel)
et Powell (depuis best-fit M5). Ecrit results/audit/probe_c_results.json.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution, minimize

from desi_w0wa_refit.arms import make_cmb_arm
from desi_w0wa_refit.bao import load_bao_data
from desi_w0wa_refit.cmb import CMBCompressedPrior

PROJECT_ROOT = Path(r"C:\Users\flash\dev\desi-w0wa-refit")
DATA_DIR = PROJECT_ROOT / "data"
OUT = PROJECT_ROOT / "results" / "audit" / "probe_c_results.json"

SEED = 20260611
BOUNDS_LCDM = [(0.01, 0.99), (0.2, 1.0), (0.005, 0.1)]
BOUNDS_W0WA = BOUNDS_LCDM + [(-3.0, 1.0), (-3.0, 2.0)]

M5_LCDM = np.array([0.30071666585110013, 0.6849510285097398, 0.022360434401952914])
M5_W0WA = np.array(
    [0.3452655783764524, 0.6431610742204024, 0.022222218323527013,
     -0.5155004373150214, -1.4117506996852378]
)
M5_CHI2 = {"lcdm": 12.760648836820375, "w0wa": 6.7836389114696845}


def official_lcdm_point() -> np.ndarray:
    """Lit H0, ombh2, omm dans le margestats officiel LCDM."""
    vals: dict[str, float] = {}
    for line in (DATA_DIR / "desi_dr2_base_cmbcompressed_chain.margestats").read_text().splitlines():
        parts = line.split()
        if parts and parts[0] in ("H0", "ombh2", "omm"):
            vals[parts[0]] = float(parts[1].split("\\")[0])
    return np.array([vals["omm"], vals["H0"] / 100.0, vals["ombh2"]])


OFFICIAL_W0WA = np.array([0.353, 0.637, 0.02224, -0.43, -1.72])


def wrap_for_de(fn, bounds):
    """Remplace inf par 1e9 + 1e3 * distance aux bornes/contraintes (pas de NaN)."""
    lo = np.array([b[0] for b in bounds])
    hi = np.array([b[1] for b in bounds])
    n = len(bounds)

    def wrapped(x):
        val = fn(x)
        if np.isfinite(val):
            return float(val)
        d = float(np.sum(np.maximum(0.0, lo - x) + np.maximum(0.0, x - hi)))
        if n == 5:  # contrainte dure w0 + wa < 0
            d += max(0.0, float(x[3] + x[4]))
        return 1e9 + 1e3 * d

    return wrapped


def run_nm(fn, x0, bounds):
    r = minimize(fn, x0, method="Nelder-Mead", bounds=bounds,
                 options={"xatol": 1e-10, "fatol": 1e-10, "maxiter": 20000, "maxfev": 20000})
    return float(r.fun), [float(v) for v in r.x], int(r.nfev)


def run_powell(fn, x0, bounds):
    r = minimize(fn, x0, method="Powell", bounds=bounds,
                 options={"xtol": 1e-10, "ftol": 1e-10, "maxiter": 20000, "maxfev": 100000})
    return float(r.fun), [float(v) for v in r.x], int(r.nfev)


def main() -> None:
    bao = load_bao_data(
        DATA_DIR / "desi_gaussian_bao_ALL_GCcomb_mean.txt",
        DATA_DIR / "desi_gaussian_bao_ALL_GCcomb_cov.txt",
    )
    arm = make_cmb_arm(bao, CMBCompressedPrior())
    off_lcdm = official_lcdm_point()

    results: dict[str, dict] = {"lcdm": {}, "w0wa": {}}
    specs = [
        ("lcdm", arm.chi2_lcdm, BOUNDS_LCDM, M5_LCDM, off_lcdm),
        ("w0wa", arm.chi2_w0wa, BOUNDS_W0WA, M5_W0WA, OFFICIAL_W0WA),
    ]
    for model, fn, bounds, x_m5, x_off in specs:
        res = results[model]
        res["chi2_at_m5_bestfit"] = float(fn(x_m5))
        res["chi2_at_official_point"] = float(fn(x_off))
        res["official_point"] = [float(v) for v in x_off]

        t0 = time.perf_counter()
        de = differential_evolution(
            wrap_for_de(fn, bounds), bounds, seed=SEED, popsize=15,
            maxiter=200, tol=1e-10, polish=True,
        )
        res["DE"] = {"chi2": float(de.fun), "x": [float(v) for v in de.x],
                     "nfev": int(de.nfev), "nit": int(de.nit),
                     "success": bool(de.success), "time_s": round(time.perf_counter() - t0, 1)}
        # re-evalue le point DE avec la vraie fonction (sans penalite)
        res["DE"]["chi2_true"] = float(fn(np.array(de.x)))

        for label, x0 in [("NM_from_m5", x_m5), ("NM_from_official", x_off)]:
            t0 = time.perf_counter()
            f, x, nfev = run_nm(fn, x0, bounds)
            res[label] = {"chi2": f, "x": x, "nfev": nfev,
                          "time_s": round(time.perf_counter() - t0, 1)}

        t0 = time.perf_counter()
        f, x, nfev = run_powell(fn, x_m5, bounds)
        res["Powell_from_m5"] = {"chi2": f, "x": x, "nfev": nfev,
                                 "time_s": round(time.perf_counter() - t0, 1)}

        best = min(res[k]["chi2_true" if k == "DE" else "chi2"]
                   for k in ("DE", "NM_from_m5", "NM_from_official", "Powell_from_m5"))
        res["best_chi2_any_method"] = best
        res["m5_chi2"] = M5_CHI2[model]
        res["best_minus_m5"] = best - M5_CHI2[model]
        print(f"[{model}] m5={M5_CHI2[model]:.6f} best={best:.6f} "
              f"diff={best - M5_CHI2[model]:+.3e}")
        for k in ("DE", "NM_from_m5", "NM_from_official", "Powell_from_m5"):
            print(f"  {k:18s} chi2={res[k]['chi2']:.6f} nfev={res[k]['nfev']}")

    OUT.write_text(json.dumps(results, indent=2))
    print(f"\nwritten: {OUT}")


if __name__ == "__main__":
    main()
