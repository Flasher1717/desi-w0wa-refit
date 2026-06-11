"""M4 model tests: CPL closed form vs integral, LCDM nesting, astropy oracles.

Pre-registered tolerances (SPEC + PREREGISTRATION.md P7): closed form vs
defining integral < 1e-12 relative on the prior grid; astropy oracles
< 1e-6 over the domain; LCDM == w0waCDM(-1, 0) exactly (same code paths).
"""

# astropy.cosmology ships no type information; relax ONLY the
# unknown-type diagnostics in this oracle-comparison module (src/ stays
# fully strict; no `Any` or `type: ignore` anywhere).
# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false
# pyright: reportUnknownVariableType=false, reportAttributeAccessIssue=false
# pyright: reportCallIssue=false

import itertools

import astropy.units as u
import numpy as np
import pytest
from astropy.cosmology import FlatLambdaCDM, Flatw0waCDM

from desi_w0wa_refit.cosmology import (
    Background,
    cpl_log_de_density_closed,
    cpl_log_de_density_integral,
)

# Prior grid of the project (RESULTS.md section 1.2): w0 in U[-3,1],
# wa in U[-3,2]; G3.3 additionally explores the wider official DES chain
# priors (w0 in [-5,1], wa in [-20,10]) so those corners are included.
W0_GRID = [-5.0, -3.0, -2.0, -1.0, -0.5, 0.0, 1.0]
WA_GRID = [-20.0, -3.0, -1.5, 0.0, 1.0, 2.0, 10.0]
Z_GRID = np.asarray([0.0, 0.05, 0.295, 0.51, 1.0, 1.484, 2.33, 2.5])


def test_cpl_closed_form_matches_integral_below_1e_minus_12() -> None:
    for w0, wa in itertools.product(W0_GRID, WA_GRID):
        closed = cpl_log_de_density_closed(Z_GRID, w0, wa)
        integral = np.asarray([cpl_log_de_density_integral(float(z), w0, wa) for z in Z_GRID])
        # |delta ln f| < 1e-12  <=>  |f_closed / f_integral - 1| < 1e-12.
        scale = np.maximum(1.0, np.abs(integral))
        assert np.max(np.abs(closed - integral) / scale) < 1e-12


def test_lcdm_is_exactly_w0wacdm_at_minus_one_zero() -> None:
    lcdm = Background(h=0.7, omega_cb=0.31)
    nested = Background(h=0.7, omega_cb=0.31, w0=-1.0, wa=0.0)
    z = np.linspace(0.0, 2.5, 257)
    np.testing.assert_array_equal(lcdm.e2(z), nested.e2(z))
    np.testing.assert_array_equal(nested.de_density(z), np.ones_like(z))


def test_oracle_flat_lcdm_no_radiation() -> None:
    ours = Background(h=0.7, omega_cb=0.3)
    oracle = FlatLambdaCDM(H0=70.0, Om0=0.3, Tcmb0=0.0)
    z = np.linspace(0.01, 2.5, 64)
    np.testing.assert_allclose(ours.efunc(z), oracle.efunc(z), rtol=1e-12)
    np.testing.assert_allclose(
        ours.comoving_distance_mpc(z),
        oracle.comoving_distance(z).to_value(u.Mpc),
        rtol=1e-6,
    )


@pytest.mark.parametrize(
    ("omega_m", "w0", "wa"),
    [
        (0.20, -0.5, -1.5),
        (0.31, -0.8, -0.6),
        (0.35, -1.5, 1.0),
        (0.45, -2.5, 2.0),
        (0.05, -3.0, -3.0),
    ],
)
def test_oracle_flat_w0wacdm_no_radiation(omega_m: float, w0: float, wa: float) -> None:
    ours = Background(h=0.676, omega_cb=omega_m, w0=w0, wa=wa)
    oracle = Flatw0waCDM(H0=67.6, Om0=omega_m, w0=w0, wa=wa, Tcmb0=0.0)
    z = np.linspace(0.01, 2.5, 64)
    np.testing.assert_allclose(ours.efunc(z), oracle.efunc(z), rtol=1e-12)
    np.testing.assert_allclose(
        ours.comoving_distance_mpc(z),
        oracle.comoving_distance(z).to_value(u.Mpc),
        rtol=1e-6,
    )


