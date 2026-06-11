"""Sonde D follow-up: per-row implied theta* of the official likelihood vs ours."""
import numpy as np

from desi_w0wa_refit.cmb import CMB_PRIOR_COV, CMB_PRIOR_MEAN, DESIParams

mu = np.asarray(CMB_PRIOR_MEAN)
S = np.asarray(CMB_PRIOR_COV)
S22 = S[1:, 1:]
S12 = S[0, 1:]
S22i = np.linalg.inv(S22)
sig_cond = float(np.sqrt(S[0, 0] - S12 @ S22i @ S12))


def run(path, has_w, n=200, stride=37):
    with open(path) as f:
        header = f.readline().lstrip("#").split()
    idx = {name: i for i, name in enumerate(header)}
    data = np.loadtxt(path, max_rows=n * stride)
    rows = data[::stride][:n]
    rel = []
    for r in rows:
        ombh2 = r[idx["ombh2"]]
        ombch2 = ombh2 + r[idx["omch2"]]
        y = np.array([ombh2, ombch2])
        chi2_2d = float((y - mu[1:]) @ S22i @ (y - mu[1:]))
        th_cond = mu[0] + S12 @ S22i @ (y - mu[1:])
        rem = r[idx["chi2__CMB_compressed"]] - chi2_2d
        if rem < 0:
            continue
        p = DESIParams(
            omega_m=r[idx["omm"]], h=r[idx["H0"]] / 100.0, omega_b_h2=ombh2,
            w0=r[idx["w"]] if has_w else -1.0, wa=r[idx["wa"]] if has_w else 0.0,
        )
        th_ours = p.theta_star()
        s = np.sqrt(rem) * sig_cond
        # choose the sign giving the implied CAMB theta closest to ours
        cands = (th_cond + s, th_cond - s)
        th_camb = min(cands, key=lambda t: abs(t - th_ours))
        rel.append((th_ours - th_camb) / th_camb)
    rel = np.array(rel)
    print(f"{path}  n_used={len(rel)}")
    print(f"  (theta_ours - theta_CAMB)/theta_CAMB: mean={rel.mean()*100:+.4f}%  "
          f"median={np.median(rel)*100:+.4f}%  std={rel.std()*100:.4f}%  "
          f"sigma_units mean={(rel.mean()*0.010410/ sig_cond):+.2f} (sig_cond={sig_cond:.3e})")


run(r"data\desi_dr2_base_cmbcompressed_chain.1.txt", has_w=False)
run(r"data\desi_dr2_base_w_wa_cmbcompressed_chain.1.txt", has_w=True)
