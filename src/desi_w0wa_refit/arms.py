"""Chi-squared builders for the five pre-registered M5 combinations.

Arms (PREREGISTRATION.md P4): BAO alone; BAO+CMB; BAO+CMB+{Pantheon+,
Union3, DES-SN5YR}; each fit for flat LCDM and flat w0waCDM.

Parametrizations follow DESI DR2 (RESULTS.md sections 1.2-1.3):

- BAO alone is "background-only": sampled (Omega_m, h r_d) for LCDM and
  (Omega_m, h r_d, w0, wa) for w0waCDM; r_d is absorbed into the free
  h r_d and radiation is not parameterizable (pure matter + DE).
  With h = 1 internally, D / r_d = D(h=1) / (h r_d).
- The CMB arms sample (Omega_m, h, omega_b h^2 [, w0, wa]) exactly like
  the official DESI compressed-prior chains (yaml block: H0, ombh2, w,
  wa, omm), with the physical background (photons + baseline neutrinos),
  r_d from Aubourg Eq. (16) and the Gaussian (theta_star, omega_b h^2,
  omega_bc h^2) prior.

Priors (RESULTS.md section 1.2 + pinned yaml): Omega_m U[0.01, 0.99],
h r_d U[10, 1000] Mpc, H0 U[20, 100], omega_b h^2 U[0.005, 0.1],
w0 U[-3, 1], wa U[-3, 2], w0 + wa < 0. Hard priors return +inf.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from desi_w0wa_refit.bao import BAOData, FloatArray
from desi_w0wa_refit.cmb import CMBCompressedPrior, DESIParams
from desi_w0wa_refit.cosmology import Background
from desi_w0wa_refit.sne import SNSample

OMEGA_M_BOUNDS = (0.01, 0.99)
HRD_BOUNDS = (10.0, 1000.0)
H_BOUNDS = (0.2, 1.0)
OMEGA_B_H2_BOUNDS = (0.005, 0.1)
W0_BOUNDS = (-3.0, 1.0)
WA_BOUNDS = (-3.0, 2.0)

INFINITY = float("inf")


def bao_predictions(background: Background, bao: BAOData, rd_mpc: float) -> FloatArray:
    """Model vector in the exact row order of the BAO file (Lya quirk safe)."""
    d_m = background.comoving_distance_mpc(bao.z)
    d_h = background.hubble_distance_mpc(bao.z)
    d_v = (bao.z * d_m**2 * d_h) ** (1.0 / 3.0)
    by_observable = {"DM_over_rs": d_m, "DH_over_rs": d_h, "DV_over_rs": d_v}
    out = np.empty(bao.n_points, dtype=np.float64)
    for index, observable in enumerate(bao.observables):
        out[index] = by_observable[observable][index] / rd_mpc
    return out


def _within(value: float, bounds: tuple[float, float]) -> bool:
    return bounds[0] <= value <= bounds[1]


def sn_only_chi2(sample: SNSample, omega_m: float, w0: float = -1.0, wa: float = 0.0) -> float:
    """Offset-marginalized SN-only chi2 (h fixed: fully degenerate with M)."""
    background = Background(h=0.7, omega_cb=omega_m, w0=w0, wa=wa)
    mu = background.distance_modulus(sample.z_cmb, sample.z_hel)
    return sample.chi2_marginalized(mu)


@dataclass(frozen=True)
class Arm:
    """One data combination with chi2 callables for both models."""

    name: str
    n_data: int
    bounds_lcdm: tuple[tuple[float, float], ...]
    bounds_w0wa: tuple[tuple[float, float], ...]
    chi2_lcdm: Callable[[FloatArray], float]
    chi2_w0wa: Callable[[FloatArray], float]
    param_names_lcdm: tuple[str, ...]
    param_names_w0wa: tuple[str, ...]

    @staticmethod
    def w0wa_start_constraint(x: FloatArray) -> bool:
        """Start-point filter w0 + wa < 0 (also enforced as a hard prior)."""
        return float(x[-2] + x[-1]) < 0.0


def make_bao_only_arm(bao: BAOData) -> Arm:
    def chi2(omega_m: float, hrd: float, w0: float, wa: float) -> float:
        if not (_within(omega_m, OMEGA_M_BOUNDS) and _within(hrd, HRD_BOUNDS)):
            return INFINITY
        if not (_within(w0, W0_BOUNDS) and _within(wa, WA_BOUNDS) and w0 + wa < 0.0):
            return INFINITY
        background = Background(h=1.0, omega_cb=omega_m, w0=w0, wa=wa)
        return bao.chi2(bao_predictions(background, bao, hrd))

    return Arm(
        name="BAO",
        n_data=bao.n_points,
        bounds_lcdm=(OMEGA_M_BOUNDS, HRD_BOUNDS),
        bounds_w0wa=(OMEGA_M_BOUNDS, HRD_BOUNDS, W0_BOUNDS, WA_BOUNDS),
        chi2_lcdm=lambda x: chi2(float(x[0]), float(x[1]), -1.0, 0.0),
        chi2_w0wa=lambda x: chi2(float(x[0]), float(x[1]), float(x[2]), float(x[3])),
        param_names_lcdm=("omega_m", "hrd_mpc"),
        param_names_w0wa=("omega_m", "hrd_mpc", "w0", "wa"),
    )


def make_cmb_arm(
    bao: BAOData,
    prior: CMBCompressedPrior,
    sn_sample: SNSample | None = None,
) -> Arm:
    name = "BAO+CMB" if sn_sample is None else f"BAO+CMB+{sn_sample.name}"
    n_data = bao.n_points + 3 + (0 if sn_sample is None else sn_sample.n_sne)

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
        if params.omega_bc_h2 <= omega_b_h2:  # omega_c h^2 must stay positive
            return INFINITY
        if not 0.0 < params.omega_bc_h2 / h**2 < 1.5:
            return INFINITY
        background = params.background()
        total = bao.chi2(bao_predictions(background, bao, params.r_drag_mpc()))
        total += prior.chi2(params.theta_star(background), omega_b_h2, params.omega_bc_h2)
        if sn_sample is not None:
            mu = background.distance_modulus(sn_sample.z_cmb, sn_sample.z_hel)
            total += sn_sample.chi2_marginalized(mu)
        return total

    return Arm(
        name=name,
        n_data=n_data,
        bounds_lcdm=(OMEGA_M_BOUNDS, H_BOUNDS, OMEGA_B_H2_BOUNDS),
        bounds_w0wa=(OMEGA_M_BOUNDS, H_BOUNDS, OMEGA_B_H2_BOUNDS, W0_BOUNDS, WA_BOUNDS),
        chi2_lcdm=lambda x: chi2(float(x[0]), float(x[1]), float(x[2]), -1.0, 0.0),
        chi2_w0wa=lambda x: chi2(float(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4])),
        param_names_lcdm=("omega_m", "h", "omega_b_h2"),
        param_names_w0wa=("omega_m", "h", "omega_b_h2", "w0", "wa"),
    )
