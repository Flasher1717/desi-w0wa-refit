"""Traceability of every load-bearing figure quoted in RESULTS.md (M8).

Each figure displayed in the final report (executive summary section 0,
fit tables sections 4 and 6, MCMC marginals section 7, low-z profile
section 8, P8 constants) is recomputed here from the committed JSON run
records under results/ and compared after rounding to the precision shown
in the document. The JSON records are the source of truth; a mismatch
means RESULTS.md drifted from the recorded runs.
"""

import json
from pathlib import Path
from typing import cast

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


def _load(name: str) -> dict[str, object]:
    payload = json.loads((RESULTS_DIR / name).read_text(encoding="utf-8"))
    return cast(dict[str, object], payload)


def _node(record: dict[str, object], *keys: str) -> float:
    value: object = record[keys[0]]
    for key in keys[1:]:
        value = cast(dict[str, object], value)[key]
    assert isinstance(value, (int, float))
    return float(value)


def _quoted(record: dict[str, object], digits: int, *keys: str) -> float:
    return round(_node(record, *keys), digits)


# --- Section 4 - raw analytic pipeline (m5_fits.json) ---------------------

# arm -> (chi2_lcdm, chi2_w0wa, delta_chi2_map, nsigma, delta_aic, delta_bic)
SECTION_4_TABLE = {
    "BAO": (10.271, 5.619, -4.652, 1.66, -0.65, 0.48),
    "BAO+CMB": (12.761, 6.784, -5.977, 1.96, -1.98, -0.43),
    "BAO+CMB+PantheonPlus": (1418.52, 1412.12, -6.406, 2.05, -2.41, 8.36),
    "BAO+CMB+Union3": (41.163, 29.033, -12.131, 3.05, -8.13, -4.86),
    "BAO+CMB+DES-SN5YR": (1662.20, 1645.74, -16.456, 3.65, -12.46, -1.42),
}

# arm -> compression effect (nsigma - published), as quoted in section 4
SECTION_4_COMPRESSION = {
    "BAO+CMB+PantheonPlus": -0.75,
    "BAO+CMB+Union3": -0.75,
    "BAO+CMB+DES-SN5YR": -0.55,
}


def test_section_4_raw_fit_table() -> None:
    raw = _load("m5_fits.json")
    for arm, (c_l, c_w, dchi2, nsig, daic, dbic) in SECTION_4_TABLE.items():
        chi2_digits = 2 if c_l > 100 else 3
        assert _quoted(raw, chi2_digits, arm, "lcdm", "chi2") == c_l, arm
        assert _quoted(raw, chi2_digits, arm, "w0wacdm", "chi2") == c_w, arm
        assert _quoted(raw, 3, arm, "delta_chi2_map") == dchi2, arm
        assert _quoted(raw, 2, arm, "nsigma") == nsig, arm
        assert _quoted(raw, 2, arm, "delta_aic") == daic, arm
        assert _quoted(raw, 2, arm, "delta_bic") == dbic, arm
    for arm, effect in SECTION_4_COMPRESSION.items():
        assert _quoted(raw, 2, arm, "nsigma_minus_published") == effect, arm


def test_section_4_raw_sne_best_fit_w0() -> None:
    raw = _load("m5_fits.json")
    quoted = {
        "BAO+CMB+PantheonPlus": -0.864,
        "BAO+CMB+Union3": -0.704,
        "BAO+CMB+DES-SN5YR": -0.778,
    }
    for arm, w0 in quoted.items():
        assert _quoted(raw, 3, arm, "w0wacdm", "params", "w0") == w0, arm


# --- Section 6 - P8-corrected pipeline (m5_fits_corrected.json) -----------

SECTION_6_TABLE = {
    "BAO": (10.271, 5.619, -4.652, 1.66, -0.65, 0.48),
    "BAO+CMB": (15.151, 7.129, -8.023, 2.36, -4.02, -2.48),
    "BAO+CMB+PantheonPlus": (1420.95, 1413.37, -7.574, 2.28, -3.57, 7.19),
    "BAO+CMB+Union3": (43.584, 29.790, -13.794, 3.29, -9.79, -6.52),
    "BAO+CMB+DES-SN5YR": (1664.65, 1646.67, -17.984, 3.84, -13.98, -2.94),
}

