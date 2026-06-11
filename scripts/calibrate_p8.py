"""Measure the P8 calibration constants from the pinned official chains.

P8 (PREREGISTRATION.md) corrects the two analytic pre-recombination
outputs of the CMB arms by constant multiplicative factors, calibrated
against the official DESI DR2 compressed-prior chains (pinned in
data_manifest.json, no network here):

- KAPPA_R_DRAG = weighted mean of rdrag_CAMB / r_d_Aubourg, using the
  per-point CAMB ``rdrag`` column.
- KAPPA_THETA_STAR = weighted mean of theta_star_CAMB / theta_star_ours,
  where theta_star_CAMB is reconstructed per point by inverting the
  quadratic form of the ``chi2__CMB_compressed`` column at known
  (ombh2, ombch2): chi2 = r^T Sigma^-1 r is quadratic in the theta_star
  residual, giving two roots (the theory value and its mirror across
  the conditional ridge, separated by ~3.5e-6 — the chains hug the
  ridge). Picking the root closest to our RAW analytic value would
  systematically select the lower root (our bias ~-1.1e-5 puts us below
  both) and underestimate kappa by ~E[separation]/2; instead the root
  choice is iterated to a fixed point with the guess kappa_n * ours,
  which symmetrizes mis-assignments (zero-mean error) and converges in
  a few passes.

Both constants are model-independent (computed on the LCDM and w0waCDM
chains and pooled with equal weight per chain) and data-independent
(no SNe involved). The frozen values live in cmb.py; a requires_data
test re-derives them on a subsample.

Usage: uv run python scripts/calibrate_p8.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from desi_w0wa_refit.bao import FloatArray
from desi_w0wa_refit.cmb import CMB_PRIOR_COV, CMB_PRIOR_MEAN, DESIParams

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"


def load_chain_columns(path: Path, names: tuple[str, ...]) -> dict[str, FloatArray]:
    with path.open(encoding="utf-8") as fh:
        header = fh.readline().removeprefix("#").split()
    indices = [header.index(name) for name in names]
    data = np.loadtxt(path, usecols=indices)
    return {name: data[:, i] for i, name in enumerate(names)}


def invert_theta_star(
    chi2_cmb: FloatArray, ombh2: FloatArray, ombch2: FloatArray, theta_guess: FloatArray
) -> tuple[FloatArray, FloatArray]:
    """Solve the prior quadratic for theta_star at known (ombh2, ombch2).

    Returns (theta_star_root, root_separation). chi2 = a x^2 + 2 b x + c
    with x = theta - mu_theta and delta = (ombh2, ombch2) residuals.
    """
    inv_cov = np.linalg.inv(np.asarray(CMB_PRIOR_COV))
    a = inv_cov[0, 0]
    d1 = ombh2 - CMB_PRIOR_MEAN[1]
    d2 = ombch2 - CMB_PRIOR_MEAN[2]
    b = inv_cov[0, 1] * d1 + inv_cov[0, 2] * d2
    c = inv_cov[1, 1] * d1**2 + 2.0 * inv_cov[1, 2] * d1 * d2 + inv_cov[2, 2] * d2**2
    discriminant = b**2 - a * (c - chi2_cmb)
    discriminant = np.maximum(discriminant, 0.0)
    sqrt_disc = np.sqrt(discriminant)
    x_plus = (-b + sqrt_disc) / a
    x_minus = (-b - sqrt_disc) / a
    theta_plus = CMB_PRIOR_MEAN[0] + x_plus
    theta_minus = CMB_PRIOR_MEAN[0] + x_minus
    pick_plus = np.abs(theta_plus - theta_guess) <= np.abs(theta_minus - theta_guess)
    theta = np.asarray(np.where(pick_plus, theta_plus, theta_minus), dtype=np.float64)
    return theta, np.asarray(np.abs(theta_plus - theta_minus), dtype=np.float64)


def analyze_chain(model: str, has_w: bool, stride: int) -> dict[str, object]:
    names: tuple[str, ...] = (
        "weight",
        "H0",
        "ombh2",
        "omm",
        "omch2",
        "rdrag",
        "chi2__CMB_compressed",
    )
    if has_w:
        names = (*names, "w", "wa")
    weight_parts: list[FloatArray] = []
    ratio_r_parts: list[FloatArray] = []
    chi2_parts: list[FloatArray] = []
    ombh2_parts: list[FloatArray] = []
    ombch2_parts: list[FloatArray] = []
    theta_ours_parts: list[FloatArray] = []
    for index in (1, 2, 3, 4):
        path = DATA_DIR / f"desi_dr2_{model}_cmbcompressed_chain.{index}.txt"
        cols = load_chain_columns(path, names)
        n = cols["weight"].size
        rows = np.arange(0, n, stride)
        rd_ours = np.empty(rows.size)
        theta_ours = np.empty(rows.size)
        for out_i, row in enumerate(rows):
            params = DESIParams(
                omega_m=float(cols["omm"][row]),
                h=float(cols["H0"][row]) / 100.0,
                omega_b_h2=float(cols["ombh2"][row]),
                w0=float(cols["w"][row]) if has_w else -1.0,
                wa=float(cols["wa"][row]) if has_w else 0.0,
            )
            rd_ours[out_i] = params.r_drag_mpc()
            theta_ours[out_i] = params.theta_star()
        weight_parts.append(cols["weight"][rows])
        ratio_r_parts.append(cols["rdrag"][rows] / rd_ours)
        chi2_parts.append(cols["chi2__CMB_compressed"][rows])
        ombh2_parts.append(cols["ombh2"][rows])
        ombch2_parts.append(cols["omch2"][rows] + cols["ombh2"][rows])
        theta_ours_parts.append(theta_ours)
    weights = np.concatenate(weight_parts)
    ratio_r = np.concatenate(ratio_r_parts)
    chi2_all = np.concatenate(chi2_parts)
    ombh2_all = np.concatenate(ombh2_parts)
    ombch2_all = np.concatenate(ombch2_parts)
    theta_ours_all = np.concatenate(theta_ours_parts)
    wsum = float(weights.sum())

    def wmean(values: FloatArray) -> float:
        return float(np.sum(weights * values) / wsum)

    def wstd(values: FloatArray) -> float:
        mean = wmean(values)
        return float(np.sqrt(np.sum(weights * (values - mean) ** 2) / wsum))

    # Fixed-point iteration on the root assignment (see docstring).
    kappa = 1.0
    history: list[float] = []
    separation = np.zeros_like(theta_ours_all)
    for _ in range(12):
        theta_camb, separation = invert_theta_star(
            chi2_all, ombh2_all, ombch2_all, kappa * theta_ours_all
        )
        kappa_new = wmean(theta_camb / theta_ours_all)
        history.append(kappa_new)
        if abs(kappa_new - kappa) < 1e-9:
            kappa = kappa_new
            break
        kappa = kappa_new
    theta_camb, separation = invert_theta_star(
        chi2_all, ombh2_all, ombch2_all, kappa * theta_ours_all
    )
    ratio_t = theta_camb / theta_ours_all

    return {
        "n_points": int(ratio_r.size),
        "kappa_r": wmean(ratio_r),
        "kappa_r_std": wstd(ratio_r),
        "kappa_theta": kappa,
        "kappa_theta_std": wstd(ratio_t),
        "kappa_theta_iterations": history,
        "median_root_separation": float(np.median(separation)),
        "frac_sep_lt_2e-6": float(np.mean(separation < 2e-6)),
    }


def main() -> int:
    stride = 10
    per_model: dict[str, dict[str, object]] = {}
    for model, has_w in (("base", False), ("base_w_wa", True)):
        print(f"Analyzing {model} chains (stride {stride})...")
        per_model[model] = analyze_chain(model, has_w, stride)
        for key, value in per_model[model].items():
            print(f"  {key}: {value}")

    def model_kappa(name: str) -> tuple[float, float]:
        value_base = per_model["base"][name]
        value_w = per_model["base_w_wa"][name]
        assert isinstance(value_base, float) and isinstance(value_w, float)
        return value_base, value_w

    kappa_r = 0.5 * sum(model_kappa("kappa_r"))
    kappa_theta = 0.5 * sum(model_kappa("kappa_theta"))
    out = {
        "method": "P8 calibration on pinned official chains (see script docstring)",
        "stride": stride,
        "per_model": per_model,
        "KAPPA_R_DRAG": kappa_r,
        "KAPPA_THETA_STAR": kappa_theta,
    }
    print(f"\nKAPPA_R_DRAG     = {kappa_r:.9f}")
    print(f"KAPPA_THETA_STAR = {kappa_theta:.9f}")
    RESULTS_DIR.mkdir(exist_ok=True)
    out_path = RESULTS_DIR / "calibration_p8.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"Written {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
