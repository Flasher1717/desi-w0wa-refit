"""Sonde D: compare our chi2_CMB vs official chi2__CMB_compressed on chain rows."""
import numpy as np

from desi_w0wa_refit.cmb import CMBCompressedPrior, DESIParams

prior = CMBCompressedPrior()


def run(path, has_w, n=200, stride=37):
    with open(path) as f:
        header = f.readline().lstrip("#").split()
    data = np.loadtxt(path, max_rows=n * stride)
    idx = {name: i for i, name in enumerate(header)}
    rows = data[::stride][:n]
    ours, theirs, dth = [], [], []
    for r in rows:
        omm = r[idx["omm"]]
        h = r[idx["H0"]] / 100.0
        ombh2 = r[idx["ombh2"]]
        omch2 = r[idx["omch2"]]
        w0 = r[idx["w"]] if has_w else -1.0
        wa = r[idx["wa"]] if has_w else 0.0
        p = DESIParams(omega_m=omm, h=h, omega_b_h2=ombh2, w0=w0, wa=wa)
        ombch2_chain = ombh2 + omch2
        # check internal mapping consistency
        assert abs(p.omega_bc_h2 - ombch2_chain) < 5e-7, (p.omega_bc_h2, ombch2_chain)
        th = p.theta_star()
        ours.append(prior.chi2(th, ombh2, ombch2_chain))
        theirs.append(r[idx["chi2__CMB_compressed"]])
        dth.append(th)
    ours = np.array(ours)
    theirs = np.array(theirs)
    d = ours - theirs
    print(f"{path}")
    print(f"  n={len(ours)}  mean diff={d.mean():+.4f}  median={np.median(d):+.4f}  "
          f"std={d.std():.4f}  min={d.min():+.4f}  max={d.max():+.4f}")
    print(f"  mean ours={ours.mean():.4f}  mean theirs={theirs.mean():.4f}")
    # implied theta* offset: solve chi2 diff via residual derivative is messy; instead
    # report theta* stats
    print(f"  our theta* mean={np.mean(dth):.8f}")
    return ours, theirs


run(r"data\desi_dr2_base_cmbcompressed_chain.1.txt", has_w=False)
run(r"data\desi_dr2_base_w_wa_cmbcompressed_chain.1.txt", has_w=True)