SECTION_6_COMPRESSION = {
    "BAO+CMB+PantheonPlus": -0.52,
    "BAO+CMB+Union3": -0.51,
    "BAO+CMB+DES-SN5YR": -0.36,
}

# arm -> (w0, wa) of the w0waCDM best fit, as quoted in section 6
SECTION_6_BEST_FITS = {
    "BAO+CMB+PantheonPlus": (-0.853, -0.52),
    "BAO+CMB+Union3": (-0.686, -0.99),
    "BAO+CMB+DES-SN5YR": (-0.766, -0.78),
}


def test_section_6_corrected_fit_table() -> None:
    corrected = _load("m5_fits_corrected.json")
    for arm, (c_l, c_w, dchi2, nsig, daic, dbic) in SECTION_6_TABLE.items():
        chi2_digits = 2 if c_l > 100 else 3
        assert _quoted(corrected, chi2_digits, arm, "lcdm", "chi2") == c_l, arm
        assert _quoted(corrected, chi2_digits, arm, "w0wacdm", "chi2") == c_w, arm
        assert _quoted(corrected, 3, arm, "delta_chi2_map") == dchi2, arm
        assert _quoted(corrected, 2, arm, "nsigma") == nsig, arm
        assert _quoted(corrected, 2, arm, "delta_aic") == daic, arm
        assert _quoted(corrected, 2, arm, "delta_bic") == dbic, arm
    for arm, effect in SECTION_6_COMPRESSION.items():
        assert _quoted(corrected, 2, arm, "nsigma_minus_published") == effect, arm


def test_section_6_replication_points() -> None:
    corrected = _load("m5_fits_corrected.json")
    bao_cmb_w0wa = ("BAO+CMB", "w0wacdm", "params")
    assert _quoted(corrected, 4, *bao_cmb_w0wa, "omega_m") == 0.3509
    assert _quoted(corrected, 4, *bao_cmb_w0wa, "h") == 0.6372
    assert _quoted(corrected, 3, *bao_cmb_w0wa, "w0") == -0.445
    assert _quoted(corrected, 3, *bao_cmb_w0wa, "wa") == -1.645
    for arm, (w0, wa) in SECTION_6_BEST_FITS.items():
        assert _quoted(corrected, 3, arm, "w0wacdm", "params", "w0") == w0, arm
        assert _quoted(corrected, 2, arm, "w0wacdm", "params", "wa") == wa, arm
    # BAO-only LCDM exact-replication landmark (sections 4 and 6)
    assert _quoted(corrected, 4, "BAO", "lcdm", "params", "omega_m") == 0.2975
    assert _quoted(corrected, 2, "BAO", "lcdm", "params", "hrd_mpc") == 101.54


# --- Section 7 - MCMC marginals (m6_mcmc.json) -----------------------------

# arm -> (w0 mean, w0 std, wa mean, wa std, d_euclidean, d_mahalanobis)
SECTION_7_TABLE = {
    "BAO": (-0.476, 0.262, -1.660, 0.963, 2.84, 3.20),
    "BAO+CMB": (-0.430, 0.217, -1.709, 0.633, 1.74, 2.60),
    "BAO+CMB+PantheonPlus": (-0.848, 0.056, -0.552, 0.220, 0.54, 2.65),
    "BAO+CMB+Union3": (-0.675, 0.090, -1.041, 0.310, 1.04, 3.50),
    "BAO+CMB+DES-SN5YR": (-0.761, 0.058, -0.806, 0.239, 0.81, 4.09),
}


