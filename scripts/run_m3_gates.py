"""Run the pre-registered M3 anchor gates (PREREGISTRATION.md P3).

G3.1  Pantheon+ LCDM SN-only best fit:   |Omega_m - 0.334| < 0.010
G3.2  DES-SN5YR LCDM SN-only best fit:   |Omega_m - 0.352| < 0.010
G3.3  DES-SN5YR w0waCDM SN-only posterior means vs the official weighted
      polychord chain, with the chain's own priors (omega_m U[0.01,0.99],
      w0 U[-5,1], wa U[-20,10]): |mean - mean_chain| < 0.2 sigma_chain
      on each of (Omega_m, w0, wa).
G3.4  Union3 structural validation (22 nodes, SPD by construction) and
      recorded LCDM best fit for downstream G5 coherence.

Writes results/m3_gates.json and prints a human-readable report.
Deterministic: all seeds derive from ROOT_SEED via derive_seed (P7).

Usage: uv run python scripts/run_m3_gates.py
"""

# emcee ships no type information; relax only the unknown-type
# diagnostics here (no `Any`, no `type: ignore`).
# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false
# pyright: reportUnknownVariableType=false, reportAttributeAccessIssue=false

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import emcee
import numpy as np

from desi_w0wa_refit.bao import FloatArray
from desi_w0wa_refit.chains import read_cosmosis_chain
from desi_w0wa_refit.cosmology import Background
from desi_w0wa_refit.fitting import derive_seed, minimize_multistart
from desi_w0wa_refit.sne import SNSample, load_des_sn5yr, load_pantheon_plus, load_union3

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"

# Official DES SN-only chain priors (embedded in the pinned chain header).
G33_BOUNDS = ((0.01, 0.99), (-5.0, 1.0), (-20.0, 10.0))
G33_NWALKERS = 32
G33_NSTEPS = 6000
G33_BURN = 1500


def sn_only_chi2(sample: SNSample, omega_m: float, w0: float = -1.0, wa: float = 0.0) -> float:
    """Offset-marginalized SN-only chi2 (h fixed, fully degenerate with M)."""
    background = Background(h=0.7, omega_cb=omega_m, w0=w0, wa=wa)
    mu = background.distance_modulus(sample.z_cmb, sample.z_hel)
    return sample.chi2_marginalized(mu)


def fit_lcdm_omega_m(sample: SNSample, run_name: str) -> tuple[float, float]:
    """Best-fit (Omega_m, chi2) for flat LCDM, SN only."""

    def chi2_fn(x: FloatArray) -> float:
        if not 0.01 <= float(x[0]) <= 0.99:
            return float("inf")
        return sn_only_chi2(sample, float(x[0]))

    fit = minimize_multistart(chi2_fn, [(0.01, 0.99)], run_name=run_name, n_starts=8)
    return float(fit.x[0]), fit.chi2


def g33_log_prob(theta: FloatArray, sample: SNSample) -> float:
    omega_m, w0, wa = float(theta[0]), float(theta[1]), float(theta[2])
    for value, (low, high) in zip((omega_m, w0, wa), G33_BOUNDS, strict=True):
        if not low <= value <= high:
            return -np.inf
    return -0.5 * sn_only_chi2(sample, omega_m, w0, wa)


def run_g33(des: SNSample) -> dict[str, object]:
    chain = read_cosmosis_chain(DATA_DIR / "DES-SN5YR_fw0wacdm_SN.txt")

    rng = np.random.RandomState(derive_seed("m3-g33-emcee"))
    p0 = np.column_stack(
        [
            rng.uniform(0.05, 0.95, G33_NWALKERS),
            rng.uniform(-3.0, 0.5, G33_NWALKERS),
            rng.uniform(-15.0, 5.0, G33_NWALKERS),
        ]
    )
    sampler = emcee.EnsembleSampler(G33_NWALKERS, 3, g33_log_prob, args=(des,))
    state = emcee.State(p0, random_state=rng.get_state())
    t0 = time.perf_counter()
    sampler.run_mcmc(state, G33_NSTEPS, progress=False)
    runtime = time.perf_counter() - t0

    tau = sampler.get_autocorr_time(tol=0)
    tau_max = float(np.max(tau))
    if 50 * tau_max >= G33_NSTEPS:
        raise RuntimeError(
            f"G3.3 emcee not converged: nsteps={G33_NSTEPS} <= 50*tau_max={50 * tau_max:.1f}"
        )
    flat_raw = sampler.get_chain(discard=G33_BURN, thin=max(1, int(tau_max / 2)), flat=True)
    if flat_raw is None:
        raise RuntimeError("emcee returned no chain")
    flat = np.asarray(flat_raw, dtype=np.float64)

    per_param: dict[str, dict[str, float | bool]] = {}
    passed = True
    for column_index, name in enumerate(("omega_m", "w", "wa")):
        mean_chain = chain.weighted_mean(name)
        sigma_chain = chain.weighted_std(name)
        mean_ours = float(np.mean(flat[:, column_index]))
        pull = abs(mean_ours - mean_chain) / sigma_chain
        ok = pull < 0.2
        passed = passed and ok
        per_param[name] = {
            "mean_chain": mean_chain,
            "sigma_chain": sigma_chain,
            "mean_pipeline": mean_ours,
            "sigma_pipeline": float(np.std(flat[:, column_index])),
            "pull_in_sigma_chain": pull,
            "pass": ok,
        }
        print(
            f"  {name:8s} chain {mean_chain:+.4f} +/- {sigma_chain:.4f}"
            f"  pipeline {mean_ours:+.4f}  pull {pull:.3f} sigma_chain  pass={ok}"
        )

    # Diagnostic (not a gate): our log-likelihood in the official DES
    # convention (-0.5 (chi2_marg + ln(c/2pi))) evaluated at the official
    # chain points, against the chain's own `like` column. Restricted to
    # the weighted posterior support: polychord output also stores dead
    # exploration points (223/908 with like < -1000 but total weight
    # 4e-82) where both codes blow up differently. Their chain used the
    # pippin files (n=1828) and CAMB theory, so a small smooth residual
    # is expected; a covariance-convention error would shift chi2 by
    # hundreds.
    like_chain = chain.column("like")
    weights = chain.weights
    keep = np.flatnonzero(weights > 1e-6 * float(weights.max()))
    deltas: list[float] = []
    for index in keep:
        omega_m = float(chain.column("omega_m")[index])
        w0 = float(chain.column("w")[index])
        wa = float(chain.column("wa")[index])
        ours_like = -0.5 * (sn_only_chi2(des, omega_m, w0, wa) + des.offset_log_norm)
        deltas.append(ours_like - float(like_chain[index]))
    delta_arr = np.asarray(deltas)
    diagnostic = {
        "weight_covered": float(weights[keep].sum() / weights.sum()),
        "mean_delta": float(np.mean(delta_arr)),
        "std_delta": float(np.std(delta_arr)),
        "max_abs_delta": float(np.max(np.abs(delta_arr))),
        "n_points": int(delta_arr.size),
    }
    print(f"  diagnostic like vs official: {diagnostic}")

    return {
        "anchor_chain": "DES-SN5YR_fw0wacdm_SN.txt (polychord, weighted)",
        "priors": "omega_m U[0.01,0.99], w0 U[-5,1], wa U[-20,10] (from chain header)",
        "sampler": {
            "nwalkers": G33_NWALKERS,
            "nsteps": G33_NSTEPS,
            "burn": G33_BURN,
            "seed_name": "m3-g33-emcee",
            "tau": [float(t) for t in tau],
            "runtime_s": round(runtime, 1),
        },
        "per_param": per_param,
        "pass": passed,
        "diagnostic_like_vs_official": diagnostic,
    }


