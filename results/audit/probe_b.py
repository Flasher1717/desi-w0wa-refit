# SONDE B - Attribution r_d : Aubourg Eq.(16) vs rdrag CAMB des chaines officielles.
# Ecrit uniquement sous results/audit/. Ne modifie aucun fichier committe.
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from desi_w0wa_refit.arms import bao_predictions
from desi_w0wa_refit.bao import load_bao_data
from desi_w0wa_refit.cmb import (
    OMEGA_NU_H2_DESI,
    DESIParams,
    sound_horizon_drag_aubourg_mpc,
)

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUT = Path(__file__).resolve().parent


def load_chain(stem: str) -> tuple[dict[str, np.ndarray], int]:
    """Concatenate the 4 cobaya chain files; return columns dict + n points."""
    arrays = []
    cols: list[str] | None = None
    for n in range(1, 5):
        path = DATA / f"{stem}.{n}.txt"
        with path.open("r", encoding="utf-8") as fh:
            header = fh.readline()
        assert header.startswith("#")
        these_cols = header[1:].split()
        if cols is None:
            cols = these_cols
        else:
            assert these_cols == cols, f"column mismatch in {path}"
        arrays.append(np.loadtxt(path))
    data = np.concatenate(arrays, axis=0)
    assert cols is not None
    return {name: data[:, i] for i, name in enumerate(cols)}, data.shape[0]


def analyze(stem: str, label: str) -> dict:
    cols, npts = load_chain(stem)
    ombh2 = cols["ombh2"]
    omch2 = cols["omch2"]
    rdrag = cols["rdrag"]  # CAMB, enregistre point par point
    omm = cols["omm"]
    h0 = cols["H0"]

    aubourg = np.array(
        [sound_horizon_drag_aubourg_mpc(b, b + c) for b, c in zip(ombh2, omch2)]
    )
    diff = aubourg - rdrag  # Mpc, signe : Aubourg - CAMB
    rel = aubourg / rdrag - 1.0  # relatif

    # Regression lineaire du biais relatif sur (ombh2, omch2)
    design = np.column_stack([np.ones(npts), ombh2, omch2])
    coef, *_ = np.linalg.lstsq(design, rel, rcond=None)
    intercept, slope_b, slope_c = coef
    resid_std = float(np.std(rel - design @ coef))

    # Biais au point Planck (prediction de la regression)
    planck_b, planck_c = 0.02236, 0.1432 - 0.02236
    rel_planck_reg = float(intercept + slope_b * planck_b + slope_c * planck_c)
    aubourg_planck = sound_horizon_drag_aubourg_mpc(planck_b, planck_b + planck_c)

    # Coherence omch2 vs mapping omm*(H0/100)^2 - 0.06/93.14 - ombh2 (20 points)
    idx = np.linspace(0, npts - 1, 20).astype(int)
    omch2_mapped = omm[idx] * (h0[idx] / 100.0) ** 2 - OMEGA_NU_H2_DESI - ombh2[idx]
    map_absdiff = np.abs(omch2_mapped - omch2[idx])

    return {
        "label": label,
        "n_points": int(npts),
        "bias_mean_mpc": float(np.mean(diff)),
        "bias_std_mpc": float(np.std(diff)),
        "bias_min_mpc": float(np.min(diff)),
        "bias_max_mpc": float(np.max(diff)),
        "bias_rel_mean": float(np.mean(rel)),
        "bias_rel_std": float(np.std(rel)),
        "regression": {
            "intercept": float(intercept),
            "slope_ombh2_relbias_per_unit": float(slope_b),
            "slope_omch2_relbias_per_unit": float(slope_c),
            "resid_std_rel": resid_std,
        },
        "planck_point": {
            "ombh2": planck_b,
            "omch2": planck_c,
            "aubourg_rd_mpc": float(aubourg_planck),
            "rel_bias_regression": rel_planck_reg,
            "abs_bias_regression_mpc": float(
                rel_planck_reg / (1.0 + rel_planck_reg) * aubourg_planck
            ),
        },
        "omch2_mapping_check_20pts": {
            "max_abs_diff": float(np.max(map_absdiff)),
            "mean_abs_diff": float(np.mean(map_absdiff)),
        },
        "rdrag_camb_mean_mpc": float(np.mean(rdrag)),
        "aubourg_mean_mpc": float(np.mean(aubourg)),
    }


def chi2_bao_at_bestfit(rd_scale: float) -> tuple[float, float]:
    bao = load_bao_data(
        DATA / "desi_gaussian_bao_ALL_GCcomb_mean.txt",
        DATA / "desi_gaussian_bao_ALL_GCcomb_cov.txt",
    )
    params = DESIParams(omega_m=0.30072, h=0.68495, omega_b_h2=0.02236)
    bg = params.background()
    rd = params.r_drag_mpc() * rd_scale
    return float(bao.chi2(bao_predictions(bg, bao, rd))), rd


def main() -> None:
    results = {
        "lcdm": analyze("desi_dr2_base_cmbcompressed_chain", "LCDM"),
        "w0wacdm": analyze("desi_dr2_base_w_wa_cmbcompressed_chain", "w0waCDM"),
    }

    # Biais relatif global (pondere par le nombre de points des deux chaines)
    n1, n2 = results["lcdm"]["n_points"], results["w0wacdm"]["n_points"]
    b1, b2 = results["lcdm"]["bias_rel_mean"], results["w0wacdm"]["bias_rel_mean"]
    rel_bias_global = (n1 * b1 + n2 * b2) / (n1 + n2)  # (Aubourg - CAMB)/CAMB

    chi2_base, rd_base = chi2_bao_at_bestfit(1.0)
    # Correction vers CAMB : rd_CAMB ~ rd_Aubourg / (1 + biais_rel)
    chi2_corr, rd_corr = chi2_bao_at_bestfit(1.0 / (1.0 + rel_bias_global))
    # Lecture litterale de la consigne : rd * (1 + biais relatif mesure)
    chi2_lit, rd_lit = chi2_bao_at_bestfit(1.0 + rel_bias_global)

    results["chi2_bao_effect"] = {
        "bestfit": {"omega_m": 0.30072, "h": 0.68495, "omega_b_h2": 0.02236},
        "rel_bias_global_aubourg_minus_camb_over_camb": rel_bias_global,
        "rd_aubourg_mpc": rd_base,
        "chi2_bao_rd_aubourg": chi2_base,
        "rd_corrected_to_camb_mpc": rd_corr,
        "chi2_bao_rd_corrected_to_camb": chi2_corr,
        "delta_chi2_corrected_minus_base": chi2_corr - chi2_base,
        "rd_times_1_plus_bias_mpc": rd_lit,
        "chi2_bao_rd_times_1_plus_bias": chi2_lit,
        "delta_chi2_literal_minus_base": chi2_lit - chi2_base,
    }

    out_path = OUT / "probe_b_results.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