def test_section_7_mcmc_marginals() -> None:
    mcmc = _load("m6_mcmc.json")
    for arm, (w0, w0_std, wa, wa_std, d_euc, d_mah) in SECTION_7_TABLE.items():
        assert _quoted(mcmc, 3, arm, "marginals", "w0", "mean") == w0, arm
        assert _quoted(mcmc, 3, arm, "marginals", "w0", "std") == w0_std, arm
        assert _quoted(mcmc, 3, arm, "marginals", "wa", "mean") == wa, arm
        assert _quoted(mcmc, 3, arm, "marginals", "wa", "std") == wa_std, arm
        assert _quoted(mcmc, 2, arm, "distance_map_to_lcdm_euclidean_w0wa") == d_euc, arm
        assert _quoted(mcmc, 2, arm, "distance_map_to_lcdm_mahalanobis_w0wa") == d_mah, arm


# --- Section 8 - low-z profile (m7_cuts.json) ------------------------------

# cut -> (n_sne, delta_chi2_map, nsigma, delta_nsigma, w0, wa, dw0, dwa)
CutRow = tuple[float, float, float, float, float, float, float, float]

SECTION_8_PANTHEON: dict[str, CutRow] = {
    "C-a": (960, -6.247, 2.014, -0.265, -0.780, -0.715, 0.073, -0.193),
    "C-b": (1357, -7.155, 2.198, -0.081, -0.845, -0.544, 0.008, -0.021),
    "C-c": (960, -6.247, 2.014, -0.265, -0.780, -0.715, 0.073, -0.193),
    "C-d": (1322, -6.921, 2.152, -0.127, -0.852, -0.522, 0.001, -0.000),
}

SECTION_8_DES: dict[str, CutRow] = {
    "C-a": (1632, -3.887, 1.464, -2.373, -0.818, -0.616, -0.052, 0.162),
    "C-b": (1753, -16.160, 3.607, -0.230, -0.755, -0.806, 0.011, -0.028),
    "C-c": (1635, -4.184, 1.540, -2.297, -0.811, -0.639, -0.045, 0.139),
    "C-d": (1829, -17.984, 3.837, 0.000, -0.766, -0.778, -0.000, 0.000),
}

# arm -> (n_sne, delta_chi2_map, nsigma, w0, wa) quoted for the baselines
SECTION_8_BASELINES = {
    "BAO+CMB+PantheonPlus": (1590, -7.574, 2.279, -0.853, -0.522),
    "BAO+CMB+DES-SN5YR": (1829, -17.984, 3.837, -0.766, -0.778),
}


def _check_cut_rows(cuts: dict[str, object], arm: str, table: dict[str, CutRow]) -> None:
    for cut, row in table.items():
        n_sne, dchi2, nsig, dnsig, w0, wa, dw0, dwa = row
        assert _node(cuts, arm, cut, "n_sne") == n_sne, (arm, cut)
        assert _quoted(cuts, 3, arm, cut, "delta_chi2_map") == dchi2, (arm, cut)
        assert _quoted(cuts, 3, arm, cut, "nsigma") == nsig, (arm, cut)
        assert _quoted(cuts, 3, arm, cut, "delta_nsigma_vs_baseline") == dnsig, (arm, cut)
        assert _quoted(cuts, 3, arm, cut, "w0_map") == w0, (arm, cut)
        assert _quoted(cuts, 3, arm, cut, "wa_map") == wa, (arm, cut)
        assert _quoted(cuts, 3, arm, cut, "delta_w0") == dw0, (arm, cut)
        assert _quoted(cuts, 3, arm, cut, "delta_wa") == dwa, (arm, cut)


def test_section_8_lowz_profile_tables() -> None:
    cuts = _load("m7_cuts.json")
    for arm, (n_sne, dchi2, nsig, w0, wa) in SECTION_8_BASELINES.items():
        assert _node(cuts, arm, "baseline", "n_sne") == n_sne, arm
        assert _quoted(cuts, 3, arm, "baseline", "delta_chi2_map") == dchi2, arm
        assert _quoted(cuts, 3, arm, "baseline", "nsigma") == nsig, arm
        assert _quoted(cuts, 3, arm, "baseline", "w0_map") == w0, arm
        assert _quoted(cuts, 3, arm, "baseline", "wa_map") == wa, arm
    _check_cut_rows(cuts, "BAO+CMB+PantheonPlus", SECTION_8_PANTHEON)
    _check_cut_rows(cuts, "BAO+CMB+DES-SN5YR", SECTION_8_DES)


