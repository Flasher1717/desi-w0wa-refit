"""M6: w0waCDM posteriors (emcee) and corner plots for the five arms.

Pre-registered execution policy (P7 + SPEC M6), all fixed BEFORE the
runs and committed:

- sampler emcee, seeds derived from ROOT_SEED via derive_seed("m6-<arm>");
- walkers initialized in a deterministic Gaussian ball around the M5b
  MAP best fit (results/m5_fits_corrected.json), resampled until the
  posterior is finite at every walker;
- per-arm settings in ARM_SETTINGS below; convergence REQUIRED:
  (nsteps - burn) > 50 * max(tau), hard error otherwise;
- outputs: results/m6_mcmc.json (marginals, distances to LCDM),
  results/chains/m6_<arm>.npz (thinned flat chains),
  results/figures/m6_corner_<arm>.png (w0, wa corner among others).

The pipeline includes the P8 calibration (PREREGISTRATION.md P8).
Distance of the best fit to the LCDM point (-1, 0) is reported both as
Euclidean in the (w0, wa) plane and as Mahalanobis with the (w0, wa)
marginal covariance of the chain.

Usage: uv run python scripts/run_m6_mcmc.py
"""

# emcee/corner/matplotlib ship no type information; relax only the
# unknown-type diagnostics here (no `Any`, no `type: ignore`).
# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false
# pyright: reportUnknownVariableType=false, reportAttributeAccessIssue=false

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import corner
import emcee
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from desi_w0wa_refit.arms import Arm, make_bao_only_arm, make_cmb_arm
from desi_w0wa_refit.bao import FloatArray, load_bao_data
from desi_w0wa_refit.cmb import CMBCompressedPrior
from desi_w0wa_refit.fitting import derive_seed
from desi_w0wa_refit.sne import load_des_sn5yr, load_pantheon_plus, load_union3

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
CHAINS_DIR = RESULTS_DIR / "chains"
M5_RESULTS = RESULTS_DIR / "m5_fits_corrected.json"

# Committed BEFORE the M6 runs (P7). Lengths serve the pre-registered
# convergence REQUIREMENT (nsteps - burn > 50 tau); the first attempt
# (10000/8000 steps) failed it on BAO+CMB (50 tau = 9312 > 8000) and was
# lengthened across the CMB arms — documented in MILESTONES.md, the
# criterion itself never moved.
ARM_SETTINGS: dict[str, dict[str, int]] = {
    "BAO": {"nwalkers": 40, "nsteps": 12000, "burn": 2000},
    "BAO+CMB": {"nwalkers": 40, "nsteps": 22000, "burn": 3000},
    "BAO+CMB+PantheonPlus": {"nwalkers": 40, "nsteps": 16000, "burn": 3000},
    "BAO+CMB+Union3": {"nwalkers": 40, "nsteps": 20000, "burn": 3000},
    "BAO+CMB+DES-SN5YR": {"nwalkers": 40, "nsteps": 16000, "burn": 3000},
}
BALL_SCALE = 0.02  # relative Gaussian ball around the MAP for walker init


def init_walkers(
    arm: Arm, map_point: FloatArray, nwalkers: int, rng: np.random.RandomState
) -> FloatArray:
    ndim = map_point.size
    scales = np.maximum(np.abs(map_point) * BALL_SCALE, 1e-3)
    walkers = np.empty((nwalkers, ndim))
    filled = 0
    while filled < nwalkers:
        candidate = map_point + scales * rng.standard_normal(ndim)
        if np.isfinite(arm.chi2_w0wa(candidate)):
            walkers[filled] = candidate
            filled += 1
    return walkers


