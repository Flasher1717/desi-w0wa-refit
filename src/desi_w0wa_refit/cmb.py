"""Compressed CMB prior and pre-recombination fitting formulas.

Everything here is pre-registered (PREREGISTRATION.md P1-P2); formulas
were extracted from the papers with equation numbers, never from memory.

- Compressed prior: Gaussian on (theta_star, omega_b h^2, omega_bc h^2),
  full-precision means and covariance from the official DESI DR2 cobaya
  yaml (pinned in data_manifest.json), matching arXiv:2503.14738v3
  Eqs. (35)-(36) after rounding [PREREGISTRATION.md P1].
- r_d (sound horizon at the drag epoch): Aubourg et al. 2015,
  arXiv:1411.1074, Eq. (16) (documented precision 0.021 %), with the
  paper's own omega_nu = 0.0107 (sum m_nu / 1 eV). Permanent
  cross-check: the DESI DR2 paper's own scaling, arXiv:2503.14738v3
  Eq. (2), within 0.3 %.
- z_star (photon decoupling): Hu & Sugiyama 1996, astro-ph/9510117,
  Appendix E, Eq. (E-1) (percent-level; limitation pre-registered in P2
  and bounded by gate G5.2).
- r_s(z_star): numerical integral of c_s / H [EH98, astro-ph/9709112,
  Eq. (5) and surrounding text]: R = 31.5 omega_b Theta_2.7^-4
  (z/10^3)^-1, c_s = c / sqrt(3 (1 + R)); T_CMB = 2.7255 K committed
  here (DESI DR2 baseline).
- theta_star = r_s(z_star) / D_M(z_star).
- DESI parameter mapping (official chain.updated.yaml, pinned):
  omega_bc h^2 = Omega_m h^2 - sum m_nu / 93.14; baseline neutrinos
  sum m_nu = 0.06 eV in one massive state, Neff = 3.044.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

import numpy as np
from scipy.integrate import quad, simpson

from desi_w0wa_refit.bao import FloatArray, validate_covariance
from desi_w0wa_refit.cosmology import C_KM_S, Background

# DESI DR2 baseline (PREREGISTRATION.md P2, from Section V + official yaml).
T_CMB_K: Final = 2.7255
NEFF: Final = 3.044
SUM_MNU_EV: Final = 0.06
# DESI's own mapping constant (official yaml: omch2 = omm h^2 - mnu/93.14 - ombh2).
OMEGA_NU_H2_DESI: Final = SUM_MNU_EV / 93.14
# Aubourg et al. 2015, text after Eq. (16): omega_nu = 0.0107 (sum m_nu / 1 eV).
OMEGA_NU_H2_AUBOURG: Final = 0.0107 * SUM_MNU_EV

# P8 — calibrated amendment (PREREGISTRATION.md P8, decided AFTER the
# G5.2 audit, full transparency there): constant multiplicative
# corrections of the analytic outputs, measured against the pinned
# official DESI chains by scripts/calibrate_p8.py. Applied ONLY in the
# DESIParams pipeline entry points; the raw formulas stay untouched.
KAPPA_R_DRAG: Final = 1.000279376
KAPPA_THETA_STAR: Final = 1.001314308

# P1 — full-precision compressed prior (theta_star, omega_b h^2, omega_bc h^2),
# official DESI DR2 yaml, cross-verified on two independent chain files.
CMB_PRIOR_MEAN: Final = (0.01041027, 0.02223208, 0.14207901)
CMB_PRIOR_COV: Final = (
    (6.6209942e-12, 1.24442058e-10, -1.19287532e-09),
    (1.24442058e-10, 2.13441666e-08, -9.40008323e-08),
    (-1.19287532e-09, -9.40008323e-08, 1.48841714e-06),
)


def sound_horizon_drag_aubourg_mpc(
    omega_b_h2: float, omega_cb_h2: float, omega_nu_h2: float = OMEGA_NU_H2_AUBOURG
) -> float:
    """r_d in Mpc [Aubourg et al. 2015, Eq. (16); precision 0.021 %]."""
    return (
        55.154
        * math.exp(-72.3 * (omega_nu_h2 + 0.0006) ** 2)
        / (omega_cb_h2**0.25351 * omega_b_h2**0.12807)
    )


def sound_horizon_drag_desi_eq2_mpc(
    omega_b_h2: float, omega_bc_h2: float, neff: float = NEFF
) -> float:
    """r_d scaling of the DESI DR2 paper itself [2503.14738v3, Eq. (2)]."""
    return (
        147.05
        * (omega_b_h2 / 0.02236) ** -0.13
        * (omega_bc_h2 / 0.1432) ** -0.23
        * (neff / 3.04) ** -0.1
    )


def z_star_hu_sugiyama(omega_b_h2: float, omega_m_h2: float) -> float:
    """Photon-decoupling redshift [HS96, App. E, Eq. (E-1)]."""
    g1 = 0.0783 * omega_b_h2**-0.238 / (1.0 + 39.5 * omega_b_h2**0.763)
    g2 = 0.560 / (1.0 + 21.1 * omega_b_h2**1.81)
    return 1048.0 * (1.0 + 0.00124 * omega_b_h2**-0.738) * (1.0 + g1 * omega_m_h2**g2)


def sound_horizon_at_z_mpc(background: Background, omega_b_h2: float, z: float) -> float:
    """r_s(z) = int_z^inf c_s dz' / H(z') in Mpc [EH98 Eq. (5) + text].

    Integrated in a = 1/(1+z') so the infinite tail maps to a -> 0 where
    the radiation-dominated integrand stays finite.
    """
    theta_27 = T_CMB_K / 2.7

    def integrand(a: float) -> float:
        z_prime = 1.0 / a - 1.0
        baryon_to_photon = 31.5 * omega_b_h2 * theta_27**-4 * 1.0e3 / z_prime
        c_s = C_KM_S / math.sqrt(3.0 * (1.0 + baryon_to_photon))
        hubble = float(background.hubble_km_s_mpc(np.asarray(z_prime)))
        return c_s / (hubble * a * a)

    value, _ = quad(integrand, 0.0, 1.0 / (1.0 + z), epsabs=0.0, epsrel=1e-9, limit=300)
    return value


def sound_horizon_at_z_fast_mpc(background: Background, omega_b_h2: float, z: float) -> float:
    """Same integral as sound_horizon_at_z_mpc on a fixed vectorized grid.

    Substitution a = x^2 regularizes the radiation-dominated end (the
    integrand goes to zero linearly in x); fixed 4097-point Simpson is
    deterministic and ~10x faster than adaptive quad. Cross-validated
    against the quad version to < 1e-7 relative in the tests.
    """
    theta_27 = T_CMB_K / 2.7
    x_max = math.sqrt(1.0 / (1.0 + z))
    x = np.linspace(0.0, x_max, 4097)
    z_prime = np.empty_like(x)
    z_prime[0] = np.inf
    z_prime[1:] = 1.0 / (x[1:] ** 2) - 1.0
    integrand = np.zeros_like(x)
    baryon_to_photon = 31.5 * omega_b_h2 * theta_27**-4 * 1.0e3 / z_prime[1:]
    c_s = C_KM_S / np.sqrt(3.0 * (1.0 + baryon_to_photon))
    hubble = background.hubble_km_s_mpc(z_prime[1:])
    integrand[1:] = 2.0 * c_s / (x[1:] ** 3 * hubble)
    return float(simpson(integrand, x=x))


def comoving_distance_fast_mpc(background: Background, z: float) -> float:
    """D_C(z) on a fixed log(1+z) Simpson grid (high-z capable, fast).

    Cross-validated against comoving_distance_scalar_mpc (adaptive quad)
    to < 1e-7 relative in the tests.
    """
    u = np.linspace(0.0, math.log1p(z), 4097)
    zp1 = np.exp(u)
    integrand = zp1 * background.inv_efunc(zp1 - 1.0)
    return float(simpson(integrand, x=u)) * C_KM_S / (100.0 * background.h)


def theta_star(
    background: Background, omega_b_h2: float, omega_m_h2: float, *, fast: bool = True
) -> float:
    """theta_star = r_s(z_star) / D_M(z_star) (flat: D_M = D_C)."""
    z_star = z_star_hu_sugiyama(omega_b_h2, omega_m_h2)
    if fast:
        r_s = sound_horizon_at_z_fast_mpc(background, omega_b_h2, z_star)
        d_m = comoving_distance_fast_mpc(background, z_star)
    else:
        r_s = sound_horizon_at_z_mpc(background, omega_b_h2, z_star)
        d_m = background.comoving_distance_scalar_mpc(z_star)
    return r_s / d_m


@dataclass(frozen=True)
class DESIParams:
    """DESI DR2 sampling block for the compressed-CMB arm: (omm, H0, ombh2[, w, wa])."""

    omega_m: float  # total matter, INCLUDING non-relativistic neutrinos (DESI convention)
    h: float
    omega_b_h2: float
    w0: float = -1.0
    wa: float = 0.0

    @property
    def omega_bc_h2(self) -> float:
        """omega_b h^2 + omega_c h^2, EXCLUDING neutrinos [official yaml mapping]."""
        return self.omega_m * self.h**2 - OMEGA_NU_H2_DESI

    @property
    def omega_m_h2(self) -> float:
        return self.omega_m * self.h**2

    def background(self) -> Background:
        """Physical background with photons and DESI baseline neutrinos."""
        return Background(
            h=self.h,
            omega_cb=self.omega_bc_h2 / self.h**2,
            w0=self.w0,
            wa=self.wa,
            t_cmb_k=T_CMB_K,
            neff=NEFF,
            m_nu_ev=(SUM_MNU_EV,),
        )

    def r_drag_mpc(self) -> float:
        """Aubourg Eq. (16) with the P8 calibration constant applied."""
        return KAPPA_R_DRAG * sound_horizon_drag_aubourg_mpc(self.omega_b_h2, self.omega_bc_h2)

    def theta_star(self, background: Background | None = None) -> float:
        """Analytic theta_star with the P8 calibration constant applied."""
        bg = self.background() if background is None else background
        return KAPPA_THETA_STAR * theta_star(bg, self.omega_b_h2, self.omega_m_h2)


class CMBCompressedPrior:
    """Gaussian prior chi^2 on (theta_star, omega_b h^2, omega_bc h^2) [P1]."""

    def __init__(self) -> None:
        self.mean: FloatArray = np.asarray(CMB_PRIOR_MEAN, dtype=np.float64)
        self.cov: FloatArray = np.asarray(CMB_PRIOR_COV, dtype=np.float64)
        validate_covariance(self.cov, name="CMB compressed prior covariance")
        self._cholesky: FloatArray = np.asarray(np.linalg.cholesky(self.cov), dtype=np.float64)

    def chi2(self, theta_star_value: float, omega_b_h2: float, omega_bc_h2: float) -> float:
        residual = (
            np.asarray([theta_star_value, omega_b_h2, omega_bc_h2], dtype=np.float64) - self.mean
        )
        whitened = np.linalg.solve(self._cholesky, residual)
        return float(whitened @ whitened)