def test_section_0_executive_summary_figures() -> None:
    corrected = _load("m5_fits_corrected.json")
    cuts = _load("m7_cuts.json")
    # 1st headline figure: the five anchors, all gates green.
    anchors = {
        "BAO": 1.66,
        "BAO+CMB": 2.36,
        "BAO+CMB+PantheonPlus": 2.28,
        "BAO+CMB+Union3": 3.29,
        "BAO+CMB+DES-SN5YR": 3.84,
    }
    for arm, nsig in anchors.items():
        assert _quoted(corrected, 2, arm, "nsigma") == nsig, arm
        assert cast(dict[str, object], corrected[arm])["pass"] is True, arm
    assert _quoted(corrected, 3, "BAO+CMB", "delta_chi2_map") == -8.023
    # 2nd headline figure: DES profile collapse vs targeted CfA+CSP cut.
    des = "BAO+CMB+DES-SN5YR"
    assert _quoted(cuts, 2, des, "C-a", "nsigma") == 1.46
    assert _quoted(cuts, 2, des, "C-c", "nsigma") == 1.54
    assert _quoted(cuts, 2, des, "C-b", "delta_nsigma_vs_baseline") == -0.23
    # 3rd headline figure: Pantheon+ robustness.
    pplus = "BAO+CMB+PantheonPlus"
    assert _quoted(cuts, 2, pplus, "C-a", "nsigma") == 2.01
    assert _quoted(cuts, 2, pplus, "C-b", "delta_nsigma_vs_baseline") == -0.08
    assert _quoted(cuts, 2, pplus, "C-d", "delta_nsigma_vs_baseline") == -0.13


def test_p8_constants_quoted_in_results() -> None:
    calibration = _load("calibration_p8.json")
    assert _quoted(calibration, 9, "KAPPA_R_DRAG") == 1.000279376
    assert _quoted(calibration, 9, "KAPPA_THETA_STAR") == 1.001314308
    # Residual scatter quoted as 7.6e-6 (w0waCDM chains, the relevant model).
    scatter = _node(calibration, "per_model", "base_w_wa", "kappa_theta_std")
    assert round(scatter * 1e6, 1) == 7.6


# --- Section 11.1 - V1 Keeley-style mock test (m11_mocks.json) -------------

# run -> (chi2_real, k_below, p rounded as quoted, z_one, z_two, n_flagged)
SECTION_11_V1 = {
    "G11.2_pantheon_keeley": (1386.405, 1, 0.0002, 3.54, 3.72, 0),
    "V1_des_primary": (1640.083, 5, 0.0006, 3.24, 3.43, 0),
    "V1b_des_bestfit_fiducial": (1640.083, 7, 0.0008, 3.16, 3.35, 0),
    "V1c_des_nobeams": (1639.389, 287, 0.0288, 1.90, 2.19, 0),
}


def test_section_11_1_mock_runs() -> None:
    mocks = _load("m11_mocks.json")
    for run, (chi2, k, p, z_one, z_two, flagged) in SECTION_11_V1.items():
        assert _quoted(mocks, 3, run, "chi2_real") == chi2, run
        assert _node(mocks, run, "k_below") == k, run
        assert round(_node(mocks, run, "p_low_tail"), 4) == p, run
        assert _quoted(mocks, 2, run, "z_one_sided") == z_one, run
        assert _quoted(mocks, 2, run, "z_two_sided_keeley_convention") == z_two, run
        assert _node(mocks, run, "n_flagged") == flagged, run
    # G11.2 gates green; DES mock distribution as quoted (mean 1828.1, std 59.5)
    g112 = cast(dict[str, object], mocks["G11.2_pantheon_keeley"])
    assert g112["pass"] is True
    assert _quoted(mocks, 1, "V1_des_primary", "mock_chi2_mean") == 1828.1
    assert _quoted(mocks, 1, "V1_des_primary", "mock_chi2_std") == 59.5
    # diagnostics quoted in 11.1
    diag = "diagnostics_p9_4c"
    assert _quoted(mocks, 3, diag, "pantheon_keeley", "normalized_residual_std_ddof0") == 0.914
    assert _quoted(mocks, 3, diag, "des", "normalized_residual_std_ddof0") == 0.904
    delta2_key = "delta2_diag_subtraction_for_chi2_eq_n"
    assert _quoted(mocks, 5, diag, "pantheon_keeley", delta2_key) == 0.00219
    assert _quoted(mocks, 5, diag, "des", delta2_key) == 0.00207


