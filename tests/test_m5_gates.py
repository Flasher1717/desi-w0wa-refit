"""M5 gates as permanent checks against the committed run records.

The raw-pipeline record (results/m5_fits.json) documents the history:
G5.2 FAILED and was audited (RESULTS.md section 5). The P8-corrected
record (results/m5_fits_corrected.json) must satisfy every
pre-registered window (G5.1b-G5.6b, same windows as P4).
"""

import json
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"

ARMS = ("BAO", "BAO+CMB", "BAO+CMB+PantheonPlus", "BAO+CMB+Union3", "BAO+CMB+DES-SN5YR")


def test_raw_pipeline_record_keeps_g52_failure_history() -> None:
    raw = json.loads((RESULTS_DIR / "m5_fits.json").read_text(encoding="utf-8"))
    assert raw["BAO+CMB"]["pass"] is False  # audited, attributed, kept
    for arm in ARMS:
        if arm != "BAO+CMB":
            assert raw[arm]["pass"] is True


def test_corrected_pipeline_passes_all_windows() -> None:
    corrected = json.loads((RESULTS_DIR / "m5_fits_corrected.json").read_text(encoding="utf-8"))
    for key in corrected:
        assert corrected[key]["pass"] is True, key
    for arm in ARMS:
        nsigma = corrected[arm]["nsigma"]
        low, high = corrected[arm]["gate_window"]
        assert low <= nsigma <= high


def test_p8_leaves_the_bao_only_arm_untouched() -> None:
    raw = json.loads((RESULTS_DIR / "m5_fits.json").read_text(encoding="utf-8"))
    corrected = json.loads((RESULTS_DIR / "m5_fits_corrected.json").read_text(encoding="utf-8"))
    assert raw["BAO"]["delta_chi2_map"] == corrected["BAO"]["delta_chi2_map"]
    assert raw["BAO"]["lcdm"] == corrected["BAO"]["lcdm"]
    assert raw["BAO"]["w0wacdm"] == corrected["BAO"]["w0wacdm"]


def test_ordering_gate_recorded() -> None:
    corrected = json.loads((RESULTS_DIR / "m5_fits_corrected.json").read_text(encoding="utf-8"))
    values = corrected["G5.6b_ordering"]["values"]
    assert values[0] < values[1] < values[2]
