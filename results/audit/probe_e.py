"""SONDE E - theta* sensitivity probe (attribution diagnostic, NOT a result fix).

Refit the BAO+CMB-compressed arm (both models, same bounds/seeds policy as M5)
with the prior mean on theta* shifted by our measured model bias
(-1.013e-5, i.e. theta*_model - theta*_published at the prior mean point).
Covariance unchanged. If Nsigma moves from 1.957 back toward the published
2.4, the G5.2 failure is attributable to the HS96 z* theta* bias (P2).

Writes results/audit/probe_e.json.
Run from project root: python -m uv run python results/audit/probe_e.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from desi_w0wa_refit.arms import (
    H_BOUNDS,
    OMEGA_B_H2_BOUNDS,
    OMEGA_M_BOUNDS,
    W0_BOUNDS,
    WA_BOUNDS,
    Arm,
    bao_predictions,
)
from desi_w0wa_refit.bao import load_bao_data
from desi_w0wa_refit.cmb import CMB_PRIOR_COV, CMB_PRIOR_MEAN, DESIParams
from desi_w0wa_refit.fitting import minimize_multistart, nsigma_from_delta_chi2

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUT_PATH = Path(__file__).resolve().parent / "probe_e.json"

THETA_STAR_BIAS = -1.013e-5  # theta*_model - theta*_published at prior mean point
SHIFTED_MEAN = np.asarray(
    [CMB_PRIOR_MEAN[0] + THETA_STAR_BIAS, CMB_PRIOR_MEAN[1], CMB_PRIOR_MEAN[2]],
    dtype=np.float64,
)

INFINITY = float("inf")


class ShiftedPrior:
    """Same Gaussian as CMBCompressedPrior but with the theta* mean shifted."""

    def __init__(self) -> None:
        self.mean = SHIFTED_MEAN
        self.cov = np.asarray(CMB_PRIOR_COV, dtype=np.float64)
        self._cholesky = np.linalg.cholesky(self.cov)

    def chi2(self, theta_star_value: float, omega_b_h2: float, omega_bc_h2: float) -> float:
        residual = (
            np.asarray([theta_star_value, omega_b_h2, omega_bc_h2], dtype=np.float64) - self.mean
        )
        whitened = np.linalg.solve(self._cholesky, residual)
        return float(whitened @ whitened)


def _within(value: float, bounds: tuple[float, float]) -> bool:
    return bounds[0] <= value <= bounds[1]


def make_shifted_chi2(bao, prior):
    """Identical logic to arms.make_cmb_arm (no SNe) with the shifted prior."""

    def chi2(omega_m: float, h: float, omega_b_h2: float, w0: float, wa: float) -> float:
        if not (
            _within(omega_m, OMEGA_M_BOUNDS)
            and _within(h, H_BOUNDS)
            and _within(omega_b_h2, OMEGA_B_H2_BOUNDS)
        ):
            return INFINITY
        if not (_within(w0, W0_BOUNDS) and _within(wa, WA_BOUNDS) and w0 + wa < 0.0):
            return INFINITY
        params = DESIParams(omega_m=omega_m, h=h, omega_b_h2=omega_b_h2, w0=w0, wa=wa)
        if params.omega_bc_h2 <= omega_b_h2:
            return INFINITY
        if not 0.0 < params.omega_bc_h2 / h**2 < 1.5:
            return INFINITY
        background = params.background()
        total = bao.chi2(bao_predictions(background, bao, params.r_drag_mpc()))
        total += prior.chi2(params.theta_star(background), omega_b_h2, params.omega_bc_h2)
        return total

    return chi2


def main() -> None:
    bao = load_bao_data(
        DATA_DIR / "desi_gaussian_bao_ALL_GCcomb_mean.txt",
        DATA_DIR / "desi_gaussian_bao_ALL_GCcomb_cov.txt",
    )
    prior = ShiftedPrior()
    chi2 = make_shifted_chi2(bao, prior)

    chi2_lcdm = lambda x: chi2(float(x[0]), float(x[1]), float(x[2]), -1.0, 0.0)  # noqa: E731
    chi2_w0wa = lambda x: chi2(  # noqa: E731
        float(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4])
    )

    fit_lcdm = minimize_multistart(
        chi2_lcdm,
        [OMEGA_M_BOUNDS, H_BOUNDS, OMEGA_B_H2_BOUNDS],
        run_name="audit-e-lcdm",
        n_starts=24,
    )
    print(
        f"LCDM    chi2 = {fit_lcdm.chi2:.6f}  omega_m={fit_lcdm.x[0]:.6f} "
        f"h={fit_lcdm.x[1]:.6f} ombh2={fit_lcdm.x[2]:.6f}"
    )

    fit_w0wa = minimize_multistart(
        chi2_w0wa,
        [OMEGA_M_BOUNDS, H_BOUNDS, OMEGA_B_H2_BOUNDS, W0_BOUNDS, WA_BOUNDS],
        run_name="audit-e-w0wa",
        n_starts=40,
        constraint=Arm.w0wa_start_constraint,
    )
    print(
        f"w0waCDM chi2 = {fit_w0wa.chi2:.6f}  omega_m={fit_w0wa.x[0]:.6f} "
        f"h={fit_w0wa.x[1]:.6f} ombh2={fit_w0wa.x[2]:.6f} "
        f"w0={fit_w0wa.x[3]:.6f} wa={fit_w0wa.x[4]:.6f}"
    )

    delta_chi2_map = fit_w0wa.chi2 - fit_lcdm.chi2
    nsigma = nsigma_from_delta_chi2(-delta_chi2_map)
    print(f"Delta chi2_MAP = {delta_chi2_map:+.6f}  ->  {nsigma:.6f} sigma")
    print("Reference unshifted: Delta chi2_MAP = -5.977 -> 1.957 sigma")
    print("Published anchor:    Delta chi2_MAP = -8.0   -> 2.4 sigma")

    out = {
        "theta_star_bias_applied": THETA_STAR_BIAS,
        "shifted_prior_mean": [float(v) for v in SHIFTED_MEAN],
        "lcdm": {
            "chi2": fit_lcdm.chi2,
            "params": {
                "omega_m": float(fit_lcdm.x[0]),
                "h": float(fit_lcdm.x[1]),
                "omega_b_h2": float(fit_lcdm.x[2]),
            },
            "top5_start_chi2s": [float(v) for v in fit_lcdm.start_chi2s[:5]],
        },
        "w0wacdm": {
            "chi2": fit_w0wa.chi2,
            "params": {
                "omega_m": float(fit_w0wa.x[0]),
                "h": float(fit_w0wa.x[1]),
                "omega_b_h2": float(fit_w0wa.x[2]),
                "w0": float(fit_w0wa.x[3]),
                "wa": float(fit_w0wa.x[4]),
            },
            "top5_start_chi2s": [float(v) for v in fit_w0wa.start_chi2s[:5]],
        },
        "delta_chi2_map": delta_chi2_map,
        "nsigma": nsigma,
        "reference_unshifted": {"delta_chi2_map": -5.977, "nsigma": 1.957},
        "published_anchor": {"delta_chi2_map": -8.0, "nsigma": 2.4},
    }
    OUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"Written {OUT_PATH}")


if __name__ == "__main__":
    main()
