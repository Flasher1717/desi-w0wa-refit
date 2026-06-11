"""Flat w0waCDM (CPL) background cosmology, independent implementation.

Conventions mirror astropy's FLRW machinery exactly so astropy can serve
as an external oracle in the tests (astropy is never imported here):

- E^2(z) = Ogamma0 (1 + nu_rel(z)) (1+z)^4 + Om0 (1+z)^3
  + Ode0 f_DE(z), flat closure Ode0 = 1 - Om0 - Ogamma0 - Onu0
  [astropy FLRW.efunc / FlatFLRWMixin].
- nu_rel(z): neutrino density relative to photons, analytic fitting
  formula of Komatsu et al. 2011, ApJS 192, 18, Eq. (26):
  0.22710731766 * (Neff/n_nu) * [n_massless
  + sum_massive (1 + (0.3173 y_i(z))^1.83)^(1/1.83)],
  y_i(z) = m_i / (k_B T_nu0 (1+z)), T_nu0 = (4/11)^(1/3) T_cmb
  [same constants as astropy; massive neutrinos are NOT added to Om0].
- f_DE(z) for CPL w(a) = w0 + wa (1 - a):
  closed form (1+z)^(3 (1 + w0 + wa)) exp(-3 wa z / (1+z)), tested
  against the defining integral exp(3 int_0^z (1 + w(z'))/(1+z') dz')
  to < 1e-12 relative (M4 pre-registered tolerance).
- LCDM is exactly w0waCDM(w0=-1, wa=0) through the same code paths.

Radiation/neutrinos are OFF by default (t_cmb_k = 0): the SN-only and
BAO-only ("background-only", (Omega_m, h r_d) sampling) arms use pure
matter + dark energy, matching the DESI DR2 background-only
parametrization where omega_r is not even parameterizable. The CMB arms
construct a Background with t_cmb_k = 2.7255, neff = 3.044 and one
massive neutrino of 0.06 eV (DESI DR2 baseline, PREREGISTRATION.md P2).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Final

import numpy as np
from scipy.constants import G, c, k, parsec, sigma
from scipy.integrate import cumulative_simpson, quad
from scipy.interpolate import CubicSpline

from desi_w0wa_refit.bao import FloatArray

C_KM_S: Final = 299792.458  # speed of light, km/s (exact, SI definition)

# Komatsu et al. 2011 Eq. (26) fitting constants (identical to astropy).
_NU_FERMI_DIRAC: Final = 0.22710731766  # 7/8 (4/11)^(4/3)
_KOMATSU_K: Final = 0.3173
_KOMATSU_P: Final = 1.83
_T_NU_OVER_T_CMB: Final = (4.0 / 11.0) ** (1.0 / 3.0)
_K_B_EV_PER_K: Final = k / 1.602176634e-19  # Boltzmann constant, eV/K (CODATA)

# Guard for exp() in the dark-energy density: e^700 is finite in float64
# and the clip only ever binds in regions where E^2 is enormous anyway.
_LOG_CLIP: Final = 700.0


def _omega_gamma_h2(t_cmb_k: float) -> float:
    """Photon density parameter times h^2 from T_CMB.

    rho_gamma = 4 sigma_SB T^4 / c^3 (mass density), divided by the
    critical density at h = 1, rho_crit = 3 H0^2 / (8 pi G).
    """
    rho_gamma = 4.0 * sigma * t_cmb_k**4 / c**3
    h0_si = 100.0 * 1000.0 / (1.0e6 * parsec)  # 100 km/s/Mpc in 1/s
    rho_crit_h1 = 3.0 * h0_si**2 / (8.0 * math.pi * G)
    return rho_gamma / rho_crit_h1


def cpl_log_de_density_closed(z: FloatArray, w0: float, wa: float) -> FloatArray:
    """ln f_DE(z), closed form for CPL: 3[(1+w0+wa) ln(1+z) - wa z/(1+z)]."""
    zp1 = 1.0 + np.asarray(z, dtype=np.float64)
    return 3.0 * ((1.0 + w0 + wa) * np.log(zp1) - wa * (zp1 - 1.0) / zp1)


def cpl_log_de_density_integral(z: float, w0: float, wa: float) -> float:
    """ln f_DE(z) from the defining integral 3 int (1 + w(z'))/(1+z') dz'."""

    def integrand(zp: float) -> float:
        return (1.0 + w0 + wa * zp / (1.0 + zp)) / (1.0 + zp)

    value, _ = quad(integrand, 0.0, z, epsabs=1e-13, epsrel=1e-13, limit=200)
    return 3.0 * value


@dataclass(frozen=True)
class Background:
    """Flat w0waCDM background (LCDM = same paths with w0=-1, wa=0)."""

    h: float
    omega_cb: float  # baryons + CDM today, in units of the critical density
    w0: float = -1.0
    wa: float = 0.0
    t_cmb_k: float = 0.0  # 0 disables photons and neutrinos entirely
    neff: float = 0.0
    m_nu_ev: tuple[float, ...] = ()
    omega_gamma0: float = field(init=False, repr=False, compare=False, default=0.0)
    omega_de0: float = field(init=False, repr=False, compare=False, default=0.0)
    _nu_y0: tuple[float, ...] = field(init=False, repr=False, compare=False, default=())
    _n_massless: int = field(init=False, repr=False, compare=False, default=0)
    _neff_per_nu: float = field(init=False, repr=False, compare=False, default=0.0)

    def __post_init__(self) -> None:
        if self.h <= 0.0:
            raise ValueError(f"h must be positive, got {self.h}")
        if not 0.0 < self.omega_cb < 1.5:
            raise ValueError(f"omega_cb out of range: {self.omega_cb}")
        omega_gamma0 = 0.0
        nu_y0: tuple[float, ...] = ()
        n_massless = 0
        neff_per_nu = 0.0
        if self.t_cmb_k > 0.0:
            omega_gamma0 = _omega_gamma_h2(self.t_cmb_k) / self.h**2
            n_nu = math.floor(self.neff)
            if n_nu > 0:
                massive = tuple(m for m in self.m_nu_ev if m > 0.0)
                if len(massive) > n_nu:
                    raise ValueError("more massive neutrinos than floor(Neff)")
                t_nu0 = _T_NU_OVER_T_CMB * self.t_cmb_k
                nu_y0 = tuple(m / (_K_B_EV_PER_K * t_nu0) for m in massive)
                n_massless = n_nu - len(massive)
                neff_per_nu = self.neff / n_nu
        elif self.neff > 0.0 or self.m_nu_ev:
            raise ValueError("neutrinos require t_cmb_k > 0")
        object.__setattr__(self, "omega_gamma0", omega_gamma0)
        object.__setattr__(self, "_nu_y0", nu_y0)
        object.__setattr__(self, "_n_massless", n_massless)
        object.__setattr__(self, "_neff_per_nu", neff_per_nu)
        onu0 = omega_gamma0 * float(self.nu_relative_density(np.asarray(0.0)))
        omega_de0 = 1.0 - self.omega_cb - omega_gamma0 - onu0
        object.__setattr__(self, "omega_de0", omega_de0)

    def nu_relative_density(self, z: FloatArray) -> FloatArray:
        """Neutrino density / photon density [Komatsu 2011 Eq. (26)]."""
        z = np.asarray(z, dtype=np.float64)
        if self.t_cmb_k <= 0.0 or self._neff_per_nu == 0.0:
            return np.zeros_like(z)
        if not self._nu_y0:
            return np.full_like(z, _NU_FERMI_DIRAC * self.neff)
        zp1 = 1.0 + z
        rel_mass = np.full_like(z, float(self._n_massless))
        for y0 in self._nu_y0:
            rel_mass = rel_mass + (1.0 + (_KOMATSU_K * y0 / zp1) ** _KOMATSU_P) ** (
                1.0 / _KOMATSU_P
            )
        return _NU_FERMI_DIRAC * self._neff_per_nu * rel_mass

    def de_density(self, z: FloatArray) -> FloatArray:
        """f_DE(z) = rho_DE(z) / rho_DE(0), CPL closed form."""
        log_f = cpl_log_de_density_closed(z, self.w0, self.wa)
        return np.exp(np.minimum(log_f, _LOG_CLIP))

    def e2(self, z: FloatArray) -> FloatArray:
        """E^2(z) = (H(z)/H0)^2, astropy FLRW.efunc convention."""
        z = np.asarray(z, dtype=np.float64)
        zp1 = 1.0 + z
        radiation = self.omega_gamma0 * (1.0 + self.nu_relative_density(z))
        return zp1**3 * (radiation * zp1 + self.omega_cb) + self.omega_de0 * self.de_density(z)

    def efunc(self, z: FloatArray) -> FloatArray:
        return np.sqrt(self.e2(z))

    def inv_efunc(self, z: FloatArray) -> FloatArray:
        return 1.0 / np.sqrt(self.e2(z))

    def hubble_km_s_mpc(self, z: FloatArray) -> FloatArray:
        """H(z) in km/s/Mpc."""
        return 100.0 * self.h * self.efunc(z)

    def comoving_distance_mpc(self, z: FloatArray) -> FloatArray:
        """D_C(z) in Mpc (flat, so also D_M), vectorized.

        Cumulative Simpson on a dense uniform grid plus a cubic spline;
        grid residual is far below the 1e-6 oracle tolerance.
        """
        z = np.atleast_1d(np.asarray(z, dtype=np.float64))
        z_max = float(z.max())
        if z_max == 0.0:
            return np.zeros_like(z)
        n_grid = 4097
        z_grid = np.linspace(0.0, z_max, n_grid)
        integrand = self.inv_efunc(z_grid)
        cumulative = cumulative_simpson(integrand, x=z_grid, initial=0.0)
        spline = CubicSpline(z_grid, cumulative)
        return (C_KM_S / (100.0 * self.h)) * np.asarray(spline(z), dtype=np.float64)

    def comoving_distance_scalar_mpc(self, z: float) -> float:
        """D_C(z) in Mpc by adaptive quadrature (any z, e.g. z_star)."""

        def integrand(zp: float) -> float:
            return float(self.inv_efunc(np.asarray(zp)))

        value, _ = quad(integrand, 0.0, z, epsabs=0.0, epsrel=1e-10, limit=300)
        return (C_KM_S / (100.0 * self.h)) * value

    def hubble_distance_mpc(self, z: FloatArray) -> FloatArray:
        """D_H(z) = c / H(z) in Mpc."""
        return C_KM_S / self.hubble_km_s_mpc(z)

    def volume_distance_mpc(self, z: FloatArray) -> FloatArray:
        """D_V(z) = [z D_M^2(z) D_H(z)]^(1/3) in Mpc."""
        z = np.atleast_1d(np.asarray(z, dtype=np.float64))
        d_m = self.comoving_distance_mpc(z)
        d_h = self.hubble_distance_mpc(z)
        return np.asarray((z * d_m**2 * d_h) ** (1.0 / 3.0), dtype=np.float64)

    def distance_modulus(self, z_cmb: FloatArray, z_hel: FloatArray) -> FloatArray:
        """mu = 5 log10((1 + z_hel) D_M(z_cmb) / 10 pc).

        Matches the cobaya SN base class
        (5 log10((1+zhel)(1+zcmb) D_A) with D_A = D_M / (1+zcmb)).
        """
        d_l_mpc = (1.0 + np.asarray(z_hel, dtype=np.float64)) * self.comoving_distance_mpc(z_cmb)
        return 5.0 * np.log10(d_l_mpc) + 25.0