def main() -> int:
    print("Loading samples...")
    pantheon = load_pantheon_plus(
        DATA_DIR / "Pantheon+SH0ES.dat", DATA_DIR / "Pantheon+SH0ES_STAT+SYS.cov"
    )
    des = load_des_sn5yr(DATA_DIR / "DES-SN5YR_HD.csv", DATA_DIR / "DES-SN5YR_STAT+SYS.txt.gz")
    union3 = load_union3(DATA_DIR / "Union3_lcparam_full.txt", DATA_DIR / "Union3_mag_covmat.txt")

    results: dict[str, dict[str, object]] = {}

    print("G3.1 Pantheon+ LCDM SN-only...")
    omega_m_g31, chi2_g31 = fit_lcdm_omega_m(pantheon, "m3-g31-pantheon-lcdm")
    pass_g31 = abs(omega_m_g31 - 0.334) < 0.010
    results["G3.1"] = {
        "sample": f"PantheonPlus ({pantheon.n_sne} SNe, zHD > 0.01)",
        "anchor": "Omega_m = 0.334 +/- 0.018 [Brout 2022, Table 3]",
        "omega_m_pipeline": omega_m_g31,
        "chi2_min": chi2_g31,
        "criterion": "|Omega_m - 0.334| < 0.010",
        "abs_diff": abs(omega_m_g31 - 0.334),
        "pass": pass_g31,
    }
    print(f"  Omega_m = {omega_m_g31:.4f}  (anchor 0.334)  pass={pass_g31}")

    print("G3.2 DES-SN5YR LCDM SN-only...")
    omega_m_g32, chi2_g32 = fit_lcdm_omega_m(des, "m3-g32-des-lcdm")
    pass_g32 = abs(omega_m_g32 - 0.352) < 0.010
    results["G3.2"] = {
        "sample": f"DES-SN5YR ({des.n_sne} SNe)",
        "anchor": "Omega_m = 0.352 +/- 0.017 [DES 2024, Table 2]",
        "omega_m_pipeline": omega_m_g32,
        "chi2_min": chi2_g32,
        "criterion": "|Omega_m - 0.352| < 0.010",
        "abs_diff": abs(omega_m_g32 - 0.352),
        "pass": pass_g32,
    }
    print(f"  Omega_m = {omega_m_g32:.4f}  (anchor 0.352)  pass={pass_g32}")

    print("G3.3 DES-SN5YR w0waCDM SN-only vs official chain (emcee)...")
    results["G3.3"] = run_g33(des)

    print("G3.4 Union3 structural + LCDM fit...")
    omega_m_g34, chi2_g34 = fit_lcdm_omega_m(union3, "m3-g34-union3-lcdm")
    pass_g34 = union3.n_sne == 22
    results["G3.4"] = {
        "sample": "Union3 (22 spline nodes)",
        "structural": "22 nodes, SPD covariance (validated by the loader)",
        "omega_m_pipeline": omega_m_g34,
        "chi2_min": chi2_g34,
        "n_nodes": union3.n_sne,
        "pass": pass_g34,
    }
    print(f"  Omega_m = {omega_m_g34:.4f}  chi2 = {chi2_g34:.2f}  pass={pass_g34}")

    RESULTS_DIR.mkdir(exist_ok=True)
    out_path = RESULTS_DIR / "m3_gates.json"
    out_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"\nWritten {out_path}")

    all_pass = all(bool(gate["pass"]) for gate in results.values())
    print(f"ALL GATES PASS: {all_pass}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