def run_arm(arm: Arm) -> dict[str, object]:
    settings = ARM_SETTINGS[arm.name]
    nwalkers, nsteps, burn = settings["nwalkers"], settings["nsteps"], settings["burn"]
    m5 = json.loads(M5_RESULTS.read_text(encoding="utf-8"))
    map_params = m5[arm.name]["w0wacdm"]["params"]
    map_point = np.asarray([map_params[name] for name in arm.param_names_w0wa])

    def log_prob(theta: FloatArray) -> float:
        return -0.5 * arm.chi2_w0wa(theta)

    rng = np.random.RandomState(derive_seed(f"m6-{arm.name}"))
    p0 = init_walkers(arm, map_point, nwalkers, rng)
    ndim = map_point.size
    sampler = emcee.EnsembleSampler(nwalkers, ndim, log_prob)
    state = emcee.State(p0, random_state=rng.get_state())
    t0 = time.perf_counter()
    sampler.run_mcmc(state, nsteps, progress=False)
    runtime = time.perf_counter() - t0

    tau = np.asarray(sampler.get_autocorr_time(tol=0), dtype=np.float64)
    tau_max = float(np.max(tau))
    if (nsteps - burn) <= 50 * tau_max:
        raise RuntimeError(
            f"{arm.name}: not converged, nsteps-burn={nsteps - burn} <= 50*tau={50 * tau_max:.0f}"
        )
    thin = max(1, int(tau_max / 2))
    flat_raw = sampler.get_chain(discard=burn, thin=thin, flat=True)
    if flat_raw is None:
        raise RuntimeError("emcee returned no chain")
    flat = np.asarray(flat_raw, dtype=np.float64)

    names = arm.param_names_w0wa
    marginals = {
        name: {
            "mean": float(np.mean(flat[:, i])),
            "std": float(np.std(flat[:, i])),
            "p16": float(np.percentile(flat[:, i], 16)),
            "p50": float(np.percentile(flat[:, i], 50)),
            "p84": float(np.percentile(flat[:, i], 84)),
        }
        for i, name in enumerate(names)
    }
    i_w0, i_wa = names.index("w0"), names.index("wa")
    w0_map, wa_map = float(map_point[i_w0]), float(map_point[i_wa])
    cov_ww = np.cov(flat[:, [i_w0, i_wa]].T)
    delta = np.asarray([w0_map + 1.0, wa_map - 0.0])
    mahalanobis = float(np.sqrt(delta @ np.linalg.solve(cov_ww, delta)))
    euclidean = float(np.sqrt(delta @ delta))

    CHAINS_DIR.mkdir(parents=True, exist_ok=True)
    safe = arm.name.replace("+", "_")
    np.savez_compressed(
        CHAINS_DIR / f"m6_{safe}.npz", samples=flat, names=np.asarray(names), tau=tau
    )

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    figure = corner.corner(
        flat,
        labels=list(names),
        truths=[None] * (ndim - 2) + [-1.0, 0.0],
        show_titles=True,
        title_fmt=".3f",
    )
    figure.suptitle(f"{arm.name} — flat w0waCDM (P8 pipeline)", y=1.02)
    figure.savefig(FIGURES_DIR / f"m6_corner_{safe}.png", dpi=150, bbox_inches="tight")
    plt.close(figure)

    print(
        f"  tau_max={tau_max:.1f} thin={thin} n_flat={flat.shape[0]}  "
        f"w0={marginals['w0']['mean']:+.3f}+/-{marginals['w0']['std']:.3f}  "
        f"wa={marginals['wa']['mean']:+.3f}+/-{marginals['wa']['std']:.3f}  "
        f"dist_LCDM: eucl={euclidean:.3f} mahal={mahalanobis:.2f}  ({runtime:.0f}s)"
    )
    return {
        "settings": settings,
        "seed_name": f"m6-{arm.name}",
        "tau": [float(t) for t in tau],
        "thin": thin,
        "n_flat_samples": int(flat.shape[0]),
        "marginals": marginals,
        "map_point": {name: float(map_point[i]) for i, name in enumerate(names)},
        "distance_map_to_lcdm_euclidean_w0wa": euclidean,
        "distance_map_to_lcdm_mahalanobis_w0wa": mahalanobis,
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
    out_path = RESULTS_DIR / "m6_mcmc.json"
    results: dict[str, object] = {}
    if out_path.is_file():
        results = json.loads(out_path.read_text(encoding="utf-8"))
    for arm in arms:
        previous = results.get(arm.name)
        if isinstance(previous, dict) and previous.get("settings") == ARM_SETTINGS[arm.name]:
            print(f"=== {arm.name} === (already sampled with identical settings, kept)")
            continue
        print(f"=== {arm.name} ===")
        results[arm.name] = run_arm(arm)
        out_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"\nWritten {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