# --- Section 11.2 - V2 leave-one-group-out (m12_loo.json) ------------------

# group -> (n_sne, dchi2, nsigma, dnsigma, w0, wa, sigma_w0, sigma_wa)
LooRow = tuple[float, float, float, float, float, float, float | None, float | None]

SECTION_11_LOO_PANTHEON: dict[str, LooRow] = {
    "cfa": (1433, -7.429, 2.251, -0.028, -0.845, -0.541, 0.107, 0.406),
    "csp": (1514, -7.545, 2.274, -0.006, -0.851, -0.530, 0.095, 0.368),
    "foundation": (1417, -9.622, 2.646, 0.367, -0.824, -0.595, 0.102, 0.391),
    "misc-lowz": (1389, -5.459, 1.844, -0.436, -0.868, -0.475, 0.115, 0.429),
    "des-in-pp": (1387, -4.754, 1.681, -0.598, -0.885, -0.453, 0.107, 0.404),
    "cfa+csp": (1357, -7.155, 2.198, -0.081, -0.845, -0.544, 0.114, 0.430),
}

SECTION_11_LOO_DES: dict[str, LooRow] = {
    "cfa+csp": (1753, -16.160, 3.607, -0.230, -0.755, -0.806, 0.118, 0.461),
    "foundation": (1711, -8.787, 2.502, -1.335, -0.792, -0.699, 0.304, 1.092),
    "des": (194, -8.861, 2.515, -1.323, -0.456, -1.615, None, None),
    "cfa-only-desc": (1761, -15.826, 3.563, -0.274, -0.760, -0.792, 0.116, 0.453),
    "csp-only-desc": (1821, -18.282, 3.874, 0.036, -0.764, -0.786, 0.093, 0.377),
}

# arm -> baseline (sigma_curv_w0, sigma_curv_wa) quoted in 11.2
SECTION_11_LOO_BASELINE_SIGMAS = {
    "BAO+CMB+PantheonPlus": (0.091, 0.356),
    "BAO+CMB+DES-SN5YR": (0.093, 0.376),
}


def _check_loo_rows(loo: dict[str, object], arm: str, table: dict[str, LooRow]) -> None:
    for group, row in table.items():
        n_sne, dchi2, nsig, dnsig, w0, wa, s_w0, s_wa = row
        assert _node(loo, arm, group, "n_sne") == n_sne, (arm, group)
        assert _quoted(loo, 3, arm, group, "delta_chi2_map") == dchi2, (arm, group)
        assert _quoted(loo, 3, arm, group, "nsigma") == nsig, (arm, group)
        assert _quoted(loo, 3, arm, group, "delta_nsigma_vs_baseline") == dnsig, (arm, group)
        assert _quoted(loo, 3, arm, group, "w0_map") == w0, (arm, group)
        assert _quoted(loo, 3, arm, group, "wa_map") == wa, (arm, group)
        arm_table = cast(dict[str, object], loo[arm])
        group_row = cast(dict[str, object], arm_table[group])
        if s_w0 is None:
            assert group_row["sigma_curv_w0"] is None, (arm, group)
            assert group_row["sigma_curv_wa"] is None, (arm, group)
            assert group_row["boundary_flagged"] is True, (arm, group)
        else:
            assert _quoted(loo, 3, arm, group, "sigma_curv_w0") == s_w0, (arm, group)
            assert _quoted(loo, 3, arm, group, "sigma_curv_wa") == s_wa, (arm, group)


