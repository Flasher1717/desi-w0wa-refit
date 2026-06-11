"""Pre-registered M3 anchor gates as permanent pytest checks (P3).

G3.1, G3.2 and G3.4 are re-fit inline (fast, deterministic); G3.3 needs
a ~10 min seeded emcee run, so its pre-registered criteria are asserted
against the committed results/m3_gates.json produced by
scripts/run_m3_gates.py.
"""

import json
from pathlib import Path

import numpy as np
import pytest

from desi_w0wa_refit.arms import sn_only_chi2
from desi_w0wa_refit.bao import FloatArray
from desi_w0wa_refit.fitting import minimize_multistart
from desi_w0wa_refit.sne import SNSample, load_des_sn5yr, load_pantheon_plus, load_union3

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_PATH = PROJECT_ROOT / "results" / "m3_gates.json"


def _fit_lcdm_omega_m(sample: SNSample, run_name: str) -> float:
    def chi2_fn(x: FloatArray) -> float:
        if not 0.01 <= float(x[0]) <= 0.99:
            return float("inf")
        return sn_only_chi2(sample, float(x[0]))

    fit = minimize_multistart(chi2_fn, [(0.01, 0.99)], run_name=run_name, n_starts=8)
    return float(fit.x[0])


@pytest.mark.requires_data
def test_g31_pantheon_lcdm_anchor() -> None:
    pantheon = load_pantheon_plus(
        DATA_DIR / "Pantheon+SH0ES.dat", DATA_DIR / "Pantheon+SH0ES_STAT+SYS.cov"
    )
    omega_m = _fit_lcdm_omega_m(pantheon, "m3-g31-pantheon-lcdm")
    assert abs(omega_m - 0.334) < 0.010  # Brout 2022, Table 3


@pytest.mark.requires_data
def test_g32_des_lcdm_anchor() -> None:
    des = load_des_sn5yr(DATA_DIR / "DES-SN5YR_HD.csv", DATA_DIR / "DES-SN5YR_STAT+SYS.txt.gz")
    omega_m = _fit_lcdm_omega_m(des, "m3-g32-des-lcdm")
    assert abs(omega_m - 0.352) < 0.010  # DES 2024, Table 2


@pytest.mark.requires_data
def test_g34_union3_structure() -> None:
    union3 = load_union3(DATA_DIR / "Union3_lcparam_full.txt", DATA_DIR / "Union3_mag_covmat.txt")
    assert union3.n_sne == 22  # SPD covariance already enforced by the loader
    assert float(union3.z_cmb[0]) == 0.05
    assert np.all(np.diff(union3.z_cmb) > 0.0)


def test_g33_recorded_results_meet_preregistered_criteria() -> None:
    # The committed output of scripts/run_m3_gates.py (deterministic seeds).
    recorded = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    g33 = recorded["G3.3"]
    assert g33["pass"] is True
    for name in ("omega_m", "w", "wa"):
        info = g33["per_param"][name]
        assert info["pull_in_sigma_chain"] < 0.2
        assert info["pass"] is True
    sampler = g33["sampler"]
    assert sampler["nsteps"] > 50 * max(sampler["tau"])  # convergence (P7)


def test_all_recorded_m3_gates_pass() -> None:
    recorded = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    for gate_name in ("G3.1", "G3.2", "G3.3", "G3.4"):
        assert recorded[gate_name]["pass"] is True, gate_name
