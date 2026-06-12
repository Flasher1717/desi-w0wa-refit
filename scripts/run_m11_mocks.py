"""M11: V1 Keeley-style mock test on DES-SN5YR (PREREGISTRATION.md P9).

Runs, in this order (P9 freezes at the first of these runs):

  pilot   P9.4: 50 mocks from the PRIMARY seed stream, timing ONLY --
          declared non-scientific; chi2 values are neither reported nor
          compared to the real chi2. Writes results/m11_pilot.json.
  full    1. G11.2 anchor: Pantheon+ in the Keeley selection (N = 1580),
             fiducial Omega_m = 0.3; gates |chi2_real - 1387.10| <= 1.0
             and p <= 0.0027. A failed gate is a STOP-audit, the DES
             verdict is not interpreted past it.
          2. V1 primary: DES-SN5YR (N = 1829), fiducial Omega_m = 0.3.
          3. V1b secondary (non-gating): DES, fiducial at the real-data
             best-fit Omega_m.
          4. V1c secondary (non-gating): DES without the 75
             MUERR_FINAL > 1 rows (BEAMS-downweighted).
          5. Descriptive diagnostics (P9.4c) on both real samples.
          Writes results/m11_mocks.json.

All seeds derive from ROOT_SEED via derive_seed (P7): mock i of each
run uses derive_seed(f"<stream>-{i}") with streams m11-v1pp-mock,
m11-v1-mock, m11-v1b-mock, m11-v1c-mock.

Usage: uv run python scripts/run_m11_mocks.py pilot|full
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np

from desi_w0wa_refit.mocks import (
    MockTestResult,
    delta2_for_chi2_eq_n,
    draw_mock,
    fit_lcdm_profiled,
    mu_lcdm,
    normalized_residual_std,
    run_mock_test,
)
from desi_w0wa_refit.sne import SNSample, load_des_sn5yr, load_pantheon_plus_keeley

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"

N_MOCKS = 10_000  # P9.3
KEELEY_CHI2_PP = 1387.10  # arXiv:2212.07917v3 Sec. 2
GATE_CHI2_TOL = 1.0  # G11.2
GATE_P_MAX = 0.0027  # G11.2 (GO M10.2)
FLAGGED_ABORT_FRACTION = 0.01  # P9.2 failure policy
MUERR_BEAMS_THRESHOLD = 1.0  # P9.4b


def sample_hash(sample: SNSample) -> str:
    """SHA256 of the filtered data vector (same convention as M7)."""
    digest = hashlib.sha256()
    for array in (sample.z_cmb, sample.z_hel, sample.mag):
        digest.update(np.ascontiguousarray(array).tobytes())
    if sample.survey_ids is not None:
        digest.update(np.ascontiguousarray(sample.survey_ids).tobytes())
    return digest.hexdigest()


def load_des() -> SNSample:
    return load_des_sn5yr(DATA_DIR / "DES-SN5YR_HD.csv", DATA_DIR / "DES-SN5YR_STAT+SYS.txt.gz")


def des_muerr_final() -> np.ndarray:
    """MUERR_FINAL column in file order (for the P9.4b BEAMS mask)."""
    lines = (DATA_DIR / "DES-SN5YR_HD.csv").read_text(encoding="utf-8").splitlines()
    header = [token.strip() for token in lines[0].split(",")]
    index = header.index("MUERR_FINAL")
    return np.asarray(
        [line.split(",")[index] for line in lines[1:] if line.strip()], dtype=np.float64
    )


def summarize(result: MockTestResult) -> dict[str, object]:
    chi2s = result.mock_chi2
    quantiles = np.quantile(chi2s, [0.01, 0.05, 0.5, 0.95, 0.99])
    return {
        "n_mocks": result.n_mocks,
        "seed_stream": result.seed_stream,
        "fid_omega_m": result.fid_omega_m,
        "chi2_real": result.chi2_real,
        "omega_m_real": result.omega_m_real,
        "k_below": result.k_below,
        "n_flagged": result.n_flagged,
        "p_low_tail": result.p_low_tail,
        "z_one_sided": result.z_one_sided,
        "z_two_sided_keeley_convention": result.z_two_sided,
        "mock_chi2_mean": float(chi2s.mean()),
        "mock_chi2_std": float(chi2s.std()),
        "mock_chi2_quantiles_1_5_50_95_99": [float(q) for q in quantiles],
        "mock_chi2_values_rounded_1e-4": [round(float(c), 4) for c in chi2s],
    }


def check_flagged(result: MockTestResult, label: str) -> None:
    fraction = result.n_flagged / result.n_mocks
    if fraction > FLAGGED_ABORT_FRACTION:
        raise RuntimeError(
            f"{label}: {result.n_flagged}/{result.n_mocks} flagged mock fits "
            f"(> {FLAGGED_ABORT_FRACTION:.0%}) -- STOP audit before any interpretation (P9.2)"
        )


def run_pilot() -> int:
    """P9.4 timing pilot: 50 primary-stream mocks, NO chi2 reported."""
    des = load_des()
    mu_fid = mu_lcdm(des, 0.3)
    t0 = time.perf_counter()
    from desi_w0wa_refit.fitting import derive_seed

    for index in range(50):
        mock_mag = draw_mock(des, mu_fid, derive_seed(f"m11-v1-mock-{index}"))
        fit_lcdm_profiled(des, mock_mag)  # result intentionally discarded
    elapsed = time.perf_counter() - t0
    per_mock = elapsed / 50.0
    report = {
        "declared": "non-scientific timing pilot (P9.4); chi2 values discarded",
        "n_mocks": 50,
        "seed_stream": "m11-v1-mock (primary stream, P9.4)",
        "total_s": round(elapsed, 1),
        "per_mock_s": round(per_mock, 3),
        "extrapolated_10000_min": round(per_mock * 10_000 / 60.0, 1),
        "machine": platform.node(),
    }
    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / "m11_pilot.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Written {out}")
    return 0


def run_full() -> int:
    results: dict[str, object] = {
        "preregistration": "P9 (frozen at this run)",
        "n_mocks": N_MOCKS,
        "root_seed_scheme": "derive_seed(f'<stream>-{i}') from ROOT_SEED 20260611 (P7)",
    }

    # --- 1. G11.2 anchor: Pantheon+ Keeley selection -------------------
    print("G11.2 anchor: Pantheon+ (Keeley selection, N expected 1580)...")
    pantheon = load_pantheon_plus_keeley(
        DATA_DIR / "Pantheon+SH0ES.dat", DATA_DIR / "Pantheon+SH0ES_STAT+SYS.cov"
    )
    print(f"  N = {pantheon.n_sne}, subset sha256 = {sample_hash(pantheon)[:16]}...")
    t0 = time.perf_counter()
    pp_result = run_mock_test(
        pantheon, seed_stream="m11-v1pp-mock", n_mocks=N_MOCKS, fid_omega_m=0.3
    )
    pp_runtime = time.perf_counter() - t0
    check_flagged(pp_result, "G11.2")
    gate_chi2 = abs(pp_result.chi2_real - KEELEY_CHI2_PP) <= GATE_CHI2_TOL
    gate_p = pp_result.p_low_tail <= GATE_P_MAX
    pp_summary = summarize(pp_result)
    pp_summary.update(
        {
            "n_sne": pantheon.n_sne,
            "subset_sha256": sample_hash(pantheon),
            "anchor_chi2_published": KEELEY_CHI2_PP,
            "gate_chi2_pass": gate_chi2,
            "gate_p_pass": gate_p,
            "pass": gate_chi2 and gate_p,
            "runtime_s": round(pp_runtime, 1),
        }
    )
    results["G11.2_pantheon_keeley"] = pp_summary
    print(
        f"  chi2_real = {pp_result.chi2_real:.3f} (anchor {KEELEY_CHI2_PP}, "
        f"gate {gate_chi2})  k = {pp_result.k_below}  p = {pp_result.p_low_tail:.6f} "
        f"(gate {gate_p})  [{pp_runtime:.0f}s]"
    )
    if not (gate_chi2 and gate_p):
        out = RESULTS_DIR / "m11_mocks.json"
        out.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
        print("G11.2 FAILED -- STOP audit (the DES runs are not executed).")
        return 1

    # --- 2. V1 primary: DES-SN5YR, Keeley fiducial ----------------------
    print("V1 primary: DES-SN5YR (N = 1829), fiducial Omega_m = 0.3...")
    des = load_des()
    t0 = time.perf_counter()
    des_result = run_mock_test(des, seed_stream="m11-v1-mock", n_mocks=N_MOCKS, fid_omega_m=0.3)
    des_runtime = time.perf_counter() - t0
    check_flagged(des_result, "V1")
    p = des_result.p_low_tail
    if p < 0.0027:
        verdict = "anomalously low chi2 (p < 0.0027)"
    elif p <= 0.9973:
        verdict = "compatible (0.0027 <= p <= 0.9973)"
    else:
        verdict = "anomalously HIGH tail (p > 0.9973)"
    des_summary = summarize(des_result)
    des_summary.update(
        {
            "n_sne": des.n_sne,
            "subset_sha256": sample_hash(des),
            "preregistered_verdict": verdict,
            "runtime_s": round(des_runtime, 1),
        }
    )
    results["V1_des_primary"] = des_summary
    print(
        f"  chi2_real = {des_result.chi2_real:.3f}  k = {des_result.k_below}  "
        f"p = {p:.6f}  -> {verdict}  [{des_runtime:.0f}s]"
    )

    # --- 3. V1b secondary: fiducial at the real best fit ----------------
    real_fit = fit_lcdm_profiled(des, des.mag)
    print(f"V1b secondary: DES fiducial at best-fit Omega_m = {real_fit.omega_m:.4f}...")
    t0 = time.perf_counter()
    v1b_result = run_mock_test(
        des, seed_stream="m11-v1b-mock", n_mocks=N_MOCKS, fid_omega_m=real_fit.omega_m
    )
    v1b_runtime = time.perf_counter() - t0
    check_flagged(v1b_result, "V1b")
    v1b_summary = summarize(v1b_result)
    v1b_summary.update({"non_gating": True, "runtime_s": round(v1b_runtime, 1)})
    results["V1b_des_bestfit_fiducial"] = v1b_summary
    print(f"  k = {v1b_result.k_below}  p = {v1b_result.p_low_tail:.6f}  [{v1b_runtime:.0f}s]")

    # --- 4. V1c secondary: without the BEAMS-downweighted rows ----------
    muerr = des_muerr_final()
    keep = muerr <= MUERR_BEAMS_THRESHOLD
    des_nobeams = des.subset(keep)
    print(
        f"V1c secondary: DES without MUERR_FINAL > 1 "
        f"({int((~keep).sum())} rows removed, N = {des_nobeams.n_sne})..."
    )
    t0 = time.perf_counter()
    v1c_result = run_mock_test(
        des_nobeams, seed_stream="m11-v1c-mock", n_mocks=N_MOCKS, fid_omega_m=0.3
    )
    v1c_runtime = time.perf_counter() - t0
    check_flagged(v1c_result, "V1c")
    v1c_summary = summarize(v1c_result)
    v1c_summary.update(
        {
            "non_gating": True,
            "n_sne": des_nobeams.n_sne,
            "n_removed": int((~keep).sum()),
            "subset_sha256": sample_hash(des_nobeams),
            "runtime_s": round(v1c_runtime, 1),
        }
    )
    results["V1c_des_nobeams"] = v1c_summary
    print(
        f"  chi2_real = {v1c_result.chi2_real:.3f}  k = {v1c_result.k_below}  "
        f"p = {v1c_result.p_low_tail:.6f}  [{v1c_runtime:.0f}s]"
    )

    # --- 5. Descriptive diagnostics (P9.4c, non-gating) ------------------
    print("Diagnostics (descriptive, non-gating)...")
    diagnostics: dict[str, object] = {}
    for label, sample in (("pantheon_keeley", pantheon), ("des", des)):
        fit = fit_lcdm_profiled(sample, sample.mag)
        resid_std = normalized_residual_std(sample, fit)
        delta2, chi2_at_root = delta2_for_chi2_eq_n(sample)
        diagnostics[label] = {
            "normalized_residual_std_ddof0": resid_std,
            "delta2_diag_subtraction_for_chi2_eq_n": delta2,
            "chi2_at_delta2_root": chi2_at_root,
            "sign_convention": "positive = subtraction (errors overestimated)",
        }
        print(f"  {label}: resid_std = {resid_std:.4f}  delta2 = {delta2:+.6f}")
    results["diagnostics_p9_4c"] = diagnostics

    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / "m11_mocks.json"
    out.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"Written {out}")
    return 0


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"pilot", "full"}:
        print(__doc__)
        return 2
    return run_pilot() if sys.argv[1] == "pilot" else run_full()


if __name__ == "__main__":
    sys.exit(main())
