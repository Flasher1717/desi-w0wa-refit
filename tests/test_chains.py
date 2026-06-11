"""Tests for the CosmoSIS chain reader (synthetic + pinned real chain)."""

from pathlib import Path

import numpy as np
import pytest

from desi_w0wa_refit.chains import read_cosmosis_chain

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def test_reads_synthetic_weighted_chain(tmp_path: Path) -> None:
    path = tmp_path / "chain.txt"
    path.write_text(
        "#cosmological_parameters--omega_m\tcosmological_parameters--w\tweight\n"
        "#sampler=polychord\n"
        "0.30 -1.00 1.0\n"
        "0.40 -0.80 3.0\n",
        encoding="utf-8",
    )
    chain = read_cosmosis_chain(path)
    assert chain.columns == ("omega_m", "w", "weight")
    assert abs(chain.weighted_mean("omega_m") - (0.3 + 3 * 0.4) / 4.0) < 1e-15
    expected_var = (1.0 * (0.3 - 0.375) ** 2 + 3.0 * (0.4 - 0.375) ** 2) / 4.0
    assert abs(chain.weighted_std("omega_m") - float(np.sqrt(expected_var))) < 1e-15


def test_rejects_file_without_header(tmp_path: Path) -> None:
    path = tmp_path / "bad.txt"
    path.write_text("0.3 0.4\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing CosmoSIS header"):
        read_cosmosis_chain(path)


@pytest.mark.requires_data
def test_reads_pinned_official_des_chain() -> None:
    chain = read_cosmosis_chain(DATA_DIR / "DES-SN5YR_fw0wacdm_SN.txt")
    for name in ("omega_m", "h0", "w", "wa", "weight", "like", "post"):
        assert name in chain.columns
    # Header records nsample=908 for the weighted posterior.
    assert chain.samples.shape[0] == 908
    # Sanity: the weighted means live in the physically expected region
    # (the published degenerate best fit is Omega_m=0.495, w0=-0.36,
    # wa=-8.8; means differ from the MAP but stay inside the priors).
    assert 0.01 < chain.weighted_mean("omega_m") < 0.99
    assert -5.0 < chain.weighted_mean("w") < 1.0
    assert -20.0 < chain.weighted_mean("wa") < 10.0
