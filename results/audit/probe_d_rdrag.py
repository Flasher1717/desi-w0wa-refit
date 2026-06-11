"""Sonde D bonus: our Aubourg r_d vs CAMB rdrag column in official chains."""
import numpy as np

from desi_w0wa_refit.cmb import DESIParams


def run(path, has_w, n=300, stride=25):
    with open(path) as f:
        header = f.readline().lstrip("#").split()
    idx = {name: i for i, name in enumerate(header)}
    data = np.loadtxt(path, max_rows=n * stride)
    rows = data[::stride][:n]
    rel = []
    for r in rows:
        p = DESIParams(
            omega_m=r[idx["omm"]], h=r[idx["H0"]] / 100.0, omega_b_h2=r[idx["ombh2"]],
            w0=r[idx["w"]] if has_w else -1.0, wa=r[idx["wa"]] if has_w else 0.0,
        )
        rel.append(p.r_drag_mpc() / r[idx["rdrag"]] - 1.0)
    rel = np.array(rel) * 100
    print(f"{path}  n={len(rel)}")
    print(f"  (rd_ours/rd_CAMB - 1): mean={rel.mean():+.4f}%  median={np.median(rel):+.4f}%  "
          f"std={rel.std():.4f}%  min={rel.min():+.4f}%  max={rel.max():+.4f}%")


run(r"data\desi_dr2_base_cmbcompressed_chain.1.txt", has_w=False)
run(r"data\desi_dr2_base_w_wa_cmbcompressed_chain.1.txt", has_w=True)
