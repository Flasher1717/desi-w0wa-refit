"""SONDE A — pointwise comparison of our chi2_BAO / chi2_CMB against the
official DESI DR2 compressed-CMB chains (base and base_w_wa).

Writes nothing outside stdout; read-only on data/.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from desi_w0wa_refit.arms import bao_predictions
from desi_w0wa_refit.bao import load_bao_data
from desi_w0wa_refit.cmb import CMBCompressedPrior, DESIParams

ROOT = Path(r"C:\Users\flash\dev\desi-w0wa-refit")
DATA = ROOT / "data"

BAO = load_bao_data(
    DATA / "desi_gaussian_bao_ALL_GCcomb_mean.txt",
    DATA / "desi_gaussian_bao_ALL_GCcomb_cov.txt",
)
PRIOR = CMBCompressedPrior()


def parse_chain(path: Path) -> dict[str, np.ndarray]:
    with path.open("r", encoding="utf-8") as fh:
        header = fh.readline()
    assert header.startswith("#")
    names = header.lstrip("#").split()
    arr = np.loadtxt(path)
    assert arr.shape[1] == len(names), (arr.shape, len(names))
    return {name: arr[:, i] for i, name in enumerate(names)}


def ours_at(omm: float, h0: float, ombh2: float, w: float, wa: float):
    params = DESIParams(omega_m=omm, h=h0 / 100.0, omega_b_h2=ombh2, w0=w, wa=wa)
    bg = params.background()
    chi2_bao = BAO.chi2(bao_predictions(bg, BAO, params.r_drag_mpc()))
    chi2_cmb = PRIOR.chi2(params.theta_star(bg), ombh2, params.omega_bc_h2)
    return chi2_bao, chi2_cmb, params.r_drag_mpc(), params.theta_star(bg)


def corr(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.corrcoef(a, b)[0, 1])


def stats(label: str, d: np.ndarray) -> None:
    print(
        f"  {label}: mean={d.mean():+.6f} std={d.std():.6f} "
        f"min={d.min():+.6f} max={d.max():+.6f}"
    )


def run_model(tag: str, chain_file: Path, has_w: bool, n_sub: int = 400) -> None:
    cols = parse_chain(chain_file)
    n = len(cols["weight"])
    idx = np.unique(np.linspace(0, n - 1, n_sub).astype(int))
    print(f"\n=== {tag} : {chain_file.name} ({n} rows, {idx.size} subsampled) ===")

    omm = cols["omm"][idx]
    h0 = cols["H0"][idx]
    ombh2 = cols["ombh2"][idx]
    w = cols["w"][idx] if has_w else np.full(idx.size, -1.0)
    wa = cols["wa"][idx] if has_w else np.zeros(idx.size)
    chi2_bao_off = cols["chi2__BAO"][idx]
    chi2_cmb_off = cols["chi2__CMB_compressed"][idx]
    rdrag_off = cols["rdrag"][idx]

    bao_ours = np.empty(idx.size)
    cmb_ours = np.empty(idx.size)
    rd_ours = np.empty(idx.size)
    th_ours = np.empty(idx.size)
    for k in range(idx.size):
        bao_ours[k], cmb_ours[k], rd_ours[k], th_ours[k] = ours_at(
            omm[k], h0[k], ombh2[k], w[k], wa[k]
        )

    d_bao = bao_ours - chi2_bao_off
    d_cmb = cmb_ours - chi2_cmb_off
    d_rd = rd_ours - rdrag_off
    stats("delta chi2_BAO (ours - official)", d_bao)
    stats("delta chi2_CMB (ours - official)", d_cmb)
    stats("delta r_drag [Mpc] (Aubourg - chain rdrag)", d_rd)
    print(f"  r_drag ratio ours/official: mean={np.mean(rd_ours / rdrag_off):.6f}")
    print(f"  theta_star ours: mean={th_ours.mean():.8f} (prior mean 0.01041027)")
    for name, vec in (("omm", omm), ("H0", h0), ("w", w), ("wa", wa)):
        if has_w or name not in ("w", "wa"):
            print(
                f"  corr(delta_BAO, {name})={corr(d_bao, vec):+.3f}   "
                f"corr(delta_CMB, {name})={corr(d_cmb, vec):+.3f}"
            )


def best_point(pattern: str, has_w: bool):
    best = None
    for i in (1, 2, 3, 4):
        cols = parse_chain(DATA / pattern.format(i))
        j = int(np.argmin(cols["minuslogpost"]))
        cand = {k: cols[k][j] for k in cols}
        cand["_file"] = pattern.format(i)
        if best is None or cand["minuslogpost"] < best["minuslogpost"]:
            best = cand
        # also track min of chi2__BAO+chi2__CMB_compressed over all points
        tot = cols["chi2__BAO"] + cols["chi2__CMB_compressed"]
        jj = int(np.argmin(tot))
        cand2 = {k: cols[k][jj] for k in cols}
        cand2["_file"] = pattern.format(i)
        if "_minchi2" not in best or tot[jj] < best["_minchi2"]:
            best["_minchi2"] = float(tot[jj])
            best["_minchi2_point"] = cand2
    return best


def report_best(tag: str, bp: dict, has_w: bool) -> float:
    w = float(bp.get("w", -1.0)) if has_w else -1.0
    wa = float(bp.get("wa", 0.0)) if has_w else 0.0
    bao_o, cmb_o, rd, th = ours_at(
        float(bp["omm"]), float(bp["H0"]), float(bp["ombh2"]), w, wa
    )
    off_tot = float(bp["chi2__BAO"] + bp["chi2__CMB_compressed"])
    print(f"\n--- {tag} best minuslogpost point ({bp['_file']}) ---")
    print(
        f"  params: omm={bp['omm']:.5f} H0={bp['H0']:.4f} ombh2={bp['ombh2']:.6f} "
        f"w={w:.4f} wa={wa:.4f}  minuslogpost={bp['minuslogpost']:.4f}"
    )
    print(
        f"  official: chi2_BAO={bp['chi2__BAO']:.4f} chi2_CMB={bp['chi2__CMB_compressed']:.4f} "
        f"tot={off_tot:.4f}"
    )
    print(f"  ours:     chi2_BAO={bao_o:.4f} chi2_CMB={cmb_o:.4f} tot={bao_o + cmb_o:.4f}")
    print(f"  ours r_d={rd:.4f} vs chain rdrag={bp['rdrag']:.4f} ; theta*={th:.8f}")
    mc = bp["_minchi2_point"]
    print(
        f"  min(chi2_BAO+chi2_CMB) over all 4 chains = {bp['_minchi2']:.4f} "
        f"at omm={mc['omm']:.5f} H0={mc['H0']:.4f}"
        + (f" w={mc['w']:.4f} wa={mc['wa']:.4f}" if has_w else "")
        + f" ({mc['_file']})"
    )
    return float(bp["_minchi2"])


def main() -> None:
    run_model("w0waCDM", DATA / "desi_dr2_base_w_wa_cmbcompressed_chain.1.txt", True)
    run_model("LCDM", DATA / "desi_dr2_base_cmbcompressed_chain.1.txt", False)

    bp_w = best_point("desi_dr2_base_w_wa_cmbcompressed_chain.{}.txt", True)
    bp_l = best_point("desi_dr2_base_cmbcompressed_chain.{}.txt", False)
    min_w = report_best("w0waCDM", bp_w, True)
    min_l = report_best("LCDM", bp_l, False)
    print(
        f"\nOfficial approx delta chi2_MAP = min_tot(w0wa) - min_tot(base) "
        f"= {min_w:.4f} - {min_l:.4f} = {min_w - min_l:.4f}"
    )


if __name__ == "__main__":
    main()