def test_oracle_with_photons_and_neutrinos_desi_baseline() -> None:
    # DESI DR2 baseline neutrino convention (PREREGISTRATION.md P2):
    # T_CMB = 2.7255 K, Neff = 3.044, one massive state of 0.06 eV.
    # astropy's Om0 excludes massive neutrinos, exactly like our omega_cb.
    h = 0.6736
    omega_cb = 0.1430 / h**2
    ours = Background(h=h, omega_cb=omega_cb, t_cmb_k=2.7255, neff=3.044, m_nu_ev=(0.06,))
    oracle = FlatLambdaCDM(
        H0=100.0 * h,
        Om0=omega_cb,
        Tcmb0=2.7255 * u.K,
        Neff=3.044,
        m_nu=u.Quantity([0.06, 0.0, 0.0], u.eV),
    )
    assert abs(ours.omega_gamma0 - oracle.Ogamma0) < 1e-10
    assert abs(ours.omega_de0 - oracle.Ode0) < 1e-9
    z = np.concatenate([np.linspace(0.0, 2.5, 32), np.geomspace(3.0, 1100.0, 32)])
    np.testing.assert_allclose(ours.efunc(z), oracle.efunc(z), rtol=1e-9)
    for z_scalar in (0.5, 2.33, 1090.0):
        ours_d = ours.comoving_distance_scalar_mpc(z_scalar)
        oracle_d = float(oracle.comoving_distance(z_scalar).to_value(u.Mpc))
        assert abs(ours_d / oracle_d - 1.0) < 1e-6


def test_oracle_w0wacdm_with_radiation() -> None:
    h = 0.68
    ours = Background(
        h=h,
        omega_cb=0.30,
        w0=-0.75,
        wa=-0.8,
        t_cmb_k=2.7255,
        neff=3.044,
        m_nu_ev=(0.06,),
    )
    oracle = Flatw0waCDM(
        H0=100.0 * h,
        Om0=0.30,
        w0=-0.75,
        wa=-0.8,
        Tcmb0=2.7255 * u.K,
        Neff=3.044,
        m_nu=u.Quantity([0.06, 0.0, 0.0], u.eV),
    )
    z = np.concatenate([np.linspace(0.0, 2.5, 32), np.geomspace(3.0, 1100.0, 16)])
    np.testing.assert_allclose(ours.efunc(z), oracle.efunc(z), rtol=1e-9)
    d = ours.comoving_distance_scalar_mpc(1090.0)
    d_oracle = float(oracle.comoving_distance(1090.0).to_value(u.Mpc))
    assert abs(d / d_oracle - 1.0) < 1e-6


def test_distance_modulus_matches_astropy_distmod() -> None:
    ours = Background(h=0.7, omega_cb=0.3)
    oracle = FlatLambdaCDM(H0=70.0, Om0=0.3, Tcmb0=0.0)
    z = np.linspace(0.02, 1.2, 32)
    mu = ours.distance_modulus(z, z)  # z_hel = z_cmb -> astropy's distmod
    np.testing.assert_allclose(mu, oracle.distmod(z).to_value(u.mag), rtol=0, atol=1e-6)


def test_scalar_and_vector_comoving_distances_agree() -> None:
    ours = Background(h=0.7, omega_cb=0.3, w0=-0.9, wa=0.3)
    for z in (0.1, 0.51, 1.484, 2.33):
        vec = float(ours.comoving_distance_mpc(np.asarray([z]))[0])
        scalar = ours.comoving_distance_scalar_mpc(z)
        assert abs(vec / scalar - 1.0) < 1e-9


def test_volume_distance_definition() -> None:
    ours = Background(h=0.7, omega_cb=0.3)
    z = np.asarray([0.295])
    d_m = ours.comoving_distance_mpc(z)
    d_h = ours.hubble_distance_mpc(z)
    expected = (z * d_m**2 * d_h) ** (1.0 / 3.0)
    np.testing.assert_allclose(ours.volume_distance_mpc(z), expected, rtol=1e-14)


def test_background_input_validation() -> None:
    with pytest.raises(ValueError, match="h must be positive"):
        Background(h=0.0, omega_cb=0.3)
    with pytest.raises(ValueError, match="omega_cb out of range"):
        Background(h=0.7, omega_cb=0.0)
    with pytest.raises(ValueError, match="neutrinos require"):
        Background(h=0.7, omega_cb=0.3, neff=3.044)
    with pytest.raises(ValueError, match="more massive neutrinos"):
        Background(h=0.7, omega_cb=0.3, t_cmb_k=2.7255, neff=1.0, m_nu_ev=(0.06, 0.06))