def test_section_11_2_loo_tables() -> None:
    loo = _load("m12_loo.json")
    for arm, (s_w0, s_wa) in SECTION_11_LOO_BASELINE_SIGMAS.items():
        assert _quoted(loo, 3, arm, "baseline", "sigma_curv_w0") == s_w0, arm
        assert _quoted(loo, 3, arm, "baseline", "sigma_curv_wa") == s_wa, arm
    _check_loo_rows(loo, "BAO+CMB+PantheonPlus", SECTION_11_LOO_PANTHEON)
    _check_loo_rows(loo, "BAO+CMB+DES-SN5YR", SECTION_11_LOO_DES)
    # the reused rows must point at the frozen M7 record
    for arm in SECTION_11_LOO_BASELINE_SIGMAS:
        arm_table = cast(dict[str, object], loo[arm])
        reused = cast(dict[str, object], arm_table["cfa+csp"])
        assert "m7_cuts.json" in str(reused["reused_from"]), arm


# --- Section 11.3 - V3 paired common SNe (m13_pairs.json) ------------------

# label -> (n, mean, sem) as quoted in the Tier R table
SECTION_11_TIER_R = {
    "DES5Y": (145, -0.0122, 0.0055),
    "FOUND": (118, -0.0508, 0.0070),
    "CFA3S": (14, -0.0344, 0.0112),
    "CFA3K": (27, -0.0616, 0.0163),
    "CFA4P2": (18, -0.0547, 0.0196),
    "CFA4P3": (3, 0.0285, 0.0869),
    "CSP": (7, 0.0037, 0.0207),
}


def test_section_11_3_tier_r() -> None:
    pairs = _load("m13_pairs.json")
    tier_r = cast(dict[str, object], pairs["tier_r"])
    assert tier_r["pass"] is True
    assert tier_r["g13_3_pass"] is True
    assert _node(pairs, "tier_r", "n_pairs") == 332
    for label, (n, mean, sem) in SECTION_11_TIER_R.items():
        assert _node(pairs, "tier_r", "groups", label, "n") == n, label
        assert _quoted(pairs, 4, "tier_r", "groups", label, "mean") == mean, label
        assert _quoted(pairs, 4, "tier_r", "groups", label, "sem_ddof0") == sem, label
    assert _node(pairs, "tier_r", "all_low_z", "n") == 187
    assert _quoted(pairs, 4, "tier_r", "all_low_z", "mean") == -0.0482
    assert _quoted(pairs, 4, "tier_r", "all_low_z", "sem_ddof0") == 0.0058
    assert _quoted(pairs, 4, "tier_r", "differential_lowz_minus_des") == -0.036


def test_section_11_3_tier_p() -> None:
    pairs = _load("m13_pairs.json")
    tier_p = cast(dict[str, object], pairs["tier_p"])
    assert _node(pairs, "tier_p", "n_objects") == 335
    assert _node(pairs, "tier_p", "n_primary_after_exclusion") == 334
    assert tier_p["excluded_cid"] == "1304442"
    rules = cast(dict[str, object], tier_p["duplicate_rule_counts"])
    assert rules == {"same-survey": 332, "smallest-err": 3}
    assert _quoted(pairs, 4, "tier_p", "primary", "s_low_minus_high") == -0.0358
    assert _quoted(pairs, 4, "tier_p", "primary", "sem_s_quadrature") == 0.0080
    assert _node(pairs, "tier_p", "primary", "n_low") == 190
    assert _node(pairs, "tier_p", "primary", "n_high") == 144
    assert _quoted(pairs, 4, "tier_p", "sensitivity_with_1304442", "s_low_minus_high") == -0.0363
    assert (
        _quoted(pairs, 4, "tier_p", "secondary_covariance_aware", "sigma_s_covariance_aware")
        == 0.0334
    )
    assert _quoted(pairs, 4, "tier_p", "descriptive_s_mb_based_all335") == -0.0363
